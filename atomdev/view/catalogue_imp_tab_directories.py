from pathlib import Path

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QListWidgetItem, QFileDialog, QHBoxLayout, QWidget, QSizePolicy, QSpacerItem, QVBoxLayout
from pylizlib.core.os.snap import Snapshot
from pylizlib.qtfw.util.ui import UiUtils
from qfluentwidgets import FluentIcon, PushButton, Action, RoundMenu, ListWidget


class TabDirectories(QWidget):

    Signal_btn_add_dir = Signal(str)
    Signal_btn_choose_dir = Signal()
    signal_data_changed = Signal(bool)

    def __init__(
            self,
            payload_data: Snapshot | None = None,
            starred_dirs: list[Path] = []
    ):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.directories: list[Path] = []
        self.starred_dirs_paths = [p.__str__() for p in starred_dirs]
        self.payload_data: Snapshot | None = payload_data

        # Widget
        self.listWidget = ListWidget(self)
        self.listWidget.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.listWidget.customContextMenuRequested.connect(self.__show_context_menu)
        self.btn_widget = self.__get_btn_widget()

        # Aggiungo i widget al layout
        self.layout.addSpacerItem(QSpacerItem(20, 10, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))
        self.layout.addWidget(self.btn_widget)
        self.layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))
        self.layout.addWidget(self.listWidget)
        self.layout.addStretch()

        self.Signal_btn_add_dir.connect(self.__on_add_directory_request)
        self.Signal_btn_choose_dir.connect(self.__on_add_directory_request)

        # Se sono in edit mode, popolo la lista
        if self.payload_data:
            for dir_assoc in self.payload_data.directories:
                self.add_directory(Path(dir_assoc.original_path), execute_checks=False)
            self._capture_initial_directories_state()

    # AGGIUNTO: Metodo per catturare lo stato iniziale delle directory
    def _capture_initial_directories_state(self):
        """Cattura lo stato iniziale delle directory per il tracking delle modifiche"""
        self._initial_directories = set(str(d) for d in self.directories)

    # AGGIUNTO: Metodo per verificare se ci sono state modifiche
    def _check_directories_changed(self):
        """Verifica se le directory sono state modificate rispetto allo stato iniziale"""
        if not hasattr(self, '_initial_directories'):
            # Se non c'è stato iniziale, considera modificato se ci sono directory
            return len(self.directories) > 0

        current_directories = set(str(d) for d in self.directories)
        changed = current_directories != self._initial_directories
        self.signal_data_changed.emit(changed)
        return None

    def __show_context_menu(self, pos):
        item = self.listWidget.itemAt(pos)
        if item is not None:
            menu = RoundMenu()
            action_delete = Action(FluentIcon.DELETE, "Cancella",
                                   triggered=lambda: self.__delete_selected_item(item))
            menu.addAction(action_delete)
            global_pos = self.listWidget.mapToGlobal(pos)
            menu.exec(global_pos)

    def __get_btn_widget(self):
        btn_container = QWidget(self)
        btn_layout = QHBoxLayout(btn_container)
        btn_layout.addStretch()  # spazio a sinistra

        self.btn_choose_dir = PushButton("Aggiungi cartella locale", self, FluentIcon.FOLDER_ADD)
        self.btn_choose_dir.setMaximumWidth(300)
        self.btn_choose_dir.clicked.connect(lambda: self.Signal_btn_choose_dir.emit())
        btn_layout.addWidget(self.btn_choose_dir)

        self.btn_choose_dir_starred = UiUtils.create_widget_act_bar_btn(
            self,
            self.starred_dirs_paths,
            "Aggiungi cartella preferita",
            FluentIcon.FOLDER_ADD,
            False,
            self.Signal_btn_add_dir,
            FluentIcon.FOLDER
        )
        self.btn_choose_dir_starred.setMaximumWidth(300)
        btn_layout.addWidget(self.btn_choose_dir_starred)
        btn_layout.addStretch()  # spazio a destra
        return btn_container

    def __on_add_directory_request(self, path: str | None = None):
        if path is None:
            dir_path = QFileDialog.getExistingDirectory(self, "Seleziona una cartella ad aggiungere alla lista", )
            if dir_path:
                self.add_directory(Path(dir_path))
            else:
                return
        else:
            self.add_directory(Path(path))

    def add_directory(self, directory: Path, execute_checks: bool = True):
        if execute_checks:
            if directory in self.directories:
                UiUtils.show_message("Attenzione", "La cartella selezionata è già presente nella lista.", self)
                return
            if not directory.exists():
                UiUtils.show_message("Attenzione", "La cartella selezionata non esiste nel sistema.", self)
                return
            if not directory.is_dir():
                UiUtils.show_message("Attenzione", "La cartella selezionata non è una cartella valida.", self)
                return
        self.directories.append(directory)
        item = QListWidgetItem(directory.__str__())
        self.listWidget.addItem(item)

        if execute_checks:
            self._check_directories_changed()

    def __delete_selected_item(self, item: QListWidgetItem):
        dir_path = Path(item.text())
        if dir_path in self.directories:
            self.directories.remove(dir_path)
        self.listWidget.takeItem(self.listWidget.row(item))
        self._check_directories_changed()