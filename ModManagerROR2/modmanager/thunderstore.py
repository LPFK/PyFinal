"""
Thunderstore API - Functions for interacting with the Thunderstore mod repository.

API Documentation: https://thunderstore.io/api/docs/
"""

import json
import os
import tempfile
import urllib.request
import urllib.error
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


# Thunderstore API endpoints
BASE_URL = "https://thunderstore.io"
COMMUNITY = "riskofrain2"
API_V1_PACKAGES = f"{BASE_URL}/c/{COMMUNITY}/api/v1/package/"


@dataclass
class ThunderstorePackage:
    """Represents a package from Thunderstore."""
    name: str
    full_name: str
    owner: str
    description: str
    version: str
    download_url: str
    downloads: int
    rating: int
    categories: list[str]
    dependencies: list[str]
    date_updated: str
    is_deprecated: bool
    
    def __str__(self) -> str:
        return f"{self.full_name} v{self.version}"


def fetch_all_packages(timeout: int = 30) -> tuple[bool, list[dict] | str]:
    """
    Fetch all packages from Thunderstore API.
    
    Args:
        timeout: Request timeout in seconds
        
    Returns:
        Tuple of (success, packages_list or error_message)
    """
    try:
        req = urllib.request.Request(
            API_V1_PACKAGES,
            headers={"User-Agent": "RoR2ModManager/1.0"}
        )
        
        with urllib.request.urlopen(req, timeout=timeout) as response:
            data = json.loads(response.read().decode("utf-8"))
            return True, data
            
    except urllib.error.HTTPError as e:
        return False, f"HTTP Error {e.code}: {e.reason}"
    except urllib.error.URLError as e:
        return False, f"Connection failed: {e.reason}"
    except json.JSONDecodeError:
        return False, "Failed to parse API response"
    except Exception as e:
        return False, f"Error: {str(e)}"


def parse_package(data: dict) -> ThunderstorePackage | None:
    """
    Parse a package dictionary from the API into a ThunderstorePackage.
    
    Args:
        data: Package data from API
        
    Returns:
        ThunderstorePackage object or None if parsing fails
    """
    try:
        # Get latest version info
        versions = data.get("versions", [])
        if not versions:
            return None
        
        latest = versions[0]
        
        return ThunderstorePackage(
            name=data.get("name", "Unknown"),
            full_name=data.get("full_name", ""),
            owner=data.get("owner", ""),
            description=latest.get("description", ""),
            version=latest.get("version_number", "0.0.0"),
            download_url=latest.get("download_url", ""),
            downloads=latest.get("downloads", 0),
            rating=data.get("rating_score", 0),
            categories=[c for c in data.get("categories", [])],
            dependencies=latest.get("dependencies", []),
            date_updated=data.get("date_updated", ""),
            is_deprecated=data.get("is_deprecated", False)
        )
    except (KeyError, TypeError, IndexError):
        return None


def search_packages(packages: list[dict], query: str, limit: int = 20) -> list[ThunderstorePackage]:
    """
    Search packages by name or description.
    
    Args:
        packages: List of package data from API
        query: Search query string
        limit: Maximum results to return
        
    Returns:
        List of matching ThunderstorePackage objects
    """
    if not query:
        return []
    
    query_lower = query.lower()
    results = []
    
    for pkg_data in packages:
        if len(results) >= limit:
            break
            
        name = pkg_data.get("name", "").lower()
        full_name = pkg_data.get("full_name", "").lower()
        
        # Check latest version description
        versions = pkg_data.get("versions", [])
        description = versions[0].get("description", "").lower() if versions else ""
        
        # Match against name, full_name, or description
        if query_lower in name or query_lower in full_name or query_lower in description:
            pkg = parse_package(pkg_data)
            if pkg and not pkg.is_deprecated:
                results.append(pkg)
    
    return results


def get_popular_packages(packages: list[dict], limit: int = 20) -> list[ThunderstorePackage]:
    """
    Get the most popular packages by download count.
    
    Args:
        packages: List of package data from API
        limit: Maximum results to return
        
    Returns:
        List of ThunderstorePackage objects sorted by downloads
    """
    parsed = []
    
    for pkg_data in packages:
        pkg = parse_package(pkg_data)
        if pkg and not pkg.is_deprecated:
            parsed.append(pkg)
    
    # Sort by downloads (descending)
    parsed.sort(key=lambda p: p.downloads, reverse=True)
    
    return parsed[:limit]


def get_recently_updated(packages: list[dict], limit: int = 20) -> list[ThunderstorePackage]:
    """
    Get recently updated packages.
    
    Args:
        packages: List of package data from API
        limit: Maximum results to return
        
    Returns:
        List of ThunderstorePackage objects sorted by update date
    """
    parsed = []
    
    for pkg_data in packages:
        pkg = parse_package(pkg_data)
        if pkg and not pkg.is_deprecated:
            parsed.append(pkg)
    
    # Sort by date_updated (descending)
    parsed.sort(key=lambda p: p.date_updated, reverse=True)
    
    return parsed[:limit]


def download_package(package: ThunderstorePackage, dest_dir: str) -> tuple[bool, str]:
    """
    Download a package zip file from Thunderstore.
    
    Args:
        package: ThunderstorePackage to download
        dest_dir: Directory to save the zip file
        
    Returns:
        Tuple of (success, file_path or error_message)
    """
    if not package.download_url:
        return False, "No download URL available"
    
    try:
        # Create destination directory if needed
        dest_path = Path(dest_dir)
        dest_path.mkdir(parents=True, exist_ok=True)
        
        # Generate filename
        filename = f"{package.full_name}-{package.version}.zip"
        filepath = dest_path / filename
        
        # Download the file
        req = urllib.request.Request(
            package.download_url,
            headers={"User-Agent": "RoR2ModManager/1.0"}
        )
        
        with urllib.request.urlopen(req, timeout=60) as response:
            with open(filepath, "wb") as f:
                # Read in chunks to handle large files
                chunk_size = 8192
                while True:
                    chunk = response.read(chunk_size)
                    if not chunk:
                        break
                    f.write(chunk)
        
        return True, str(filepath)
        
    except urllib.error.HTTPError as e:
        return False, f"Download failed - HTTP {e.code}: {e.reason}"
    except urllib.error.URLError as e:
        return False, f"Download failed: {e.reason}"
    except IOError as e:
        return False, f"Failed to save file: {e}"
    except Exception as e:
        return False, f"Error: {str(e)}"


def get_package_by_name(packages: list[dict], full_name: str) -> ThunderstorePackage | None:
    """
    Get a specific package by its full name (Owner-Name).
    
    Args:
        packages: List of package data from API
        full_name: Full package name (e.g., "bbepis-BepInExPack")
        
    Returns:
        ThunderstorePackage or None if not found
    """
    full_name_lower = full_name.lower()
    
    for pkg_data in packages:
        if pkg_data.get("full_name", "").lower() == full_name_lower:
            return parse_package(pkg_data)
    
    return None


def format_package_info(package: ThunderstorePackage) -> str:
    """
    Format package information for display.
    
    Args:
        package: ThunderstorePackage to format
        
    Returns:
        Formatted string representation
    """
    lines = [
        f"Name: {package.full_name}",
        f"Version: {package.version}",
        f"Author: {package.owner}",
        f"Downloads: {package.downloads:,}",
        f"Rating: {package.rating}",
        f"Description: {package.description}",
    ]
    
    if package.categories:
        lines.append(f"Categories: {', '.join(package.categories)}")
    
    if package.dependencies:
        lines.append(f"Dependencies ({len(package.dependencies)}):")
        for dep in package.dependencies[:10]:  # Limit displayed deps
            lines.append(f"  - {dep}")
        if len(package.dependencies) > 10:
            lines.append(f"  ... and {len(package.dependencies) - 10} more")
    
    if package.is_deprecated:
        lines.append("⚠ This package is DEPRECATED")
    
    return "\n".join(lines)


def filter_by_category(packages: list[dict], category: str, limit: int = 50) -> list[ThunderstorePackage]:
    """
    Filter packages by category.
    
    Args:
        packages: List of package data from API
        category: Category to filter by
        limit: Maximum results
        
    Returns:
        List of matching packages
    """
    category_lower = category.lower()
    results = []
    
    for pkg_data in packages:
        if len(results) >= limit:
            break
            
        categories = [c.lower() for c in pkg_data.get("categories", [])]
        
        if category_lower in categories:
            pkg = parse_package(pkg_data)
            if pkg and not pkg.is_deprecated:
                results.append(pkg)
    
    # Sort by downloads
    results.sort(key=lambda p: p.downloads, reverse=True)
    
    return results
