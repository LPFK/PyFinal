"""
Menus - Command-line interface menu functions.
"""

from pathlib import Path

from scanner import scan_mods_directory
from manager import toggle_mod, install_mod_from_zip
from config import parse_config_file, save_config_file
from utils import filter_mods_by_name, format_mod_info


def list_all_mods(plugins_path: str) -> None:
    """Display a list of all installed mods."""
    mods = scan_mods_directory(plugins_path)
    
    if not mods:
        print("\nNo mods found in the plugins folder.")
        return
    
    print(f"\n{'#':<4} {'Status':<10} {'Name':<30} {'Version':<12}")
    print("-" * 60)
    
    for i, mod in enumerate(mods, 1):
        status = "✓ ON" if mod.get("enabled", True) else "✗ OFF"
        name = mod.get("name", "Unknown")[:28]
        version = mod.get("version_number", "?")[:10]
        print(f"{i:<4} {status:<10} {name:<30} {version:<12}")
    
    print(f"\nTotal: {len(mods)} mod(s)")


def view_mod_details_menu(plugins_path: str) -> None:
    """Menu to view detailed information about a specific mod."""
    mods = scan_mods_directory(plugins_path)
    
    if not mods:
        print("\nNo mods found.")
        return
    
    list_all_mods(plugins_path)
    
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
    mods = scan_mods_directory(plugins_path)
    
    if not mods:
        print("\nNo mods found.")
        return
    
    list_all_mods(plugins_path)
    
    try:
        choice = input("\nEnter mod number to toggle (0 to cancel): ").strip()
        if choice == "0":
            return
        
        index = int(choice) - 1
        if 0 <= index < len(mods):
            mod = mods[index]
            success, new_state = toggle_mod(mod["path"])
            if success:
                state_str = "enabled" if new_state else "disabled"
                print(f"\n✓ {mod['name']} has been {state_str}.")
            else:
                print(f"\n✗ Failed to toggle {mod['name']}.")
        else:
            print("Invalid mod number.")
    except ValueError:
        print("Please enter a valid number.")


def search_mods_menu(plugins_path: str) -> None:
    """Menu to search for mods by name."""
    mods = scan_mods_directory(plugins_path)
    
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
    
    success, message = install_mod_from_zip(zip_path, plugins_path)
    
    if success:
        print(f"\n✓ {message}")
    else:
        print(f"\n✗ {message}")


def edit_config_menu(plugins_path: str) -> None:
    """Menu to edit mod configuration files."""
    plugins_dir = Path(plugins_path)
    config_dir = plugins_dir.parent / "config"
    
    if not config_dir.exists():
        print(f"\nConfig directory not found: {config_dir}")
        return
    
    config_files = sorted(config_dir.glob("*.cfg"))
    
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
    """
    Interactive editor for a config file.
    
    Args:
        config_path: Path to the config file
    """
    settings = parse_config_file(config_path)
    
    if not settings:
        print("No editable settings found in this config file.")
        return
    
    print(f"\nEditing: {Path(config_path).name}")
    print("-" * 50)
    
    setting_list = list(settings.items())
    for i, (key, value) in enumerate(setting_list, 1):
        print(f"  [{i}] {key} = {value}")
    
    print("\nEnter setting number to edit (0 to save and exit):")
    
    while True:
        try:
            choice = input("\nSetting #: ").strip()
            if choice == "0":
                if save_config_file(config_path, settings):
                    print("✓ Config saved successfully.")
                else:
                    print("✗ Failed to save config.")
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
