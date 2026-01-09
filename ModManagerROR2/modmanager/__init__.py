"""
RoR2 Mod Manager Package

A Risk of Rain 2 Mod Visualizer and Manager with Thunderstore integration.
"""

from .exceptions import (
    ModManagerError,
    ManifestError,
    ModNotFoundError,
    ModAlreadyExistsError,
    InstallationError,
    UninstallError,
    ConfigError,
    ThunderstoreError,
    NetworkError,
    DownloadError,
    InvalidZipError,
    DependencyError
)
from .scanner import scan_mods_directory, parse_manifest
from .manager import toggle_mod, install_mod_from_zip, uninstall_mod
from .config import parse_config_file, save_config_file, get_config_files
from .utils import filter_mods_by_name, format_mod_info, get_mod_dependencies
from .dependencies import check_dependencies, parse_dependency_string, find_missing_dependencies
from .settings import load_plugins_path, save_plugins_path, setup_plugins_path, get_config_dir
from .thunderstore import (
    fetch_all_packages,
    search_packages,
    get_popular_packages,
    download_package,
    parse_package,
    format_package_info,
    ThunderstorePackage
)

__all__ = [
    # Exceptions
    "ModManagerError",
    "ManifestError",
    "ModNotFoundError",
    "ModAlreadyExistsError",
    "InstallationError",
    "UninstallError",
    "ConfigError",
    "ThunderstoreError",
    "NetworkError",
    "DownloadError",
    "InvalidZipError",
    "DependencyError",
    # Scanner
    "scan_mods_directory",
    "parse_manifest",
    # Manager
    "toggle_mod",
    "install_mod_from_zip",
    "uninstall_mod",
    # Config
    "parse_config_file",
    "save_config_file",
    "get_config_files",
    # Utils
    "filter_mods_by_name",
    "format_mod_info",
    "get_mod_dependencies",
    # Dependencies
    "check_dependencies",
    "parse_dependency_string",
    "find_missing_dependencies",
    # Settings
    "load_plugins_path",
    "save_plugins_path",
    "setup_plugins_path",
    "get_config_dir",
    # Thunderstore
    "fetch_all_packages",
    "search_packages",
    "get_popular_packages",
    "download_package",
    "parse_package",
    "format_package_info",
    "ThunderstorePackage",
]

__version__ = "3.0.0"
