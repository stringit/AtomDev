from PySide6.QtCore import Signal, Qt
from PySide6.QtWidgets import QVBoxLayout
from pylizlib.core.data.unit import get_normalized_gb_mb_str
from pylizlib.qtfw.widgets.card import MasterListSettingCard
from qfluentwidgets import PushSettingCard, FluentIcon, PushButton, SwitchSettingCard, OptionsSettingCard

from atomdev.application.app import app, app_settings, AppSettings
from atomdev.view.util.frame import DevlizQFrame
from atomdev.view.util.setting import SettingGroupManager


class WidgetSettings(DevlizQFrame):

    signal_open_dir_request = Signal()
    signal_close_and_clear_request = Signal()
    signal_open_about_dialog_request = Signal()
    signal_request_update = Signal()
    signal_ask_catalogue_path = Signal()
    signal_open_tags_dialog = Signal()
    signal_clear_backups_request = Signal()

    def __init__(self, parent=None):
        super().__init__(name="Settings", parent=parent)

        # Label titolo
        self.install_label_title()

        # Aggiungo i widgets
        self.__add_groups(self.get_scroll_layout())

        # Installo lo scroll nel layout principale
        self.install_scroll_on(self.master_layout)



    def __add_groups(self, layout: QVBoxLayout):
        self.__add_group_snapshot(layout)
        self.__add_group_favorites(layout)
        self.__add_group_app(layout)
        self.__add_group_info(layout)

    def __add_group_snapshot(self, layout: QVBoxLayout):

        # Percorso catalogo generale
        setting_catalogue = AppSettings.catalogue_path
        self.card_general_catalogue = PushSettingCard(
            text="Scegli directory",
            icon=FluentIcon.BOOK_SHELF,
            title="Percorso del catalogo",
            content=app_settings.get(setting_catalogue)
        )

        # Tag configurazioni
        setting_tags = AppSettings.config_tags
        self.card_fav_tags = MasterListSettingCard(
            config_item=setting_tags,
            item_type=MasterListSettingCard.Type.TEXT,
            card_title="Tag configurazioni",
            card_icon=FluentIcon.TAG,
            main_btn=PushButton("Aggiungi tag", self),
            card_content="Aggiungi uno o più tag da assegnare alle configurazioni",
            parent=self if setting_tags.enabled else None,
            dialog_title="Aggiungi tag",
            dialog_content="Inserisci il nome del tag",
            dialog_button_yes="Aggiungi",
            dialog_button_no="Annulla",
            dialog_error="Il tag non può essere vuoto o già esistente",
            deletion_title="Conferma eliminazione",
            deletion_content="Sei sicuro di voler eliminare questo tag?"
        )

        # custom data snapshots
        setting_custom_data = AppSettings.snap_custom_data
        self.card_snap_custom_data = MasterListSettingCard(
            config_item=setting_custom_data,
            item_type=MasterListSettingCard.Type.TEXT,
            card_title="Snapshots - Dati personalizzati",
            card_icon=FluentIcon.QUICK_NOTE,
            main_btn=PushButton("Aggiungi variabile", self),
            card_content="Aggiungi una o un più variabili personalizzate da assegnare agli snapshots",
            parent=self if setting_custom_data.enabled else None,
            dialog_title="Aggiungi variabile",
            dialog_content="Inserisci il nome della variabile",
            dialog_button_yes="Aggiungi",
            dialog_button_no="Annulla",
            dialog_error="La variabile non può essere vuota o già esistente",
            deletion_title="Conferma eliminazione",
            deletion_content="Sei sicuro di voler eliminare questa variabile?"
        )

        # Backup pre-installazione
        setting_backup_before_install = AppSettings.backup_before_install
        self.card_backup_before_install = SwitchSettingCard(
            icon=FluentIcon.BASKETBALL,
            title="Abilita backup pre-installazione",
            content="Esegui il backup delle cartelle locali (presenti su questo pc) contenute nella configurazione prima di installarla",
            configItem=setting_backup_before_install
        )

        # Backup pre-modifica
        setting_backup_before_edit = AppSettings.backup_before_edit
        self.card_backup_before_edit = SwitchSettingCard(
            icon=FluentIcon.BASKETBALL,
            title="Abilita backup pre-modifica",
            content="Esegui il backup delle cartelle locali (presenti su questo pc) contenute nella configurazione prima di modificarle",
            configItem=setting_backup_before_edit
        )

        # Backup pre-eliminazione
        setting_backup_before_delete = AppSettings.backup_before_delete
        self.card_backup_before_delete= SwitchSettingCard(
            icon=FluentIcon.BASKETBALL,
            title="Abilita backup pre-eliminazione",
            content="Esegui il backup delle cartelle locali (presenti su questo pc) contenute nella configurazione prima di eliminarle",
            configItem=setting_backup_before_delete
        )

        grp_manager = SettingGroupManager(self.tr("Snapshots"), self)
        grp_manager.add_widget(setting_catalogue, self.card_general_catalogue, self.signal_ask_catalogue_path)
        grp_manager.add_widget(setting_tags, self.card_fav_tags, None)
        grp_manager.add_widget(setting_custom_data, self.card_snap_custom_data, None)
        grp_manager.add_widget(setting_backup_before_install, self.card_backup_before_install,None)
        grp_manager.add_widget(setting_backup_before_edit, self.card_backup_before_edit, None)
        grp_manager.add_widget(setting_backup_before_delete, self.card_backup_before_delete, None)
        grp_manager.install_group_on(layout)


    def __add_group_favorites(self, layout: QVBoxLayout):

        # Cartelle preferite
        setting_fav_dirs = AppSettings.starred_dirs
        self.card_fav_dirs = MasterListSettingCard(
            config_item=setting_fav_dirs,
            item_type=MasterListSettingCard.Type.FOLDER,
            card_title="Cartelle preferite",
            card_icon=FluentIcon.FOLDER,
            main_btn=PushButton("Aggiungi cartella", self),
            card_content="Aggiungi una o più cartelle preferite",
            parent=self if setting_fav_dirs.enabled else None,
            dialog_title="Seleziona cartella",
        )

        # File preferite
        setting_fav_files = AppSettings.starred_files
        self.card_fav_files = MasterListSettingCard(
            config_item=setting_fav_files,
            item_type=MasterListSettingCard.Type.FILE,
            card_title="File preferiti",
            card_icon=FluentIcon.DOCUMENT,
            main_btn=PushButton("Aggiungi file", self),
            card_content="Aggiungi uno o più file preferiti",
            parent=self if setting_fav_files.enabled else None,
            dialog_title="Seleziona file",
            dialog_file_filter="All Files (*.*)"
        )

        # Eseguibili preferiti
        setting_fav_exe = AppSettings.starred_exes
        self.card_fav_exes = MasterListSettingCard(
            config_item=setting_fav_exe,
            item_type=MasterListSettingCard.Type.FILE,
            card_title="Eseguibili preferiti",
            card_icon=FluentIcon.APPLICATION,
            main_btn=PushButton("Scegli un eseguibile", self),
            card_content="Aggiungi uno o più file preferiti da monitorare nella home",
            parent=self if setting_fav_exe.enabled else None,
            dialog_title="Seleziona eseguibile",
            dialog_file_filter="Executable Files (*.exe);;All Files (*.*)"
        )

        # Servizi preferiti
        setting_fav_services = AppSettings.starred_services
        self.card_fav_services = MasterListSettingCard(
            config_item=setting_fav_services,
            item_type=MasterListSettingCard.Type.TEXT,
            card_title="Servizi preferiti",
            card_icon=FluentIcon.SETTING,
            main_btn=PushButton("Aggiungi servizio", self),
            card_content="Aggiungi uno o più servizi di Windows da monitorare nella home",
            parent=self if setting_fav_services.enabled else None,
            dialog_title="Aggiungi servizio",
            dialog_content="Inserisci il nome del servizio di Windows (es. Spooler)",
            dialog_button_yes="Aggiungi",
            dialog_button_no="Annulla",
            dialog_error="Il nome del servizio non può essere vuoto o già esistente",
            deletion_title="Conferma eliminazione",
            deletion_content="Sei sicuro di voler eliminare questo servizio?"
        )

        grp_manager = SettingGroupManager(self.tr("Preferiti"), self)
        grp_manager.add_widget(setting_fav_dirs, self.card_fav_dirs, None)
        grp_manager.add_widget(setting_fav_files, self.card_fav_files, None)
        grp_manager.add_widget(setting_fav_exe, self.card_fav_exes, None)
        grp_manager.add_widget(setting_fav_services, self.card_fav_services, None)
        grp_manager.install_group_on(layout)



    def __add_group_app(self, layout: QVBoxLayout):

        # Directory di lavoro
        self.card_working_folder = PushSettingCard(
            text="Apri Cartella",
            icon=FluentIcon.FOLDER,
            title="Cartella di lavoro di " + app.name,
            content=app.path.__str__()
        )

        # Cancella backups
        size_str = get_normalized_gb_mb_str(0)
        self.card_clear_backups = PushSettingCard(
            text="Cancella backups",
            icon=FluentIcon.DELETE,
            title="Cancella Backups di " +  app.name,
            #content="Questa operazione eliminerà tutti i file di backup creati dall'applicazione. (Attualmente: " + size_str + ")"
            content="Questa operazione eliminerà tutti i file di backup creati dall'applicazione."
        )

        # Tema applicazione
        self.card_theme = OptionsSettingCard(
            AppSettings.themeMode,
            icon=FluentIcon.BRUSH,
            title="Tema dell'applicazione",
            content="Seleziona il tema dell'applicazione",
            texts=["Chiaro", "Scuro"],
        )

        grp_manager = SettingGroupManager(self.tr("Applicazione"), self)
        grp_manager.add_widget(None, self.card_working_folder, self.signal_open_dir_request)
        grp_manager.add_widget(None, self.card_clear_backups, self.signal_clear_backups_request)
        grp_manager.add_widget(None, self.card_theme, None)
        grp_manager.install_group_on(layout)

    def __add_group_info(self, layout: QVBoxLayout):

        # Informazioni applicazione
        self.card_info_app = PushSettingCard(
            text="Informazioni",
            icon=FluentIcon.APPLICATION,
            title=f"Informazioni su {app.name}",
            content=app.version
        )

        grp_manager = SettingGroupManager(self.tr("Informazioni"), self)
        grp_manager.add_widget(None, self.card_info_app, self.signal_open_about_dialog_request)
        grp_manager.install_group_on(layout)
