"""
Tests for RoR2 Mod Manager | Les tests pour le gestionnaire de mods de Risk of Rain 2 AKA RoR2 Mod Manager
Run with: pytest test_project.py -v | Pour lancer les tests: pytest test_project.py -v
"""

import json
import tempfile
import os
import shutil
import zipfile
from pathlib import Path
from unittest.mock import patch, MagicMock

# Import all testable functions from project.py | Importer toutes les fonctions testables de project.py
from project import (
    # Scanner
    parse_manifest,
    scan_mods_directory,
    # Manager
    toggle_mod,
    install_mod_from_zip,
    uninstall_mod,
    # Dependencies
    check_dependencies,
    parse_dependency_string,
    find_missing_dependencies,
    # Config
    parse_config_file,
    save_config_file,
    # Utils
    filter_mods_by_name,
    format_mod_info,
    get_mod_dependencies,
    # Thunderstore
    search_packages,
    get_popular_packages,
    parse_package,
    format_package_info,
)


# =============================================================================
# Scanner Tests | Tests pour scanner.py
# =============================================================================

class TestParseManifest:
    """Tests for the parse_manifest function."""
    
    def test_parse_manifest_valid(self):
        """Test parsing a valid manifest.json file."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump({
                "name": "TestMod",
                "version_number": "1.0.0",
                "website_url": "https://example.com",
                "description": "A test mod",
                "dependencies": ["BepInEx-BepInExPack-5.4.0"]
            }, f)
            temp_path = f.name
        
        try:
            result = parse_manifest(temp_path)
            assert result is not None
            assert result["name"] == "TestMod"
            assert result["version_number"] == "1.0.0"
            assert result["description"] == "A test mod"
            assert "BepInEx-BepInExPack-5.4.0" in result["dependencies"]
        finally:
            os.unlink(temp_path)
    
    def test_parse_manifest_missing_fields(self):
        """Test parsing a manifest with missing optional fields."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump({"name": "MinimalMod"}, f)
            temp_path = f.name
        
        try:
            result = parse_manifest(temp_path)
            assert result is not None
            assert result["name"] == "MinimalMod"
            assert result["version_number"] == "0.0.0"
            assert result["description"] == "No description"
        finally:
            os.unlink(temp_path)
    
    def test_parse_manifest_file_not_found(self):
        """Test parsing a non-existent file returns None."""
        result = parse_manifest("/nonexistent/path/manifest.json")
        assert result is None
    
    def test_parse_manifest_invalid_json(self):
        """Test parsing an invalid JSON file returns None."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            f.write("{ invalid json }")
            temp_path = f.name
        
        try:
            result = parse_manifest(temp_path)
            assert result is None
        finally:
            os.unlink(temp_path)


class TestScanModsDirectory:
    """Tests for the scan_mods_directory function."""
    
    def test_scan_mods_directory_nonexistent(self):
        """Test scanning a non-existent directory returns empty list."""
        result = scan_mods_directory("/nonexistent/path")
        assert result == []
    
    def test_scan_mods_directory_with_mods(self):
        """Test scanning a directory with mods."""
        with tempfile.TemporaryDirectory() as tmpdir:
            mod_folder = Path(tmpdir) / "Author-TestMod"
            mod_folder.mkdir()
            
            manifest = mod_folder / "manifest.json"
            manifest.write_text(json.dumps({
                "name": "TestMod",
                "version_number": "1.0.0",
                "description": "Test"
            }))
            
            result = scan_mods_directory(tmpdir)
            assert len(result) == 1
            assert result[0]["name"] == "TestMod"
    
    def test_scan_mods_directory_disabled_mod(self):
        """Test that disabled mods are detected correctly."""
        with tempfile.TemporaryDirectory() as tmpdir:
            mod_folder = Path(tmpdir) / "Author-TestMod.disabled"
            mod_folder.mkdir()
            
            manifest = mod_folder / "manifest.json"
            manifest.write_text(json.dumps({
                "name": "TestMod",
                "version_number": "1.0.0"
            }))
            
            result = scan_mods_directory(tmpdir)
            assert len(result) == 1
            assert result[0]["enabled"] is False


# =============================================================================
# Utils Tests
# =============================================================================

class TestFilterModsByName:
    """Tests for the filter_mods_by_name function."""
    
    def test_filter_mods_by_name_found(self):
        """Test filtering finds matching mods."""
        mods = [
            {"name": "QuickRestart", "version_number": "1.0.0"},
            {"name": "LookingGlass", "version_number": "2.0.0"},
            {"name": "BetterUI", "version_number": "1.5.0"}
        ]
        result = filter_mods_by_name(mods, "Glass")
        assert len(result) == 1
        assert result[0]["name"] == "LookingGlass"
    
    def test_filter_mods_by_name_case_insensitive(self):
        """Test filtering is case-insensitive."""
        mods = [
            {"name": "QuickRestart", "version_number": "1.0.0"},
            {"name": "BetterUI", "version_number": "1.5.0"}
        ]
        result = filter_mods_by_name(mods, "QUICK")
        assert len(result) == 1
        assert result[0]["name"] == "QuickRestart"
    
    def test_filter_mods_by_name_no_match(self):
        """Test filtering returns empty list when no match."""
        mods = [
            {"name": "QuickRestart", "version_number": "1.0.0"},
            {"name": "BetterUI", "version_number": "1.5.0"}
        ]
        result = filter_mods_by_name(mods, "NonExistent")
        assert len(result) == 0
    
    def test_filter_mods_by_name_empty_search(self):
        """Test empty search returns all mods."""
        mods = [
            {"name": "QuickRestart", "version_number": "1.0.0"},
            {"name": "BetterUI", "version_number": "1.5.0"}
        ]
        result = filter_mods_by_name(mods, "")
        assert len(result) == 2


class TestFormatModInfo:
    """Tests for the format_mod_info function."""
    
    def test_format_mod_info_enabled(self):
        """Test formatting an enabled mod."""
        mod = {
            "name": "TestMod",
            "version_number": "1.0.0",
            "description": "A test mod",
            "enabled": True
        }
        result = format_mod_info(mod)
        assert "TestMod" in result
        assert "1.0.0" in result
        assert "Enabled" in result
    
    def test_format_mod_info_disabled(self):
        """Test formatting a disabled mod."""
        mod = {
            "name": "DisabledMod",
            "version_number": "2.0.0",
            "description": "Disabled mod",
            "enabled": False
        }
        result = format_mod_info(mod)
        assert "DisabledMod" in result
        assert "Disabled" in result
    
    def test_format_mod_info_with_dependencies(self):
        """Test formatting includes dependencies."""
        mod = {
            "name": "TestMod",
            "version_number": "1.0.0",
            "description": "A test mod",
            "enabled": True,
            "dependencies": ["Dep1", "Dep2"]
        }
        result = format_mod_info(mod)
        assert "Dep1" in result
        assert "Dep2" in result


class TestGetModDependencies:
    """Tests for the get_mod_dependencies function."""
    
    def test_get_mod_dependencies_with_deps(self):
        """Test getting dependencies from a mod with dependencies."""
        mod = {
            "name": "TestMod",
            "dependencies": ["BepInEx-BepInExPack-5.4.0", "RiskofThunder-R2API-5.0.0"]
        }
        result = get_mod_dependencies(mod)
        assert len(result) == 2
        assert "BepInEx-BepInExPack-5.4.0" in result
    
    def test_get_mod_dependencies_empty(self):
        """Test getting dependencies from a mod without dependencies."""
        mod = {"name": "TestMod", "dependencies": []}
        result = get_mod_dependencies(mod)
        assert result == []
    
    def test_get_mod_dependencies_missing_key(self):
        """Test getting dependencies when key is missing."""
        mod = {"name": "TestMod"}
        result = get_mod_dependencies(mod)
        assert result == []


# =============================================================================
# Manager Tests
# =============================================================================

class TestToggleMod:
    """Tests for the toggle_mod function."""
    
    def test_toggle_mod_disable(self):
        """Test disabling an enabled mod."""
        with tempfile.TemporaryDirectory() as tmpdir:
            mod_folder = Path(tmpdir) / "TestMod"
            mod_folder.mkdir()
            
            success, new_state = toggle_mod(str(mod_folder))
            
            assert success is True
            assert new_state is False
            assert (Path(tmpdir) / "TestMod.disabled").exists()
            assert not mod_folder.exists()
    
    def test_toggle_mod_enable(self):
        """Test enabling a disabled mod."""
        with tempfile.TemporaryDirectory() as tmpdir:
            mod_folder = Path(tmpdir) / "TestMod.disabled"
            mod_folder.mkdir()
            
            success, new_state = toggle_mod(str(mod_folder))
            
            assert success is True
            assert new_state is True
            assert (Path(tmpdir) / "TestMod").exists()
            assert not mod_folder.exists()
    
    def test_toggle_mod_nonexistent(self):
        """Test toggling a non-existent mod fails."""
        success, new_state = toggle_mod("/nonexistent/path")
        assert success is False


class TestInstallModFromZip:
    """Tests for the install_mod_from_zip function."""
    
    def test_install_mod_from_zip_success(self):
        """Test successful mod installation from zip."""
        with tempfile.TemporaryDirectory() as tmpdir:
            plugins_dir = Path(tmpdir) / "plugins"
            plugins_dir.mkdir()
            
            zip_path = Path(tmpdir) / "TestMod.zip"
            with zipfile.ZipFile(zip_path, "w") as zf:
                manifest = {"name": "TestMod", "version_number": "1.0.0"}
                zf.writestr("manifest.json", json.dumps(manifest))
            
            success, message = install_mod_from_zip(str(zip_path), str(plugins_dir))
            
            assert success is True
            assert "TestMod" in message
            assert (plugins_dir / "TestMod").exists()
    
    def test_install_mod_from_zip_no_manifest(self):
        """Test installation fails when zip has no manifest."""
        with tempfile.TemporaryDirectory() as tmpdir:
            plugins_dir = Path(tmpdir) / "plugins"
            plugins_dir.mkdir()
            
            zip_path = Path(tmpdir) / "BadMod.zip"
            with zipfile.ZipFile(zip_path, "w") as zf:
                zf.writestr("readme.txt", "No manifest here")
            
            success, message = install_mod_from_zip(str(zip_path), str(plugins_dir))
            
            assert success is False
            assert "manifest.json" in message.lower()
    
    def test_install_mod_from_zip_file_not_found(self):
        """Test installation fails when zip file doesn't exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            success, message = install_mod_from_zip("/nonexistent.zip", tmpdir)
            assert success is False
            assert "not found" in message.lower()
    
    def test_install_mod_from_zip_already_exists(self):
        """Test installation fails when mod folder already exists."""
        with tempfile.TemporaryDirectory() as tmpdir:
            plugins_dir = Path(tmpdir) / "plugins"
            plugins_dir.mkdir()
            
            existing = plugins_dir / "TestMod"
            existing.mkdir()
            
            zip_path = Path(tmpdir) / "TestMod.zip"
            with zipfile.ZipFile(zip_path, "w") as zf:
                zf.writestr("manifest.json", json.dumps({"name": "TestMod"}))
            
            success, message = install_mod_from_zip(str(zip_path), str(plugins_dir))
            
            assert success is False
            assert "already exists" in message.lower()


class TestUninstallMod:
    """Tests for the uninstall_mod function."""
    
    def test_uninstall_mod_success(self):
        """Test successful mod uninstallation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            mod_folder = Path(tmpdir) / "Author-TestMod"
            mod_folder.mkdir()
            (mod_folder / "manifest.json").write_text(json.dumps({"name": "TestMod"}))
            (mod_folder / "plugin.dll").write_text("fake dll")
            
            success, message = uninstall_mod(str(mod_folder))
            
            assert success is True
            assert "TestMod" in message
            assert not mod_folder.exists()
    
    def test_uninstall_mod_nonexistent(self):
        """Test uninstalling non-existent mod fails."""
        success, message = uninstall_mod("/nonexistent/path")
        assert success is False
        assert "not found" in message.lower()
    
    def test_uninstall_mod_with_config(self):
        """Test uninstalling mod with config file deletion."""
        with tempfile.TemporaryDirectory() as tmpdir:
            mod_folder = Path(tmpdir) / "plugins" / "Author-TestMod"
            mod_folder.mkdir(parents=True)
            (mod_folder / "manifest.json").write_text(json.dumps({"name": "TestMod"}))
            
            config_dir = Path(tmpdir) / "config"
            config_dir.mkdir()
            config_file = config_dir / "author.testmod.cfg"
            config_file.write_text("setting = value")
            
            success, message = uninstall_mod(
                str(mod_folder), 
                delete_config=True, 
                config_dir=str(config_dir)
            )
            
            assert success is True
            assert not mod_folder.exists()
            assert not config_file.exists()


# =============================================================================
# Dependency Tests | Tests pour dependencies.py
# =============================================================================

class TestParseDependencyString:
    """Tests for the parse_dependency_string function."""
    
    def test_parse_dependency_string_valid(self):
        """Test parsing a valid dependency string."""
        result = parse_dependency_string("bbepis-BepInExPack-5.4.2100")
        
        assert result is not None
        assert result.author == "bbepis"
        assert result.name == "BepInExPack"
        assert result.version == "5.4.2100"
    
    def test_parse_dependency_string_with_hyphen_in_name(self):
        """Test parsing dependency with hyphen in mod name."""
        result = parse_dependency_string("Author-Mod-Name-Here-1.0.0")
        
        assert result is not None
        assert result.author == "Author"
        assert result.name == "Mod-Name-Here"
        assert result.version == "1.0.0"
    
    def test_parse_dependency_string_invalid(self):
        """Test parsing invalid dependency string."""
        result = parse_dependency_string("invalid")
        assert result is None
    
    def test_parse_dependency_string_empty(self):
        """Test parsing empty string."""
        result = parse_dependency_string("")
        assert result is None
    
    def test_parse_dependency_string_none(self):
        """Test parsing None."""
        result = parse_dependency_string(None)
        assert result is None


class TestCheckDependencies:
    """Tests for the check_dependencies function."""
    
    def test_check_dependencies_all_satisfied(self):
        """Test when all dependencies are satisfied."""
        mod = {
            "name": "TestMod",
            "dependencies": ["Author-DepMod-1.0.0"]
        }
        installed = [
            {"name": "DepMod", "folder_name": "Author-DepMod"}
        ]
        
        result = check_dependencies(mod, installed)
        
        assert result["satisfied"] is True
        assert len(result["missing"]) == 0
        assert len(result["found"]) == 1
    
    def test_check_dependencies_missing(self):
        """Test when dependencies are missing."""
        mod = {
            "name": "TestMod",
            "dependencies": ["Author-MissingMod-1.0.0"]
        }
        installed = []
        
        result = check_dependencies(mod, installed)
        
        assert result["satisfied"] is False
        assert len(result["missing"]) == 1
        assert "Author-MissingMod-1.0.0" in result["missing"]
    
    def test_check_dependencies_no_dependencies(self):
        """Test mod with no dependencies."""
        mod = {"name": "TestMod", "dependencies": []}
        
        result = check_dependencies(mod, [])
        
        assert result["satisfied"] is True
        assert len(result["missing"]) == 0


class TestFindMissingDependencies:
    """Tests for the find_missing_dependencies function."""
    
    def test_find_missing_dependencies_none_missing(self):
        """Test when no dependencies are missing."""
        mods = [
            {"name": "ModA", "dependencies": [], "folder_name": "Author-ModA"},
            {"name": "ModB", "dependencies": ["Author-ModA-1.0.0"], "folder_name": "Author-ModB"}
        ]
        
        result = find_missing_dependencies(mods)
        
        assert len(result) == 0
    
    def test_find_missing_dependencies_some_missing(self):
        """Test when some dependencies are missing."""
        mods = [
            {"name": "ModA", "dependencies": ["Author-MissingMod-1.0.0"], "folder_name": "Author-ModA"}
        ]
        
        result = find_missing_dependencies(mods)
        
        assert "ModA" in result
        assert "Author-MissingMod-1.0.0" in result["ModA"]


# =============================================================================
# Config Tests | Tests pour config.py
# =============================================================================

class TestParseConfigFile:
    """Tests for the parse_config_file function."""
    
    def test_parse_config_file_valid(self):
        """Test parsing a valid config file."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".cfg", delete=False) as f:
            f.write("[General]\n")
            f.write("# This is a comment\n")
            f.write("EnableFeature = true\n")
            f.write("MaxValue = 100\n")
            temp_path = f.name
        
        try:
            result = parse_config_file(temp_path)
            assert result["EnableFeature"] == "true"
            assert result["MaxValue"] == "100"
        finally:
            os.unlink(temp_path)
    
    def test_parse_config_file_empty(self):
        """Test parsing an empty config file."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".cfg", delete=False) as f:
            f.write("# Only comments\n")
            temp_path = f.name
        
        try:
            result = parse_config_file(temp_path)
            assert result == {}
        finally:
            os.unlink(temp_path)
    
    def test_parse_config_file_nonexistent(self):
        """Test parsing a non-existent file returns empty dict."""
        result = parse_config_file("/nonexistent/config.cfg")
        assert result == {}


class TestSaveConfigFile:
    """Tests for the save_config_file function."""
    
    def test_save_config_file_success(self):
        """Test saving config preserves structure and updates values."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".cfg", delete=False) as f:
            f.write("[General]\n")
            f.write("# Comment to preserve\n")
            f.write("Setting1 = old_value\n")
            f.write("Setting2 = keep_this\n")
            temp_path = f.name
        
        try:
            settings = {"Setting1": "new_value", "Setting2": "keep_this"}
            result = save_config_file(temp_path, settings)
            
            assert result is True
            
            with open(temp_path, "r") as f:
                content = f.read()
            
            assert "new_value" in content
            assert "[General]" in content
            assert "# Comment to preserve" in content
        finally:
            os.unlink(temp_path)
    
    def test_save_config_file_nonexistent(self):
        """Test saving to non-existent file fails gracefully."""
        result = save_config_file("/nonexistent/path/config.cfg", {"key": "value"})
        assert result is False


# =============================================================================
# Thunderstore Tests | Tests pour thunderstore.py
# =============================================================================

class TestParsePackage:
    """Tests for the parse_package function."""
    
    def test_parse_package_valid(self):
        """Test parsing valid package data."""
        data = {
            "name": "TestMod",
            "full_name": "Author-TestMod",
            "owner": "Author",
            "rating_score": 5,
            "is_deprecated": False,
            "date_updated": "2024-01-01",
            "categories": ["Mods"],
            "versions": [{
                "version_number": "1.0.0",
                "description": "A test mod",
                "download_url": "https://example.com/mod.zip",
                "downloads": 1000,
                "dependencies": ["bbepis-BepInExPack-5.4.0"]
            }]
        }
        
        result = parse_package(data)
        
        assert result is not None
        assert result.name == "TestMod"
        assert result.full_name == "Author-TestMod"
        assert result.version == "1.0.0"
        assert result.downloads == 1000
    
    def test_parse_package_no_versions(self):
        """Test parsing package with no versions returns None."""
        data = {
            "name": "TestMod",
            "versions": []
        }
        
        result = parse_package(data)
        assert result is None
    
    def test_parse_package_missing_fields(self):
        """Test parsing package with missing fields uses defaults."""
        data = {
            "versions": [{
                "version_number": "1.0.0"
            }]
        }
        
        result = parse_package(data)
        
        assert result is not None
        assert result.name == "Unknown"


class TestSearchPackages:
    """Tests for the search_packages function."""
    
    def test_search_packages_found(self):
        """Test search finds matching packages."""
        packages = [
            {
                "name": "BetterUI",
                "full_name": "Author-BetterUI",
                "is_deprecated": False,
                "versions": [{"description": "UI improvements", "version_number": "1.0.0"}]
            },
            {
                "name": "OtherMod",
                "full_name": "Author-OtherMod",
                "is_deprecated": False,
                "versions": [{"description": "Something else", "version_number": "1.0.0"}]
            }
        ]
        
        result = search_packages(packages, "Better")
        
        assert len(result) == 1
        assert result[0].name == "BetterUI"
    
    def test_search_packages_empty_query(self):
        """Test empty search returns empty list."""
        packages = [
            {"name": "TestMod", "versions": [{"version_number": "1.0.0"}]}
        ]
        
        result = search_packages(packages, "")
        assert len(result) == 0
    
    def test_search_packages_no_match(self):
        """Test search with no matches returns empty list."""
        packages = [
            {
                "name": "TestMod",
                "full_name": "Author-TestMod",
                "is_deprecated": False,
                "versions": [{"description": "Test", "version_number": "1.0.0"}]
            }
        ]
        
        result = search_packages(packages, "NonExistent")
        assert len(result) == 0


class TestGetPopularPackages:
    """Tests for the get_popular_packages function."""
    
    def test_get_popular_packages_sorted(self):
        """Test popular packages are sorted by downloads."""
        packages = [
            {
                "name": "LessPopular",
                "full_name": "A-LessPopular",
                "is_deprecated": False,
                "versions": [{"downloads": 100, "version_number": "1.0.0"}]
            },
            {
                "name": "MostPopular",
                "full_name": "A-MostPopular",
                "is_deprecated": False,
                "versions": [{"downloads": 10000, "version_number": "1.0.0"}]
            }
        ]
        
        result = get_popular_packages(packages, limit=10)
        
        assert len(result) == 2
        assert result[0].name == "MostPopular"
        assert result[1].name == "LessPopular"
    
    def test_get_popular_packages_excludes_deprecated(self):
        """Test deprecated packages are excluded."""
        packages = [
            {
                "name": "ActiveMod",
                "full_name": "A-ActiveMod",
                "is_deprecated": False,
                "versions": [{"downloads": 100, "version_number": "1.0.0"}]
            },
            {
                "name": "OldMod",
                "full_name": "A-OldMod",
                "is_deprecated": True,
                "versions": [{"downloads": 10000, "version_number": "1.0.0"}]
            }
        ]
        
        result = get_popular_packages(packages, limit=10)
        
        assert len(result) == 1
        assert result[0].name == "ActiveMod"


class TestFormatPackageInfo:
    """Tests for the format_package_info function."""
    
    def test_format_package_info_basic(self):
        """Test formatting basic package info."""
        from modmanager.thunderstore import ThunderstorePackage
        
        package = ThunderstorePackage(
            name="TestMod",
            full_name="Author-TestMod",
            owner="Author",
            description="A test mod",
            version="1.0.0",
            download_url="https://example.com/mod.zip",
            downloads=1000,
            rating=5,
            categories=["Mods"],
            dependencies=[],
            date_updated="2024-01-01",
            is_deprecated=False
        )
        
        result = format_package_info(package)
        
        assert "Author-TestMod" in result
        assert "1.0.0" in result
        assert "1,000" in result  # Formatted downloads
        assert "A test mod" in result
