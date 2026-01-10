from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QFormLayout, QVBoxLayout, QWidget
from pylizlib.core.data.gen import gen_random_string
from pylizlib.core.os.snap import Snapshot
from pylizlib.qtfw.widgets.input import MultiSelectionComboBox
from qfluentwidgets import BodyLabel, LineEdit, ComboBox

from atomdev.application.app import snap_settings


class TabDetails(QWidget):

    signal_data_changed = Signal(bool)

    def __init__(
            self,
            payload_data: Snapshot | None = None,
            tags: list[str] = [],
            custom_data_keys: list[str] = [],
    ):
        super().__init__()
        self.payload_data: Snapshot | None = payload_data
        self.tags = tags
        self.layout = QVBoxLayout(self)
        self.custom_data_keys = custom_data_keys
        self.custom_data_inputs = {}

        # Form layout
        self.form_layout = QFormLayout()
        self.form_layout.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        self.form_layout.setFormAlignment(Qt.AlignmentFlag.AlignCenter)
        self.form_layout.setSpacing(20)

        # Creo i campi
        self.__create_fields(self.tags)

        # Aggiungo tutto al layout principale
        self.layout.addLayout(self.form_layout)
        self.layout.addStretch()

        # Se sono in edit mode, popolo i campi
        if self.payload_data:
            self.__populate_fields()
            self._capture_initial_state()
            self._connect_change_signals()


    def __create_fields(self, tags: list[str]):
        # Campo id
        self.form_id_label = BodyLabel("ID:", self)
        self.form_id_value = LineEdit()
        self.form_id_value.setText(gen_random_string(snap_settings.snap_id_length))
        self.form_id_value.setReadOnly(True)
        self.form_id_value.setMaximumWidth(250)
        self.form_layout.addRow(self.form_id_label, self.form_id_value)

        # Campo nome
        self.form_name_label = BodyLabel("Nome:", self)
        self.form_name_input = LineEdit()
        self.form_name_input.setMaximumWidth(250)
        self.form_layout.addRow(self.form_name_label, self.form_name_input)

        # Campo descrizione
        self.form_desc_label = BodyLabel("Descrizione:", self)
        self.form_desc_input = LineEdit()
        self.form_desc_input.setMaximumWidth(250)
        self.form_layout.addRow(self.form_desc_label, self.form_desc_input)

        # Campo tags
        self.form_tags_label = BodyLabel("Tags:", self)
        self.form_tags_input = MultiSelectionComboBox(self)
        self.form_tags_input.addItems(tags)
        self.form_tags_input.setMaximumWidth(250)
        self.form_tags_input.setPlaceholderText("Aggiungi tag...")
        self.form_layout.addRow(self.form_tags_label, self.form_tags_input)

        # Campi custom
        for key in self.custom_data_keys:
            label = BodyLabel(f"{key.capitalize()}:", self)
            line_edit = LineEdit()
            line_edit.setMaximumWidth(250)
            self.form_layout.addRow(label, line_edit)
            self.custom_data_inputs[key] = line_edit

    def __populate_fields(self):
        if not self.payload_data:
            return
        self.form_id_value.setText(self.payload_data.id)
        self.form_name_input.setText(self.payload_data.name)
        self.form_desc_input.setText(self.payload_data.desc)
        self.form_tags_input.setCheckedItems(self.payload_data.tags)
        if hasattr(self.payload_data, 'data') and self.payload_data.data:
            for key, widget in self.custom_data_inputs.items():
                widget.setText(self.payload_data.data.get(key, ""))

    def _capture_initial_state(self):
        self._initial = {
            "name": self.form_name_input.text(),
            "desc": self.form_desc_input.text(),
            "tags": set(self.form_tags_input.get_items()),
            "custom_data": {
                key: widget.text() for key, widget in self.custom_data_inputs.items()
            }
        }

    def _connect_change_signals(self):
        self.form_name_input.textChanged.connect(self._on_changed)
        self.form_desc_input.textChanged.connect(self._on_changed)
        self.form_tags_input.selectionChanged.connect(lambda _: self._on_changed())
        for widget in self.custom_data_inputs.values():
            widget.textChanged.connect(self._on_changed)

    def _on_changed(self):
        current = {
            "name": self.form_name_input.text(),
            "desc": self.form_desc_input.text(),
            "tags": set(self.form_tags_input.get_items()),
            "custom_data": {
                key: widget.text() for key, widget in self.custom_data_inputs.items()
            }
        }
        changed = (current != self._initial)
        self.signal_data_changed.emit(changed)

    def get_custom_data(self) -> dict[str, str]:
        """
        Restituisce un dizionario con i dati personalizzati inseriti nel form.

        :return: Un dizionario con chiave-valore dei dati personalizzati.
        """
        return {key: widget.text() for key, widget in self.custom_data_inputs.items()}