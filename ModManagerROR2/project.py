"""
RoR2 Mod Manager - A Risk of Rain 2 manual Mod Visualizer and Manager
Final Project - Python 1 - Live Campus
"""

import json
import os
from pathlib import Path


def main():
    """Main entry point for the mod manager."""
    print("=" * 50)
    print("  RoR2 Mod Manager - Risk of Rain 2")
    print("=" * 50)
    
    # TODO: Implement menu system
    # - List all mods
    # - View mod details
    # - Enable/Disable mods
    # - Search mods
    # - Exit
    
    while True:
        print("\n[1] List all mods")
        print("[2] View mod details")
        print("[3] Enable/Disable mod")
        print("[4] Search mods")
        print("[0] Exit")
        
        choice = input("\nChoose an option: ").strip()
        
        if choice == "0":
            print("Goodbye!")
            break
        elif choice == "1":
            # TODO: Call list_mods function
            pass
        elif choice == "2":
            # TODO: Call view_mod_details function
            pass
        elif choice == "3":
            # TODO: Call toggle_mod function
            pass
        elif choice == "4":
            # TODO: Call search_mods function
            pass
        else:
            print("Invalid option. Please try again.")


    """
    Scan the BepInEx/plugins directory and return a list of mod information.
    
    Args:
        plugins_path: Path to the BepInEx/plugins directory
        
    Returns:
        List of dictionaries containing mod information from manifest.json files
      |
     |
    V
    """
def scan_mods_directory(plugins_path: str) -> list[dict]:

    mods = []
    plugins_dir = Path(plugins_path)
    
    if not plugins_dir.exists():
        return mods
    
    for mod_folder in plugins_dir.iterdir():
        if mod_folder.is_dir():
            manifest_path = mod_folder / "manifest.json"
            if manifest_path.exists():
                mod_info = parse_manifest(str(manifest_path))
                if mod_info:
                    mod_info["path"] = str(mod_folder)
                    mod_info["enabled"] = not mod_folder.name.endswith(".disabled")
                    mods.append(mod_info)
    
    return mods


    """
    Parse a mod's manifest.json file and return its contents.
    
    Args:
        manifest_path: Path to the manifest.json file
        
    Returns:
        Dictionary containing mod metadata, or None if parsing fails
      |
     |
    V
    """
def parse_manifest(manifest_path: str) -> dict | None:
    try:
        with open(manifest_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            return {
                "name": data.get("name", "Unknown"),
                "version_number": data.get("version_number", "0.0.0"),
                "website_url": data.get("website_url", ""),
                "description": data.get("description", "No description"),
                "dependencies": data.get("dependencies", [])
            }
    except (json.JSONDecodeError, FileNotFoundError, IOError):
        return None


    """
    Filter a list of mods by name (case-insensitive search).
    
    Args:
        mods: List of mod dictionaries
        search_term: Search string to filter by
        
    Returns:
        List of mods whose names contain the search term
      |
     |
    V
    """
def filter_mods_by_name(mods: list[dict], search_term: str) -> list[dict]:
    if not search_term:
        return mods
    
    search_lower = search_term.lower()
    return [mod for mod in mods if search_lower in mod.get("name", "").lower()]

    """
    Format a mod's information into a readable string for display.
    
    Args:
        mod: Dictionary containing mod information
        
    Returns:
        Formatted string representation of the mod
      |
     |
    V
    """
def format_mod_info(mod: dict) -> str:
    status = "✓ Enabled" if mod.get("enabled", True) else "✗ Disabled"
    
    lines = [
        f"Name: {mod.get('name', 'Unknown')}",
        f"Version: {mod.get('version_number', '0.0.0')}",
        f"Status: {status}",
        f"Description: {mod.get('description', 'No description')}",
    ]
    
    dependencies = mod.get("dependencies", [])
    if dependencies:
        lines.append(f"Dependencies: {', '.join(dependencies)}")
    
    website = mod.get("website_url", "")
    if website:
        lines.append(f"Website: {website}")
    
    return "\n".join(lines)


    """
    Extract and return the list of dependencies for a mod.
    
    Args:
        mod: Dictionary containing mod information
        
    Returns:
        List of dependency strings
      |
     |
    V
    """
def get_mod_dependencies(mod: dict) -> list[str]:
    return mod.get("dependencies", [])


if __name__ == "__main__":
    main()
