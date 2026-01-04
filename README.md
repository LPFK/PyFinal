# RoR2 Mod Manager

A Risk of Rain 2 Mod Visualizer and Manager built in Python.

## Project Structure

```
ror2_mod_manager/
├── project.py          # Main entry point + function exports
├── test_project.py     # Pytest tests (30 tests)
├── requirements.txt    # Dependencies
├── scanner.py          # Mod discovery & manifest parsing
├── manager.py          # Enable/disable & installation
├── config.py           # BepInEx config file editing
├── utils.py            # Display formatting & utilities
├── settings.py         # App configuration
└── menus.py            # CLI menu interfaces
```

## Features

- **List all mods** - View installed mods with status
- **View mod details** - See full info including dependencies
- **Enable/Disable mods** - Toggle mods on/off
- **Search mods** - Find mods by name
- **Install from zip** - Add new mods from downloaded zip files
- **Edit config** - Modify BepInEx config files

## Installation

```bash
python -m venv .venv
pip install -r requirements.txt
```

## Usage

```bash
python project.py
```

On first run, you'll be asked to provide the path to your `BepInEx/plugins` folder.
exemple in my case E:\SteamLibrary\steamapps\common\Risk of Rain 2\BepInEx\plugins
then use the menu to enable/disable mods, search for mods, install mods from zip, edit config files, change mods folder, or exit.

## Running Tests

```bash
pytest test_project.py -v
```

## Module Overview

| Module | Purpose |
|--------|---------|
| `scanner.py` | `scan_mods_directory()`, `parse_manifest()` |
| `manager.py` | `toggle_mod()`, `install_mod_from_zip()` |
| `config.py` | `parse_config_file()`, `save_config_file()` |
| `utils.py` | `filter_mods_by_name()`, `format_mod_info()`, `get_mod_dependencies()` |
| `settings.py` | `load_plugins_path()`, `save_plugins_path()`, `setup_plugins_path()` |
| `menus.py` | All interactive CLI menu functions |
