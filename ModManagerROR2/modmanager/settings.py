"""
Settings - Application configuration and path management.
"""

import json
import logging
from pathlib import Path

from .exceptions import ConfigError

logger = logging.getLogger(__name__)

CONFIG_FILE = "manager_config.json"


def get_config_path() -> Path:
    """Get the path to the config file (in project root)."""
    return Path(__file__).parent.parent / CONFIG_FILE


def load_plugins_path() -> str:
    """
    Load the saved plugins path from config file.
    
    Returns:
        The saved plugins path, or empty string if not configured
    """
    config_path = get_config_path()
    
    if not config_path.exists():
        logger.debug("Config file not found")
        return ""
    
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)
            path = config.get("plugins_path", "")
            if path and Path(path).exists():
                return path
            elif path:
                logger.warning(f"Saved plugins path no longer exists: {path}")
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in config file: {e}")
    except IOError as e:
        logger.error(f"Error reading config file: {e}")
    
    return ""


def save_plugins_path(plugins_path: str) -> bool:
    """
    Save the plugins path to config file.
    
    Args:
        plugins_path: Path to save
        
    Returns:
        True if saved successfully, False otherwise
    """
    config_path = get_config_path()
    
    try:
        # Load existing config or create new
        config = {}
        if config_path.exists():
            try:
                with open(config_path, "r", encoding="utf-8") as f:
                    config = json.load(f)
            except (json.JSONDecodeError, IOError):
                pass
        
        config["plugins_path"] = plugins_path
        
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2)
        
        logger.info(f"Saved plugins path: {plugins_path}")
        return True
        
    except PermissionError as e:
        logger.error(f"Permission denied saving config: {e}")
        return False
    except IOError as e:
        logger.error(f"Error saving config: {e}")
        return False


def setup_plugins_path() -> str:
    """
    Prompt user to enter their BepInEx/plugins path (CLI version).
    
    Returns:
        Valid plugins path or empty string if cancelled
    """
    print("\nEnter the path to your BepInEx/plugins folder.")
    print("Example: C:/Program Files/Steam/steamapps/common/Risk of Rain 2/BepInEx/plugins")
    print("(or 'cancel' to abort)")
    
    while True:
        try:
            path = input("\nPath: ").strip()
        except (EOFError, KeyboardInterrupt):
            return ""
        
        if path.lower() == "cancel":
            return ""
        
        path_obj = Path(path)
        if path_obj.exists() and path_obj.is_dir():
            save_plugins_path(path)
            return path
        else:
            print(f"Path does not exist or is not a directory: {path}")
            print("Please try again or type 'cancel'.")


def get_config_dir(plugins_path: str) -> str:
    """
    Get the BepInEx/config directory path from plugins path.
    
    Args:
        plugins_path: Path to BepInEx/plugins
        
    Returns:
        Path to BepInEx/config directory
    """
    return str(Path(plugins_path).parent / "config")


def get_downloads_dir() -> Path:
    """
    Get the downloads directory for mod zips.
    
    Returns:
        Path to downloads directory
    """
    downloads = Path(__file__).parent.parent / "downloads"
    try:
        downloads.mkdir(exist_ok=True)
    except PermissionError:
        logger.error("Permission denied creating downloads directory")
        # Fallback to temp directory
        import tempfile
        downloads = Path(tempfile.gettempdir()) / "ror2mm_downloads"
        downloads.mkdir(exist_ok=True)
    return downloads


def validate_plugins_path(path: str) -> tuple[bool, str]:
    """
    Validate that a path is a valid BepInEx plugins directory.
    
    Args:
        path: Path to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not path:
        return False, "Path is empty"
    
    path_obj = Path(path)
    
    if not path_obj.exists():
        return False, "Path does not exist"
    
    if not path_obj.is_dir():
        return False, "Path is not a directory"
    
    # Check if it looks like a BepInEx plugins folder
    parent = path_obj.parent
    if parent.name != "BepInEx":
        logger.warning("Path may not be a BepInEx plugins folder")
    
    return True, ""
