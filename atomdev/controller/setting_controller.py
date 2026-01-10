import os
import shutil
from pathlib import Path

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QFileDialog
from loguru import logger
from pylizlib.qtfw.util.ui import UiUtils
from pylizlib.qtfw.widgets.dialog.about import AboutMessageBox
from qfluentwidgets import MessageBox

from atomdev.application.app import app_settings, AppSettings, PATH_BACKUPS, RESOURCE_ID_LOGO, app
from atomdev.model.dashboard import DashboardModel
from atomdev.view.setting import WidgetSettings


class SettingController:

    def __init__(self, dash_model: DashboardModel):
        self.view = WidgetSettings()
        self.dash_model = dash_model

        self.view.signal_request_update.connect(self.dash_model.update)
        self.view.signal_ask_catalogue_path.connect(self.__ask_catalogue_path)
        self.view.signal_open_dir_request.connect(self.__open_directory)
        self.view.signal_clear_backups_request.connect(self.__clear_backup_directory)
        self.view.signal_open_about_dialog_request.connect(self.__open_info_dialog)

    def __ask_catalogue_path(self):
        directory = QFileDialog.getExistingDirectory(None, "Seleziona la cartella del catalogo")
        if directory:
            logger.trace(f"Percorso selezionato: {directory}")
            app_settings.set(AppSettings.catalogue_path, Path(directory))
            self.view.card_general_catalogue.setContent(directory)
            self.dash_model.snap_catalogue.set_catalogue_path(Path(directory))
            self.dash_model.update()
        else:
            logger.trace("Nessun percorso selezionato.")

    def __open_directory(self):
        import subprocess
        import platform

        path = app.path

        if platform.system() == "Windows":
            os.startfile(path)
        elif platform.system() == "Darwin":
            subprocess.Popen(["open", path])
        else:
            subprocess.Popen(["xdg-open", path])

    def __clear_backup_directory(self):
        try:
            w = MessageBox("Pulizia cartella di backup", "Sei sicuro di voler pulire la cartella di backup ? Questa operazione eliminerà tutti i file presenti nella cartella di backup.", parent=self.view)
            if  w.exec_():
                shutil.rmtree(PATH_BACKUPS)
        except Exception as e:
            logger.error(f"Errore durante la pulizia della cartella di backup: {str(e)}")
            UiUtils.show_message("Errore", "Si è verificato un errore durante la pulizia della cartella di backup: " + str(e))
            return

    def __open_info_dialog(self):
        w = AboutMessageBox(QIcon(RESOURCE_ID_LOGO), app.name,app.version, self.view)
        if w.exec_():
            pass
