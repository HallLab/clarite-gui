from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDockWidget, QTabWidget

from widgets.commands import LoadButtons, ModifyButtons, DescribeButtons, PlotButtons, AnalyzeButtons


class CommandDockWidget(QDockWidget):
    """
    Widget that displays the command buttons
    """
    def __init__(self, *args, **kwargs):
        super(CommandDockWidget, self).__init__(*args, **kwargs)
        self.appctx = self.parent().appctx  # Get App Context
        self.appctx.command_dock_widget = self  # Add reference to this widget to the app context
        self.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        self.setWindowTitle("Commands")
        self.setup_ui()

    def setup_ui(self):
        tabs = QTabWidget(self)  
        tabs.setTabPosition(QTabWidget.West)
        tabs.addTab(LoadButtons(self), "Load")
        tabs.addTab(ModifyButtons(self), "Modify")
        tabs.addTab(DescribeButtons(self), "Describe")
        tabs.addTab(PlotButtons(self), "Plot")
        tabs.addTab(AnalyzeButtons(self), "Analyze")
        self.setWidget(tabs)
