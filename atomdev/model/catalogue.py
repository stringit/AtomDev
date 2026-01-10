from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt
from pylizlib.core.os.snap import Snapshot, SnapshotSortKey, SnapshotUtils

from atomdev.application.app import app_settings, AppSettings
from atomdev.domain.data import DevlizSnapshotData


class SnapshotTableModel(QAbstractTableModel):
    """
    A table model for displaying Snapshot data in a QTableView.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self._snapshots: list[Snapshot] = []
        self._headers = []
        self.update_headers()

    def update_headers(self):
        """Updates the headers based on application settings."""
        headers = ["Nome", "Descrizione"]
        snap_custom_data = app_settings.get(AppSettings.snap_custom_data)
        for i in snap_custom_data:
            headers.append(i)
        headers.append("Data/Ora")
        headers.append("Tags")
        self._headers = headers
        self.headerDataChanged.emit(Qt.Orientation.Horizontal, 0, len(self._headers) - 1)

    def rowCount(self, parent=QModelIndex()):
        if parent.isValid():
            return 0
        return len(self._snapshots)

    def columnCount(self, parent=QModelIndex()):
        if parent.isValid():
            return 0
        return len(self._headers)

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid() or role != Qt.ItemDataRole.DisplayRole:
            return None

        try:
            snapshot = self._snapshots[index.row()]
            snap_custom_data_keys = app_settings.get(AppSettings.snap_custom_data)
            table_data = snapshot.get_for_table_array(snap_custom_data_keys)
            return str(table_data[index.column()])
        except (IndexError, KeyError):
            return None

    def headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole):
        if role == Qt.ItemDataRole.DisplayRole and orientation == Qt.Orientation.Horizontal:
            try:
                return self._headers[section]
            except IndexError:
                return None
        return None

    def set_snapshots(self, snapshots: list[Snapshot]):
        """Resets the model with a new list of snapshots."""
        self.beginResetModel()
        self._snapshots = snapshots if snapshots is not None else []
        self.endResetModel()

    def get_snapshot(self, row: int) -> Snapshot | None:
        """Returns the snapshot at a given row, or None if the row is invalid."""
        try:
            return self._snapshots[row]
        except IndexError:
            return None


class CatalogueModel:
    """
    Manages the data and business logic for the snapshot catalogue.
    """

    def __init__(self):
        self._all_snapshots: list[Snapshot] = []
        self._filtered_snapshots: list[Snapshot] = []
        self._is_filtered = False
        self.table_model = SnapshotTableModel()

    def set_snapshots(self, snapshots: list[Snapshot]):
        """Sets the master list of snapshots and updates the table view."""
        self._all_snapshots = snapshots if snapshots is not None else []
        self.filter("")  # Apply current filter or show all

    def get_snapshot_at(self, row: int) -> Snapshot | None:
        """Gets the snapshot at a specific row of the current view (filtered or not)."""
        return self.table_model.get_snapshot(row)

    def sort(self, sort_key: SnapshotSortKey):
        """Sorts the master list of snapshots and updates the view."""
        self._all_snapshots = SnapshotUtils.sort_snapshots(self._all_snapshots, sort_key)
        # After sorting, the view should reflect the sorted, unfiltered data
        self._is_filtered = False
        self._filtered_snapshots = []
        self.table_model.set_snapshots(self._all_snapshots)

    def filter(self, text: str):
        """Filters snapshots based on a text query and updates the view."""
        text = text.lower().strip()
        if not text:
            self._is_filtered = False
            self.table_model.set_snapshots(self._all_snapshots)
        else:
            self._is_filtered = True
            self._filtered_snapshots = [
                config for config in self._all_snapshots
                if (text in config.name.lower() or
                    text in config.desc.lower() or
                    any(text in tag.lower() for tag in config.tags) or
                    (config.data and any(text in str(value).lower() for value in config.data.values())))
            ]
            self.table_model.set_snapshots(self._filtered_snapshots)

    def count(self) -> int:
        """Returns the count of snapshots in the current view (filtered or not)."""
        return len(self._all_snapshots)

    def get_mb_size(self) -> str:
        """Returns the total size of all snapshots in MB."""
        return DevlizSnapshotData(snapshot_list=self._all_snapshots).get_mb_size
