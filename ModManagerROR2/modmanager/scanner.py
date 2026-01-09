"""
Mod Scanner - Functions for discovering and parsing installed mods.
"""

import json
import logging
from pathlib import Path

from .exceptions import ManifestError, ModNotFoundError

logger = logging.getLogger(__name__)


def scan_mods_directory(plugins_path: str) -> list[dict]:
    """
    Scan the BepInEx/plugins directory and return a list of mod information.
    
    Args:
        plugins_path: Path to the BepInEx/plugins directory
        
    Returns:
        List of dictionaries containing mod information from manifest.json files
        
    Raises:
        ModNotFoundError: If the plugins directory doesn't exist
    """
    mods = []
    plugins_dir = Path(plugins_path)
    
    if not plugins_dir.exists():
        logger.warning(f"Plugins directory not found: {plugins_path}")
        return mods
    
    if not plugins_dir.is_dir():
        raise ModNotFoundError(f"Path is not a directory: {plugins_path}")
    
    try:
        for mod_folder in plugins_dir.iterdir():
            if mod_folder.is_dir():
                manifest_path = mod_folder / "manifest.json"
                if manifest_path.exists():
                    try:
                        mod_info = parse_manifest(str(manifest_path))
                        if mod_info:
                            mod_info["path"] = str(mod_folder)
                            mod_info["folder_name"] = mod_folder.name.replace(".disabled", "")
                            mod_info["enabled"] = not mod_folder.name.endswith(".disabled")
                            mods.append(mod_info)
                    except ManifestError as e:
                        logger.warning(f"Failed to parse manifest in {mod_folder}: {e}")
                        continue
    except PermissionError as e:
        logger.error(f"Permission denied accessing {plugins_path}: {e}")
        raise ModNotFoundError(f"Permission denied: {plugins_path}")
    
    return sorted(mods, key=lambda m: m.get("name", "").lower())


def parse_manifest(manifest_path: str) -> dict | None:
    """
    Parse a mod's manifest.json file and return its contents.
    
    Args:
        manifest_path: Path to the manifest.json file
        
    Returns:
        Dictionary containing mod metadata, or None if parsing fails
        
    Raises:
        ManifestError: If the manifest file cannot be read or parsed
    """
    path = Path(manifest_path)
    
    if not path.exists():
        return None
    
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
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in manifest: {manifest_path} - {e}")
        return None
    except UnicodeDecodeError as e:
        logger.error(f"Encoding error reading manifest: {manifest_path} - {e}")
        return None
    except IOError as e:
        logger.error(f"IO error reading manifest: {manifest_path} - {e}")
        return None
