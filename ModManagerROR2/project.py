"""
RoR2 Mod Manager v3.0 - A Risk of Rain 2 Mod Visualizer and Manager

Features:
    - List, search, enable/disable installed mods
    - Install mods from local zip files
    - Uninstall mods with optional config cleanup
    - Dependency checking and visualization
    - Browse and download mods from Thunderstore
    - Edit BepInEx config files
    - Comprehensive exception handling
    - GUI and CLI interfaces
    - Start Modded or vanilla

Usage:
    python project.py          # Launch GUI (default)
    python project.py --cli    # Launch CLI mode
    python project.py --help   # Show help
"""

import logging
import sys

# Setup logging
logging.basicConfig(
    level=logging.WARNING,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('mod_manager.log', encoding='utf-8'),
    ]
)
logger = logging.getLogger(__name__)

# Import core functions from the package
from modmanager import (
    # Exceptions
    ModManagerError,
    ManifestError,
    ModNotFoundError,
    ModAlreadyExistsError,
    InstallationError,
    UninstallError,
    ConfigError,
    ThunderstoreError,
    NetworkError,
    DownloadError,
    InvalidZipError,
    DependencyError,
    # Scanner
    scan_mods_directory,
    parse_manifest,
    # Manager
    toggle_mod,
    install_mod_from_zip,
    uninstall_mod,
    # Dependencies
    check_dependencies,
    parse_dependency_string,
    find_missing_dependencies,
    # Config
    parse_config_file,
    save_config_file,
    # Utils
    filter_mods_by_name,
    format_mod_info,
    get_mod_dependencies,
    # Settings
    load_plugins_path,
    setup_plugins_path,
    # Thunderstore
    fetch_all_packages,
    search_packages,
    get_popular_packages,
    download_package,
    parse_package,
    format_package_info,
)


def run_cli():
    """Run the CLI interface."""
    # Import menus only when needed
    from modmanager.menus import (
        list_all_mods,
        view_mod_details_menu,
        toggle_mod_menu,
        search_mods_menu,
        install_mod_menu,
        uninstall_mod_menu,
        check_dependencies_menu,
        edit_config_menu,
        thunderstore_menu,
        launch_game_menu,
    )
    
    print("=" * 50)
    print("  RoR2 Mod Manager v3.0 (CLI)")
    print("  Risk of Rain 2 Mod Visualizer & Manager")
    print("=" * 50)
    
    # Load or setup plugins path
    try:
        plugins_path = load_plugins_path()
    except Exception as e:
        logger.error(f"Error loading config: {e}")
        plugins_path = ""
    
    if not plugins_path:
        print("\nFirst time setup - please configure your mods folder.")
        try:
            plugins_path = setup_plugins_path()
        except KeyboardInterrupt:
            print("\n\nSetup cancelled.")
            return
        except Exception as e:
            print(f"\nError during setup: {e}")
            logger.exception("Setup error")
            return
        
        if not plugins_path:
            print("No valid path provided. Exiting.")
            return
    
    print(f"\nMods folder: {plugins_path}")
    
    while True:
        try:
            print("\n" + "=" * 50)
            print("  MAIN MENU")
            print("=" * 50)
            print("\n🎮 Launch Game")
            print("  [M] Start Vanilla")
            print("  [V] Start Modded")
            print()
            print("📦 Installed Mods")
            print("  [1] List all mods")
            print("  [2] View mod details")
            print("  [3] Enable/Disable mod")
            print("  [4] Search mods")
            print()
            print("🔧 Mod Management")
            print("  [5] Install mod from zip")
            print("  [6] Uninstall mod")
            print("  [7] Check dependencies")
            print()
            print("🌐 Thunderstore")
            print("  [8] Browse & Download mods")
            print()
            print("⚙️  Settings")
            print("  [9] Edit mod config")
            print("  [C] Change mods folder")
            print("  [G] Configure game path")
            print()
            print("  [0] Exit")
            print("=" * 50)
            
            choice = input("Choose an option: ").strip().upper()
            
            if choice == "0":
                print("\nGoodbye! Happy modding!")
                break
            elif choice == "M":
                from modmanager.menus import start_modded_menu
                start_vanilla_menu(plugins_path)
            elif choice == "V":
                from modmanager.menus import start_vanilla_menu
                start_Modded_menu(plugins_path)
            elif choice == "1":
                list_all_mods(plugins_path)
            elif choice == "2":
                view_mod_details_menu(plugins_path)
            elif choice == "3":
                toggle_mod_menu(plugins_path)
            elif choice == "4":
                search_mods_menu(plugins_path)
            elif choice == "5":
                install_mod_menu(plugins_path)
            elif choice == "6":
                uninstall_mod_menu(plugins_path)
            elif choice == "7":
                check_dependencies_menu(plugins_path)
            elif choice == "8":
                thunderstore_menu(plugins_path)
            elif choice == "9":
                edit_config_menu(plugins_path)
            elif choice == "C":
                try:
                    new_path = setup_plugins_path()
                    if new_path:
                        plugins_path = new_path
                        print(f"Mods folder changed to: {plugins_path}")
                except KeyboardInterrupt:
                    print("\nCancelled.")
                except Exception as e:
                    print(f"\nError: {e}")
            elif choice == "G":
                from modmanager.menus import configure_game_path_menu
                configure_game_path_menu(plugins_path)
            else:
                print("Invalid option. Please try again.")
                
        except KeyboardInterrupt:
            print("\n\nUse [0] to exit properly.")
        except Exception as e:
            print(f"\n✗ An unexpected error occurred: {e}")
            logger.exception("Unexpected error in main menu")
            print("The error has been logged. Please try again.")


def run_gui():
    """Run the GUI interface."""
    # Test tkinter availability first
    try:
        import tkinter as tk
        # Test if we can create a window
        test_root = tk.Tk()
        test_root.destroy()
    except ImportError as e:
        print(f"✗ tkinter is not available: {e}")
        print("\nTo fix this on Windows:")
        print("  1. Reinstall Python and check 'tcl/tk and IDLE' option")
        print("  2. Or run: python project.py --cli")
        print("\nFalling back to CLI mode...\n")
        run_cli()
        return
    except Exception as e:
        print(f"✗ tkinter error: {e}")
        print("Falling back to CLI mode...\n")
        run_cli()
        return
    
    # Now run the GUI
    from modmanager import run_gui as _run_gui
    _run_gui()


def main():
    """Main entry point - handles CLI arguments."""
    # Check for command line arguments
    if len(sys.argv) > 1:
        arg = sys.argv[1].lower()
        
        if arg in ("--cli", "-c"):
            run_cli()
            return
        elif arg in ("--gui", "-g"):
            run_gui()
            return
        elif arg in ("--help", "-h"):
            print(__doc__)
            print("\nOptions:")
            print("  --gui, -g    Run graphical interface (default)")
            print("  --cli, -c    Run command-line interface")
            print("  --help, -h   Show this help message")
            return
        else:
            print(f"Unknown argument: {arg}")
            print("Use --help for usage information.")
            return
    
    # Default: try GUI, fall back to CLI
    run_gui()


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.critical(f"Critical error: {e}", exc_info=True)
        print(f"\n✗ Critical error: {e}")
        print("Please check mod_manager.log for details.")
        sys.exit(1)
