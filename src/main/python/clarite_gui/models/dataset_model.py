from typing import List

import clarite
import pandas as pd


class Dataset:
    """
    Dataset is a simple class to hold datasets as they are used in CLARITE.
    Each has a name, a "kind", and the actual data.

    kinds
    -----
    data - input data to be used in the analysis, which may have any variables as columns and observations as rows.
    result - output from the ewas function which means there are certain columns defined and each row is a variable.
    """
    def __init__(self, name: str, kind: str, df: pd.DataFrame):
        self.name = name
        self.kind = kind
        self.df = df
        self.number = None

        # TODO: Validate 'kind'

    def __repr__(self):
        return f"Dataset('{self.name}', '{self.kind}')\n{self.df.head()}"

    def __len__(self):
        return len(self.df)

    def get_selector_name(self):
        """Return a name used for this dataset in the drop-down selector"""
        return f"{self.number} - {self.name}"

    def get_python_name(self):
        """Name used to represent the dataset in generated python code"""
        return f"df{self.number}_{self.name.replace(' ', '_')}"

    def get_types(self) -> List[str]:
        return clarite.describe.get_types(self.df)

    def set_number(self, number):
        """Associate a number with each dataset as they are added.  Not always == index in appctx.datasets"""
        self.number = number

    def get_column_name(self, i: int) -> str:
        """
        Get the i-th column
        :param i:
        :return: str
        """
        return list(self.df)[i]

    def get_row_name(self, i: int) -> str:
        """
        Get the i-th index value
        :param i:
        :return: str
        """
        return str(self.df.index[i])
