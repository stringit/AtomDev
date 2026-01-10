from pathlib import Path

from PySide6.QtCore import Signal, Qt, QMargins, QModelIndex
from PySide6.QtGui import QActionGroup
from PySide6.QtWidgets import QHBoxLayout, QWidget, QHeaderView
from pylizlib.core.os.snap import Snapshot, SnapshotSortKey
from qfluentwidgets import SearchLineEdit, Action, FluentIcon, CommandBar, setFont, BodyLabel, RoundMenu, \
    TransparentDropDownPushButton, CheckableMenu, MenuIndicatorType, TableView

from atomdev.application.app import app_settings, AppSettings
from atomdev.model.catalogue import CatalogueModel
from atomdev.view.util.frame import DevlizQFrame


class SnapshotCatalogueUiBuilder:

    def __init__(self, parent):
        self.parent = parent


class SnapshotCatalogueWidget(DevlizQFrame):
    signal_import_requested = Signal()
    signal_sort_requested = Signal(SnapshotSortKey)
    signal_edit_requested = Signal(Snapshot)
    signal_install_requested = Signal(Snapshot)
    signal_delete_requested = Signal(Snapshot)
    signal_delete_installed_folders_requested = Signal(Snapshot)
    signal_open_folder_requested = Signal(Snapshot)
    signal_open_assoc_folder_requested = Signal(Path)
    signal_duplicate_requested = Signal(Snapshot)
    signal_search_internal_content_all = Signal()
    signal_search_internal_content_single = Signal(Snapshot)
    signal_export_request_snapshot = Signal(Snapshot)
    signal_export_request_assoc_folders = Signal(Snapshot)
    signal_update_with_local_dirs_requested = Signal(Snapshot)

    def __init__(self, model: CatalogueModel, parent=None):
        super().__init__(name="Catalogo", parent=parent)

        # Il modello è l'unica fonte di verità per i dati
        self.model = model

        # Aggiungo i widgets
        self.__setup_label()
        self.__setup_action_bar()
        self.__setup_table()
        self.__setup_footer()

    def __setup_label(self):
        self.install_label_title()

    def __setup_action_bar(self):
        self.search_line_edit = SearchLineEdit(self)
        self.search_line_edit.textChanged.connect(self.model.filter)

        self.action_import = Action(FluentIcon.ADD, 'Importa', triggered=lambda: self.signal_import_requested.emit())
        self.action_edit = Action(FluentIcon.EDIT, 'Modifica', enabled=False,triggered=lambda: self.signal_edit_requested.emit())

        menu_combobox_sort = TransparentDropDownPushButton("Ordina", self, FluentIcon.SCROLL)
        menu_combobox_sort.setMenu(self.__get_sort_menu())
        menu_combobox_sort.setFixedHeight(34)

        self.action_search_internal_all = Action(FluentIcon.SEARCH, "Cerca contenuto",triggered=lambda: self.signal_search_internal_content_all.emit())

        left_command_bar = CommandBar()
        left_command_bar.setMinimumWidth(600)
        left_command_bar.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        left_command_bar.addAction(self.action_import)
        left_command_bar.addAction(self.action_search_internal_all)
        left_command_bar.addWidget(menu_combobox_sort)

        lay = QHBoxLayout()
        lay.addWidget(left_command_bar)
        lay.addStretch(1)
        lay.addWidget(self.search_line_edit)

        container = QWidget()
        container.setLayout(lay)

        self.master_layout.addWidget(container)

    def __get_sort_menu(self, pos=None):
        menu = CheckableMenu(parent=self, indicatorType=MenuIndicatorType.RADIO)

        action_sort_name = Action(FluentIcon.QUICK_NOTE, "Nome", checkable=True, triggered=lambda: self.signal_sort_requested.emit(SnapshotSortKey.NAME))
        action_sort_author = Action(FluentIcon.PEOPLE, "Autore", checkable=True,triggered=lambda: self.signal_sort_requested.emit(SnapshotSortKey.AUTHOR))
        action_sort_date_create = Action(FluentIcon.CALENDAR, "Data creazione", checkable=True,triggered=lambda: self.signal_sort_requested.emit( SnapshotSortKey.DATE_CREATED))
        action_sort_date_modify = Action(FluentIcon.EDIT, "Data modifica", checkable=True,triggered=lambda: self.signal_sort_requested.emit(SnapshotSortKey.DATE_MODIFIED))
        action_sort_date_dim_mb_assoc = Action(FluentIcon.FOLDER, "Dimensione", checkable=True,triggered=lambda: self.signal_sort_requested.emit(SnapshotSortKey.ASSOC_DIR_MB_SIZE))

        action_sort_group = QActionGroup(self)
        action_sort_group.addAction(action_sort_name)
        action_sort_group.addAction(action_sort_author)
        action_sort_group.addAction(action_sort_date_create)
        action_sort_group.addAction(action_sort_date_modify)
        action_sort_group.addAction(action_sort_date_dim_mb_assoc)

        menu.addActions([
            action_sort_name,
            action_sort_author,
            action_sort_date_create,
            action_sort_date_modify,
            action_sort_date_dim_mb_assoc,
        ])

        if pos is not None:
            menu.exec(pos, ani=True)

        return menu

    def __setup_table(self):
        self.table = TableView(self)
        self.table.setModel(self.model.table_model)

        # Abilita bordi e angoli arrotondati come nel TableWidget originale
        self.table.setBorderVisible(True)
        self.table.setBorderRadius(8)

        self.table.setWordWrap(False)
        self.table.verticalHeader().hide()
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        self.table.setSelectionBehavior(TableView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(TableView.SelectionMode.SingleSelection)

        self.table.doubleClicked.connect(self._on_table_item_double_clicked)
        self.table.selectionModel().selectionChanged.connect(self._on_item_selection_changed)
        self.table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self._show_context_menu)

        # Percentuali colonne
        self.column_percents = [0.20, 0.25, 0.10, 0.10, 0.18, 0.17]
        self._distribuisci_colonne_perc()
        self.table.resizeEvent = self._table_resize_event

        self.master_layout.addWidget(self.table)

    def __setup_footer(self, count: int = 0, size: str = "0"):
        lay = QHBoxLayout()
        self.footer_path_label = BodyLabel(app_settings.get(AppSettings.catalogue_path), self)
        setFont(self.footer_path_label, 12)
        self.footer_path_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

        self.footer_stats_label = BodyLabel(f"Totale configurazioni: {count} ({size})", self)
        setFont(self.footer_stats_label, 12)
        self.footer_stats_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

        lay.addWidget(self.footer_path_label)
        lay.addStretch(1)
        lay.addWidget(self.footer_stats_label)

        lay.setContentsMargins(QMargins(5, 0, 5, 0))

        container = QWidget(self)
        container.setLayout(lay)
        self.master_layout.addWidget(container)

    def _get_export_context_menu(self, snapshot: Snapshot) -> RoundMenu:
        submenu = RoundMenu("Esporta", self)
        submenu.setIcon(FluentIcon.DOWNLOAD)
        submenu.addActions([
            Action(FluentIcon.DICTIONARY, 'Snapshot (.zip)', triggered=lambda: self.signal_export_request_snapshot.emit(snapshot)),
            Action(FluentIcon.FOLDER, 'Cartelle associate (.zip)', triggered=lambda: self.signal_export_request_assoc_folders.emit(snapshot)),
        ])
        return submenu

    def _get_delete_context_menu(self, snapshot: Snapshot) -> RoundMenu:
        submenu = RoundMenu("Cancella", self)
        submenu.setIcon(FluentIcon.DELETE)
        submenu.addActions([
            Action(FluentIcon.DELETE, 'Cartelle installate', triggered=lambda: self.signal_delete_installed_folders_requested.emit(snapshot)),
            Action(FluentIcon.DELETE, 'Snapshot intero', triggered=lambda: self.signal_delete_requested.emit(snapshot)),
        ])
        return submenu

    def _get_open_context_menu(self, snapshot: Snapshot) -> RoundMenu:
        submenu = RoundMenu("Apri", self)
        submenu.setIcon(FluentIcon.VIEW)
        submenu.addActions([
            Action(FluentIcon.FOLDER, 'Cartella snapshot', triggered=lambda: self.signal_open_folder_requested.emit(snapshot)),
        ])
        for assoc in snapshot.directories:
            submenu.addAction(Action(FluentIcon.FOLDER, f'Cartella locale associata: {Path(assoc.original_path).name}', triggered=lambda a=assoc: self.signal_open_assoc_folder_requested.emit(Path(assoc.original_path))))
        return submenu

    def _show_context_menu(self, pos):
        index = self.table.indexAt(pos)
        if not index.isValid():
            return

        config = self.model.get_snapshot_at(index.row())
        if not config:
            return

        menu = RoundMenu()
        menu.addAction(Action(FluentIcon.DOWN, "Installa", triggered=lambda: self.signal_install_requested.emit(config)))
        menu.addAction(Action(FluentIcon.EDIT, "Modifica", triggered=lambda: self.signal_edit_requested.emit(config)))
        menu.addAction(Action(FluentIcon.SEARCH, "Cerca contenuto",triggered=lambda: self.signal_search_internal_content_single.emit(config)))
        menu.addAction(Action(FluentIcon.UP, "Aggiorna con locali", triggered=lambda: self.signal_update_with_local_dirs_requested.emit(config)))
        menu.addAction(Action(FluentIcon.DICTIONARY_ADD, "Duplica", triggered=lambda: self.signal_duplicate_requested.emit(config)))
        menu.addSeparator()
        menu.addMenu(self._get_open_context_menu(config))
        menu.addMenu(self._get_export_context_menu(config))
        menu.addMenu(self._get_delete_context_menu(config))
        global_pos = self.table.viewport().mapToGlobal(pos)
        menu.exec(global_pos)

    def _on_table_item_double_clicked(self, index: QModelIndex):
        config = self.model.get_snapshot_at(index.row())
        if config:
            self.signal_open_folder_requested.emit(config)

    def _on_item_selection_changed(self):
        has_selection = self.table.selectionModel().hasSelection()
        self.action_edit.setEnabled(has_selection)

    def _distribuisci_colonne_perc(self):
        total_width = self.table.viewport().width()
        if total_width > 0:
            for idx, perc in enumerate(self.column_percents):
                width = int(total_width * perc)
                self.table.setColumnWidth(idx, width)

    def _table_resize_event(self, event):
        self._distribuisci_colonne_perc()
        super(type(self.table), self.table).resizeEvent(event)

    def sort(self, method: SnapshotSortKey):
        self.search_line_edit.clear()
        self.model.sort(method)

    def reload_data(self):
        self.footer_stats_label.setText(f"Totale configurazioni: {self.model.count()} ({self.model.get_mb_size()})")

        # Aggiorna il path se necessario e le intestazioni della tabella
        new_path = app_settings.get(AppSettings.catalogue_path)
        if self.footer_path_label.text() != new_path:
            self.footer_path_label.setText(new_path)

        self._distribuisci_colonne_perc()

        

