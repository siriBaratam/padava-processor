"""
=========================================================
Energy Supply Chain Analytics Engine
Data Loader
=========================================================

Loads all datasets, validates them and returns cleaned
DataFrames.
"""

import os
import pandas as pd

from .config import DATASET_PATHS, REQUIRED_COLUMNS


class DataLoader:

    def __init__(self):

        self.datasets = {}

    # ---------------------------------------------------
    # Load Single Dataset
    # ---------------------------------------------------

    def load_dataset(self, dataset_name):

        if dataset_name not in DATASET_PATHS:
            raise ValueError(
                f"Unknown dataset: {dataset_name}"
            )

        file_path = DATASET_PATHS[dataset_name]

        if not os.path.exists(file_path):
            raise FileNotFoundError(
                f"Dataset not found: {file_path}"
            )

        try:
            df = pd.read_excel(file_path)

        except Exception as e:
            raise Exception(
                f"Unable to read {file_path}\n{e}"
            )

        # Clean column names
        df.columns = (
            df.columns
            .str.strip()
            .str.lower()
            .str.replace(" ", "_")
        )

        return df

    # ---------------------------------------------------
    # Validate Required Columns
    # ---------------------------------------------------

    def validate_columns(
        self,
        dataset_name,
        dataframe
    ):

        required = REQUIRED_COLUMNS[dataset_name]

        missing = []

        for col in required:

            if col.lower() not in dataframe.columns:
                missing.append(col)

        if missing:

            raise ValueError(

                f"\n{dataset_name} dataset is missing columns:\n"

                f"{missing}"

            )

    # ---------------------------------------------------
    # Handle Missing Values
    # ---------------------------------------------------

    def clean_missing_values(
        self,
        dataframe
    ):

        dataframe = dataframe.copy()

        # Remove duplicate rows
        dataframe.drop_duplicates(
            inplace=True
        )

        # Replace NaN in object columns
        object_cols = dataframe.select_dtypes(
            include="object"
        ).columns

        dataframe[object_cols] = dataframe[
            object_cols
        ].fillna("Unknown")

        # Replace NaN in numeric columns
        numeric_cols = dataframe.select_dtypes(
            include="number"
        ).columns

        dataframe[numeric_cols] = dataframe[
            numeric_cols
        ].fillna(0)

        return dataframe

    # ---------------------------------------------------
    # Dataset Summary
    # ---------------------------------------------------

    def dataset_summary(
        self,
        dataset_name,
        dataframe
    ):

        return {

            "Dataset": dataset_name,

            "Rows": len(dataframe),

            "Columns": len(dataframe.columns),

            "Missing Values":

                int(
                    dataframe
                    .isnull()
                    .sum()
                    .sum()
                )

        }

    # ---------------------------------------------------
    # Load All Datasets
    # ---------------------------------------------------

    def load_all(self):

        summaries = []

        for dataset_name in DATASET_PATHS.keys():

            df = self.load_dataset(
                dataset_name
            )

            self.validate_columns(
                dataset_name,
                df
            )

            df = self.clean_missing_values(
                df
            )

            self.datasets[dataset_name] = df

            summaries.append(

                self.dataset_summary(
                    dataset_name,
                    df
                )

            )

        return self.datasets, summaries

    # ---------------------------------------------------
    # Get Dataset
    # ---------------------------------------------------

    def get_dataset(
        self,
        dataset_name
    ):

        if dataset_name not in self.datasets:

            raise ValueError(

                f"{dataset_name} not loaded."

            )

        return self.datasets[dataset_name]