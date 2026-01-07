"""
RoR2 Mod Manager - A Risk of Rain 2 Mod Visualizer and Manager | RoR2 Mod Manager - Un gestionnaire de mods pour Risk of Rain 2
Final Project - Python 1
"""

# Import core functions from the package | Importer les fonctions principales du package
from modmanager import (
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

# Import menus | Importer les menus
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


def main():
    """Main entry point for the mod manager."""
    print("=" * 50)
    print("  RoR2 Mod Manager v2.0")
    print("  Risk of Rain 2 Mod Visualizer & Manager")
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
            new_path = setup_plugins_path()
            if new_path:
                plugins_path = new_path
                print(f"Mods folder changed to: {plugins_path}")
        else:
            print("Invalid option. Please try again.")


if __name__ == "__main__":
    main()
