from PySide6.QtCore import QAbstractItemModel, Qt, Signal, QModelIndex
from PySide6.QtGui import QActionGroup
from PySide6.QtWidgets import QDialog, QHBoxLayout, QVBoxLayout, QWidget, QFrame, QHeaderView
from qfluentwidgets import (
    LineEdit,
    TableView,
    TreeView,
    FluentStyleSheet,
    CommandBar,
    Action,
    FluentIcon,
    TransparentDropDownPushButton,
    CheckableMenu,
    CardWidget,
    BodyLabel,
    ProgressBar,
    CaptionLabel,
    ComboBox,
    RoundMenu
)
from pylizlib.core.os.snap import QueryType, SearchTarget


class CatalogueSearcherView(QDialog):
    signal_delete_requested = Signal(int)
    signal_file_double_clicked = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)

        # Basic dialog settings
        self.setWindowTitle("Ricerca nel Catalogo")
        self.resize(1200, 800)

        # Main layout
        self.main_layout = QHBoxLayout(self)
        self.main_layout.setContentsMargins(10, 10, 10, 10)
        self.main_layout.setSpacing(10)

        # Left and Right sections
        self.left_widget = QWidget(self)
        self.right_widget = QWidget(self)

        # --- Left Section ---
        self.left_layout = QVBoxLayout(self.left_widget)
        self.left_layout.setContentsMargins(0, 0, 0, 0)
        self.left_layout.setSpacing(10)

        # CommandBar
        self.command_bar = CommandBar(self)
        self.action_start = Action(FluentIcon.SEARCH, "Start", self)
        self.action_stop = Action(FluentIcon.POWER_BUTTON, "Stop", self, enabled=False)

        self.target_button = TransparentDropDownPushButton("Target", self, FluentIcon.TILES)
        self.target_button.setMenu(self.__create_target_menu())

        self.query_type_button = TransparentDropDownPushButton("Tipo", self, FluentIcon.FONT)
        self.query_type_button.setMenu(self.__create_query_type_menu())

        self.extensions_button = TransparentDropDownPushButton("Estensioni", self, FluentIcon.FILTER)
        self.extensions_button.setMenu(self.__create_extensions_menu())

        self.command_bar.addAction(self.action_start)
        self.command_bar.addAction(self.action_stop)
        self.command_bar.addSeparator()
        self.command_bar.addWidget(self.target_button)
        self.command_bar.addWidget(self.query_type_button)
        self.command_bar.addWidget(self.extensions_button)

        # Search bar
        self.search_widget = QWidget(self)
        self.search_layout = QHBoxLayout(self.search_widget)
        self.search_layout.setContentsMargins(0, 0, 0, 0)
        self.search_bar = LineEdit(self)
        self.search_bar.setPlaceholderText("Inserisci il testo da cercare...")
        self.search_layout.addWidget(self.search_bar)

        # Status Card (initially hidden)
        self.status_card = CardWidget(self)
        status_layout = QVBoxLayout(self.status_card)

        self.status_card_label = BodyLabel("In attesa...", self.status_card)
        status_layout.addWidget(self.status_card_label)

        # Progress bar
        self.status_card_progress_bar = ProgressBar(self.status_card)
        status_layout.addWidget(self.status_card_progress_bar)

        # Percentage and ETA labels in a new QHBoxLayout below the progress bar
        progress_info_layout = QHBoxLayout()
        self.status_card_percentage_label = CaptionLabel("0%", self.status_card)
        self.status_card_eta_label = CaptionLabel("ETA: --", self.status_card)

        self.status_card_percentage_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self.status_card_eta_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

        progress_info_layout.addWidget(self.status_card_percentage_label)
        progress_info_layout.addStretch(1)
        progress_info_layout.addWidget(self.status_card_eta_label)
        status_layout.addLayout(progress_info_layout)

        self.status_card.hide()

        # Results table
        self.results_table = TableView(self)
        self.results_table.verticalHeader().hide()
        self.results_table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.results_table.customContextMenuRequested.connect(self._show_context_menu)
        self.results_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        self.column_percents = [0.25, 0.25, 0.15, 0.1625, 0.1875]
        self._distribuisci_colonne_perc()
        self.results_table.resizeEvent = self._table_resize_event

        # Add widgets to left layout
        self.left_layout.addWidget(self.command_bar)
        self.left_layout.addWidget(self.search_widget)
        self.left_layout.addWidget(self.status_card)
        self.left_layout.addSpacing(30)
        self.left_layout.addWidget(self.results_table)

        # --- Right Section ---
        self.right_layout = QVBoxLayout(self.right_widget)
        self.right_layout.setContentsMargins(0, 0, 0, 0)
        self.right_layout.setSpacing(5)
        self.tree_view = TreeView(self)
        self.tree_view.doubleClicked.connect(self._on_tree_view_double_clicked)
        self.tree_view.header().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.tree_view.header().setStretchLastSection(False)
        self.tree_view.setIndentation(20)
        FluentStyleSheet.TREE_VIEW.apply(self.tree_view)
        self.right_layout.addWidget(self.tree_view)

        # Add widgets to main layout
        self.main_layout.addWidget(self.left_widget, 2)
        line = QFrame()
        line.setFrameShape(QFrame.Shape.VLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        self.main_layout.addWidget(line)
        self.main_layout.addWidget(self.right_widget, 1)

        # Apply Fluent Design stylesheet
        FluentStyleSheet.DIALOG.apply(self)

        # Set initial placeholder
        self._update_search_bar_placeholder()

    def _on_tree_view_double_clicked(self, index: QModelIndex):
        item = self.tree_view.model().itemFromIndex(index)
        if item and item.parent():  # It's a child item (file path)
            file_path = item.text()
            self.signal_file_double_clicked.emit(file_path)

    def _show_context_menu(self, pos):
        index = self.results_table.indexAt(pos)
        if not index.isValid():
            return

        menu = RoundMenu(parent=self)
        delete_action = Action(FluentIcon.DELETE, "Rimuovi dalla ricerca")
        delete_action.triggered.connect(lambda: self.signal_delete_requested.emit(index.row()))
        menu.addAction(delete_action)
        menu.exec(self.results_table.viewport().mapToGlobal(pos))

    def __create_extensions_menu(self):
        menu = CheckableMenu(parent=self)

        # Create an action group and allow non-exclusive selection
        action_group = QActionGroup(self)
        action_group.setExclusive(False)

        self.action_ext_txt = Action(".txt", self, checkable=True)
        self.action_ext_log = Action(".log", self, checkable=True)
        self.action_ext_ini = Action(".ini", self, checkable=True)
        self.action_ext_json = Action(".json", self, checkable=True)
        self.action_ext_xml = Action(".xml", self, checkable=True)

        # Set default checked state
        self.action_ext_txt.setChecked(True)
        self.action_ext_log.setChecked(True)
        self.action_ext_ini.setChecked(True)
        self.action_ext_json.setChecked(True)
        self.action_ext_xml.setChecked(True)

        # Add actions to the group
        action_group.addAction(self.action_ext_txt)
        action_group.addAction(self.action_ext_log)
        action_group.addAction(self.action_ext_ini)
        action_group.addAction(self.action_ext_json)
        action_group.addAction(self.action_ext_xml)

        menu.addActions([self.action_ext_txt, self.action_ext_log, self.action_ext_ini, self.action_ext_json, self.action_ext_xml])
        return menu

    def __create_target_menu(self):
        menu = CheckableMenu(parent=self)
        action_group = QActionGroup(self)
        action_group.setExclusive(True)

        self.action_target_map = {}
        target_names = {
            SearchTarget.FILE_NAME: "Nome del file",
            SearchTarget.FILE_CONTENT: "Contenuto del file"
        }
        for target in SearchTarget:
            action = Action(target_names.get(target, target.name.replace("_", " ").title()), self, checkable=True)
            action.setData(target)
            action.triggered.connect(self._update_search_bar_placeholder)
            self.action_target_map[target] = action
            action_group.addAction(action)
            menu.addAction(action)

        # Set default
        self.action_target_map[SearchTarget.FILE_CONTENT].setChecked(True)
        return menu

    def __create_query_type_menu(self):
        menu = CheckableMenu(parent=self)
        action_group = QActionGroup(self)
        action_group.setExclusive(True)

        self.action_query_type_map = {}
        for query_type in QueryType:
            action = Action(query_type.name.title(), self, checkable=True)
            action.setData(query_type)
            action.triggered.connect(self._update_search_bar_placeholder)
            self.action_query_type_map[query_type] = action
            action_group.addAction(action)
            menu.addAction(action)

        # Set default
        self.action_query_type_map[QueryType.TEXT].setChecked(True)
        return menu

    def _update_search_bar_placeholder(self):
        target = self.get_selected_search_target()
        query_type = self.get_selected_query_type()

        if target == SearchTarget.FILE_CONTENT and query_type == QueryType.TEXT:
            self.search_bar.setPlaceholderText("Cerca il contenuto di un file")
        elif target == SearchTarget.FILE_CONTENT and query_type == QueryType.REGEX:
            self.search_bar.setPlaceholderText("Cerca il contenuto di un file usando una regex")
        elif target == SearchTarget.FILE_NAME and query_type == QueryType.TEXT:
            self.search_bar.setPlaceholderText("Cerca il nome di un file")
        elif target == SearchTarget.FILE_NAME and query_type == QueryType.REGEX:
            self.search_bar.setPlaceholderText("Cerca il nome di un file usando una regex")

    def get_selected_extensions(self) -> list[str]:
        extensions = []
        if self.action_ext_txt.isChecked():
            extensions.append(".txt")
        if self.action_ext_log.isChecked():
            extensions.append(".log")
        if self.action_ext_ini.isChecked():
            extensions.append(".ini")
        if self.action_ext_json.isChecked():
            extensions.append(".json")
        if self.action_ext_xml.isChecked():
            extensions.append(".xml")
        return extensions

    def get_selected_query_type(self) -> QueryType:
        for query_type, action in self.action_query_type_map.items():
            if action.isChecked():
                return query_type
        return QueryType.TEXT  # Default fallback

    def get_selected_search_target(self) -> SearchTarget:
        for target, action in self.action_target_map.items():
            if action.isChecked():
                return target
        return SearchTarget.FILE_CONTENT  # Default fallback

    def set_operation_status(self, active: bool):
        """Sets the UI state based on whether a search operation is active."""
        is_enabled = not active
        self.search_bar.setEnabled(is_enabled)
        self.results_table.setEnabled(is_enabled)
        self.extensions_button.setEnabled(is_enabled)
        self.target_button.setEnabled(is_enabled)
        self.query_type_button.setEnabled(is_enabled)

        if active:
            self.status_card.show()
        else:
            self.status_card.hide()

    def update_status_card(self, text: str, value: int, eta: str = "--"):
        """Updates the status card with text, progress, and ETA."""
        self.status_card_label.setText(text)
        self.status_card_progress_bar.setValue(value)
        self.status_card_percentage_label.setText(f"{value}%")
        self.status_card_eta_label.setText(f"ETA: {eta}")

    def setModel(self, model: QAbstractItemModel):
        self.results_table.setModel(model)
        self._distribuisci_colonne_perc()

    def _distribuisci_colonne_perc(self):
        total_width = self.results_table.viewport().width()
        if total_width == 0:
            return
        for idx, perc in enumerate(self.column_percents):
            width = int(total_width * perc)
            self.results_table.setColumnWidth(idx, width)

    def _table_resize_event(self, event):
        self._distribuisci_colonne_perc()
        super(type(self.results_table), self.results_table).resizeEvent(event)