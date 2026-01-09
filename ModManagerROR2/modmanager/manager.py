"""
Mod Manager - Functions for managing mods (enable/disable, install, uninstall).
"""

import logging
import shutil
import zipfile
from pathlib import Path

from .exceptions import (
    ModNotFoundError,
    ModAlreadyExistsError,
    InstallationError,
    UninstallError,
    InvalidZipError
)
from .scanner import parse_manifest

logger = logging.getLogger(__name__)


def toggle_mod(mod_path: str) -> tuple[bool, bool]:
    """
    Toggle a mod's enabled/disabled state by renaming its folder.
    
    Args:
        mod_path: Path to the mod folder
        
    Returns:
        Tuple of (success, new_enabled_state)
        
    Raises:
        ModNotFoundError: If the mod folder doesn't exist
    """
    path = Path(mod_path)
    
    if not path.exists():
        raise ModNotFoundError(f"Mod folder not found: {mod_path}")
    
    try:
        if path.name.endswith(".disabled"):
            # Enable the mod
            new_path = path.parent / path.name[:-9]
            if new_path.exists():
                logger.error(f"Cannot enable: {new_path} already exists")
                return False, False
            path.rename(new_path)
            logger.info(f"Enabled mod: {path.name[:-9]}")
            return True, True
        else:
            # Disable the mod
            new_path = path.parent / (path.name + ".disabled")
            if new_path.exists():
                logger.error(f"Cannot disable: {new_path} already exists")
                return False, True
            path.rename(new_path)
            logger.info(f"Disabled mod: {path.name}")
            return True, False
    except PermissionError as e:
        logger.error(f"Permission denied toggling mod: {e}")
        return False, path.name.endswith(".disabled")
    except OSError as e:
        logger.error(f"OS error toggling mod: {e}")
        return False, not path.name.endswith(".disabled")


def install_mod_from_zip(zip_path: str, plugins_path: str) -> tuple[bool, str]:
    """
    Install a mod from a zip file to the plugins directory.
    
    Args:
        zip_path: Path to the mod zip file
        plugins_path: Path to the BepInEx/plugins directory
        
    Returns:
        Tuple of (success, message)
        
    Raises:
        InvalidZipError: If the zip file is invalid
        ModAlreadyExistsError: If the mod already exists
        InstallationError: If installation fails
    """
    zip_file = Path(zip_path)
    
    # Validate zip file exists
    if not zip_file.exists():
        raise InstallationError(f"File not found: {zip_path}")
    
    # Validate extension
    if not zip_file.suffix.lower() == ".zip":
        raise InvalidZipError("File must be a .zip archive")
    
    # Validate it's a real zip file
    if not zipfile.is_zipfile(zip_path):
        raise InvalidZipError("Invalid or corrupted zip file")
    
    try:
        with zipfile.ZipFile(zip_path, "r") as zf:
            file_list = zf.namelist()
            has_manifest = any("manifest.json" in f for f in file_list)
            
            if not has_manifest:
                raise InvalidZipError("No manifest.json found - not a valid mod")
            
            # Determine mod folder name from zip name
            mod_folder_name = zip_file.stem
            dest_path = Path(plugins_path) / mod_folder_name
            
            # Check if mod already exists
            if dest_path.exists():
                raise ModAlreadyExistsError(f"Mod folder already exists: {mod_folder_name}")
            
            disabled_path = Path(plugins_path) / (mod_folder_name + ".disabled")
            if disabled_path.exists():
                raise ModAlreadyExistsError(f"Mod already exists (disabled): {mod_folder_name}")
            
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
            
            logger.info(f"Successfully installed: {mod_name}")
            return True, f"Successfully installed: {mod_name}"
            
    except zipfile.BadZipFile:
        raise InvalidZipError("Corrupted zip file")
    except PermissionError as e:
        raise InstallationError(f"Permission denied: {e}")
    except OSError as e:
        raise InstallationError(f"Installation failed: {e}")


def uninstall_mod(mod_path: str, delete_config: bool = False, config_dir: str | None = None) -> tuple[bool, str]:
    """
    Uninstall a mod by deleting its folder.
    
    Args:
        mod_path: Path to the mod folder
        delete_config: Whether to also delete associated config files
        config_dir: Path to BepInEx/config directory
        
    Returns:
        Tuple of (success, message)
        
    Raises:
        ModNotFoundError: If the mod folder doesn't exist
        UninstallError: If uninstallation fails
    """
    path = Path(mod_path)
    
    if not path.exists():
        raise ModNotFoundError(f"Mod folder not found: {mod_path}")
    
    if not path.is_dir():
        raise UninstallError(f"Not a directory: {mod_path}")
    
    # Get mod info before deletion
    mod_name = path.name.replace(".disabled", "")
    manifest_path = path / "manifest.json"
    if manifest_path.exists():
        try:
            manifest = parse_manifest(str(manifest_path))
            if manifest:
                mod_name = manifest.get("name", mod_name)
        except Exception:
            pass  # Use folder name if manifest fails
    
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
                        try:
                            cfg_file.unlink()
                            deleted_configs.append(cfg_file.name)
                            logger.info(f"Deleted config: {cfg_file.name}")
                        except OSError as e:
                            logger.warning(f"Failed to delete config {cfg_file}: {e}")
        
        if deleted_configs:
            msg = f"Uninstalled {mod_name} and removed config(s): {', '.join(deleted_configs)}"
        else:
            msg = f"Successfully uninstalled: {mod_name}"
        
        logger.info(msg)
        return True, msg
        
    except PermissionError as e:
        raise UninstallError(f"Permission denied: {e}")
    except OSError as e:
        raise UninstallError(f"Uninstall failed: {e}")
