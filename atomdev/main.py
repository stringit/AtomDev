import sys

from PySide6.QtWidgets import QApplication


from atomdev.controller.dashboard import DashboardController
from atomdev.view.splash import SplashWindow



if __name__ == "__main__":
    app = QApplication(sys.argv)
    splash = SplashWindow()
    splash.show()
    splash.close()
    dashboard = DashboardController()
    dashboard.start()
    app.exec()