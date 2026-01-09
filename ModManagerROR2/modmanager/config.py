"""
Config Editor - Functions for parsing and editing BepInEx config files.
"""

import logging
from pathlib import Path

from .exceptions import ConfigError

logger = logging.getLogger(__name__)


def parse_config_file(config_path: str) -> dict[str, str]:
    """
    Parse a BepInEx config file (.cfg) and extract key-value settings.
    
    Args:
        config_path: Path to the config file
        
    Returns:
        Dictionary of setting names to their values
        
    Raises:
        ConfigError: If the config file cannot be read
    """
    settings = {}
    path = Path(config_path)
    
    if not path.exists():
        logger.debug(f"Config file not found: {config_path}")
        return settings
    
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line or line.startswith("#") or line.startswith("["):
                    continue
                
                if "=" in line:
                    key, _, value = line.partition("=")
                    key = key.strip()
                    value = value.strip()
                    if key:
                        settings[key] = value
    except UnicodeDecodeError as e:
        logger.warning(f"Encoding error in config file {config_path}: {e}")
        # Try with latin-1 encoding as fallback
        try:
            with open(config_path, "r", encoding="latin-1") as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#") or line.startswith("["):
                        continue
                    if "=" in line:
                        key, _, value = line.partition("=")
                        key = key.strip()
                        value = value.strip()
                        if key:
                            settings[key] = value
        except Exception as e2:
            logger.error(f"Failed to read config file: {e2}")
    except PermissionError as e:
        logger.error(f"Permission denied reading config: {config_path}")
        raise ConfigError(f"Permission denied: {config_path}")
    except IOError as e:
        logger.error(f"IO error reading config: {e}")
    
    return settings


    """
    Save modified settings back to a config file, preserving structure.
    
    Args:
        config_path: Path to the config file
        settings: Dictionary of settings to save
        
    Returns:
        True if saved successfully, False otherwise
        
    Raises:
        ConfigError: If the config file cannot be written
    """
def save_config_file(config_path: str, settings: dict[str, str]) -> bool:
    path = Path(config_path)
    
    if not path.exists():
        raise ConfigError(f"Config file not found: {config_path}")
    
    try:
        # Read original file
        with open(config_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
        
        # Update lines with new values
        new_lines = []
        for line in lines:
            stripped = line.strip()
            if stripped and not stripped.startswith("#") and not stripped.startswith("[") and "=" in stripped:
                key, _, _ = stripped.partition("=")
                key = key.strip()
                if key in settings:
                    indent = len(line) - len(line.lstrip())
                    new_lines.append(" " * indent + f"{key} = {settings[key]}\n")
                    continue
            new_lines.append(line)
        
        # Write back
        with open(config_path, "w", encoding="utf-8") as f:
            f.writelines(new_lines)
        
        logger.info(f"Saved config file: {config_path}")
        return True
        
    except PermissionError as e:
        logger.error(f"Permission denied writing config: {config_path}")
        raise ConfigError(f"Permission denied: {config_path}")
    except IOError as e:
        logger.error(f"IO error writing config: {e}")
        return False


    """
    Get all config files in a directory.
    
    Args:
        config_dir: Path to the config directory
        
    Returns:
        List of Path objects for .cfg files
    """
def get_config_files(config_dir: str) -> list[Path]:
    path = Path(config_dir)
    
    if not path.exists():
        logger.debug(f"Config directory not found: {config_dir}")
        return []
    
    try:
        return sorted(path.glob("*.cfg"))
    except PermissionError:
        logger.error(f"Permission denied accessing config directory: {config_dir}")
        return []
