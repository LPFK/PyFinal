"""
Dependency Checker - Functions for checking and validating mod dependencies.
"""

import logging
from dataclasses import dataclass

from .exceptions import DependencyError

logger = logging.getLogger(__name__)


@dataclass
class DependencyInfo:
    """Parsed dependency information."""
    author: str
    name: str
    version: str
    full_string: str
    
    def __str__(self) -> str:
        return f"{self.author}-{self.name}-{self.version}"


def parse_dependency_string(dep_string: str) -> DependencyInfo | None:
    """
    Parse a dependency string into its components.
    
    Thunderstore format: "Author-ModName-Version"
    Example: "bbepis-BepInExPack-5.4.2100"
    
    Args:
        dep_string: Dependency string
        
    Returns:
        DependencyInfo object or None if parsing fails
    """
    if not dep_string or not isinstance(dep_string, str):
        return None
    
    dep_string = dep_string.strip()
    parts = dep_string.split("-")
    
    if len(parts) < 3:
        logger.debug(f"Invalid dependency format: {dep_string}")
        return None
    
    author = parts[0]
    version = parts[-1]
    name = "-".join(parts[1:-1])
    
    if not author or not name or not version:
        return None
    
    return DependencyInfo(
        author=author,
        name=name,
        version=version,
        full_string=dep_string
    )


def check_dependencies(mod: dict, installed_mods: list[dict]) -> dict:
    """
    Check if all dependencies for a mod are installed.
    
    Args:
        mod: Mod dictionary with 'dependencies' key
        installed_mods: List of all installed mod dictionaries
        
    Returns:
        Dictionary with satisfied, missing, found, and details
    """
    dependencies = mod.get("dependencies", [])
    
    if not dependencies:
        return {
            "satisfied": True,
            "missing": [],
            "found": [],
            "details": []
        }
    
    # Build lookup set
    installed_identifiers = set()
    for installed_mod in installed_mods:
        folder_name = installed_mod.get("folder_name", "")
        name = installed_mod.get("name", "")
        
        installed_identifiers.add(folder_name.lower())
        installed_identifiers.add(name.lower())
        
        if "-" in folder_name:
            parts = folder_name.split("-", 1)
            if len(parts) > 1:
                installed_identifiers.add(parts[1].lower())
    
    missing = []
    found = []
    details = []
    
    for dep_string in dependencies:
        try:
            dep_info = parse_dependency_string(dep_string)
            
            if not dep_info:
                details.append({
                    "dependency": dep_string,
                    "status": "invalid",
                    "message": "Could not parse dependency string"
                })
                continue
            
            is_found = False
            dep_name_lower = dep_info.name.lower()
            dep_full_lower = f"{dep_info.author}-{dep_info.name}".lower()
            
            if dep_name_lower in installed_identifiers or dep_full_lower in installed_identifiers:
                is_found = True
            
            if is_found:
                found.append(dep_string)
                details.append({
                    "dependency": dep_string,
                    "status": "found",
                    "parsed": {
                        "author": dep_info.author,
                        "name": dep_info.name,
                        "version": dep_info.version
                    }
                })
            else:
                missing.append(dep_string)
                details.append({
                    "dependency": dep_string,
                    "status": "missing",
                    "parsed": {
                        "author": dep_info.author,
                        "name": dep_info.name,
                        "version": dep_info.version
                    }
                })
        except Exception as e:
            logger.error(f"Error checking dependency {dep_string}: {e}")
            details.append({
                "dependency": dep_string,
                "status": "error",
                "message": str(e)
            })
    
    return {
        "satisfied": len(missing) == 0,
        "missing": missing,
        "found": found,
        "details": details
    }


def find_missing_dependencies(mods: list[dict]) -> dict[str, list[str]]:
    """
    Find all missing dependencies across all installed mods.
    
    Args:
        mods: List of all installed mod dictionaries
        
    Returns:
        Dictionary mapping mod names to their missing dependencies
    """
    missing_deps = {}
    
    for mod in mods:
        try:
            result = check_dependencies(mod, mods)
            
            if not result["satisfied"]:
                mod_name = mod.get("name", "Unknown")
                missing_deps[mod_name] = result["missing"]
        except Exception as e:
            logger.error(f"Error checking dependencies for {mod.get('name', 'Unknown')}: {e}")
    
    return missing_deps


def get_dependency_tree(mod: dict, all_mods: list[dict], depth: int = 0, max_depth: int = 10) -> dict:
    """
    Build a dependency tree for a mod.
    
    Args:
        mod: The mod to analyze
        all_mods: List of all installed mods
        depth: Current recursion depth
        max_depth: Maximum recursion depth
        
    Returns:
        Dictionary representing the dependency tree
    """
    if depth >= max_depth:
        return {"name": mod.get("name", "Unknown"), "truncated": True}
    
    dependencies = mod.get("dependencies", [])
    
    tree = {
        "name": mod.get("name", "Unknown"),
        "version": mod.get("version_number", "0.0.0"),
        "dependencies": []
    }
    
    for dep_string in dependencies:
        dep_info = parse_dependency_string(dep_string)
        if not dep_info:
            tree["dependencies"].append({
                "name": dep_string,
                "status": "invalid"
            })
            continue
        
        found_mod = None
        for installed in all_mods:
            folder = installed.get("folder_name", "").lower()
            name = installed.get("name", "").lower()
            
            if dep_info.name.lower() in folder or dep_info.name.lower() == name:
                found_mod = installed
                break
        
        if found_mod:
            sub_tree = get_dependency_tree(found_mod, all_mods, depth + 1, max_depth)
            sub_tree["status"] = "installed"
            tree["dependencies"].append(sub_tree)
        else:
            tree["dependencies"].append({
                "name": f"{dep_info.author}-{dep_info.name}",
                "version": dep_info.version,
                "status": "missing"
            })
    
    return tree
