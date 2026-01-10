from PySide6.QtWidgets import QSizePolicy, QSpacerItem
from pylizlib.qtfw.domain.setting import QtFwQConfigItem
from qfluentwidgets import SettingCardGroup, ConfigItem

from atomdev.application.app import AppSettings, app_settings


class SettingGroupManager:

    def __init__(self, name: str, parent, group_enabled: bool = True):
        self.group_enabled = group_enabled
        self.group = SettingCardGroup(name, parent)
        self.group.setSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.Fixed)
        self.debug_test_mode = app_settings.get(AppSettings.debug_test_mode)


    def add_widget(self, setting: QtFwQConfigItem | None, widget, signal):
        if setting is None:
            self.__add_widget_(widget, signal)
            return
        if self.debug_test_mode:
            self.__add_widget_(widget, signal)
            return
        if not setting.enabled:
            return
        self.__add_widget_(widget, signal)


    def __add_widget_(self, widget, signal):
        widget.setSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.Fixed)
        if signal is not None:
            widget.clicked.connect(signal.emit)
        self.group.addSettingCard(widget)

    def install_group_on(self, layout):
        layout.addSpacerItem(QSpacerItem(1, 5))
        layout.addWidget(self.group)

    def install_spacer_on(self, layout):
        layout.addSpacerItem(QSpacerItem(1, 10))
