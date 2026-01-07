# RoR2 Mod Manager v2.0

A Risk of Rain 2 Mod Visualizer and Manager with **Thunderstore integration** ( Like Mo2 but for Risk of Rain 2 and with more features !! | Comme Mo2 mais pour Risk of Rain 2 et avec plus de fonctionnalités !!).

## Features

### 📦 Installed Mods | Mod installés
- **List all mods** - View installed mods with status |  Liste de tous les mods installés avec leur statut 
- **View mod details** - Full info including dependencies |  Voir les détails d'un mod 
- **Enable/Disable mods** - Toggle mods without deleting |  Activer/Désactiver des mods sans les supprimer 
- **Search mods** - Find mods by name |  Rechercher des mods par nom 

### 🔧 Mod Management | Gestion des mods
- **Install from zip** - Add mods from downloaded zip files |  Installer des mods depuis des fichiers zip 
- **Uninstall mods** - Remove mods with optional config cleanup |  Supprimer des mods avec nettoyage optionnel des fichiers de configuration 
- **Dependency checker** - Find missing dependencies |  Trouver les dépendances manquantes 

### 🌐 Thunderstore Integration | Intégration de Thunderstore
- **Search mods** - Search the Thunderstore database |  Rechercher des mods dans la base de données de Thunderstore, Via leurs API 
- **Browse popular** - View most downloaded mods |  Voir les mods les plus téléchargés 
- **Recently updated** - See latest mod updates |  Voir les dernières mises à jour des mods 
- **Download & install** - One-click mod installation |  Télécharger et installer des mods en un clic 

### ⚙️ Settings | Paramètres
- **Edit configs** - Modify BepInEx config files |  Modifier les fichiers de configuration de BepInEx(ModLoader) 
- **Path management** - Configure your mods folder |  Configurer le dossier des mods 

## Project Structure | Structure du projet

```
ror2_mod_manager/
├── project.py              # Main entry point | Point d'entrée principal
├── test_project.py         # 51 pytest tests | 51 tests pytest
├── requirements.txt        # Dependencies | Dépendances
├── README.md               # This file | Ce fichier
│
└── modmanager/             # Main package | Package principal
    ├── __init__.py         # Package exports | Exportations du package
    ├── scanner.py          # Mod discovery | Fetch des mods du Thunderstore
    ├── manager.py          # Install/uninstall/toggle | Installation/desinstallation/activation/desactivation
    ├── dependencies.py     # Dependency checking | Vérification des dépendances
    ├── config.py           # Config file editing | Edition des fichiers de configuration
    ├── utils.py            # Formatting utilities | Utilitaires de formatage
    ├── settings.py         # App configuration | Configuration de l'application
    ├── menus.py            # CLI menus | Menus CLI (Super intuitif)
    └── thunderstore.py     # Thunderstore API | API Thunderstore
```

## Installation | Installation (C'est le meme mot que en anglais ehehe)

```bash
'(Recommanded create a virtual environment before running the program | Je recommande de créer un environnement virtuel avant de lancer le programme)'
1. - python -m venv RoR2MM (Windows) | python3 -m venv RoR2MM (Linux/Mac)
2. - RoR2MM\Scripts\activate (Windows) | source RoR2MM/bin/activate (Linux/Mac)
3. - pip install -r requirements.txt
```

## Usage | Utilisation

```bash
python project.py
```

On first run, you'll be asked for your `BepInEx/plugins` folder path. | Sur le premier lancement, il vous sera demandé pour le chemin du dossier `BepInEx/plugins`.

Example paths | Exemples de chemins :
```
Windows: C:/Program Files/Steam/steamapps/common/Risk of Rain 2/BepInEx/plugins
Windows: E:\SteamLibrary\steamapps\common\Risk of Rain 2\BepInEx\plugins ( That's my path )
Linux:   ~/.steam/steam/steamapps/common/Risk of Rain 2/BepInEx/plugins
```

## Running Tests | Lancer les tests

```bash
pytest test_project.py -v
```

## Menu Overview | Aperçu des menus

```
==================================================
  MAIN MENU | MENU PRINCIPAL
==================================================

📦 Installed Mods | Mod installés
  [1] List all mods | Liste de tous les mods
  [2] View mod details | Voir les détails d'un mod
  [3] Enable/Disable mod | Activer/Désactiver des mods
  [4] Search mods | Rechercher des mods

🔧 Mod Management | Gestion des mods
  [5] Install mod from zip | Installer des mods depuis des fichiers zip
  [6] Uninstall mod | Supprimer des mods
  [7] Check dependencies | Vérifier les dépendances

🌐 Thunderstore | Thunderstore
  [8] Browse & Download mods | Parcourir et télécharger des mods

⚙️  Settings | Paramètres
  [9] Edit mod config | Modifier les fichiers de configuration des mods
  [C] Change mods folder | Changer le dossier des mods

  [0] Exit | Quitter
==================================================
```

## Thunderstore Menu | Menu Thunderstore

```
==================================================
  THUNDERSTORE - Browse & Download Mods | Thunderstore - Parcourir et télécharger des mods
==================================================
[1] Search mods | Rechercher des mods
[2] Popular mods | Les mods les plus populaires
[3] Recently updated | Les mods les plus récemment mis à jour
[4] Refresh mod list | Rafraîchir la liste des mods
[0] Back to main menu | Retour au menu principal
```

## API Reference | Référence API

### Scanner (`modmanager/scanner.py`)
| Function | Description |
|----------|-------------|
| `scan_mods_directory(path)` | Scan plugins folder for mods | Parcourir le dossier des mods |
| `parse_manifest(path)` | Parse a manifest.json file | Parser un fichier manifest.json |

### Manager (`modmanager/manager.py`)
| Function | Description |
|----------|-------------|
| `toggle_mod(path)` | Enable/disable a mod | Activer/désactiver un mod |
| `install_mod_from_zip(zip, plugins)` | Install from zip | Installer depuis un fichier zip |
| `uninstall_mod(path, del_cfg, cfg_dir)` | Remove a mod | Supprimer un mod |

### Dependencies (`modmanager/dependencies.py`)
| Function | Description |
|----------|-------------|
| `parse_dependency_string(dep)` | Parse "Author-Mod-Version" | Parser "Author-Mod-Version" |
| `check_dependencies(mod, installed)` | Check if deps are met | Vérifier si les dépendances sont remplies |
| `find_missing_dependencies(mods)` | Find all missing deps | Trouver toutes les dépendances manquantes |
| `get_dependency_tree(mod, all)` | Build dependency tree | Construire l'arbre des dépendances |

### Thunderstore (`modmanager/thunderstore.py`)
| Function | Description |
|----------|-------------|
| `fetch_all_packages()` | Fetch all mods from API | Récupérer tous les mods de l'API |
| `search_packages(pkgs, query)` | Search by name/description | Rechercher par nom/description |
| `get_popular_packages(pkgs)` | Get most downloaded | Obtenir les mods les plus téléchargés |
| `get_recently_updated(pkgs)` | Get latest updates | Obtenir les mises à jour les plus récentes |
| `download_package(pkg, dir)` | Download mod zip | Télécharger un mod zip |
| `parse_package(data)` | Parse API response | Parser la réponse de l'API |

### Config (`modmanager/config.py`)
| Function | Description |
|----------|-------------|
| `parse_config_file(path)` | Read .cfg settings | Lire les paramètres .cfg |
| `save_config_file(path, settings)` | Save settings | Sauvegarder les paramètres |

### Utils (`modmanager/utils.py`)
| Function | Description |
|----------|-------------|
| `filter_mods_by_name(mods, term)` | Search installed mods | Rechercher des mods installés |
| `format_mod_info(mod)` | Pretty-print mod info | Afficher les informations des mods |
| `get_mod_dependencies(mod)` | Get dependency list | Obtenir la liste des dépendances |
| `format_dependency_tree(tree)` | Format tree display | Format de l'arbre des dépendances |

## How Thunderstore Download Works | Comment le téléchargement Thunderstore fonctionne

1. The app fetches the package list from `thunderstore.io/c/riskofrain2/api/v1/package/` | L'application récupère la liste des paquets de `thunderstore.io/c/riskofrain2/api/v1/package/`
2. You can search, browse popular, or see recent updates | Vous pouvez rechercher, parcourir les mods les plus populaires, ou voir les mises à jour les plus récentes
3. Select a mod to view details | Sélectionnez un mod pour voir les détails
4. Choose "Download and install" to | Choisissez "Télécharger et installer" pour :
   - Download the zip to `./downloads/` | Télécharger le zip dans `./downloads/`
   - Extract to your plugins folder | Extraire dans votre dossier de plugins
   - Check for missing dependencies | Vérifier les dépendances manquantes

## Requirements | Exigences

- Python 3.10+ | Python 3.10+
- Internet connection (for Thunderstore features) | Connexion Internet (pour les fonctionnalités Thunderstore)
- Risk of Rain 2 with BepInEx installed | Risk of Rain 2 avec BepInEx installé

## License | Licence ( Encore une fois le meme mot que en anglais ehehe )

MIT License - Made for educational purposes. | MIT License - Made for educational purposes.
