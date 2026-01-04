"""
Mod Scanner - Functions for discovering and parsing mods.
"""

import json
from pathlib import Path


def scan_mods_directory(plugins_path: str) -> list[dict]:
    """
    Scan the BepInEx/plugins directory and return a list of mod information.
    
    Args:
        plugins_path: Path to the BepInEx/plugins directory
        
    Returns:
        List of dictionaries containing mod information from manifest.json files
    """
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
    
    return sorted(mods, key=lambda m: m.get("name", "").lower())


def parse_manifest(manifest_path: str) -> dict | None:
    """
    Parse a mod's manifest.json file and return its contents.
    
    Args:
        manifest_path: Path to the manifest.json file
        
    Returns:
        Dictionary containing mod metadata, or None if parsing fails
    """
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
