import logging
import sys
from pathlib import Path

from loguru import logger
from loguru_logging_intercept import setup_loguru_logging_intercept
from pylizlib.core.app.pylizapp import PylizApp
from pylizlib.core.os.snap import SnapshotSettings
from pylizlib.core.os.utils import PATH_DEFAULT_GIT_BASH
from pylizlib.qtfw.domain.setting import QtFwQConfigItem
from pylizlib.qtfw.model.qconfig import TextListValidator, ExecutableValidator
from qfluentwidgets import QConfig, ConfigItem, BoolValidator, qconfig, FolderValidator

from atomdev.project import version, name, authors

# Application object
app = PylizApp(name, version, name, authors[0][0])

# Application directories
PATH_CATALOGUE = Path(app.get_path()).joinpath("Catalogue")
PATH_SCRIPTS = Path(app.get_path()).joinpath("Scripts")
PATH_TRASH = Path(app.get_path()).joinpath("Trash")
PATH_LOGS = Path(app.get_path()).joinpath("Logs")
PATH_TEMP = Path(app.get_path()).joinpath("Temp")
PATH_BACKUPS = Path(app.get_path()).joinpath("Backups")
PATH_JSON_SETTING_FILE = Path(app.get_path()).joinpath("Settings.json")

# VALORI DI DEFAULT DELLE IMPOSTAZIONI
DEFAULT_SETTING_CATALOGUE_PATH = PATH_CATALOGUE.__str__()
DEFAULT_SETTING_STARRED_DIRS = []
DEFAULT_SETTING_STARRED_FILES = []
DEFAULT_SETTING_STARRED_EXES = []
DEFAULT_SETTING_STARRED_SERVICES = []
DEFAULT_SETTING_CONFIGURATION_TAGS = ["JIRA", "IntLay", "WTC"]
DEFAULT_SETTING_SNAPSHOTS_CUSTOM_DATA = ["Famiglia", "Macchina"]
DEFAULT_SETTING_PATH_GIT_BASH = PATH_DEFAULT_GIT_BASH.__str__()
DEFAULT_SETTING_CONFIG_BACKUP_BEFORE_INSTALL = True
DEFAULT_SETTING_CONFIG_BACKUP_BEFORE_EDIT = False
DEFAULT_SETTING_CONFIG_BACKUP_BEFORE_DELETE = True

# DEFINIZIONE DEI GRUPPI DI IMPOSTAZIONI
SETTING_GROUP_CONFIGS = "Configurazioni"
SETTING_GROUP_SCRIPTS = "Scripts"
SETTING_GROUP_FAVORITES = "Preferiti"
SETTING_GROUP_APP = "App"

# GESTIONE RISORSE
RESOURCE_ID_LOGO = ':/resources/logo2.png'

# GESTIONE LOGS
logger.remove()
if sys.stdout:
    logger.add(sys.stdout,level="DEBUG",format="{time:HH:mm:ss} | {level} | {message}", colorize=True)
logger.add(
    Path(PATH_LOGS).joinpath("{time:YYYY-MM-DD}.log").__str__(),
    level="DEBUG", format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {module}:{function}:{line} - {message}",
    rotation="00:00", retention="30 days", compression=None
)
setup_loguru_logging_intercept(level=logging.DEBUG, modules="pylizlib")
logger.info("{} Application Started. Version: {}", app.name, app.version)



# DEFINIZIONE DELLE IMPOSTAZIONI DELL'APPLICAZIONE
class AppSettings(QConfig):
    config_tags = QtFwQConfigItem(True, SETTING_GROUP_CONFIGS, "Tag configurazioni", DEFAULT_SETTING_CONFIGURATION_TAGS, TextListValidator())
    catalogue_path = QtFwQConfigItem(True, SETTING_GROUP_CONFIGS, "Catalogue Path", DEFAULT_SETTING_CATALOGUE_PATH, FolderValidator())
    backup_before_install = QtFwQConfigItem(True, SETTING_GROUP_CONFIGS, "Backup Before Install", DEFAULT_SETTING_CONFIG_BACKUP_BEFORE_INSTALL, BoolValidator())
    backup_before_edit = QtFwQConfigItem(True, SETTING_GROUP_CONFIGS, "Backup Before Edit", DEFAULT_SETTING_CONFIG_BACKUP_BEFORE_EDIT, BoolValidator())
    backup_before_delete = QtFwQConfigItem(True, SETTING_GROUP_CONFIGS, "Backup Before Delete", DEFAULT_SETTING_CONFIG_BACKUP_BEFORE_DELETE, BoolValidator())
    snap_custom_data = QtFwQConfigItem(False, SETTING_GROUP_CONFIGS, "Snapshots custom data", DEFAULT_SETTING_SNAPSHOTS_CUSTOM_DATA, TextListValidator())
    git_bash_path = QtFwQConfigItem(False, SETTING_GROUP_SCRIPTS, "Git Bash path", DEFAULT_SETTING_PATH_GIT_BASH, ExecutableValidator())
    starred_dirs = QtFwQConfigItem(True, SETTING_GROUP_FAVORITES,"Cartelle preferite", DEFAULT_SETTING_STARRED_DIRS, TextListValidator())
    starred_files = QtFwQConfigItem(False, SETTING_GROUP_FAVORITES,"File preferiti", DEFAULT_SETTING_STARRED_FILES, TextListValidator())
    starred_exes = QtFwQConfigItem(False, SETTING_GROUP_FAVORITES, "Eseguibili Preferiti", DEFAULT_SETTING_STARRED_EXES, TextListValidator())
    starred_services = QtFwQConfigItem(False, SETTING_GROUP_FAVORITES, "Servizi Preferiti", DEFAULT_SETTING_STARRED_SERVICES, TextListValidator())
    debug_test_mode = QtFwQConfigItem(False, SETTING_GROUP_APP, "DebugTestMode", False, BoolValidator())


# CARICAMENTO IMPOSTAZIONI
app_settings = AppSettings()
qconfig.load(PATH_JSON_SETTING_FILE, app_settings)

# IMPSOTAZIONE DEGLI SNAPSHOTS
snap_settings = SnapshotSettings(
    backup_path=PATH_BACKUPS,
    backup_pre_install=app_settings.get(AppSettings.backup_before_install),
    backup_pre_delete=app_settings.get(AppSettings.backup_before_delete),
    backup_pre_modify=app_settings.get(AppSettings.backup_before_edit),
    install_with_everyone_full_control=True,
    snap_id_length=20,
    folder_id_length=6
)