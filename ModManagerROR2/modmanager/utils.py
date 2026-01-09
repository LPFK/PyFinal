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


def format_dependency_tree(tree: dict, indent: int = 0) -> str:
    """
    Format a dependency tree into a readable string.
    
    Args:
        tree: Dependency tree dictionary
        indent: Current indentation level
        
    Returns:
        Formatted string representation of the tree
    """
    lines = []
    prefix = "  " * indent
    
    name = tree.get("name", "Unknown")
    version = tree.get("version", "")
    status = tree.get("status", "")
    
    if status == "missing":
        line = f"{prefix}✗ {name} v{version} (MISSING)"
    elif status == "installed":
        line = f"{prefix}✓ {name} v{version}"
    else:
        line = f"{prefix}• {name}"
        if version:
            line += f" v{version}"
    
    lines.append(line)
    
    if tree.get("truncated"):
        lines.append(f"{prefix}  ... (truncated)")
    
    for dep in tree.get("dependencies", []):
        lines.append(format_dependency_tree(dep, indent + 1))
    
    return "\n".join(lines)


def format_file_size(bytes_size: int) -> str:
    """
    Format bytes into human-readable size.
    
    Args:
        bytes_size: Size in bytes
        
    Returns:
        Formatted string (e.g., "1.5 MB")
    """
    for unit in ["B", "KB", "MB", "GB"]:
        if bytes_size < 1024:
            return f"{bytes_size:.1f} {unit}"
        bytes_size /= 1024
    return f"{bytes_size:.1f} TB"


def truncate_string(text: str, max_length: int, suffix: str = "...") -> str:
    """
    Truncate a string to a maximum length.
    
    Args:
        text: String to truncate
        max_length: Maximum length
        suffix: Suffix to add if truncated
        
    Returns:
        Truncated string
    """
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix
