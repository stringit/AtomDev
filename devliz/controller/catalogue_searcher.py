import os

from qfluentwidgets import MessageBox

from pylizlib.core.os.snap import SnapshotCatalogue, Snapshot

from devliz.model.catalogue_searcher import CatalogueSearcherModel
from devliz.view.catalogue_searcher import CatalogueSearcherView


class CatalogueSearcherController:
    """
    Controller for the catalogue searcher component.

    This class connects the CatalogueSearcherView (the UI) with the
    CatalogueSearcherModel (the business logic and data). It handles user
    interactions from the view and invokes the corresponding actions in the model.
    """

    def __init__(self, catalogue: SnapshotCatalogue, parent=None):
        """
        Initializes the CatalogueSearcherController.

        Args:
            catalogue (SnapshotCatalogue): The catalogue data source.
            parent (QWidget, optional): The parent widget. Defaults to None.
        """
        self.view = CatalogueSearcherView(parent)
        self.model = CatalogueSearcherModel(catalogue)

        # Connect view and model
        self.view.setModel(self.model.table_model)
        self.view.tree_view.setModel(self.model.tree_model_manager.model)

        # Connect signals
        self.model.signal_search_finished.connect(self._on_search_finished)
        self.view.action_start.triggered.connect(self._perform_search)
        self.view.action_stop.triggered.connect(self._stop_search)
        self.view.signal_delete_requested.connect(self._on_delete_requested)
        self.view.signal_file_double_clicked.connect(self._on_file_double_clicked)

        # Connect the status card update signal directly to the view's slot
        self.model.signal_status_card_update.connect(self.view.update_status_card)

    def _on_delete_requested(self, row: int):
        """
        Handles the request to delete a snapshot from the search table.

        Args:
            row (int): The row index of the snapshot to remove.
        """
        self.model.table_model.remove_snapshot(row)

    def _on_file_double_clicked(self, file_path: str):
        """
        Handles the double-click event on a file in the results tree.
        Attempts to open the file with the default system application.

        Args:
            file_path (str): The path to the file to open.
        """
        if os.path.isfile(file_path):
            try:
                os.startfile(file_path)
            except Exception as e:
                print(f"Error opening file {file_path}: {e}")
        elif os.path.isdir(file_path):
            print(f"Cannot open directory: {file_path}")

    def _perform_search(self):
        """
        Gathers search parameters from the view and triggers a search in the model.
        """
        search_text = self.view.search_bar.text()
        if not search_text.strip():
            m = MessageBox(
                "Testo mancante",
                "Per favore, inserisci un testo prima di avviare la ricerca.",
                self.view
            )
            m.exec()
            return

        self.view.set_operation_status(True)
        query_type = self.view.get_selected_query_type()
        search_target = self.view.get_selected_search_target()
        extensions = self.view.get_selected_extensions()

        # Toggle button states
        self.view.action_start.setEnabled(False)
        self.view.action_stop.setEnabled(True)

        self.model.search(search_text, query_type, search_target, extensions)

    def _stop_search(self):
        """Stops the search operation in the model and updates the UI state."""
        self.view.set_operation_status(False)
        self.model.stop_search()

        # Toggle button states
        self.view.action_start.setEnabled(True)
        self.view.action_stop.setEnabled(False)

    def _on_search_finished(self):
        """Handles the completion of the search operation by updating the UI state."""
        self.view.set_operation_status(False)
        self.view.action_start.setEnabled(True)
        self.view.action_stop.setEnabled(False)

    def open(self, snapshot: Snapshot | None = None):
        """
        Opens the search dialog window.

        Loads the specified snapshot(s) into the model and shows the dialog.

        Args:
            snapshot (Snapshot | None, optional): A specific snapshot to load,
                                                  or None to load all. Defaults to None.
        """
        self.model.load_snapshots_from_catalogue(snapshot)
        self.view.exec_()