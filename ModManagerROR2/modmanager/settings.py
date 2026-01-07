"""
Settings - Application configuration and path management.
"""

import json
from pathlib import Path


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
    if config_path.exists():
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                config = json.load(f)
                path = config.get("plugins_path", "")
                if path and Path(path).exists():
                    return path
        except (json.JSONDecodeError, IOError):
            pass
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
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump({"plugins_path": plugins_path}, f, indent=2)
        return True
    except IOError:
        return False


def setup_plugins_path() -> str:
    """
    Prompt user to enter their BepInEx/plugins path.
    
    Returns:
        Valid plugins path or empty string if cancelled
    """
    print("\nEnter the path to your BepInEx/plugins folder.")
    print("Example: C:/Program Files/Steam/steamapps/common/Risk of Rain 2/BepInEx/plugins")
    print("(or 'cancel' to abort)")
    
    while True:
        path = input("\nPath: ").strip()
        
        if path.lower() == "cancel":
            return ""
        
        if Path(path).exists() and Path(path).is_dir():
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


def get_downloads_dir() -> str:
    """
    Get the downloads directory for mod zips.
    
    Returns:
        Path to downloads directory
    """
    downloads = Path(__file__).parent.parent / "downloads"
    downloads.mkdir(exist_ok=True)
    return str(downloads)
