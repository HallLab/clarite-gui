import sys
from typing import List, Optional

import pandas as pd
from PyQt5.QtCore import pyqtSignal, QObject
from PyQt5.QtWidgets import QApplication

from .main_window import MainWindow
from .models import Dataset


class AppContext:
    """
    The application context holds the current data and is passed to all widgets in the app.
    The data in the application context should only be modified via its methods.
    Each method that modifies data emits a signal with the same name to update the UI.
    """

    VERSION = "1.0.0"
    ORG = "Hall Lab"
    APPLICATION = "Clarite"

    def __init__(self, *args, **kwargs):
        # Main display widgets that expose functions to update themselves (set to None initially)
        self.dataset_widget = None
        self.command_dock_widget = None

        # Data stored in the app context
        self.dataset_count = 0  # incremented each time a dataset is added
        self.datasets: List[Dataset] = []
        self.current_dataset_idx: Optional[int] = None

        self.signals = AppctxSignals()
        self.app = QApplication(sys.argv)
        self.main_window = MainWindow(self)

        self.app.setApplicationName("CLARITE")

    def run(self):
        """
        Run the application
        """
        self.main_window.show()

        # Testing code:
        # test_df = pd.DataFrame({'a': [1, 2, 3], 'b': [4, 5, 6], 'c': [7, 8, 9]}).set_index('c')
        # self.add_dataset(Dataset("test", "dataset", test_df))
        # repl_result = pd.read_csv("C:/Users/jrm5100/Documents/Projects/clarite-bmi-replication/results_Python/results/BMI_Replication_Results.txt", sep="\t").set_index(['variable', 'phenotype'])
        # self.add_dataset(Dataset("replication_results", "ewas_result", repl_result))

        return self.app.exec_()

    # Slots that update data in the app context

    def add_dataset(self, dataset):
        """Add a dataset"""
        # Update appctx data
        self.dataset_count += 1
        self.datasets.append(dataset)
        dataset.set_number(self.dataset_count)
        # Signal that a dataset was added
        self.signals.added_dataset.emit()
        # Change to the new dataset
        self.change_dataset(len(self.datasets) - 1)

    def remove_current_dataset(self):
        """Remove a dataset"""
        # Which dataset is getting deleted
        del_idx = self.current_dataset_idx
        dataset_name = self.datasets[self.current_dataset_idx].get_selector_name()
        python_name = self.datasets[self.current_dataset_idx].get_python_name()

        # Determine which dataset to switch to.  Usually the following one, meaning the index doesn't change
        if len(self.datasets) == 1:
            # No more datasets left
            self.current_dataset_idx = 0
        elif self.current_dataset_idx == len(self.datasets):
            # Last dataset currently selected, must decrement the index
            self.current_dataset_idx -= 1

        # Delete the dataset
        del self.datasets[del_idx]  # Actually delete the data
        self.signals.removed_dataset.emit(
            del_idx
        )  # Signal the UI to update the combo list

        # Log
        self.log_info("\n" + "=" * 80 + f"\nDeleted '{dataset_name}'\n" + "=" * 80)
        self.log_python(f"del {python_name}")

        # Update which dataset is selected
        self.signals.changed_dataset.emit(self.current_dataset_idx)

    def change_dataset(self, idx):
        """Change the currently selected dataset"""
        self.current_dataset_idx = idx
        self.signals.changed_dataset.emit(idx)

    def update_data(self, df: pd.DataFrame):
        """Replace the df in the current dataset with the provided one"""
        self.datasets[self.current_dataset_idx].df = df
        # Emit signal of a changed dataset (even though the index doesn't actually change) to refresh the display
        self.signals.changed_dataset.emit(self.current_dataset_idx)

    def log_info(self, message):
        """Add the message to the info log"""
        # No need to add newline, since this is done automatically
        self.signals.log_info.emit(message)

    def log_python(self, message):
        """Add the python code to the python log"""
        # Add a newline separator
        message += "\n"
        self.signals.log_python.emit(message)


class AppctxSignals(QObject):
    added_dataset = pyqtSignal()
    removed_dataset = pyqtSignal(int)
    changed_dataset = pyqtSignal(int)  # Idx of dataset that was changed to
    log_info = pyqtSignal(str)
    log_python = pyqtSignal(str)
