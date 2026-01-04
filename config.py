"""
Config Editor - Functions for parsing and editing BepInEx config files.
"""


def parse_config_file(config_path: str) -> dict[str, str]:
    """
    Parse a BepInEx config file (.cfg) and extract key-value settings.
    
    Args:
        config_path: Path to the config file
        
    Returns:
        Dictionary of setting names to their values
    """
    settings = {}
    
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                # Skip comments and empty lines
                if not line or line.startswith("#") or line.startswith("["):
                    continue
                
                # Parse key = value pairs
                if "=" in line:
                    key, _, value = line.partition("=")
                    key = key.strip()
                    value = value.strip()
                    if key:
                        settings[key] = value
    except (IOError, UnicodeDecodeError):
        pass
    
    return settings


def save_config_file(config_path: str, settings: dict[str, str]) -> bool:
    """
    Save modified settings back to a config file, preserving structure.
    
    Args:
        config_path: Path to the config file
        settings: Dictionary of settings to save
        
    Returns:
        True if saved successfully, False otherwise
    """
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
                    # Preserve original indentation
                    indent = len(line) - len(line.lstrip())
                    new_lines.append(" " * indent + f"{key} = {settings[key]}\n")
                    continue
            new_lines.append(line)
        
        # Write back
        with open(config_path, "w", encoding="utf-8") as f:
            f.writelines(new_lines)
        
        return True
    except IOError:
        return False
