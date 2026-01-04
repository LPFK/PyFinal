"""
RoR2 Mod Manager - A Risk of Rain 2 Mod Visualizer and Manager
Final Project - Python 1

Project Structure:
    project.py      - Main entry point (this file)
    scanner.py      - Mod discovery and manifest parsing
    manager.py      - Mod management (enable/disable, install)
    config.py       - BepInEx config file editing
    utils.py        - Display formatting and utilities
    settings.py     - Application settings
    menus.py        - CLI menu interfaces
"""

# Import core functions - these are the testable functions required by the project
from scanner import scan_mods_directory, parse_manifest
from manager import toggle_mod, install_mod_from_zip
from config import parse_config_file, save_config_file
from utils import filter_mods_by_name, format_mod_info, get_mod_dependencies

# Import settings and menus
from settings import load_plugins_path, setup_plugins_path
from menus import (
    list_all_mods,
    view_mod_details_menu,
    toggle_mod_menu,
    search_mods_menu,
    install_mod_menu,
    edit_config_menu
)


def main():
    """Main entry point for the mod manager."""
    print("=" * 50)
    print("  RoR2 Mod Manager - Risk of Rain 2")
    print("=" * 50)
    
    # Load or setup plugins path
    plugins_path = load_plugins_path()
    
    if not plugins_path:
        print("\nFirst time setup - please configure your mods folder.")
        plugins_path = setup_plugins_path()
        if not plugins_path:
            print("No valid path provided. Exiting.")
            return
    
    print(f"\nMods folder: {plugins_path}")
    
    while True:
        print("\n" + "-" * 40)
        print("[1] List all mods")
        print("[2] View mod details")
        print("[3] Enable/Disable mod")
        print("[4] Search mods")
        print("[5] Install mod from zip")
        print("[6] Edit mod config")
        print("[7] Change mods folder")
        print("[0] Exit")
        print("-" * 40)
        
        choice = input("Choose an option: ").strip()
        
        if choice == "0":
            print("Goodbye!")
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
            edit_config_menu(plugins_path)
        elif choice == "7":
            plugins_path = setup_plugins_path()
            if plugins_path:
                print(f"Mods folder changed to: {plugins_path}")
        else:
            print("Invalid option. Please try again.")


if __name__ == "__main__":
    main()
