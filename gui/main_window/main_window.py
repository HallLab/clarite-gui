from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMainWindow, QSplitter, QAction, QTabWidget

from .main_window_widgets import (
    CommandDockWidget,
    DatasetWidget,
    LogWidget,
    PreferencesDialog,
    AboutDialog,
    LicenseDialog,
)


class MainWindow(QMainWindow):
    def __init__(self, appctx, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.appctx = appctx
        self.setup_center_ui()
        self.setup_log_ui()
        self.setup_command_dock_ui()
        self.setup_menu()

    def setup_center_ui(self):
        """
        Set up the central widget area, which includes:
            DatasetWidget
            LogWidget
        """
        self.setWindowTitle(f"CLARITE v{self.appctx.VERSION}")
        self.setWindowIcon(QIcon(":/images/clarite_logo.png"))

        self.setContentsMargins(10, 10, 10, 10)

        # Set up the central widget
        splitter = QSplitter(self)
        splitter.setOrientation(Qt.Vertical)
        splitter.setMinimumSize(800, 600)
        self.setCentralWidget(splitter)

        # Add the main sections
        dataset_widget = DatasetWidget(parent=self)
        splitter.addWidget(dataset_widget)

        self.log_tabs = QTabWidget(parent=self)
        self.log_tabs.setTabPosition(QTabWidget.North)
        splitter.addWidget(self.log_tabs)

        # Set the initial sizes (and relative ratio) of the two groups
        splitter.setSizes([500, 100])

    def setup_log_ui(self):
        """Add log tabs each with individual widgets"""
        # Normal Log
        info_log_widget = LogWidget(parent=self)
        self.appctx.signals.log_info.connect(info_log_widget.append)
        self.log_tabs.addTab(info_log_widget, "Info Log")
        # Python Log
        python_log_widget = LogWidget(
            parent=self,
            filetype="Python Files (*.py)",
            initial_log=["import clarite\n\n"],
        )
        python_log_widget.btn_clear.setHidden(
            True
        )  # Don't allow the python log to be cleared- too tricky
        self.appctx.signals.log_python.connect(python_log_widget.append)
        self.log_tabs.addTab(python_log_widget, "Python Log")

    def setup_command_dock_ui(self):
        """
        Set up the dock widgets, which includes:
            CommandDockWidget
        """
        # Initialize command dock and place on the left
        self.command_dock_widget = CommandDockWidget(parent=self)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.command_dock_widget)

    def setup_menu(self):
        """Set up the file menu"""
        # Add menubar and get a reference to it
        menubar = self.menuBar()
        # Add menus
        file_menu = menubar.addMenu("File")
        edit_menu = menubar.addMenu("Edit")
        view_menu = menubar.addMenu("View")
        help_menu = menubar.addMenu("Help")

        # Add to File menu
        exit_action = QAction("Exit", parent=self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.setStatusTip("Exit application")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Add to Edit menu
        preferences_action = QAction("Preferences", parent=self)
        preferences_action.setStatusTip("Edit preferences")
        preferences_action.triggered.connect(
            lambda: PreferencesDialog(parent=self.appctx.main_window).show()
        )
        edit_menu.addAction(preferences_action)

        # Add to View menu
        view_commands_menu = view_menu.addMenu("Commands")
        # Show/Hide
        show_commands_action = self.command_dock_widget.toggleViewAction()
        show_commands_action.setStatusTip("Show/Hide the command dock")
        show_commands_action.setText("Show")
        view_commands_menu.addAction(show_commands_action)
        # Dock/Undock (These are reversed booleans since True = floating and it is displaying docked status instead)
        dock_commands_action = QAction("Dock", parent=self)
        dock_commands_action.setStatusTip("Dock/Undock the command dock")
        dock_commands_action.setCheckable(True)
        dock_commands_action.setChecked(not self.command_dock_widget.isFloating())
        dock_commands_action.triggered.connect(
            lambda make_floating: self.command_dock_widget.setFloating(
                not make_floating
            )
        )
        self.command_dock_widget.topLevelChanged.connect(
            lambda is_floating: dock_commands_action.setChecked(not is_floating)
        )
        view_commands_menu.addAction(dock_commands_action)

        showLogsButton = QAction("Logs", parent=self)
        showLogsButton.setStatusTip("Show the logs")
        showLogsButton.setCheckable(True)
        showLogsButton.setChecked(not self.log_tabs.isHidden())
        showLogsButton.triggered.connect(self.log_tabs.setVisible)
        view_menu.addAction(showLogsButton)

        # Add to Help menu
        showAboutButton = QAction("About", parent=self)
        showAboutButton.setStatusTip("Show information about CLARITE")
        showAboutButton.triggered.connect(
            lambda: AboutDialog(parent=self.appctx.main_window).show()
        )
        help_menu.addAction(showAboutButton)
        showLicenseButton = QAction("License Info", parent=self)
        showLicenseButton.setStatusTip("Show the license (GPLv3) for the CLARITE GUI")
        showLicenseButton.triggered.connect(
            lambda: LicenseDialog(parent=self.appctx.main_window).show()
        )
        help_menu.addAction(showLicenseButton)
