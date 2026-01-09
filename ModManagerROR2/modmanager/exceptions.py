"""
Custom Exceptions for RoR2 Mod Manager
"""


class ModManagerError(Exception):
    """Base exception for all mod manager errors."""
    pass


class ManifestError(ModManagerError):
    """Error related to manifest.json parsing."""
    pass


class ModNotFoundError(ModManagerError):
    """Mod or mod folder not found."""
    pass


class ModAlreadyExistsError(ModManagerError):
    """Mod already exists in plugins folder."""
    pass


class InstallationError(ModManagerError):
    """Error during mod installation."""
    pass


class UninstallError(ModManagerError):
    """Error during mod uninstallation."""
    pass


class ConfigError(ModManagerError):
    """Error related to config file operations."""
    pass


class ThunderstoreError(ModManagerError):
    """Error related to Thunderstore API operations."""
    pass


class NetworkError(ThunderstoreError):
    """Network connection error."""
    pass


class DownloadError(ThunderstoreError):
    """Error downloading a file."""
    pass


class InvalidZipError(InstallationError):
    """Invalid or corrupted zip file."""
    pass


class DependencyError(ModManagerError):
    """Error related to dependency checking."""
    pass
