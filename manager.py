"""
Mod Manager - Functions for managing mods (enable/disable, install).
"""

import zipfile
from pathlib import Path

from scanner import parse_manifest


def toggle_mod(mod_path: str) -> tuple[bool, bool]:
    """
    Toggle a mod's enabled/disabled state by renaming its folder.
    
    Args:
        mod_path: Path to the mod folder
        
    Returns:
        Tuple of (success, new_enabled_state)
    """
    path = Path(mod_path)
    
    if not path.exists():
        return False, False
    
    try:
        if path.name.endswith(".disabled"):
            # Enable the mod
            new_path = path.parent / path.name[:-9]  # Remove ".disabled"
            path.rename(new_path)
            return True, True
        else:
            # Disable the mod
            new_path = path.parent / (path.name + ".disabled")
            path.rename(new_path)
            return True, False
    except OSError:
        return False, False


def install_mod_from_zip(zip_path: str, plugins_path: str) -> tuple[bool, str]:
    """
    Install a mod from a zip file to the plugins directory.
    
    Args:
        zip_path: Path to the mod zip file
        plugins_path: Path to the BepInEx/plugins directory
        
    Returns:
        Tuple of (success, message)
    """
    zip_file = Path(zip_path)
    
    if not zip_file.exists():
        return False, f"File not found: {zip_path}"
    
    if not zip_file.suffix.lower() == ".zip":
        return False, "File must be a .zip archive"
    
    if not zipfile.is_zipfile(zip_path):
        return False, "Invalid zip file"
    
    try:
        with zipfile.ZipFile(zip_path, "r") as zf:
            # Check for manifest.json to validate it's a mod
            file_list = zf.namelist()
            has_manifest = any("manifest.json" in f for f in file_list)
            
            if not has_manifest:
                return False, "No manifest.json found - may not be a valid mod"
            
            # Determine mod folder name from zip name
            mod_folder_name = zip_file.stem
            dest_path = Path(plugins_path) / mod_folder_name
            
            # Check if mod already exists
            if dest_path.exists():
                return False, f"Mod folder already exists: {mod_folder_name}"
            
            # Extract to plugins folder
            dest_path.mkdir(parents=True)
            zf.extractall(dest_path)
            
            # Try to get mod name from manifest
            mod_name = mod_folder_name
            manifest_path = dest_path / "manifest.json"
            if manifest_path.exists():
                manifest = parse_manifest(str(manifest_path))
                if manifest:
                    mod_name = manifest.get("name", mod_folder_name)
            
            return True, f"Successfully installed: {mod_name}"
            
    except zipfile.BadZipFile:
        return False, "Corrupted zip file"
    except OSError as e:
        return False, f"Installation failed: {e}"
