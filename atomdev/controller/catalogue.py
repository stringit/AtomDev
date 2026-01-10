import os
from pathlib import Path

from PySide6.QtWidgets import QFileDialog
from loguru import logger
from pylizlib.core.os.snap import Snapshot
from pylizlib.qtfw.util.ui import UiUtils
from qfluentwidgets import MessageBox
from scipy.optimize import direct

from atomdev.application.app import app
from atomdev.controller.catalogue_searcher import CatalogueSearcherController
from atomdev.domain.data import DevlizSnapshotData
from atomdev.model.catalogue import CatalogueModel
from atomdev.model.dashboard import DashboardModel
from atomdev.view.catalogue import SnapshotCatalogueWidget
from atomdev.view.catalogue_imp_dialog import DialogConfig


class CatalogueController:

    def __init__(self,dash_model: DashboardModel):
        self.dash_model = dash_model
        self.model = CatalogueModel()
        self.view = SnapshotCatalogueWidget(self.model)


    def init(self):
        self.view.signal_import_requested.connect(lambda: self.__open_config_dialog(False, None))
        self.view.signal_install_requested.connect(self.__install_snapshot)
        self.view.signal_edit_requested.connect(self.__edit_snapshot)
        self.view.signal_delete_requested.connect(self.__delete_snapshot)
        self.view.signal_open_folder_requested.connect(self.__open_snap_directory)
        self.view.signal_duplicate_requested.connect(self.__duplicate_snapshot)
        self.view.signal_sort_requested.connect(self.view.sort)
        self.view.signal_search_internal_content_all.connect(self.__open_snapshot_searcher)
        self.view.signal_search_internal_content_single.connect(self.__open_snapshot_searcher_single)
        self.view.signal_export_request_snapshot.connect(self.__export_snapshot)
        self.view.signal_export_request_assoc_folders.connect(self.__export_snapshot_folders)
        self.view.signal_delete_installed_folders_requested.connect(self.__delete_snap_installed_dirs)
        self.view.signal_update_with_local_dirs_requested.connect(self.__update_assoc_dirs_from_installed)
        self.view.signal_open_assoc_folder_requested.connect(self.__open_directory)

    def update_data(self, snapshot_data: DevlizSnapshotData):
        self.model.set_snapshots(snapshot_data.snapshot_list)
        self.model.table_model.update_headers()
        self.view.reload_data()

    def __open_config_dialog(self, edit_mode: bool, snap: Snapshot | None = None):
        dialog = DialogConfig(self.dash_model.cached_data, edit_mode, snap)
        try:
            if dialog.exec():
                print(dialog.output_data)
                if edit_mode:
                    old = snap
                    new = dialog.output_data
                    self.dash_model.snap_catalogue.update_snapshot_by_objs(old, new)
                else:
                    self.dash_model.snap_catalogue.add(dialog.output_data)
                titolo = "Configurazione creata" if not edit_mode else "Configurazione modificata"
                testo = "La configurazione è stata creata con successo." if not edit_mode else "La configurazione è stata modificata con successo."
                UiUtils.show_message(titolo, testo)
                self.dash_model.update()
        except Exception as e:
            logger.error(str(e))
            UiUtils.show_message("Attenzione", "Si è verificato un errore: " + str(e))

    def __open_snapshot_searcher(self):
        controller = CatalogueSearcherController(self.dash_model.snap_catalogue, self.view)
        controller.open()

    def __open_snapshot_searcher_single(self, snapshot: Snapshot):
        controller = CatalogueSearcherController(self.dash_model.snap_catalogue, self.view)
        controller.open(snapshot=snapshot)

    def __install_snapshot(self, snap: Snapshot):
        try:
            w = MessageBox("Installa configurazione", "Sei sicuro di voler installare lo snapshot selezionato ? Tutte le directory presenti attualmente verranno rimpiazzate con quelle contenute nello snapshot.", parent=self.view)
            if w.exec_():
                self.dash_model.snap_catalogue.install(snap)
                self.dash_model.update()
        except Exception as e:
            UiUtils.show_message("Errore di installazione", "Si è verificato un errore durante l'installazione: " + str(e))

    def __edit_snapshot(self, snap: Snapshot):
        try:
            self.__open_config_dialog(True, snap)
        except Exception as e:
            UiUtils.show_message("Errore di modifica", "Si è verificato un errore durante la modifica: " + str(e))

    def __delete_snapshot(self, snap: Snapshot):
        try:
            w = MessageBox("Elimina configurazione", "Sei sicuro di voler eliminare lo snapshot selezionato ?\n\n Verranno eliminati tutti i file associati in ", parent=self.view)
            if w.exec_():
                self.dash_model.snap_catalogue.delete(snap)
                self.dash_model.update()
        except Exception as e:
            UiUtils.show_message("Errore di eliminazione", "Si è verificato un errore durante l'eliminazione: " + str(e))

    def __open_snap_directory(self, snap: Snapshot):
        path = self.dash_model.snap_catalogue.get_snap_directory_path(snap)
        self.__open_directory(path)

    def __duplicate_snapshot(self, snap: Snapshot):
        try:
            w = MessageBox("Duplica configurazione", "Sei sicuro di voler duplicare la configurazione selezionata ?", parent=self.view)
            if w.exec_():
                self.dash_model.snap_catalogue.duplicate_by_id(snap.id)
                self.dash_model.update()
        except Exception as e:
            UiUtils.show_message("Errore di duplicazione", "Si è verificato un errore durante la duplicazione: " + str(e))

    def __export_snapshot(self, snap: Snapshot):
        try:
            w = MessageBox("Esporta snapshot", "Sei sicuro di voler esportare lo snapshot selezionato ?", parent=self.view)
            if w.exec_():
                directory = QFileDialog.getExistingDirectory(
                    None,
                    "Seleziona la cartella di salvataggio dello snapshot",
                    app.path.__str__()
                )
                if directory:
                    self.dash_model.snap_catalogue.export_snapshot(snap.id, Path(directory))
        except Exception as e:
            UiUtils.show_message("Errore di duplicazione", "Si è verificato un errore durante la duplicazione: " + str(e))

    def __export_snapshot_folders(self, snap: Snapshot):
        try:
            w = MessageBox("Esporta cartelle associate", "Sei sicuro di voler esportare le cartelle associate allo snapshot selezionato ?", parent=self.view)
            if w.exec_():
                directory = QFileDialog.getExistingDirectory(
                    None,
                    "Seleziona la cartella di salvataggio delle cartelle associate",
                    app.path.__str__()
                )
                if directory:
                    self.dash_model.snap_catalogue.export_assoc_dirs(snap.id, Path(directory))
        except Exception as e:
            UiUtils.show_message("Errore di esportazione", "Si è verificato un errore durante l'esportazione: " + str(e))

    def __delete_snap_installed_dirs(self, snap: Snapshot):
        try:
            w = MessageBox("Elimina cartelle installate", "Sei sicuro di voler eliminare le cartelle installate attualmente nel sistema relative allo snapshot selezionato ?", parent=self.view)
            if w.exec_():
                self.dash_model.snap_catalogue.remove_installed_copies(snap.id)
        except Exception as e:
            UiUtils.show_message("Errore di eliminazione", "Si è verificato un errore durante l'eliminazione: " + str(e))

    def __update_assoc_dirs_from_installed(self, snap: Snapshot):
        try:
            w = MessageBox("Aggiorna cartelle associate", "Sei sicuro di voler aggiornare le cartelle associate allo snapshot selezionato con quelle attualmente installate nel sistema ?", parent=self.view)
            if w.exec_():
                self.dash_model.snap_catalogue.update_assoc_with_installed(snap.id)
        except Exception as e:
            UiUtils.show_message("Errore di aggiornamento", "Si è verificato un errore durante l'aggiornamento: " + str(e))

    def __open_directory(self, path: Path):
        if path.exists():
            os.startfile(path)
        else:
            UiUtils.show_message("Attenzione", "La cartella non esiste più in " + path.__str__())
