import json
from pathlib import Path

from PyQt5.QtCore import pyqtSlot, Qt, QSettings, QSize
from PyQt5.QtGui import QFont, QColor, QImage, QPixmap
from PyQt5.QtWidgets import QGroupBox, QHBoxLayout, QVBoxLayout, QComboBox, QLabel, QPushButton, QFileDialog

from main_window.main_window_widgets.dataset_table_view import DatasetTableView
from models import PandasDFModel
from widgets.utilities import RunProgress, confirm_click


class DatasetWidget(QGroupBox):
    """
    Widget allowing for selection and display of a dataset
    """

    def __init__(self, *args, **kwargs):
        super(DatasetWidget, self).__init__(*args, **kwargs)
        self.appctx = self.parent().appctx  # Get App Context
        self.appctx.dataset_widget = self  # Add reference to this widget to the app context
        self.setTitle("Current Dataset")
        self.setup_ui()
        self.connect_ui_signals()
        self.connect_appctx_signals()

    def read_color_settings(self):
        settings = QSettings(self.appctx.ORG, self.appctx.APPLICATION)
        settings.beginGroup("display/data")
        data_colors = dict()
        data_colors["Unknown"] = QColor(settings.value("bgcolor_unknown",
                                                            defaultValue=QColor.fromRgb(255, 255, 255)))
        data_colors["Binary"] = QColor(settings.value("bgcolor_binary",
                                                           defaultValue=QColor.fromRgb(255, 204, 153)))
        data_colors["Categorical"] = QColor(settings.value("bgcolor_categorical",
                                                                defaultValue=QColor.fromRgb(153, 204, 255)))
        data_colors["Continuous"] = QColor(settings.value("bgcolor_continuous",
                                                               defaultValue=QColor.fromRgb(204, 153, 255)))
        settings.endGroup()

        return data_colors

    def setup_ui(self):
        # Layout
        layout = QVBoxLayout(self)

        # Combobox to select data
        self.data_selector = QComboBox(self)
        layout.addWidget(self.data_selector)

        # Table to display data
        self.data_table = DatasetTableView(self)
        layout.addWidget(self.data_table)

        # Placeholder image
        self.data_placeholder_image = QLabel(parent=self)
        pixmap = QPixmap(self.appctx.get_resource('images/clarite_logo.png'))
        self.data_placeholder_image.setPixmap(pixmap)
        self.data_placeholder_image.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.data_placeholder_image)

        # Placeholder label
        self.data_placeholder_label = QLabel("Load a dataset to begin", parent=self)
        self.data_placeholder_label.setAlignment(Qt.AlignHCenter)
        self.data_placeholder_label.setStyleSheet("font-size: 20px; font-weight: bold;")
        layout.addWidget(self.data_placeholder_label)

        # Area below table
        ##################
        below_table_layout = QHBoxLayout()

        # Legend
        self.initialize_legend(below_table_layout)
        below_table_layout.addStretch()

        # Delete Button
        self.btn_delete = QPushButton(text="Delete", parent=self)
        below_table_layout.addWidget(self.btn_delete)

        # Save As button
        self.btn_save_as = QPushButton(text="Save As", parent=self)
        below_table_layout.addWidget(self.btn_save_as)

        # Save the layout
        layout.addLayout(below_table_layout)

        # Model to hold data
        self.data_model = PandasDFModel(self.appctx)
        self.data_table.setModel(self.data_model)

        # Initial state
        self.check_placeholder()
        self.hide_legend(True)

    def initialize_legend(self, layout):
        """Draw a legend for data types (shown only when viewing a dataset)"""
        self.legend_labels = dict()
        self.data_colors = self.read_color_settings()  # for drawing the legend
        for label_text, color in self.data_colors.items():
            # Create label
            qlabel = QLabel(self)
            self.legend_labels[label_text] = qlabel
            # Set text
            qlabel.setText(label_text)
            layout.addWidget(qlabel)
        self.color_legend()

    def color_legend(self):
        self.data_colors = self.read_color_settings()  # for drawing the legend
        for label_text, color in self.data_colors.items():
            qlabel = self.legend_labels[label_text]
            qlabel.setStyleSheet(f"border: 1px solid black;"
                                 f"background-color: {color.name()};"
                                 f"padding: 5;")

    def connect_ui_signals(self):
        """Signals from the UI in this widget call methods in the appcontext"""
        self.data_selector.currentIndexChanged.connect(lambda idx: self.appctx.change_dataset(idx))
        self.btn_save_as.clicked.connect(self.save_dataset)
        self.btn_delete.clicked.connect(self.delete_dataset)

    def connect_appctx_signals(self):
        """Signals from the app context are connected to slots in this widget"""
        self.appctx.signals.changed_dataset.connect(self.select_dataset)
        # Connections to add or remove a dataset affecting the combobox
        self.appctx.signals.added_dataset.connect(self.combobox_add_dataset)
        self.appctx.signals.removed_dataset.connect(self.combobox_remove_dataset)
        # Connections to update button status
        self.appctx.signals.added_dataset.connect(self.update_buttons)
        self.appctx.signals.removed_dataset.connect(self.update_buttons)
        # Connections to viewing/hiding the placeholder
        self.appctx.signals.added_dataset.connect(self.check_placeholder)
        self.appctx.signals.removed_dataset.connect(self.check_placeholder)

    # Define slots
    @pyqtSlot()
    def check_placeholder(self):
        """Hide some elements and show a placeholder if no datasets are loaded"""
        if len(self.appctx.datasets) == 0:
            self.data_placeholder_image.setVisible(True)
            self.data_placeholder_label.setVisible(True)
            self.data_selector.setVisible(False)
            self.data_table.setVisible(False)
            self.btn_save_as.setVisible(False)
            self.btn_delete.setVisible(False)
        else:
            self.data_placeholder_image.setVisible(False)
            self.data_placeholder_label.setVisible(False)
            self.data_selector.setVisible(True)
            self.data_table.setVisible(True)
            self.btn_save_as.setVisible(True)
            self.btn_delete.setVisible(True)

    @pyqtSlot(bool)
    def hide_legend(self, hide):
        for var_type, label in self.legend_labels.items():
            if hide:
                label.setVisible(False)
            else:
                label.setVisible(True)
                label.setText(self.data_model.get_legend_label(var_type.lower()))

    @pyqtSlot(int)
    def select_dataset(self, dataset_idx):
        """Update the UI to show the newly selected dataset"""
        # Update the selector
        if len(self.appctx.datasets) >= dataset_idx:
            self.data_selector.setCurrentIndex(dataset_idx)
        # Refresh the model
        self.data_model.refresh()
        # Update the legend labels
        if self.data_model.kind == 'dataset':
            self.hide_legend(False)
        else:
            self.hide_legend(True)

    @pyqtSlot()
    def combobox_add_dataset(self):
        """Add the newest dataset name to the combobox"""
        self.data_selector.addItem(self.appctx.datasets[-1].get_selector_name())

    @pyqtSlot(int)
    def combobox_remove_dataset(self, idx):
        """Remove the indicated dataset from the combobox"""
        self.data_selector.removeItem(idx)

    @pyqtSlot()
    def update_buttons(self):
        """UI Updates when the number of datasets changes"""
        if self.data_model.dataset is None:
            self.btn_delete.setEnabled(False)
            self.btn_save_as.setEnabled(False)
        else:
            self.btn_delete.setEnabled(True)
            self.btn_save_as.setEnabled(True)

    @pyqtSlot()
    def save_dataset(self):
        """
        Save the currently selected dataset
        :return:
        """
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        filename, _ = QFileDialog.getSaveFileName(self, "QFileDialog.getSaveFileName()", "",
                                                  "All Files (*);;Text Files (*.txt)", options=options)

        # Define a no-parameter function to save the data using a thread
        dataset = self.appctx.datasets[self.appctx.current_dataset_idx]

        def save_func():
            # Save Data
            dataset.df.to_csv(filename, sep="\t")
            # Save Dtypes
            dtypes = {variable_name: {'type': str(dtype)} if str(dtype) != 'category'
            else {'type': str(dtype),
                  'categories': list(dtype.categories.values.tolist()),
                  'ordered': dtype.ordered}
                      for variable_name, dtype in dataset.df.dtypes.iteritems()}
            dtypes_filename = filename + ".dtypes"
            dtypes_file = Path(dtypes_filename)
            with dtypes_file.open('w') as f:
                json.dump(dtypes, f)

        RunProgress.run_with_progress(progress_str="Saving Data...",
                                      function=save_func,
                                      slot=None,
                                      parent=self)

        # Log Info
        save_str = f"\nSaved {len(dataset.df):,} observations of {len(list(dataset.df)):,} variables" \
                   f" in '{dataset.get_selector_name()}' to '{filename}'\n"
        self.appctx.log_info("\n" + "="*80 + save_str + "="*80)

        # Log Python
        self.appctx.log_python(f"# Save data and it's associated datatypes\n"
                        f"{dataset.get_python_name()}.to_csv({filename}, sep='\t')\n")
        # TODO: Save datatypes file similar to the commandline?


    @pyqtSlot()
    def delete_dataset(self):
        del_name = self.appctx.datasets[self.appctx.current_dataset_idx].get_selector_name()
        confirm_click(parent=self,
                      txt="Are you sure you want to delete this dataset?",
                      inform_txt=del_name,
                      button_slots={'Yes': self.appctx.remove_current_dataset,
                                    'No': None})
