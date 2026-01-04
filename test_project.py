"""
Tests for RoR2 Mod Manager
Run with: pytest test_project.py -v
"""

import json
import tempfile
import os
import zipfile
from pathlib import Path

# Import all testable functions from project.py
from project import (
    parse_manifest,
    filter_mods_by_name,
    format_mod_info,
    scan_mods_directory,
    get_mod_dependencies,
    toggle_mod,
    install_mod_from_zip,
    parse_config_file,
    save_config_file
)


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
    
    def test_install_mod_from_zip_not_zip(self):
        """Test installation fails for non-zip files."""
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as f:
            f.write(b"Not a zip")
            temp_path = f.name
        
        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                success, message = install_mod_from_zip(temp_path, tmpdir)
                assert success is False
        finally:
            os.unlink(temp_path)
    
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
