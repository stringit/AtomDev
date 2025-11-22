from time import sleep

from PySide6.QtCore import QAbstractTableModel, Qt, QModelIndex, Signal, QObject
from PySide6.QtGui import QStandardItemModel, QStandardItem

from pylizlib.core.os.snap import SnapshotCatalogue, Snapshot, SnapshotSearchParams, QueryType, SearchTarget, SnapshotSearcher, \
    SnapshotSearchResult
from pylizlib.qt.handler.operation_core import Operation, Task
from pylizlib.qt.handler.operation_domain import OperationInfo, OperationStatus
from pylizlib.qt.handler.operation_runner import OperationRunner, RunnerStatistics


class SearchResultsTableModel(QAbstractTableModel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._headers = ["Nome snapshot", "Stato", "Valori trovati", "Progresso", "ETA"]
        self._data: list[Snapshot] = []
        self._progress_data = {}
        self._status_data = {}
        self._results_count_data = {}

    def rowCount(self, parent=QModelIndex()):
        return len(self._data)

    def columnCount(self, parent=QModelIndex()):
        return len(self._headers)

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid() or role != Qt.ItemDataRole.DisplayRole:
            return None

        snapshot = self._data[index.row()]
        col = index.column()

        if col == 0:
            return snapshot.name
        elif col == 1:
            return self._status_data.get(snapshot.id, "Pending")
        elif col == 2:
            return self._results_count_data.get(snapshot.id, "")
        elif col == 3:
            progress = self._progress_data.get(snapshot.id, 0)
            return f"{progress}%"
        elif col == 4:
            return "--"  # ETA
        return None

    def headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole):
        if role == Qt.ItemDataRole.DisplayRole and orientation == Qt.Orientation.Horizontal:
            return self._headers[section]
        return None

    def update_data(self, new_data: list[Snapshot]):
        """Updates the model's data and notifies the view."""
        self.beginResetModel()
        self._data = new_data
        self._progress_data.clear()
        self._status_data.clear()
        self.endResetModel()

    def remove_snapshot(self, row: int):
        if 0 <= row < self.rowCount():
            self.beginRemoveRows(QModelIndex(), row, row)
            del self._data[row]
            self.endRemoveRows()

    def reset_search_state(self):
        """Resets the progress and status data for all rows."""
        if not self._data:
            return
        self._progress_data.clear()
        self._status_data.clear()
        self._results_count_data.clear()
        # Emit dataChanged for all rows and the relevant columns (status, progress, results)
        top_left = self.index(0, 1)
        bottom_right = self.index(self.rowCount() - 1, 3)
        self.dataChanged.emit(top_left, bottom_right, [Qt.ItemDataRole.DisplayRole])

    def get_data(self):
        return self._data

    def update_progress_for_snapshot(self, snap_id: str, progress: int):
        """Finds a snapshot by its ID and updates its progress."""
        self._progress_data[snap_id] = progress
        for i, snapshot in enumerate(self._data):
            if snapshot.id == snap_id:
                index = self.index(i, 3)
                self.dataChanged.emit(index, index, [Qt.ItemDataRole.DisplayRole])
                return

    def update_status_for_snapshot(self, snap_id: str, status: str):
        """Finds a snapshot by its ID and updates its status."""
        self._status_data[snap_id] = status
        for i, snapshot in enumerate(self._data):
            if snapshot.id == snap_id:
                index = self.index(i, 1)
                self.dataChanged.emit(index, index, [Qt.ItemDataRole.DisplayRole])
                return

    def update_results_for_snapshot(self, snap_id: str, count: str):
        """Finds a snapshot by its ID and updates its results count."""
        self._results_count_data[snap_id] = count
        for i, snapshot in enumerate(self._data):
            if snapshot.id == snap_id:
                index = self.index(i, 2)
                self.dataChanged.emit(index, index, [Qt.ItemDataRole.DisplayRole])
                return


class SnapSearchTask(Task):

    def __init__(self, params: SnapshotSearchParams, snapshot: Snapshot, catalogue: SnapshotCatalogue):
        super().__init__(f"Search in {snapshot.name}")
        self.params = params
        self.snapshot = snapshot
        self.searcher = SnapshotSearcher(catalogue)

    def execute(self):
        def on_progress(file_name: str, total_files: int, current_file: int):
            self.task_update_message.emit(self.name, f"Scansione: {file_name}")
            if total_files > 0:
                self.gen_update_task_progress(current_file, total_files)

        results = self.searcher.search(self.snapshot, self.params, on_progress=on_progress)
        return results


class SearchResultsTreeModel:
    def __init__(self):
        self.model = QStandardItemModel()
        self.model.setHorizontalHeaderLabels(['Risultati'])

    def clear(self):
        self.model.clear()
        self.model.setHorizontalHeaderLabels(['Risultati'])

    def populate_from_results(self, results: list[SnapshotSearchResult]):
        self.clear()
        self.model.setHorizontalHeaderLabels([f"Risultati ({len(results)})"])

        results_by_snapshot = {}
        for res in results:
            if res.snapshot_name not in results_by_snapshot:
                results_by_snapshot[res.snapshot_name] = []
            results_by_snapshot[res.snapshot_name].append(res)

        for snapshot_name, snapshot_results in results_by_snapshot.items():
            snapshot_item = QStandardItem(f"{snapshot_name} ({len(snapshot_results)})")
            snapshot_item.setEditable(False)

            files_in_snapshot = {}
            for res in snapshot_results:
                file_path_str = str(res.file_path)
                if file_path_str not in files_in_snapshot:
                    files_in_snapshot[file_path_str] = []
                files_in_snapshot[file_path_str].append(res)

            for file_path_str, file_results in files_in_snapshot.items():
                file_item = QStandardItem(file_path_str)
                file_item.setEditable(False)
                snapshot_item.appendRow(file_item)

            self.model.appendRow(snapshot_item)


class CatalogueSearcherModel(QObject):
    signal_search_started = Signal()
    signal_search_stopped = Signal()
    signal_search_finished = Signal()
    signal_status_card_update = Signal(str, int, str)

    def __init__(self, catalogue: SnapshotCatalogue):
        super().__init__()
        self.catalogue = catalogue
        self.table_model = SearchResultsTableModel()
        self.tree_model_manager = SearchResultsTreeModel()
        self.runner = OperationRunner()

        self._current_message = "In attesa..."
        self._current_progress = 0
        self._current_eta = "--:--"

        self.runner.runner_start.connect(self.signal_search_started)
        self.runner.runner_stop.connect(self.signal_search_stopped)
        self.runner.runner_finish.connect(self.on_runner_finished)
        self.runner.op_finished.connect(self.on_operation_finished)
        self.runner.op_update_status.connect(self.on_operation_status_changed)
        self.runner.op_update_progress.connect(self.on_operation_progress_changed)
        self.runner.task_start.connect(self.on_task_start)
        self.runner.task_update_message.connect(self.on_task_update_message)
        self.runner.runner_update_progress.connect(self.on_runner_progress)
        self.runner.op_eta_update.connect(self.on_eta_update)

        self._op_id_to_snap_id = {}

    def __get_runner_operations(self, params: SnapshotSearchParams) -> list[Operation]:
        ops = []
        self._op_id_to_snap_id.clear()
        for snap in self.table_model.get_data():
            current_task = SnapSearchTask(params=params, snapshot=snap, catalogue=self.catalogue)
            op = Operation([current_task], OperationInfo(delay_each_task=0.0, name=f"Search in {snap.name})",
                                                 description="Searching snapshot contents"))
            self._op_id_to_snap_id[op.id] = snap.id
            ops.append(op)
        return ops

    def load_snapshots_from_catalogue(self, snapshot: Snapshot | None = None):
        """
        Loads snapshot names from the catalogue and populates the table model.
        If a snapshot is provided, only that snapshot is loaded. Otherwise, all snapshots are loaded.
        """
        if snapshot:
            snapshots = [snapshot]
        else:
            snapshots = self.catalogue.get_all()
        self.table_model.update_data(snapshots)

    def search(self, text: str, query_type: QueryType, search_target: SearchTarget, extensions: list[str]):
        self.table_model.reset_search_state()
        self.tree_model_manager.clear()
        self._current_message = "Avvio..."
        self._current_progress = 0
        self._current_eta = "--:--"
        self.signal_status_card_update.emit(self._current_message, self._current_progress, self._current_eta)

        params = SnapshotSearchParams(
            query=text,
            query_type=query_type,
            search_target=search_target,
            extensions=extensions
        )
        operations = self.__get_runner_operations(params)
        self.runner.clear()
        self.runner.adds(operations)
        self.runner.start()

    def stop_search(self):
        """Stops the ongoing search."""
        self.runner.stop()

    def on_operation_status_changed(self, op_id: str, status: OperationStatus):
        if op_id in self._op_id_to_snap_id:
            snap_id = self._op_id_to_snap_id[op_id]
            self.table_model.update_status_for_snapshot(snap_id, status.value)

    def on_operation_progress_changed(self, op_id: str, progress: int):
        if op_id in self._op_id_to_snap_id:
            snap_id = self._op_id_to_snap_id[op_id]
            self.table_model.update_progress_for_snapshot(snap_id, progress)

    def on_task_start(self, task_name: str):
        self._current_message = "Ricerca in corso..."
        self._current_eta = "--:--"
        self.signal_status_card_update.emit(self._current_message, self._current_progress, self._current_eta)

    def on_task_update_message(self, task_name: str, message: str):
        self._current_message = message
        self.signal_status_card_update.emit(self._current_message, self._current_progress, self._current_eta)

    def on_runner_progress(self, progress: int):
        self._current_progress = progress
        self.signal_status_card_update.emit(self._current_message, self._current_progress, self._current_eta)

    def on_eta_update(self, op_id: str, eta: str):
        self._current_eta = eta
        self.signal_status_card_update.emit(self._current_message, self._current_progress, self._current_eta)

    def on_runner_finished(self, statistics: RunnerStatistics):
        self.signal_search_finished.emit()
        all_results = []
        for op in self.runner._all_operations:
            task_results = op.get_task_results()
            if task_results and task_results[0]:
                all_results.extend(task_results[0])

        self.tree_model_manager.populate_from_results(all_results)

    def on_operation_finished(self, op: Operation):
        if op.id not in self._op_id_to_snap_id:
            return

        snap_id = self._op_id_to_snap_id[op.id]
        count_str = ""
        if op.is_completed():
            task_results = op.get_task_results()
            if task_results and isinstance(task_results[0], list):
                count = len(task_results[0])
                count_str = str(count)
            else:
                count_str = "0"
        elif op.is_failed():
            count_str = "?"

        self.table_model.update_results_for_snapshot(snap_id, count_str)