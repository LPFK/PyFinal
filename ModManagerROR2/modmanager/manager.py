"""
Mod Manager - Functions for managing mods (enable/disable, install, uninstall).
"""

import shutil
import zipfile
from pathlib import Path

from .scanner import parse_manifest


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
            new_path = path.parent / path.name[:-9]
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
            
            disabled_path = Path(plugins_path) / (mod_folder_name + ".disabled")
            if disabled_path.exists():
                return False, f"Mod already exists (disabled): {mod_folder_name}"
            
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


def uninstall_mod(mod_path: str, delete_config: bool = False, config_dir: str | None = None) -> tuple[bool, str]:
    """
    Uninstall a mod by deleting its folder.
    
    Args:
        mod_path: Path to the mod folder
        delete_config: Whether to also delete associated config files
        config_dir: Path to BepInEx/config directory
        
    Returns:
        Tuple of (success, message)
    """
    path = Path(mod_path)
    
    if not path.exists():
        return False, f"Mod folder not found: {mod_path}"
    
    if not path.is_dir():
        return False, f"Not a directory: {mod_path}"
    
    mod_name = path.name.replace(".disabled", "")
    manifest_path = path / "manifest.json"
    if manifest_path.exists():
        manifest = parse_manifest(str(manifest_path))
        if manifest:
            mod_name = manifest.get("name", mod_name)
    
    try:
        shutil.rmtree(path)
        
        deleted_configs = []
        
        if delete_config and config_dir:
            config_path = Path(config_dir)
            if config_path.exists():
                folder_name = path.name.replace(".disabled", "").lower()
                
                for cfg_file in config_path.glob("*.cfg"):
                    cfg_name = cfg_file.stem.lower()
                    if folder_name in cfg_name or mod_name.lower() in cfg_name:
                        cfg_file.unlink()
                        deleted_configs.append(cfg_file.name)
        
        if deleted_configs:
            return True, f"Uninstalled {mod_name} and removed config(s): {', '.join(deleted_configs)}"
        else:
            return True, f"Successfully uninstalled: {mod_name}"
            
    except PermissionError:
        return False, f"Permission denied - cannot delete: {mod_path}"
    except OSError as e:
        return False, f"Uninstall failed: {e}"
