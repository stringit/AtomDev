from pathlib import Path

from loguru import logger
from pylizlib.qt.domain.view import UiWidgetMode
from qfluentwidgets import FluentIcon, NavigationItemPosition

from atomdev.application.app import app_settings, AppSettings
from atomdev.controller.catalogue import CatalogueController
from atomdev.controller.setting_controller import SettingController
from atomdev.domain.data import DevlizData, DevlizSnapshotData
from atomdev.model.dashboard import DashboardModel
from atomdev.view.dashboard import DashboardView


class DashboardController:

    def __init__(self, /):
        super().__init__()

        self.view = DashboardView()
        self.model = DashboardModel(self.view)

        self.catalogue = CatalogueController(self.model)
        self.settings = SettingController(self.model)

        self.view.addSubInterface(self.catalogue.view, FluentIcon.BOOK_SHELF, self.catalogue.view.window_name, NavigationItemPosition.TOP)
        self.view.addSubInterface(self.settings.view, FluentIcon.SETTING, self.settings.view.window_name,NavigationItemPosition.BOTTOM)


        self.cached_data : DevlizData | None = None



    def __handle_data_updated(self, data: DevlizData):
        logger.debug("Updated dashboard data received in controller. Updating view...")
        logger.debug(data)
        snap_data = DevlizSnapshotData(snapshot_list=data.snapshots) # TODO: sistemare
        self.cached_data = data
        self.catalogue.update_data(snap_data)

        self.model.snap_catalogue.path_catalogue = Path(app_settings.get(AppSettings.catalogue_path))


    def __handle_update_started(self):
        self.catalogue.view.set_state(UiWidgetMode.UPDATING)

    def __handle_update_complete(self):
        self.catalogue.view.set_state(UiWidgetMode.DISPLAYING)

    def __connect_signals(self):
        self.view.f5_pressed.connect(self.model.update)
        self.model.signal_on_update_started.connect(self.__handle_update_started)
        self.model.signal_on_update_complete.connect(self.__handle_update_complete)
        self.model.signal_on_updated_data_available.connect(self.__handle_data_updated)

    def start(self):
        logger.info("Application is starting...")
        self.view.show()
        self.__connect_signals()
        self.model.update()
        self.catalogue.init()
