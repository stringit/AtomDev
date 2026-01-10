# == PROJECT VARIABLES ==
APP_NAME := Atomdev
PYTHON_MAIN_PACKAGE = atomdev
FILE_MAIN_CLI := $(PYTHON_MAIN_PACKAGE)/core/cli.py
FILE_MAIN := $(PYTHON_MAIN_PACKAGE)/main.py
QT_QRC_FILE := resources/resources.qrc
QT_RESOURCE_PY := $(PYTHON_MAIN_PACKAGE)/application/resources/resources_rc.py
INNO_SETUP_FILE := installer.iss
INNO_SETUP_VERSION_VARIABLE := MyAppVersion


# == FILES VARIABLES ==
FILE_PROJECT_TOML := pyproject.toml
FILE_PROJECT_PY_GENERATED := $(PYTHON_MAIN_PACKAGE)/project.py
FILE_MAIN_LOGO_ICO := resources/logo2.ico

# == EXTERNAL COMMANDS VARIABLES ==
QT_COMMAND_GEN_RES := pyside6-rcc