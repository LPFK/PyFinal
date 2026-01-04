"""
Utilities - Display formatting and helper functions.
"""


def filter_mods_by_name(mods: list[dict], search_term: str) -> list[dict]:
    """
    Filter a list of mods by name (case-insensitive search).
    
    Args:
        mods: List of mod dictionaries
        search_term: Search string to filter by
        
    Returns:
        List of mods whose names contain the search term
    """
    if not search_term:
        return mods
    
    search_lower = search_term.lower()
    return [mod for mod in mods if search_lower in mod.get("name", "").lower()]


def format_mod_info(mod: dict) -> str:
    """
    Format a mod's information into a readable string for display.
    
    Args:
        mod: Dictionary containing mod information
        
    Returns:
        Formatted string representation of the mod
    """
    status = "✓ Enabled" if mod.get("enabled", True) else "✗ Disabled"
    
    lines = [
        f"Name: {mod.get('name', 'Unknown')}",
        f"Version: {mod.get('version_number', '0.0.0')}",
        f"Status: {status}",
        f"Description: {mod.get('description', 'No description')}",
    ]
    
    dependencies = mod.get("dependencies", [])
    if dependencies:
        lines.append(f"Dependencies ({len(dependencies)}):")
        for dep in dependencies:
            lines.append(f"  - {dep}")
    
    website = mod.get("website_url", "")
    if website:
        lines.append(f"Website: {website}")
    
    path = mod.get("path", "")
    if path:
        lines.append(f"Path: {path}")
    
    return "\n".join(lines)


def get_mod_dependencies(mod: dict) -> list[str]:
    """
    Extract and return the list of dependencies for a mod.
    
    Args:
        mod: Dictionary containing mod information
        
    Returns:
        List of dependency strings
    """
    return mod.get("dependencies", [])
