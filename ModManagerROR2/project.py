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

Usage:
    python project.py          # Launch GUI (default)
    python project.py --cli    # Launch CLI mode
    python project.py --help   # Show help

Project Structure:
    project.py              - Main entry point (this file)
    test_project.py         - Tests
    requirements.txt        - Dependencies
    
    modmanager/             - Main package
        __init__.py         - Package exports
        exceptions.py       - Custom exceptions
        scanner.py          - Mod discovery and manifest parsing
        manager.py          - Mod management (toggle, install, uninstall)
        dependencies.py     - Dependency checking
        config.py           - BepInEx config file editing
        utils.py            - Display formatting and utilities
        settings.py         - Application settings
        menus.py            - CLI menu interfaces
        thunderstore.py     - Thunderstore API integration
        gui.py              - GUI interface (tkinter)
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
            print("\n📦 Installed Mods")
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
            print()
            print("  [0] Exit")
            print("=" * 50)
            
            choice = input("Choose an option: ").strip().upper()
            
            if choice == "0":
                print("\nGoodbye! Happy modding!")
                break
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
        elif arg in ("--help", "-h"):
            print(__doc__)
            print("\nOptions:")
            print("  --cli, -c    Run in command-line interface mode")
            print("  --help, -h   Show this help message")
            print("\nDefault: Launch GUI")
            return
        else:
            print(f"Unknown argument: {arg}")
            print("Use --help for usage information.")
            return
    
    # Default: run GUI
    try:
        run_gui()
    except ImportError as e:
        logger.error(f"GUI import error: {e}")
        print("GUI could not be loaded. Falling back to CLI...")
        print("(This may happen if tkinter is not installed)")
        run_cli()
    except Exception as e:
        logger.exception("GUI error")
        print(f"GUI error: {e}")
        print("Falling back to CLI...")
        run_cli()


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.critical(f"Critical error: {e}", exc_info=True)
        print(f"\n✗ Critical error: {e}")
        print("Please check mod_manager.log for details.")
        sys.exit(1)
