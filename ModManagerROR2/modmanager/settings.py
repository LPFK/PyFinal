"""
Settings - Application configuration and path management.
"""

import json
import logging
import os
import subprocess
import sys
from pathlib import Path

from .exceptions import ConfigError

logger = logging.getLogger(__name__)

CONFIG_FILE = "manager_config.json"

# Default Steam paths to search for RoR2
DEFAULT_STEAM_PATHS = [
    r"C:\Program Files (x86)\Steam\steamapps\common\Risk of Rain 2",
    r"C:\Program Files\Steam\steamapps\common\Risk of Rain 2",
    r"D:\Steam\steamapps\common\Risk of Rain 2",
    r"D:\SteamLibrary\steamapps\common\Risk of Rain 2",
    r"E:\Steam\steamapps\common\Risk of Rain 2",
    r"E:\SteamLibrary\steamapps\common\Risk of Rain 2",
]

ROR2_EXECUTABLE = "Risk of Rain 2.exe"
ROR2_STEAM_ID = "632360"


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


# =============================================================================
# Game Path and Launching
# =============================================================================

def get_game_path_from_plugins(plugins_path: str) -> str:
    """
    Derive the game installation path from the plugins path.
    
    Args:
        plugins_path: Path to BepInEx/plugins
        
    Returns:
        Path to game directory, or empty string if not found
    """
    if not plugins_path:
        return ""
    
    # plugins_path is typically: .../Risk of Rain 2/BepInEx/plugins
    # Game path is: .../Risk of Rain 2
    path = Path(plugins_path)
    
    # Go up from plugins -> BepInEx -> Risk of Rain 2
    game_path = path.parent.parent
    
    exe_path = game_path / ROR2_EXECUTABLE
    if exe_path.exists():
        return str(game_path)
    
    return ""


def load_game_path() -> str:
    """
    Load the saved game path from config file.
    
    Returns:
        The saved game path, or empty string if not configured
    """
    config_path = get_config_path()
    
    if not config_path.exists():
        return ""
    
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)
            path = config.get("game_path", "")
            if path and Path(path).exists():
                return path
    except (json.JSONDecodeError, IOError) as e:
        logger.error(f"Error reading game path: {e}")
    
    return ""


def save_game_path(game_path: str) -> bool:
    """
    Save the game path to config file.
    
    Args:
        game_path: Path to save
        
    Returns:
        True if saved successfully
    """
    config_path = get_config_path()
    
    try:
        config = {}
        if config_path.exists():
            try:
                with open(config_path, "r", encoding="utf-8") as f:
                    config = json.load(f)
            except (json.JSONDecodeError, IOError):
                pass
        
        config["game_path"] = game_path
        
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2)
        
        logger.info(f"Saved game path: {game_path}")
        return True
        
    except (PermissionError, IOError) as e:
        logger.error(f"Error saving game path: {e}")
        return False


def find_game_path() -> str:
    """
    Try to automatically find the RoR2 installation.
    
    Returns:
        Game path if found, empty string otherwise
    """
    # Check default Steam locations
    for steam_path in DEFAULT_STEAM_PATHS:
        exe_path = Path(steam_path) / ROR2_EXECUTABLE
        if exe_path.exists():
            logger.info(f"Found game at: {steam_path}")
            return steam_path
    
    return ""


def setup_game_path(plugins_path: str = "") -> str:
    """
    Setup game path - try to auto-detect or prompt user (CLI).
    
    Args:
        plugins_path: Optional plugins path to derive game path from
        
    Returns:
        Valid game path or empty string
    """
    # Try to derive from plugins path
    if plugins_path:
        game_path = get_game_path_from_plugins(plugins_path)
        if game_path:
            save_game_path(game_path)
            return game_path
    
    # Try auto-detection
    game_path = find_game_path()
    if game_path:
        save_game_path(game_path)
        return game_path
    
    # Prompt user
    print("\nCould not auto-detect Risk of Rain 2 installation.")
    print("Enter the path to your Risk of Rain 2 folder.")
    print("Example: C:/Program Files/Steam/steamapps/common/Risk of Rain 2")
    print("(or 'cancel' to skip)")
    
    while True:
        try:
            path = input("\nGame path: ").strip()
        except (EOFError, KeyboardInterrupt):
            return ""
        
        if path.lower() == "cancel":
            return ""
        
        path = path.strip('"\'')
        exe_path = Path(path) / ROR2_EXECUTABLE
        
        if exe_path.exists():
            save_game_path(path)
            return path
        else:
            print(f"Could not find {ROR2_EXECUTABLE} in that directory.")
            print("Please try again or type 'cancel'.")


def launch_game(modded: bool = True, game_path: str = "") -> tuple[bool, str]:
    """
    Launch Risk of Rain 2.
    
    Args:
        modded: If True, launch with mods (normal). If False, launch vanilla.
        game_path: Path to game directory (will try to load from config if empty)
        
    Returns:
        Tuple of (success, message)
    """
    # Get game path
    if not game_path:
        game_path = load_game_path()
    
    if not game_path:
        return False, "Game path not configured. Please set it in settings."
    
    exe_path = Path(game_path) / ROR2_EXECUTABLE
    
    if not exe_path.exists():
        return False, f"Game executable not found: {exe_path}"
    
    try:
        mode = "modded" if modded else "vanilla"
        logger.info(f"Launching game ({mode}): {exe_path}")
        
        if modded:
            # Normal launch - BepInEx will load
            if sys.platform == "win32":
                # Use Steam to launch (preferred)
                try:
                    os.startfile(f"steam://run/{ROR2_STEAM_ID}")
                    return True, "Launching Risk of Rain 2 (modded) via Steam..."
                except Exception:
                    # Fallback to direct launch
                    subprocess.Popen([str(exe_path)], cwd=game_path)
                    return True, "Launching Risk of Rain 2 (modded)..."
            else:
                subprocess.Popen([str(exe_path)], cwd=game_path)
                return True, "Launching Risk of Rain 2 (modded)..."
        else:
            # Vanilla launch - disable BepInEx doorstop
            if sys.platform == "win32":
                # Launch with doorstop disabled
                env = os.environ.copy()
                env["DOORSTOP_ENABLE"] = "false"
                
                # Try Steam with launch options
                try:
                    # Direct launch with env var is more reliable for vanilla
                    subprocess.Popen(
                        [str(exe_path), "--doorstop-enable", "false"],
                        cwd=game_path,
                        env=env
                    )
                    return True, "Launching Risk of Rain 2 (vanilla - mods disabled)..."
                except Exception as e:
                    logger.error(f"Failed to launch vanilla: {e}")
                    return False, f"Failed to launch: {e}"
            else:
                env = os.environ.copy()
                env["DOORSTOP_ENABLE"] = "false"
                subprocess.Popen([str(exe_path)], cwd=game_path, env=env)
                return True, "Launching Risk of Rain 2 (vanilla)..."
                
    except PermissionError:
        return False, "Permission denied. Try running as administrator."
    except FileNotFoundError:
        return False, f"Game executable not found: {exe_path}"
    except Exception as e:
        logger.exception("Error launching game")
        return False, f"Error launching game: {e}"


def launch_modded(game_path: str = "") -> tuple[bool, str]:
    """Launch the game with mods enabled."""
    return launch_game(modded=True, game_path=game_path)


def launch_vanilla(game_path: str = "") -> tuple[bool, str]:
    """Launch the game without mods (vanilla)."""
    return launch_game(modded=False, game_path=game_path)
