import datetime

from PySide6.QtWidgets import QWidget, QVBoxLayout, QStackedWidget
from loguru import logger
from pylizlib.core.data.gen import gen_random_string
from pylizlib.core.os.snap import Snapshot, SnapDirAssociation
from pylizlib.core.os.utils import get_system_username
from pylizlib.qtfw.util.ui import UiUtils
from qfluentwidgets import SegmentedWidget

from atomdev.application.app import app_settings, AppSettings
from atomdev.domain.data import DevlizData
from atomdev.view.catalogue_imp_tab_details import TabDetails
from atomdev.view.catalogue_imp_tab_directories import TabDirectories


class DialogConfigTabs(QWidget):

    def __init__(
            self,
            devliz_data: DevlizData,
            payload_data: Snapshot | None = None,
    ):
        super().__init__()
        self.payload_data: Snapshot | None = payload_data

        # struttura principale
        self.pivot = SegmentedWidget(self)
        self.stackedWidget = QStackedWidget(self)
        self.vBoxLayout = QVBoxLayout(self)

        # Creo i tabs
        self.tab_details = TabDetails(self.payload_data, app_settings.get(AppSettings.config_tags), app_settings.get(AppSettings.snap_custom_data))
        self.tab_directories = TabDirectories(self.payload_data, app_settings.get(AppSettings.starred_dirs))

        # Aggiungo i tabs al pivot
        self.__add_sub_interface(self.tab_details, "details", "Dettagli")
        self.__add_sub_interface(self.tab_directories, "directories", "Cartelle")

        # Aggiungo tutto al layout principale
        self.vBoxLayout.addWidget(self.pivot)
        self.vBoxLayout.addWidget(self.stackedWidget)
        self.vBoxLayout.setContentsMargins(30, 10, 30, 30)

        # Impostazioni globali del pivot
        self.stackedWidget.setCurrentWidget(self.tab_details)
        self.pivot.setCurrentItem(self.tab_details.objectName())
        self.pivot.currentItemChanged.connect(lambda k: self.stackedWidget.setCurrentWidget(self.findChild(QWidget, k)))

    def __add_sub_interface(self, widget: QWidget, objectName, text):
        widget.setObjectName(objectName)
        self.stackedWidget.addWidget(widget)
        self.pivot.addItem(routeKey=objectName, text=text)

    def get_actual_data(self) -> Snapshot | None:
        try:
            assoc: list[SnapDirAssociation] = []
            index = 0
            for directory in self.tab_directories.directories:
                assoc.append(
                    SnapDirAssociation(original_path=directory.__str__(), folder_id=gen_random_string(4), index=index))
                index += 1
            data = Snapshot(
                id=self.tab_details.form_id_value.text(),
                name=self.tab_details.form_name_input.text(),
                desc=self.tab_details.form_desc_input.text(),
                tags=self.tab_details.form_tags_input.get_items(),
                date_created=datetime.datetime.now(),
                author=get_system_username(),
                directories=assoc,
                data=self.tab_details.get_custom_data()
            )
            return data
        except Exception as e:
            logger.error(e)
            UiUtils.show_message("Errore", "Si è verificato un errore durante la raccolta dei dati.", self)
