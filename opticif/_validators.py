"""This module provides functionality for validating the structure of CSV and MAT files used in the CIF optimization
and DSM matrix conversion processes.
"""

import csv
from pathlib import Path
from typing import Union

from scipy.io import loadmat


class CSVStructureError(Exception):
    """Custom exception for CSV file structure errors."""


class CSVGroupingError(Exception):
    """Custom exception for CSV file grouping errors."""


class MATStructureError(Exception):
    """Custom exception for MAT file structure errors."""


def validate_node_csv_structure(
    csv_path: Union[str, Path], csv_delimiter: str = ";"
) -> None:
    """
    Checks if the node CSV file structure is valid and contains a non-empty 'name' column with no duplicates and no
    empty values. Additionally, if a 'labels' column is present, checks that nodes with the same label are grouped
    together.

    Args:
        csv_path (Union[str, Path]): The path to the node CSV file to validate.
        csv_delimiter (str): The csv_delimiter used in the CSV file. Defaults to ';'.

    Raises:
        CSVStructureError: If the node CSV file does not contain a 'name' column, contains duplicate names,
        or contains empty values.
        CSVGroupingError: If a 'labels' column is present and nodes with the same label are not grouped together.
    """
    # Check if the CSV file contains a 'name' column
    with open(csv_path, "r") as f:
        reader = csv.DictReader(f, delimiter=csv_delimiter)
        if "name" not in reader.fieldnames:
            raise CSVStructureError(
                f"'{csv_path}' should have a header with a 'name' column."
            )

        rows = list(reader)
        if "labels" in reader.fieldnames:
            last_label = None
            for row in rows:
                if (
                    last_label is not None
                    and last_label != row["labels"]
                    and last_label != ""
                    and any(r["labels"] == last_label for r in rows[rows.index(row) :])
                ):
                    raise CSVGroupingError(
                        f"'{csv_path}' should group nodes of the same label together. OptiCIF does not yet support "
                        f"nodes with more than one label."
                    )
                last_label = row["labels"]

        # Check for duplicate and empty names
        names = [row["name"] for row in rows]
        if "" in names:
            raise CSVStructureError(
                f"'{csv_path}' should not have empty values in the 'name' column."
            )
        if len(names) != len(set(names)):
            raise CSVStructureError(
                f"'{csv_path}' should not have duplicate values in the 'name' column."
            )


def validate_matrix_file_structure(matrix_path: Union[str, Path]) -> None:
    """
    Checks if the matrix file structure is valid, is square, and is binary (only uses 1s and 0s).

    Args:
        matrix_path (Union[str, Path]): The path to the matrix file to validate.

    Raises:
        MATStructureError: If the matrix file is not square, is not binary or has any formatting issues.
    """
    mat_data = loadmat(matrix_path)
    matrix = mat_data[list(mat_data.keys())[-1]]

    row_count = len(matrix)

    for i, row in enumerate(matrix):
        if len(row) != row_count:
            raise MATStructureError(
                f"The matrix in '{matrix_path}' is not square. Each row should have the same number of elements as "
                f"the number of rows."
            )

        for j, element in enumerate(row):
            if element not in [0, 1]:
                raise MATStructureError(
                    f"The matrix in '{matrix_path}' is not binary. Found '{element}' at row {i + 1}, column {j + 1}."
                )
