"""
Menus - Command-line interface menu functions with exception handling.
"""

import logging
from pathlib import Path

from .scanner import scan_mods_directory
from .manager import toggle_mod, install_mod_from_zip, uninstall_mod
from .config import parse_config_file, save_config_file, get_config_files
from .utils import filter_mods_by_name, format_mod_info, format_dependency_tree
from .dependencies import check_dependencies, find_missing_dependencies, get_dependency_tree
from .settings import get_config_dir, get_downloads_dir
from .thunderstore import (
    fetch_all_packages,
    search_packages,
    get_popular_packages,
    get_recently_updated,
    download_package,
    format_package_info,
    ThunderstorePackage
)
from .exceptions import (
    ModManagerError,
    ModNotFoundError,
    ModAlreadyExistsError,
    InstallationError,
    InvalidZipError,
    UninstallError,
    ConfigError
)

logger = logging.getLogger(__name__)

# Cache for API data
_packages_cache: list[dict] = []


def list_all_mods(plugins_path: str) -> list[dict]:
    """Display a list of all installed mods."""
    try:
        mods = scan_mods_directory(plugins_path)
    except ModManagerError as e:
        print(f"\n✗ Error scanning mods: {e}")
        return []
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        logger.exception("Error scanning mods")
        return []
    
    if not mods:
        print("\nNo mods found in the plugins folder.")
        return []
    
    print(f"\n{'#':<4} {'Status':<10} {'Name':<30} {'Version':<12}")
    print("-" * 60)
    
    for i, mod in enumerate(mods, 1):
        status = "✓ ON" if mod.get("enabled", True) else "✗ OFF"
        name = mod.get("name", "Unknown")[:28]
        version = mod.get("version_number", "?")[:10]
        print(f"{i:<4} {status:<10} {name:<30} {version:<12}")
    
    print(f"\nTotal: {len(mods)} mod(s)")
    return mods


def view_mod_details_menu(plugins_path: str) -> None:
    """Menu to view detailed information about a specific mod."""
    mods = list_all_mods(plugins_path)
    
    if not mods:
        return
    
    try:
        choice = input("\nEnter mod number to view details (0 to cancel): ").strip()
        if choice == "0":
            return
        
        index = int(choice) - 1
        if 0 <= index < len(mods):
            print("\n" + "=" * 50)
            print(format_mod_info(mods[index]))
            print("=" * 50)
        else:
            print("Invalid mod number.")
    except ValueError:
        print("Please enter a valid number.")


def toggle_mod_menu(plugins_path: str) -> None:
    """Menu to enable or disable a mod."""
    mods = list_all_mods(plugins_path)
    
    if not mods:
        return
    
    try:
        choice = input("\nEnter mod number to toggle (0 to cancel): ").strip()
        if choice == "0":
            return
        
        index = int(choice) - 1
        if 0 <= index < len(mods):
            mod = mods[index]
            try:
                success, new_state = toggle_mod(mod["path"])
                if success:
                    state_str = "enabled" if new_state else "disabled"
                    print(f"\n✓ {mod['name']} has been {state_str}.")
                else:
                    print(f"\n✗ Failed to toggle {mod['name']}.")
            except ModNotFoundError as e:
                print(f"\n✗ Mod not found: {e}")
            except ModManagerError as e:
                print(f"\n✗ Error: {e}")
        else:
            print("Invalid mod number.")
    except ValueError:
        print("Please enter a valid number.")


def search_mods_menu(plugins_path: str) -> None:
    """Menu to search for mods by name."""
    try:
        mods = scan_mods_directory(plugins_path)
    except ModManagerError as e:
        print(f"\n✗ Error: {e}")
        return
    
    if not mods:
        print("\nNo mods found.")
        return
    
    search_term = input("\nEnter search term: ").strip()
    
    if not search_term:
        print("No search term provided.")
        return
    
    results = filter_mods_by_name(mods, search_term)
    
    if not results:
        print(f"\nNo mods found matching '{search_term}'.")
        return
    
    print(f"\nFound {len(results)} mod(s) matching '{search_term}':")
    print(f"\n{'#':<4} {'Status':<10} {'Name':<30} {'Version':<12}")
    print("-" * 60)
    
    for i, mod in enumerate(results, 1):
        status = "✓ ON" if mod.get("enabled", True) else "✗ OFF"
        name = mod.get("name", "Unknown")[:28]
        version = mod.get("version_number", "?")[:10]
        print(f"{i:<4} {status:<10} {name:<30} {version:<12}")


def install_mod_menu(plugins_path: str) -> None:
    """Menu to install a mod from a zip file."""
    print("\nInstall mod from zip file")
    print("Enter the path to the mod zip file (or 'cancel'):")
    
    zip_path = input("Path: ").strip()
    
    if zip_path.lower() == "cancel":
        return
    
    # Remove quotes if present
    zip_path = zip_path.strip('"\'')
    
    try:
        success, message = install_mod_from_zip(zip_path, plugins_path)
        print(f"\n✓ {message}")
    except InvalidZipError as e:
        print(f"\n✗ Invalid zip file: {e}")
    except ModAlreadyExistsError as e:
        print(f"\n✗ {e}")
    except InstallationError as e:
        print(f"\n✗ Installation failed: {e}")
    except ModManagerError as e:
        print(f"\n✗ Error: {e}")
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        logger.exception("Installation error")


def uninstall_mod_menu(plugins_path: str) -> None:
    """Menu to uninstall a mod."""
    mods = list_all_mods(plugins_path)
    
    if not mods:
        return
    
    try:
        choice = input("\nEnter mod number to uninstall (0 to cancel): ").strip()
        if choice == "0":
            return
        
        index = int(choice) - 1
        if 0 <= index < len(mods):
            mod = mods[index]
            
            print(f"\n⚠ You are about to uninstall: {mod['name']}")
            confirm = input("Are you sure? (yes/no): ").strip().lower()
            
            if confirm != "yes":
                print("Uninstall cancelled.")
                return
            
            delete_config = False
            config_dir = get_config_dir(plugins_path)
            
            if Path(config_dir).exists():
                config_choice = input("Also delete associated config files? (yes/no): ").strip().lower()
                delete_config = config_choice == "yes"
            
            try:
                success, message = uninstall_mod(mod["path"], delete_config, config_dir)
                print(f"\n✓ {message}")
            except ModNotFoundError as e:
                print(f"\n✗ Mod not found: {e}")
            except UninstallError as e:
                print(f"\n✗ Uninstall failed: {e}")
            except ModManagerError as e:
                print(f"\n✗ Error: {e}")
        else:
            print("Invalid mod number.")
    except ValueError:
        print("Please enter a valid number.")


def check_dependencies_menu(plugins_path: str) -> None:
    """Menu to check dependencies for mods."""
    try:
        mods = scan_mods_directory(plugins_path)
    except ModManagerError as e:
        print(f"\n✗ Error: {e}")
        return
    
    if not mods:
        print("\nNo mods found.")
        return
    
    print("\nDependency Checker")
    print("-" * 40)
    print("[1] Check all mods for missing dependencies")
    print("[2] Check specific mod dependencies")
    print("[3] View dependency tree for a mod")
    print("[0] Back")
    
    choice = input("\nChoose an option: ").strip()
    
    if choice == "0":
        return
    elif choice == "1":
        check_all_dependencies(mods)
    elif choice == "2":
        check_single_mod_dependencies(mods)
    elif choice == "3":
        view_dependency_tree_menu(mods)
    else:
        print("Invalid option.")


def check_all_dependencies(mods: list[dict]) -> None:
    """Check all mods for missing dependencies."""
    print("\nChecking all mods for missing dependencies...")
    
    try:
        missing = find_missing_dependencies(mods)
    except Exception as e:
        print(f"\n✗ Error checking dependencies: {e}")
        return
    
    if not missing:
        print("\n✓ All dependencies are satisfied!")
        return
    
    print(f"\n⚠ Found {len(missing)} mod(s) with missing dependencies:\n")
    
    for mod_name, deps in missing.items():
        print(f"  {mod_name}:")
        for dep in deps:
            print(f"    ✗ {dep}")
        print()


def check_single_mod_dependencies(mods: list[dict]) -> None:
    """Check dependencies for a specific mod."""
    print(f"\n{'#':<4} {'Name':<40}")
    print("-" * 50)
    
    for i, mod in enumerate(mods, 1):
        print(f"{i:<4} {mod.get('name', 'Unknown')[:38]}")
    
    try:
        choice = input("\nEnter mod number (0 to cancel): ").strip()
        if choice == "0":
            return
        
        index = int(choice) - 1
        if 0 <= index < len(mods):
            mod = mods[index]
            result = check_dependencies(mod, mods)
            
            print(f"\nDependencies for: {mod['name']}")
            print("-" * 40)
            
            if not mod.get("dependencies"):
                print("No dependencies.")
                return
            
            for detail in result["details"]:
                dep = detail["dependency"]
                status = detail["status"]
                
                if status == "found":
                    print(f"  ✓ {dep}")
                elif status == "missing":
                    print(f"  ✗ {dep} (MISSING)")
                else:
                    print(f"  ? {dep} (invalid format)")
            
            if result["satisfied"]:
                print("\n✓ All dependencies satisfied!")
            else:
                print(f"\n⚠ Missing {len(result['missing'])} dependency(ies)")
        else:
            print("Invalid mod number.")
    except ValueError:
        print("Please enter a valid number.")


def view_dependency_tree_menu(mods: list[dict]) -> None:
    """View the dependency tree for a mod."""
    print(f"\n{'#':<4} {'Name':<40}")
    print("-" * 50)
    
    for i, mod in enumerate(mods, 1):
        print(f"{i:<4} {mod.get('name', 'Unknown')[:38]}")
    
    try:
        choice = input("\nEnter mod number (0 to cancel): ").strip()
        if choice == "0":
            return
        
        index = int(choice) - 1
        if 0 <= index < len(mods):
            mod = mods[index]
            tree = get_dependency_tree(mod, mods)
            
            print(f"\nDependency Tree for: {mod['name']}")
            print("-" * 40)
            print(format_dependency_tree(tree))
        else:
            print("Invalid mod number.")
    except ValueError:
        print("Please enter a valid number.")


def edit_config_menu(plugins_path: str) -> None:
    """Menu to edit mod configuration files."""
    config_dir = get_config_dir(plugins_path)
    
    try:
        config_files = get_config_files(config_dir)
    except Exception as e:
        print(f"\n✗ Error accessing config directory: {e}")
        return
    
    if not config_files:
        print("\nNo config files found.")
        return
    
    print(f"\nFound {len(config_files)} config file(s):")
    for i, cfg in enumerate(config_files, 1):
        print(f"  [{i}] {cfg.name}")
    
    try:
        choice = input("\nEnter config number to edit (0 to cancel): ").strip()
        if choice == "0":
            return
        
        index = int(choice) - 1
        if 0 <= index < len(config_files):
            edit_config_file(str(config_files[index]))
        else:
            print("Invalid config number.")
    except ValueError:
        print("Please enter a valid number.")


def edit_config_file(config_path: str) -> None:
    """Interactive editor for a config file."""
    try:
        settings = parse_config_file(config_path)
    except ConfigError as e:
        print(f"\n✗ Error reading config: {e}")
        return
    
    if not settings:
        print("No editable settings found in this config file.")
        return
    
    print(f"\nEditing: {Path(config_path).name}")
    print("-" * 50)
    
    setting_list = list(settings.items())
    for i, (key, value) in enumerate(setting_list, 1):
        display_value = value[:40] + "..." if len(value) > 40 else value
        print(f"  [{i}] {key} = {display_value}")
    
    print("\nEnter setting number to edit (0 to save and exit):")
    
    while True:
        try:
            choice = input("\nSetting #: ").strip()
            if choice == "0":
                try:
                    if save_config_file(config_path, settings):
                        print("✓ Config saved successfully.")
                    else:
                        print("✗ Failed to save config.")
                except ConfigError as e:
                    print(f"✗ Error saving config: {e}")
                return
            
            index = int(choice) - 1
            if 0 <= index < len(setting_list):
                key = setting_list[index][0]
                current = settings[key]
                print(f"\nCurrent value: {current}")
                new_value = input("New value (empty to keep current): ").strip()
                if new_value:
                    settings[key] = new_value
                    setting_list[index] = (key, new_value)
                    print(f"✓ Updated: {key} = {new_value}")
            else:
                print("Invalid setting number.")
        except ValueError:
            print("Please enter a valid number.")


# =============================================================================
# Thunderstore Menus
# =============================================================================

def thunderstore_menu(plugins_path: str) -> None:
    """Main menu for Thunderstore browsing and downloading."""
    global _packages_cache
    
    print("\n" + "=" * 50)
    print("  THUNDERSTORE - Browse & Download Mods")
    print("=" * 50)
    
    if not _packages_cache:
        print("\nFetching mod list from Thunderstore...")
        try:
            success, result = fetch_all_packages()
            
            if not success:
                print(f"\n✗ Failed to connect to Thunderstore: {result}")
                print("Please check your internet connection and try again.")
                return
            
            _packages_cache = result
            print(f"✓ Loaded {len(_packages_cache)} packages")
        except Exception as e:
            print(f"\n✗ Error: {e}")
            logger.exception("Thunderstore fetch error")
            return
    
    while True:
        print("\n" + "-" * 40)
        print("[1] Search mods")
        print("[2] Popular mods")
        print("[3] Recently updated")
        print("[4] Refresh mod list")
        print("[0] Back to main menu")
        print("-" * 40)
        
        choice = input("Choose an option: ").strip()
        
        if choice == "0":
            return
        elif choice == "1":
            search_thunderstore_menu(plugins_path)
        elif choice == "2":
            browse_popular_menu(plugins_path)
        elif choice == "3":
            browse_recent_menu(plugins_path)
        elif choice == "4":
            _packages_cache.clear()
            print("\nRefreshing mod list...")
            try:
                success, result = fetch_all_packages()
                if success:
                    _packages_cache.extend(result)
                    print(f"✓ Loaded {len(_packages_cache)} packages")
                else:
                    print(f"✗ Failed: {result}")
            except Exception as e:
                print(f"✗ Error: {e}")
        else:
            print("Invalid option.")


def search_thunderstore_menu(plugins_path: str) -> None:
    """Search for mods on Thunderstore."""
    global _packages_cache
    
    query = input("\nSearch for mods: ").strip()
    
    if not query:
        print("No search term provided.")
        return
    
    print(f"\nSearching for '{query}'...")
    
    try:
        results = search_packages(_packages_cache, query, limit=20)
    except Exception as e:
        print(f"✗ Search error: {e}")
        return
    
    if not results:
        print("No mods found matching your search.")
        return
    
    display_package_list(results, plugins_path)


def browse_popular_menu(plugins_path: str) -> None:
    """Browse popular mods on Thunderstore."""
    global _packages_cache
    
    print("\nFetching popular mods...")
    
    try:
        results = get_popular_packages(_packages_cache, limit=20)
    except Exception as e:
        print(f"✗ Error: {e}")
        return
    
    if not results:
        print("No mods found.")
        return
    
    print("\n📈 Most Popular Mods")
    display_package_list(results, plugins_path)


def browse_recent_menu(plugins_path: str) -> None:
    """Browse recently updated mods on Thunderstore."""
    global _packages_cache
    
    print("\nFetching recently updated mods...")
    
    try:
        results = get_recently_updated(_packages_cache, limit=20)
    except Exception as e:
        print(f"✗ Error: {e}")
        return
    
    if not results:
        print("No mods found.")
        return
    
    print("\n🕐 Recently Updated Mods")
    display_package_list(results, plugins_path)


def display_package_list(packages: list[ThunderstorePackage], plugins_path: str) -> None:
    """Display a list of Thunderstore packages with download option."""
    print(f"\n{'#':<4} {'Name':<35} {'Downloads':<12} {'Version':<10}")
    print("-" * 65)
    
    for i, pkg in enumerate(packages, 1):
        name = pkg.full_name[:33]
        downloads = f"{pkg.downloads:,}"[:10]
        version = pkg.version[:8]
        print(f"{i:<4} {name:<35} {downloads:<12} {version:<10}")
    
    print(f"\nTotal: {len(packages)} mod(s)")
    print("\nEnter mod number to view details and download (0 to go back):")
    
    while True:
        try:
            choice = input("\nMod #: ").strip()
            if choice == "0":
                return
            
            index = int(choice) - 1
            if 0 <= index < len(packages):
                view_and_download_package(packages[index], plugins_path)
                return
            else:
                print("Invalid mod number.")
        except ValueError:
            print("Please enter a valid number.")


def view_and_download_package(package: ThunderstorePackage, plugins_path: str) -> None:
    """View package details and optionally download it."""
    print("\n" + "=" * 50)
    print(format_package_info(package))
    print("=" * 50)
    
    print("\n[1] Download and install this mod")
    print("[2] Download only (don't install)")
    print("[0] Back")
    
    choice = input("\nChoose an option: ").strip()
    
    if choice == "0":
        return
    elif choice == "1":
        download_and_install_package(package, plugins_path)
    elif choice == "2":
        download_only_package(package)
    else:
        print("Invalid option.")


def download_and_install_package(package: ThunderstorePackage, plugins_path: str) -> None:
    """Download a package and install it."""
    try:
        downloads_dir = get_downloads_dir()
    except Exception as e:
        print(f"✗ Error creating downloads directory: {e}")
        return
    
    print(f"\nDownloading {package.full_name}...")
    
    try:
        success, result = download_package(package, str(downloads_dir))
        
        if not success:
            print(f"✗ Download failed: {result}")
            return
        
        print(f"✓ Downloaded to: {result}")
        
        print("\nInstalling...")
        success, message = install_mod_from_zip(result, plugins_path)
        print(f"✓ {message}")
        
        # Check dependencies
        print("\nChecking dependencies...")
        try:
            mods = scan_mods_directory(plugins_path)
            for mod in mods:
                if package.name.lower() in mod.get("name", "").lower():
                    dep_result = check_dependencies(mod, mods)
                    if not dep_result["satisfied"]:
                        print(f"\n⚠ Missing dependencies:")
                        for dep in dep_result["missing"]:
                            print(f"  - {dep}")
                        print("\nYou may need to install these from Thunderstore.")
                    else:
                        print("✓ All dependencies satisfied!")
                    break
        except Exception as e:
            logger.warning(f"Error checking dependencies: {e}")
            
    except InvalidZipError as e:
        print(f"✗ Invalid mod file: {e}")
    except ModAlreadyExistsError as e:
        print(f"✗ {e}")
    except InstallationError as e:
        print(f"✗ Installation failed: {e}")
    except ModManagerError as e:
        print(f"✗ Error: {e}")
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        logger.exception("Download/install error")


def download_only_package(package: ThunderstorePackage) -> None:
    """Download a package without installing it."""
    try:
        downloads_dir = get_downloads_dir()
    except Exception as e:
        print(f"✗ Error creating downloads directory: {e}")
        return
    
    print(f"\nDownloading {package.full_name}...")
    
    try:
        success, result = download_package(package, str(downloads_dir))
        
        if success:
            print(f"✓ Downloaded to: {result}")
        else:
            print(f"✗ Download failed: {result}")
    except Exception as e:
        print(f"✗ Error: {e}")
        logger.exception("Download error")
