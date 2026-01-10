"""
GUI Interface for RoR2 Mod Manager using tkinter.
"""

import logging
import threading
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from pathlib import Path

from .scanner import scan_mods_directory
from .manager import toggle_mod, install_mod_from_zip, uninstall_mod
from .dependencies import check_dependencies, find_missing_dependencies
from .settings import (
    load_plugins_path, 
    save_plugins_path, 
    get_config_dir, 
    get_downloads_dir,
    load_game_path,
    save_game_path,
    setup_game_path,
    get_game_path_from_plugins,
    find_game_path,
    launch_modded,
    launch_vanilla,
    ROR2_EXECUTABLE
)
from .thunderstore import (
    fetch_all_packages,
    search_packages,
    get_popular_packages,
    get_recently_updated,
    download_package,
    ThunderstorePackage
)
from .exceptions import (
    ModManagerError,
    ModNotFoundError,
    ModAlreadyExistsError,
    InstallationError,
    InvalidZipError,
    UninstallError
)

logger = logging.getLogger(__name__)


class ModManagerApp:
    """Main GUI Application for RoR2 Mod Manager."""
    
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("RoR2 Mod Manager v3.0")
        self.root.geometry("900x600")
        self.root.minsize(800, 500)
        
        # State
        self.plugins_path = ""
        self.game_path = ""
        self.mods: list[dict] = []
        self.packages_cache: list[dict] = []
        self.thunderstore_results: list[ThunderstorePackage] = []
        
        # Setup UI
        self._setup_styles()
        self._create_widgets()
        self._load_config()
    
    def _setup_styles(self):
        """Configure ttk styles."""
        style = ttk.Style()
        style.configure("Title.TLabel", font=("Segoe UI", 14, "bold"))
        style.configure("Header.TLabel", font=("Segoe UI", 11, "bold"))
        style.configure("Status.TLabel", font=("Segoe UI", 9))
        style.configure("Enabled.TLabel", foreground="green")
        style.configure("Disabled.TLabel", foreground="gray")
    
    def _create_widgets(self):
        """Create all GUI widgets."""
        # Main container
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Top bar with path
        self._create_top_bar()
        
        # Notebook (tabs)
        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        
        # Tabs
        self._create_mods_tab()
        self._create_thunderstore_tab()
        self._create_dependencies_tab()
        
        # Status bar
        self._create_status_bar()
    
    def _create_top_bar(self):
        """Create top bar with path selection and launch buttons."""
        top_frame = ttk.Frame(self.main_frame)
        top_frame.pack(fill=tk.X, pady=(0, 5))
        
        # Left side - path config
        path_frame = ttk.Frame(top_frame)
        path_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        ttk.Label(path_frame, text="Plugins Folder:", style="Header.TLabel").pack(side=tk.LEFT)
        
        self.path_var = tk.StringVar(value="Not configured")
        self.path_label = ttk.Label(path_frame, textvariable=self.path_var, 
                                     style="Status.TLabel", width=50)
        self.path_label.pack(side=tk.LEFT, padx=(10, 10))
        
        ttk.Button(path_frame, text="Browse...", command=self._browse_path).pack(side=tk.LEFT)
        ttk.Button(path_frame, text="Refresh", command=self._refresh_mods).pack(side=tk.LEFT, padx=(5, 0))
        
        # Right side - launch buttons
        launch_frame = ttk.Frame(top_frame)
        launch_frame.pack(side=tk.RIGHT)
        
        ttk.Button(launch_frame, text="🎮 Start Vanilla", 
                   command=self._launch_modded).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(launch_frame, text="🎮 Start Modded", 
                   command=self._launch_vanilla).pack(side=tk.LEFT)
    
    def _create_mods_tab(self):
        """Create the installed mods tab."""
        mods_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(mods_frame, text="📦 Installed Mods")
        
        # Search bar
        search_frame = ttk.Frame(mods_frame)
        search_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(search_frame, text="Search:").pack(side=tk.LEFT)
        self.search_var = tk.StringVar()
        self.search_var.trace("w", lambda *args: self._filter_mods())
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=30)
        search_entry.pack(side=tk.LEFT, padx=(5, 10))
        
        # Buttons
        ttk.Button(search_frame, text="Install from ZIP", 
                   command=self._install_from_zip).pack(side=tk.RIGHT)
        
        # Mods list
        list_frame = ttk.Frame(mods_frame)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        # Treeview
        columns = ("status", "name", "version", "description")
        self.mods_tree = ttk.Treeview(list_frame, columns=columns, show="headings", 
                                       selectmode="browse")
        
        self.mods_tree.heading("status", text="Status")
        self.mods_tree.heading("name", text="Name")
        self.mods_tree.heading("version", text="Version")
        self.mods_tree.heading("description", text="Description")
        
        self.mods_tree.column("status", width=80, minwidth=60)
        self.mods_tree.column("name", width=200, minwidth=150)
        self.mods_tree.column("version", width=80, minwidth=60)
        self.mods_tree.column("description", width=400, minwidth=200)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, 
                                   command=self.mods_tree.yview)
        self.mods_tree.configure(yscrollcommand=scrollbar.set)
        
        self.mods_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Context buttons
        btn_frame = ttk.Frame(mods_frame)
        btn_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(btn_frame, text="Toggle Enable/Disable", 
                   command=self._toggle_selected_mod).pack(side=tk.LEFT)
        ttk.Button(btn_frame, text="View Details", 
                   command=self._view_mod_details).pack(side=tk.LEFT, padx=(5, 0))
        ttk.Button(btn_frame, text="Uninstall", 
                   command=self._uninstall_selected_mod).pack(side=tk.LEFT, padx=(5, 0))
        ttk.Button(btn_frame, text="Check Dependencies", 
                   command=self._check_mod_dependencies).pack(side=tk.LEFT, padx=(5, 0))
    
    def _create_thunderstore_tab(self):
        """Create the Thunderstore browser tab."""
        ts_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(ts_frame, text="🌐 Thunderstore")
        
        # Search bar
        search_frame = ttk.Frame(ts_frame)
        search_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(search_frame, text="Search:").pack(side=tk.LEFT)
        self.ts_search_var = tk.StringVar()
        ts_search_entry = ttk.Entry(search_frame, textvariable=self.ts_search_var, width=30)
        ts_search_entry.pack(side=tk.LEFT, padx=(5, 5))
        ts_search_entry.bind("<Return>", lambda e: self._search_thunderstore())
        
        ttk.Button(search_frame, text="Search", 
                   command=self._search_thunderstore).pack(side=tk.LEFT)
        ttk.Button(search_frame, text="Popular", 
                   command=self._show_popular).pack(side=tk.LEFT, padx=(10, 0))
        ttk.Button(search_frame, text="Recent", 
                   command=self._show_recent).pack(side=tk.LEFT, padx=(5, 0))
        ttk.Button(search_frame, text="Refresh Cache", 
                   command=self._refresh_thunderstore).pack(side=tk.RIGHT)
        
        # Results list
        list_frame = ttk.Frame(ts_frame)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        columns = ("name", "downloads", "version", "description")
        self.ts_tree = ttk.Treeview(list_frame, columns=columns, show="headings",
                                     selectmode="browse")
        
        self.ts_tree.heading("name", text="Name")
        self.ts_tree.heading("downloads", text="Downloads")
        self.ts_tree.heading("version", text="Version")
        self.ts_tree.heading("description", text="Description")
        
        self.ts_tree.column("name", width=200, minwidth=150)
        self.ts_tree.column("downloads", width=100, minwidth=80)
        self.ts_tree.column("version", width=80, minwidth=60)
        self.ts_tree.column("description", width=400, minwidth=200)
        
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL,
                                   command=self.ts_tree.yview)
        self.ts_tree.configure(yscrollcommand=scrollbar.set)
        
        self.ts_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Download button
        btn_frame = ttk.Frame(ts_frame)
        btn_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(btn_frame, text="Download & Install", 
                   command=self._download_and_install).pack(side=tk.LEFT)
        ttk.Button(btn_frame, text="View Details", 
                   command=self._view_package_details).pack(side=tk.LEFT, padx=(5, 0))
        
        # Status label
        self.ts_status_var = tk.StringVar(value="Click 'Popular' or search to browse mods")
        ttk.Label(btn_frame, textvariable=self.ts_status_var, 
                  style="Status.TLabel").pack(side=tk.RIGHT)
    
    def _create_dependencies_tab(self):
        """Create the dependencies checker tab."""
        dep_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(dep_frame, text="🔗 Dependencies")
        
        # Buttons
        btn_frame = ttk.Frame(dep_frame)
        btn_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(btn_frame, text="Check All Mods", 
                   command=self._check_all_dependencies).pack(side=tk.LEFT)
        
        # Results text
        text_frame = ttk.Frame(dep_frame)
        text_frame.pack(fill=tk.BOTH, expand=True)
        
        self.dep_text = tk.Text(text_frame, wrap=tk.WORD, font=("Consolas", 10))
        scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL,
                                   command=self.dep_text.yview)
        self.dep_text.configure(yscrollcommand=scrollbar.set)
        
        self.dep_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.dep_text.insert(tk.END, "Click 'Check All Mods' to scan for missing dependencies.")
        self.dep_text.config(state=tk.DISABLED)
    
    def _create_status_bar(self):
        """Create bottom status bar."""
        status_frame = ttk.Frame(self.main_frame)
        status_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.status_var = tk.StringVar(value="Ready")
        ttk.Label(status_frame, textvariable=self.status_var, 
                  style="Status.TLabel").pack(side=tk.LEFT)
        
        self.mod_count_var = tk.StringVar(value="")
        ttk.Label(status_frame, textvariable=self.mod_count_var,
                  style="Status.TLabel").pack(side=tk.RIGHT)
    
    # =========================================================================
    # Config & Path
    # =========================================================================
    
    def _load_config(self):
        """Load saved configuration."""
        try:
            self.plugins_path = load_plugins_path()
            if self.plugins_path:
                self.path_var.set(self.plugins_path)
                self._refresh_mods()
                # Try to auto-detect game path
                self._load_game_path()
            else:
                self._browse_path()
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            self._browse_path()
    
    def _load_game_path(self):
        """Load or auto-detect game path."""
        self.game_path = load_game_path()
        
        if not self.game_path and self.plugins_path:
            # Try to derive from plugins path
            self.game_path = get_game_path_from_plugins(self.plugins_path)
            if self.game_path:
                save_game_path(self.game_path)
        
        if not self.game_path:
            # Try auto-detection
            self.game_path = find_game_path()
            if self.game_path:
                save_game_path(self.game_path)
    
    def _browse_path(self):
        """Open folder browser for plugins path."""
        path = filedialog.askdirectory(
            title="Select BepInEx/plugins folder",
            initialdir=self.plugins_path or Path.home()
        )
        
        if path:
            self.plugins_path = path
            self.path_var.set(path)
            try:
                save_plugins_path(path)
            except Exception as e:
                logger.error(f"Error saving path: {e}")
            self._refresh_mods()
            self._load_game_path()
    
    # =========================================================================
    # Game Launch
    # =========================================================================
    
    def _launch_modded(self):
        """Launch the game with mods enabled."""
        if not self._ensure_game_path():
            return
        
        self.status_var.set("Launching modded...")
        self.root.update()
        
        success, message = launch_modded(self.game_path)
        
        if success:
            self.status_var.set(message)
            messagebox.showinfo("Launching", message)
        else:
            self.status_var.set("Launch failed")
            messagebox.showerror("Launch Failed", message)
    
    def _launch_vanilla(self):
        """Launch the game without mods."""
        if not self._ensure_game_path():
            return
        
        self.status_var.set("Launching vanilla...")
        self.root.update()
        
        success, message = launch_vanilla(self.game_path)
        
        if success:
            self.status_var.set(message)
            messagebox.showinfo("Launching", message)
        else:
            self.status_var.set("Launch failed")
            messagebox.showerror("Launch Failed", message)
    
    def _ensure_game_path(self) -> bool:
        """Ensure game path is configured, prompt if not."""
        if self.game_path:
            return True
        
        # Try auto-detection first
        self._load_game_path()
        if self.game_path:
            return True
        
        # Ask user to browse
        messagebox.showinfo(
            "Game Path Required",
            "Please select your Risk of Rain 2 installation folder.\n\n"
            f"Look for the folder containing '{ROR2_EXECUTABLE}'."
        )
        
        path = filedialog.askdirectory(
            title="Select Risk of Rain 2 folder",
            initialdir=Path.home()
        )
        
        if path:
            exe_path = Path(path) / ROR2_EXECUTABLE
            if exe_path.exists():
                self.game_path = path
                save_game_path(path)
                return True
            else:
                messagebox.showerror(
                    "Invalid Path",
                    f"Could not find '{ROR2_EXECUTABLE}' in that folder.\n"
                    "Please select the correct Risk of Rain 2 folder."
                )
        
        return False
    
    # =========================================================================
    # Installed Mods
    # =========================================================================
    
    def _refresh_mods(self):
        """Refresh the mods list."""
        if not self.plugins_path:
            return
        
        self.status_var.set("Loading mods...")
        self.root.update()
        
        try:
            self.mods = scan_mods_directory(self.plugins_path)
            self._populate_mods_tree(self.mods)
            self.mod_count_var.set(f"{len(self.mods)} mod(s)")
            self.status_var.set("Ready")
        except ModManagerError as e:
            messagebox.showerror("Error", f"Failed to scan mods:\n{e}")
            self.status_var.set("Error loading mods")
        except Exception as e:
            logger.exception("Error refreshing mods")
            messagebox.showerror("Error", f"Unexpected error:\n{e}")
            self.status_var.set("Error")
    
    def _populate_mods_tree(self, mods: list[dict]):
        """Populate the mods treeview."""
        self.mods_tree.delete(*self.mods_tree.get_children())
        
        for mod in mods:
            status = "✓ ON" if mod.get("enabled", True) else "✗ OFF"
            name = mod.get("name", "Unknown")
            version = mod.get("version_number", "?")
            desc = mod.get("description", "")[:100]
            
            self.mods_tree.insert("", tk.END, values=(status, name, version, desc))
    
    def _filter_mods(self):
        """Filter mods based on search term."""
        search_term = self.search_var.get().lower()
        
        if not search_term:
            filtered = self.mods
        else:
            filtered = [m for m in self.mods 
                        if search_term in m.get("name", "").lower()]
        
        self._populate_mods_tree(filtered)
    
    def _get_selected_mod(self) -> dict | None:
        """Get the currently selected mod."""
        selection = self.mods_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a mod first.")
            return None
        
        item = self.mods_tree.item(selection[0])
        mod_name = item["values"][1]
        
        for mod in self.mods:
            if mod.get("name") == mod_name:
                return mod
        return None
    
    def _toggle_selected_mod(self):
        """Toggle the selected mod's enabled state."""
        mod = self._get_selected_mod()
        if not mod:
            return
        
        try:
            success, new_state = toggle_mod(mod["path"])
            if success:
                state_str = "enabled" if new_state else "disabled"
                self.status_var.set(f"{mod['name']} {state_str}")
                self._refresh_mods()
            else:
                messagebox.showerror("Error", f"Failed to toggle {mod['name']}")
        except ModNotFoundError as e:
            messagebox.showerror("Error", f"Mod not found:\n{e}")
        except ModManagerError as e:
            messagebox.showerror("Error", f"Error:\n{e}")
    
    def _view_mod_details(self):
        """Show detailed info about selected mod."""
        mod = self._get_selected_mod()
        if not mod:
            return
        
        details = f"""Name: {mod.get('name', 'Unknown')}
Version: {mod.get('version_number', '?')}
Status: {'Enabled' if mod.get('enabled', True) else 'Disabled'}
Folder: {mod.get('folder_name', '?')}

Description:
{mod.get('description', 'No description')}

Dependencies ({len(mod.get('dependencies', []))}):
{chr(10).join('  • ' + d for d in mod.get('dependencies', [])) or '  None'}

Path: {mod.get('path', '?')}"""
        
        # Create detail window
        detail_win = tk.Toplevel(self.root)
        detail_win.title(f"Mod Details - {mod.get('name', 'Unknown')}")
        detail_win.geometry("500x400")
        
        text = tk.Text(detail_win, wrap=tk.WORD, padx=10, pady=10)
        text.pack(fill=tk.BOTH, expand=True)
        text.insert(tk.END, details)
        text.config(state=tk.DISABLED)
    
    def _uninstall_selected_mod(self):
        """Uninstall the selected mod."""
        mod = self._get_selected_mod()
        if not mod:
            return
        
        confirm = messagebox.askyesno(
            "Confirm Uninstall",
            f"Are you sure you want to uninstall '{mod['name']}'?\n\nThis cannot be undone."
        )
        
        if not confirm:
            return
        
        delete_config = messagebox.askyesno(
            "Delete Config?",
            "Also delete associated config files?"
        )
        
        config_dir = get_config_dir(self.plugins_path) if delete_config else None
        
        try:
            success, message = uninstall_mod(mod["path"], delete_config, config_dir)
            messagebox.showinfo("Success", message)
            self._refresh_mods()
        except ModNotFoundError as e:
            messagebox.showerror("Error", f"Mod not found:\n{e}")
        except UninstallError as e:
            messagebox.showerror("Error", f"Uninstall failed:\n{e}")
        except ModManagerError as e:
            messagebox.showerror("Error", f"Error:\n{e}")
    
    def _check_mod_dependencies(self):
        """Check dependencies for selected mod."""
        mod = self._get_selected_mod()
        if not mod:
            return
        
        result = check_dependencies(mod, self.mods)
        
        if result["satisfied"]:
            messagebox.showinfo("Dependencies", 
                               f"✓ All dependencies for '{mod['name']}' are satisfied!")
        else:
            missing = "\n".join(f"  • {d}" for d in result["missing"])
            messagebox.showwarning("Missing Dependencies",
                                   f"'{mod['name']}' is missing dependencies:\n\n{missing}")
    
    def _install_from_zip(self):
        """Install a mod from a ZIP file."""
        if not self.plugins_path:
            messagebox.showwarning("No Path", "Please configure your plugins folder first.")
            return
        
        zip_path = filedialog.askopenfilename(
            title="Select mod ZIP file",
            filetypes=[("ZIP files", "*.zip"), ("All files", "*.*")]
        )
        
        if not zip_path:
            return
        
        self.status_var.set("Installing...")
        self.root.update()
        
        try:
            success, message = install_mod_from_zip(zip_path, self.plugins_path)
            messagebox.showinfo("Success", message)
            self._refresh_mods()
        except InvalidZipError as e:
            messagebox.showerror("Invalid ZIP", f"Invalid mod file:\n{e}")
        except ModAlreadyExistsError as e:
            messagebox.showerror("Already Exists", str(e))
        except InstallationError as e:
            messagebox.showerror("Installation Failed", str(e))
        except ModManagerError as e:
            messagebox.showerror("Error", str(e))
        finally:
            self.status_var.set("Ready")
    
    # =========================================================================
    # Thunderstore
    # =========================================================================
    
    def _ensure_packages_cache(self) -> bool:
        """Ensure packages are loaded, return False if failed."""
        if self.packages_cache:
            return True
        
        self.ts_status_var.set("Fetching mods from Thunderstore...")
        self.root.update()
        
        try:
            success, result = fetch_all_packages()
            if success:
                self.packages_cache = result
                self.ts_status_var.set(f"Loaded {len(result)} packages")
                return True
            else:
                self.ts_status_var.set(f"Failed: {result}")
                messagebox.showerror("Connection Error", 
                                    f"Failed to connect to Thunderstore:\n{result}")
                return False
        except Exception as e:
            logger.exception("Thunderstore fetch error")
            self.ts_status_var.set("Error fetching packages")
            messagebox.showerror("Error", f"Error:\n{e}")
            return False
    
    def _refresh_thunderstore(self):
        """Force refresh the Thunderstore cache."""
        self.packages_cache = []
        self._ensure_packages_cache()
    
    def _populate_ts_tree(self, packages: list[ThunderstorePackage]):
        """Populate Thunderstore results tree."""
        self.ts_tree.delete(*self.ts_tree.get_children())
        self.thunderstore_results = packages
        
        for pkg in packages:
            self.ts_tree.insert("", tk.END, values=(
                pkg.full_name,
                f"{pkg.downloads:,}",
                pkg.version,
                pkg.description[:80]
            ))
        
        self.ts_status_var.set(f"Showing {len(packages)} package(s)")
    
    def _search_thunderstore(self):
        """Search Thunderstore for mods."""
        if not self._ensure_packages_cache():
            return
        
        query = self.ts_search_var.get().strip()
        if not query:
            messagebox.showinfo("Search", "Please enter a search term.")
            return
        
        results = search_packages(self.packages_cache, query, limit=50)
        self._populate_ts_tree(results)
        
        if not results:
            self.ts_status_var.set(f"No results for '{query}'")
    
    def _show_popular(self):
        """Show popular packages."""
        if not self._ensure_packages_cache():
            return
        
        results = get_popular_packages(self.packages_cache, limit=50)
        self._populate_ts_tree(results)
    
    def _show_recent(self):
        """Show recently updated packages."""
        if not self._ensure_packages_cache():
            return
        
        results = get_recently_updated(self.packages_cache, limit=50)
        self._populate_ts_tree(results)
    
    def _get_selected_package(self) -> ThunderstorePackage | None:
        """Get the selected Thunderstore package."""
        selection = self.ts_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a package first.")
            return None
        
        item = self.ts_tree.item(selection[0])
        pkg_name = item["values"][0]
        
        for pkg in self.thunderstore_results:
            if pkg.full_name == pkg_name:
                return pkg
        return None
    
    def _view_package_details(self):
        """Show details for selected package."""
        pkg = self._get_selected_package()
        if not pkg:
            return
        
        deps = "\n".join(f"  • {d}" for d in pkg.dependencies[:15]) or "  None"
        if len(pkg.dependencies) > 15:
            deps += f"\n  ... and {len(pkg.dependencies) - 15} more"
        
        details = f"""Name: {pkg.full_name}
Author: {pkg.owner}
Version: {pkg.version}
Downloads: {pkg.downloads:,}
Rating: {pkg.rating}

Description:
{pkg.description}

Categories: {', '.join(pkg.categories) or 'None'}

Dependencies ({len(pkg.dependencies)}):
{deps}"""
        
        if pkg.is_deprecated:
            details += "\n\n⚠ This package is DEPRECATED"
        
        detail_win = tk.Toplevel(self.root)
        detail_win.title(f"Package Details - {pkg.full_name}")
        detail_win.geometry("550x450")
        
        text = tk.Text(detail_win, wrap=tk.WORD, padx=10, pady=10)
        text.pack(fill=tk.BOTH, expand=True)
        text.insert(tk.END, details)
        text.config(state=tk.DISABLED)
    
    def _download_and_install(self):
        """Download and install selected package."""
        pkg = self._get_selected_package()
        if not pkg:
            return
        
        if not self.plugins_path:
            messagebox.showwarning("No Path", "Please configure your plugins folder first.")
            return
        
        # Run in thread to not block UI
        def do_download():
            self.ts_status_var.set(f"Downloading {pkg.full_name}...")
            self.root.update()
            
            try:
                downloads_dir = get_downloads_dir()
                success, result = download_package(pkg, str(downloads_dir))
                
                if not success:
                    self.root.after(0, lambda: messagebox.showerror("Download Failed", result))
                    self.root.after(0, lambda: self.ts_status_var.set("Download failed"))
                    return
                
                self.root.after(0, lambda: self.ts_status_var.set("Installing..."))
                
                success, message = install_mod_from_zip(result, self.plugins_path)
                
                self.root.after(0, lambda: messagebox.showinfo("Success", message))
                self.root.after(0, self._refresh_mods)
                self.root.after(0, lambda: self.ts_status_var.set("Installation complete"))
                
            except ModAlreadyExistsError as e:
                self.root.after(0, lambda: messagebox.showerror("Already Installed", str(e)))
                self.root.after(0, lambda: self.ts_status_var.set("Mod already installed"))
            except (InvalidZipError, InstallationError) as e:
                self.root.after(0, lambda: messagebox.showerror("Installation Failed", str(e)))
                self.root.after(0, lambda: self.ts_status_var.set("Installation failed"))
            except Exception as e:
                logger.exception("Download/install error")
                self.root.after(0, lambda: messagebox.showerror("Error", str(e)))
                self.root.after(0, lambda: self.ts_status_var.set("Error"))
        
        thread = threading.Thread(target=do_download, daemon=True)
        thread.start()
    
    # =========================================================================
    # Dependencies
    # =========================================================================
    
    def _check_all_dependencies(self):
        """Check all mods for missing dependencies."""
        if not self.mods:
            self._refresh_mods()
        
        if not self.mods:
            messagebox.showinfo("No Mods", "No mods found to check.")
            return
        
        self.dep_text.config(state=tk.NORMAL)
        self.dep_text.delete(1.0, tk.END)
        
        try:
            missing = find_missing_dependencies(self.mods)
            
            if not missing:
                self.dep_text.insert(tk.END, "✓ All dependencies are satisfied!\n\n")
                self.dep_text.insert(tk.END, f"Checked {len(self.mods)} mod(s).")
            else:
                self.dep_text.insert(tk.END, f"⚠ Found {len(missing)} mod(s) with missing dependencies:\n\n")
                
                for mod_name, deps in missing.items():
                    self.dep_text.insert(tk.END, f"📦 {mod_name}\n")
                    for dep in deps:
                        self.dep_text.insert(tk.END, f"   ✗ {dep}\n")
                    self.dep_text.insert(tk.END, "\n")
                
                self.dep_text.insert(tk.END, "\nYou can download missing dependencies from Thunderstore.")
        except Exception as e:
            logger.exception("Error checking dependencies")
            self.dep_text.insert(tk.END, f"Error checking dependencies:\n{e}")
        
        self.dep_text.config(state=tk.DISABLED)


def run_gui():
    """Launch the GUI application."""
    root = tk.Tk()
    app = ModManagerApp(root)
    root.mainloop()


if __name__ == "__main__":
    run_gui()
