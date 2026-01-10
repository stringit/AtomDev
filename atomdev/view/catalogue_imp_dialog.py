from PySide6.QtCore import Signal, Qt
from PySide6.QtWidgets import QDialog, QVBoxLayout
from pylizlib.core.os.snap import Snapshot
from pylizlib.qtfw.util.ui import UiUtils
from qfluentwidgets import FluentStyleSheet, PushButton, PrimaryPushButton

from atomdev.domain.data import DevlizData
from atomdev.view.catalogue_imp_tabs import DialogConfigTabs


class DialogConfig(QDialog):

    signal_payload = Signal(Snapshot, bool)

    def __init__(
            self,
            devliz_data: DevlizData,
            edit_mode: bool = False,
            edit_data: Snapshot | None = None,
            parent=None
    ):
        super().__init__(parent)

        # Setto le variabili
        self.edit_mode = edit_mode
        self.edit_data: Snapshot | None = edit_data
        self.devliz_data = devliz_data
        self.output_data: Snapshot | None = None

        # Impostazioni globali del dialog
        self.setWindowTitle(self.__get_dialog_text())
        self.resize(900, 550)

        # Impostazioni layout globale
        self.layout = QVBoxLayout(self)
        self.layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)
        self.layout.setContentsMargins(50, 0, 50, 50)
        self.layout.setSpacing(30)

        # Creo i widgets
        self.__tabs = DialogConfigTabs(self.devliz_data, self.edit_data)
        self.__btn_layout = self.__get_btn_layout()

        # Gestisco lo stato combinato delle modifiche
        self._form_modified = False
        self._directories_modified = False

        # Collego il segnale di cambio dati del tab dettagli
        self.__tabs.tab_details.signal_data_changed.connect(self._on_form_changed)
        self.__tabs.tab_directories.signal_data_changed.connect(self._on_directories_changed)

        # Aggiungo i widgets al layout
        self.layout.addWidget(self.__tabs)
        self.layout.addLayout(self.__btn_layout)

        FluentStyleSheet.DIALOG.apply(self)

    def __get_dialog_text(self):
        if not self.edit_mode:
            return "Importa una configurazione"
        config_name = self.edit_data.name if self.edit_data else ""
        return "Modifica una configurazione" + (f": {config_name}" if config_name else "")

    def _on_form_changed(self, changed: bool):
        """Gestisce le modifiche del form"""
        self._form_modified = changed
        self._update_button_state()

    def _on_directories_changed(self, changed: bool):
        """Gestisce le modifiche delle directory"""
        self._directories_modified = changed
        self._update_button_state()

    def _update_button_state(self):
        """Aggiorna lo stato del pulsante basandosi su entrambe le modifiche"""
        # Il pulsante è abilitato se ci sono modifiche nel form O nelle directory
        enabled = self._form_modified or self._directories_modified
        self.btn_create.setEnabled(enabled)

    def __get_btn_layout(self):
        # Creo layout pulsanti
        btn_layout = QVBoxLayout()
        btn_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        btn_layout.setSpacing(5)
        # Creo pulsante accetta
        btn_create_text = "CREA CONFIGURAZIONE" if not self.edit_mode else "SALVA MODIFICHE"
        self.btn_create = PrimaryPushButton(btn_create_text, self)
        self.btn_create.setMaximumWidth(600)
        self.btn_create.setEnabled(False) if self.edit_mode else None
        self.btn_create.clicked.connect(self.__handle_accept)
        btn_layout.addWidget(self.btn_create)
        # Creo pulsante chiudi
        btn_close = PushButton("CHIUDI", self)
        btn_close.setMaximumWidth(600)
        btn_layout.addWidget(btn_close)
        btn_close.clicked.connect(self.reject)

        return btn_layout

    def __handle_accept(self):
        data = self.__tabs.get_actual_data()
        if data is None:
            UiUtils.show_message("Errore", "Si è verificato un errore durante la creazione dei dati.", self)
            return
        if data.name.strip() == "":
            UiUtils.show_message("Errore", "Il campo 'Nome' non può essere vuoto.", self)
            return
        if not data.directories or len(data.directories) == 0:
            UiUtils.show_message("Errore", "Deve essere associata almeno una cartella alla configurazione.", self)
            return
        self.signal_payload.emit(data, self.edit_mode)
        self.output_data = data
        self.accept()