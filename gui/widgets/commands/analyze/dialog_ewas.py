import clarite
import pandas as pd
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import (
    QDialog,
    QFormLayout,
    QDialogButtonBox,
    QLineEdit,
    QPushButton,
    QGroupBox,
    QSpinBox,
    QCheckBox,
    QComboBox,
    QFileDialog,
    QHBoxLayout,
    QLabel,
)

from gui.models import Dataset
from gui.widgets import SelectColumnDialog, SkipOnlyDialog
from gui.widgets.utilities import RunProgress, show_warning


class EWASDialog(QDialog):
    """
    This dialog allows sets settings for EWAS
    """

    SINGLE_CLUSTER_OPTIONS = ["fail", "adjust", "average", "certainty"]
    WEIGHT_TYPES = ["None", "Single Weight", "Specific Weights"]
    BUILTIN_REGRESSION_KINDS = ["glm", "weighted_glm", "r_survey"]

    def __init__(self, *args, **kwargs):
        super(EWASDialog, self).__init__(*args, **kwargs)
        self.appctx = self.parent().appctx
        self.dataset = self.appctx.datasets[self.appctx.current_dataset_idx]
        self.data_name = None
        # EWAS params
        self.outcome = None
        self.covariates = []
        self.min_n = 200
        self.regression_kind = "glm"
        self.use_survey = False
        # Survey Params
        self.survey_df = None
        self.strata = None
        self.cluster = None
        self.fpc = None
        self.nest = True
        self.weights = None
        self.single_cluster = self.SINGLE_CLUSTER_OPTIONS[0]
        self.drop_unweighted = False
        # Setup UI
        self.setup_ui()

    def get_func(self):
        """Return a function with no parameters to be run in a thread"""
        # Saved results name
        if self.data_name is None:
            data_name = f"EWAS Results for {self.appctx.datasets[self.appctx.current_dataset_idx].name}"
        else:
            data_name = self.data_name

        # EWAS parameters
        kwargs = {
            "outcome": self.outcome,
            "covariates": self.covariates,
            "data": self.dataset.df,
            "regression_kind": self.regression_kind,
            "min_n": self.min_n,
        }

        # Survey Parameters
        if self.use_survey:
            kwargs["survey_design_spec"] = clarite.survey.SurveyDesignSpec(
                survey_df=self.survey_df.df,
                strata=self.strata,
                cluster=self.cluster,
                nest=self.nest,
                fpc=self.fpc,
                weights=self.weights,
                single_cluster=self.single_cluster,
                drop_unweighted=self.drop_unweighted,
            )

        def f():
            result = clarite.analyze.ewas(**kwargs)
            return Dataset(data_name, "ewas_result", result)

        return f

    def log_command(self):
        old_data_name = self.dataset.get_python_name()  # Original selected data
        new_data_name = self.appctx.datasets[
            self.appctx.current_dataset_idx
        ].get_python_name()  # New selected data
        python_cmd_args = {
            "outcome": repr(self.outcome),
            "covariates": repr(self.covariates),
            "data": old_data_name,
            "regression_kind": repr(self.regression_kind),
            "min_n": self.min_n,
        }
        # Log Survey Design
        if self.use_survey:
            survey_df_name = self.survey_df.get_python_name()
            sds_name = f"survey_{old_data_name}"
            self.appctx.log_python(
                f"{sds_name} = clarite.survey.SurveyDesignSpec("
                f"survey_df={survey_df_name}, "
                f"strata={repr(self.strata)}, "
                f"cluster={repr(self.cluster)}, "
                f"nest={repr(self.nest)}, "
                f"fpc={repr(self.fpc)}, "
                f"weights={repr(self.weights)}, "
                f"single_cluster={repr(self.single_cluster)},"
                f"drop_unweighted={repr(self.drop_unweighted)})"
            )
            python_cmd_args["survey_design_spec"] = sds_name
        # Log EWAS
        self.appctx.log_python(
            f"{new_data_name} = clarite.analyze.ewas("
            + ", ".join([f"{k}={v}" for k, v in python_cmd_args.items()])
            + ")"
        )

    def setup_ui(self):
        self.setWindowTitle(f"EWAS")
        self.setMinimumWidth(500)
        self.setModal(True)

        layout = QFormLayout()
        self.setLayout(layout)

        # Data Name
        self.le_data_name = QLineEdit(self.data_name)
        input_name = self.appctx.datasets[self.appctx.current_dataset_idx].name
        self.le_data_name.setPlaceholderText(f"EWAS results for {input_name}")
        self.le_data_name.textChanged.connect(self.update_data_name)
        layout.addRow("Save Dataset Name: ", self.le_data_name)

        # Outcome
        self.outcome_btn = QPushButton("Not Set", parent=self)
        self.outcome_btn.clicked.connect(self.launch_get_outcome)
        layout.addRow("Outcome", self.outcome_btn)

        # Covariates
        self.covariates_btn = QPushButton("None", parent=self)
        self.covariates_btn.clicked.connect(self.launch_get_covariates)
        layout.addRow("Covariates", self.covariates_btn)

        # Min N
        self.min_n_sb = QSpinBox(self)
        self.min_n_sb.setRange(0, len(self.dataset))
        self.min_n_sb.setValue(self.min_n)
        self.min_n_sb.valueChanged.connect(self.update_min_n)
        layout.addRow("Minimum valid samples", self.min_n_sb)

        # Regression Kind
        # Note: Some methods must use survey, for others it is optional.
        regression_kind_layout = QHBoxLayout()
        # Combobox to select the regression kind, initially 'glm'
        self.regression_kind_combobox = QComboBox(self)
        for rk in self.BUILTIN_REGRESSION_KINDS:
            self.regression_kind_combobox.addItem(rk)
        self.regression_kind_combobox.currentIndexChanged.connect(
            lambda idx: self.update_regression_kind(idx)
        )
        regression_kind_layout.addWidget(self.regression_kind_combobox)
        # Space
        regression_kind_layout.addStretch()
        # Checkbox to enable/disable use of survey info when optional for the kind,
        # initially unchecked and disabled b/c 'glm' is selected
        self.use_survey_cb = QCheckBox(self)
        self.use_survey_cb.setChecked(self.use_survey)
        self.use_survey_cb.setDisabled(True)
        self.use_survey_cb.stateChanged.connect(self.update_use_survey)
        regression_kind_layout.addWidget(self.use_survey_cb)
        regression_kind_layout.addWidget(QLabel("Use Survey Information"))
        layout.addRow("Regression Kind", regression_kind_layout)

        #############################
        # Survey Settings Group Box #
        #############################
        self.survey_setting_group = QGroupBox("Survey Data Settings")
        self.survey_setting_group.setHidden(True)  # Hidden by default
        survey_setting_layout = QFormLayout()
        self.survey_setting_group.setLayout(survey_setting_layout)
        layout.addRow(self.survey_setting_group)

        # Survey df - select a dataset that has been loaded
        self.survey_df_combobox = QComboBox(self)
        for data in [d for d in self.appctx.datasets if d.kind == "dataset"]:
            self.survey_df_combobox.addItem(data.name)
        self.survey_df_combobox.currentIndexChanged.connect(
            lambda idx: self.update_survey_df(idx)
        )
        survey_setting_layout.addRow("Survey Data", self.survey_df_combobox)

        # Strata - pick a column from the survey df
        self.strata_btn = QPushButton("None", parent=self)
        self.strata_btn.clicked.connect(self.launch_get_strata)
        survey_setting_layout.addRow("Strata", self.strata_btn)

        # Cluster - pick a column from the survey df
        self.cluster_btn = QPushButton("None", parent=self)
        self.cluster_btn.clicked.connect(self.launch_get_cluster)
        survey_setting_layout.addRow("Cluster", self.cluster_btn)

        # Nest
        self.nest_checkbox = QCheckBox(self)
        self.nest_checkbox.setChecked(True)
        self.nest_checkbox.stateChanged.connect(self.update_nest)
        survey_setting_layout.addRow("Clusters nested in Strata", self.nest_checkbox)

        # FPC - pick a column from the survey df
        self.fpc_btn = QPushButton("None", parent=self)
        self.fpc_btn.clicked.connect(self.launch_get_fpc)
        survey_setting_layout.addRow("FPC", self.fpc_btn)

        # Weights
        self.weight_method_combobox = QComboBox(self)
        for option in self.WEIGHT_TYPES:
            self.weight_method_combobox.addItem(option)
        self.weight_method_combobox.currentIndexChanged.connect(
            lambda idx: self.update_weight_type(idx)
        )
        survey_setting_layout.addRow("Survey Weights", self.weight_method_combobox)

        # Weights - Single
        self.weight_single_btn = QPushButton("Not Set", parent=self)
        self.weight_single_btn.clicked.connect(self.launch_get_weight_single)
        self.weight_single_btn.setEnabled(
            False
        )  # Disabled b/c weight type is None by default
        survey_setting_layout.addRow("\tSingle Weight", self.weight_single_btn)

        # Weights - Specific
        self.weight_specific_btn = QPushButton("Not Set", parent=self)
        self.weight_specific_btn.clicked.connect(self.launch_get_weight_specific)
        self.weight_specific_btn.setEnabled(
            False
        )  # Disabled b/c weight type is None by default
        survey_setting_layout.addRow("\tSpecific Weight", self.weight_specific_btn)

        # Drop Unweighted
        self.drop_unweighted_checkbox = QCheckBox(self)
        self.drop_unweighted_checkbox.setChecked(False)
        self.drop_unweighted_checkbox.stateChanged.connect(self.update_drop_unweighted)
        survey_setting_layout.addRow(
            "Drop unweighted observations", self.drop_unweighted_checkbox
        )

        # Single Cluster Dropdown
        self.single_cluster_combobox = QComboBox(self)
        for option in self.SINGLE_CLUSTER_OPTIONS:
            self.single_cluster_combobox.addItem(option)
        self.single_cluster_combobox.currentIndexChanged.connect(
            lambda idx: self.update_single_cluster(idx)
        )
        survey_setting_layout.addRow(
            "Single Cluster Handling", self.single_cluster_combobox
        )

        # Ok/Cancel
        QBtn = QDialogButtonBox.Ok | QDialogButtonBox.Cancel

        self.buttonBox = QDialogButtonBox(QBtn)
        layout.addRow(self.buttonBox)
        self.buttonBox.accepted.connect(self.submit)
        self.buttonBox.rejected.connect(self.reject)

        # Initialize some settings
        self.update_survey_df(0)

    def update_data_name(self):
        text = self.le_data_name.text()
        if len(text.strip()) == 0:
            self.data_name = None
        else:
            self.data_name = text

    def submit(self):
        if self.data_name is not None and self.data_name in [
            d.name for d in self.appctx.datasets
        ]:
            show_warning(
                "Dataset already exists",
                f"A dataset named '{self.data_name}' already exists.\n"
                f"Use a different name or clear the dataset name field.",
            )
        elif self.outcome is None:
            show_warning("Missing Parameter", "A phenotype must be selected")
        else:
            print(f"Running EWAS...")
            # Run with a progress dialog
            RunProgress.run_with_progress(
                progress_str="Running EWAS...",
                function=self.get_func(),
                slot=self.appctx.add_dataset,
                parent=self,
            )
            self.log_command()
            self.accept()

    def launch_get_outcome(self):
        """Launch a dialog to set the phenotype"""
        phenotype = SelectColumnDialog.get_column(
            columns=list(self.dataset.df), selected=self.outcome, parent=self
        )
        if phenotype is not None:
            self.outcome = phenotype
            self.outcome_btn.setText(f"{self.outcome}")

    def launch_get_covariates(self):
        """Launch a dialog to set the covariates"""
        _, skip, only = SkipOnlyDialog.get_skip_only(
            columns=list(self.dataset.df), skip=None, only=self.covariates, parent=self
        )
        if skip is not None:
            self.covariates = [v for v in list(self.dataset.df) if v not in skip]
        elif only is not None:
            self.covariates = only
        else:
            self.covariates = []

        # Set text
        if len(self.covariates) > 0:
            self.covariates_btn.setText(f"{len(self.covariates):,} Selected")
        else:
            self.covariates_btn.setText("None")

    @pyqtSlot(int)
    def update_min_n(self, value):
        self.min_n = value

    def update_regression_kind(self, idx):
        self.regression_kind = self.BUILTIN_REGRESSION_KINDS[idx]
        # Must use survey if using weighted_glm
        if self.regression_kind == "glm":
            self.use_survey_cb.setChecked(False)
            self.use_survey_cb.setDisabled(True)
        elif self.regression_kind == "weighted_glm":
            self.use_survey_cb.setChecked(True)
            self.use_survey_cb.setDisabled(True)
        else:
            self.use_survey_cb.setDisabled(False)
        self.survey_setting_group.setHidden(not self.use_survey)
        self.adjustSize()

    def update_use_survey(self):
        self.use_survey = not self.use_survey
        self.survey_setting_group.setHidden(not self.use_survey)
        self.adjustSize()

    @pyqtSlot(int)
    def update_survey_df(self, idx):
        datasets = [d for d in self.appctx.datasets if d.kind == "dataset"]
        self.survey_df = datasets[idx]
        # Reset Strata
        self.strata = None
        self.strata_btn.setText("None")
        # Reset Cluster
        self.cluster = None
        self.cluster_btn.setText("None")
        # Reset FPC
        self.fpc = None
        self.fpc_btn.setText("None")

    def launch_get_strata(self):
        """Launch a dialog to set the strata column from the survey df"""
        strata = SelectColumnDialog.get_column(
            columns=list(self.survey_df.df), selected=self.strata, parent=self
        )
        if strata is not None:
            self.strata = strata
            self.strata_btn.setText(f"{self.strata}")

    def launch_get_cluster(self):
        """Launch a dialog to set the cluster column from the survey df"""
        cluster = SelectColumnDialog.get_column(
            columns=list(self.survey_df.df), selected=self.cluster, parent=self
        )
        if cluster is not None:
            self.cluster = cluster
            self.cluster_btn.setText(f"{self.cluster}")

    def update_nest(self):
        """Update the nest parameter to match the checkbox"""
        self.nest = self.nest_checkbox.isChecked()

    def launch_get_fpc(self):
        """Launch a dialog to set the fpc column from the survey df"""
        fpc = SelectColumnDialog.get_column(
            columns=list(self.survey_df.df), selected=self.fpc, parent=self
        )
        if fpc is not None:
            self.fpc = fpc
            self.fpc_btn.setText(f"{self.fpc}")

    @pyqtSlot(int)
    def update_weight_type(self, idx):
        """The type of weight selection was changed: enable/disable the weight settings"""
        weight_type = self.WEIGHT_TYPES[idx]
        if weight_type == "None":
            self.weights = None
            # Disable single weight
            self.weight_single_btn.setEnabled(False)
            self.weight_single_btn.setText("Not Set")
            # Disable specific weight
            self.weight_specific_btn.setEnabled(False)
            self.weight_specific_btn.setText("Not Set")
        elif weight_type == "Single Weight":
            # Enable Single Weight
            self.weight_single_btn.setEnabled(True)
            # Disable specific weight
            self.weight_specific_btn.setEnabled(False)
            self.weight_specific_btn.setText("Not Set")
        elif weight_type == "Specific Weights":
            # Disable single weight
            self.weight_single_btn.setEnabled(False)
            self.weight_single_btn.setText("Not Set")
            # Enable specific weight
            self.weight_specific_btn.setEnabled(True)

    def launch_get_weight_single(self):
        """Launch a dialog to set the single weight variable"""
        selected_variable = SelectColumnDialog.get_column(
            columns=list(self.survey_df.df), selected=None, parent=self
        )
        if selected_variable is not None:
            self.weights = selected_variable
            self.weight_single_btn.setText(f"{self.weights}")

    def launch_get_weight_specific(self):
        """Launch a dialog to load a file matching variables to weights"""
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        filename, _ = QFileDialog.getOpenFileName(
            self,
            f"Load Specific Weights File",
            "",
            f"TSV Files (*.tsv *.txt)",
            options=options,
        )
        # Set filename
        if len(filename) == 0:
            return

        # Read file
        try:
            weights = pd.read_csv(filename, sep="\t")
        except Exception as e:
            show_warning("Specific Weights File Error", f"Error reading file: {str(e)}")
            return

        # Must have two columns
        if len(list(weights)) != 2:
            show_warning(
                "Specific Weights File Error",
                f"Expected 2 columns, found {len(list(weights)):,} columns",
            )
            return

        # Set columns and convert to a dictionary
        weights.columns = ["variable", "weight"]
        weights = weights.set_index("variable")
        weights = weights.to_dict()["weight"]

        # Check that some variables/weights matched
        unique_vars = len(set(weights.keys()) & set(list(self.dataset.df)))
        unique_weights = len(set(weights.values()) & set(list(self.survey_df.df)))
        missing_weights = (
            set(list(self.dataset.df))
            - set(weights.keys())
            - set(weights.values())
            - set(self.covariates)
            - {self.outcome, self.cluster, self.strata, self.fpc}
        )
        if unique_vars < 1:
            show_warning(
                "Specific Weights File Error",
                f"Loaded {filename}\n"
                "No variables matched columns in the input data.\n\n"
                "The first column of the specific weights file must list variable names and "
                "a header line must be present.",
            )
        elif unique_weights < 1:
            show_warning(
                "Specific Weights File Error",
                f"Loaded {filename}\n"
                "No weights matched columns in the survey data.\n\n"
                "The second column of the specific weights file must list weight names and "
                "a header line must be present.",
            )
        elif len(missing_weights) > 0 and len(missing_weights) <= 5:
            show_warning(
                "Specific Weights File Error",
                f"Loaded {filename}\n"
                "Some variables are missing weights:\n\n"
                f"{', '.join(sorted(list(missing_weights)))}",
            )
        elif len(missing_weights) > 5:
            show_warning(
                "Specific Weights File Error",
                f"Loaded {filename}\n"
                "More than 5 variables are missing weights, including:\n\n"
                f"{', '.join(sorted(list(missing_weights))[:5])}",
            )
        else:
            self.weights = weights
            self.weight_specific_btn.setText(
                f"{unique_weights:,} different weights "
                f"assigned to {unique_vars:,} variables"
            )

    def update_drop_unweighted(self):
        """Update the nest parameter to match the checkbox"""
        self.drop_unweighted = self.drop_unweighted_checkbox.isChecked()

    @pyqtSlot(int)
    def update_single_cluster(self, idx):
        self.single_cluster = self.SINGLE_CLUSTER_OPTIONS[idx]
