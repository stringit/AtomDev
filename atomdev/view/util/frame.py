from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QWidget, QVBoxLayout
from pylizlib.qt.domain.view import UiWidgetMode
from qfluentwidgets import SubtitleLabel, setFont, SingleDirectionScrollArea, IndeterminateProgressBar, BodyLabel



class DevlizQFrameUiBuilder:

    def __init__(self, parent=None):
        self.parent = parent

    def get_updating_progress_bar(self):
        progress_bar = IndeterminateProgressBar(self.parent, start=True)
        progress_bar.setRange(0, 0)  # Indeterminate
        return progress_bar

    def get_label_updating(self):
        updating_label = BodyLabel("Aggiornamento in corso attendere", parent=self.parent)
        updating_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        return updating_label

    def get_label_title(self, text) -> SubtitleLabel:
        label = SubtitleLabel(text, self.parent)
        setFont(label, 24)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        return label


class DevlizQFrame(QFrame):

    def __init__(self, name: str, parent=None):
        super().__init__(parent=parent)
        self.setObjectName(name.replace(' ', '-'))
        self.window_name = name
        self.__builder = DevlizQFrameUiBuilder(self)

        # --- Layout per il widget di aggiornamento
        self._top_level_layout = QVBoxLayout(self)
        self._top_level_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self._top_level_layout.setContentsMargins(0, 0, 0, 0)

        # --- Widget di aggiornamento ---
        self.__updating_widget = QWidget(self)
        updating_layout = QVBoxLayout(self.__updating_widget)
        updating_layout.setContentsMargins(0, 0, 0, 0)
        updating_layout.addWidget(self.__builder.get_updating_progress_bar())
        updating_layout.addStretch()
        updating_layout.addWidget(self.__builder.get_label_updating())
        updating_layout.addStretch()
        self._top_level_layout.addWidget(self.__updating_widget)

        # --- Main Content Widget ---
        self.__main_content_widget = QWidget(self)
        self._top_level_layout.addWidget(self.__main_content_widget)

        self.master_layout = QVBoxLayout(self.__main_content_widget)
        self.master_layout.setAlignment(Qt.AlignmentFlag.AlignTop)


        self.__scroll_area = SingleDirectionScrollArea(orient=Qt.Orientation.Vertical)
        self.__scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.__scroll_area.setWidgetResizable(True)
        self.__scroll_view = QWidget()
        self.scroll_layout = QVBoxLayout(self.__scroll_view)

        self.set_state(UiWidgetMode.DISPLAYING)


    def get_scroll_layout(self) -> QVBoxLayout:
        return self.scroll_layout

    def install_scroll_on(self, layout: QVBoxLayout):
        self.__scroll_area.setWidget(self.__scroll_view)
        self.__scroll_area.enableTransparentBackground()
        layout.addWidget(self.__scroll_area)

    def set_state(self, mode: UiWidgetMode):
        if mode == UiWidgetMode.UPDATING:
            self.__updating_widget.show()
            self.__main_content_widget.hide()
        elif mode == UiWidgetMode.DISPLAYING:
            self.__updating_widget.hide()
            self.__main_content_widget.show()

    def install_label_title(self):
        title_label = self.__builder.get_label_title(self.window_name)
        self.master_layout.addWidget(title_label)
