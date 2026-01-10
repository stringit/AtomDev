import sys


from PySide6.QtCore import Signal
from PySide6.QtGui import QShortcut, QKeySequence, QIcon
from pylizlib.qt.domain.view import UiWidgetMode
from qfluentwidgets import FluentWindow, Theme, setTheme, setThemeColor, isDarkTheme, FluentIcon, NavigationItemPosition
from qframelesswindow.utils import getSystemAccentColor

from atomdev.application.app import app, RESOURCE_ID_LOGO

from atomdev.application.resources import resources_rc

class DashboardView(FluentWindow):

    f5_pressed = Signal()

    def __init__(self):
        super().__init__()
        self.__init_window()
        self.__init_shortcuts()

    def __init_window(self):
        self.resize(1100, 700)
        self.setWindowIcon(QIcon(RESOURCE_ID_LOGO))
        self.setWindowTitle(app.name)
        theme = Theme.LIGHT if not isDarkTheme() else Theme.DARK
        setTheme(theme, True, False)
        if sys.platform in ["win32", "darwin"]:
            setThemeColor(getSystemAccentColor(), save=True)

    def __init_shortcuts(self):
        shortcut = QShortcut(QKeySequence("F5"), self)
        shortcut.activated.connect(self.f5_pressed.emit)

    def set_state(self, state: UiWidgetMode):
        self.widget_catalogue.set_state(state)