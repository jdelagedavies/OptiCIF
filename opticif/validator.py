"""
This module contains the CSV file structure validator used by the CIF transformer.
"""

import csv
from pathlib import Path
from typing import Union


class CSVStructureError(Exception):
    """Custom exception for CSV file structure errors."""


def validate_csv_structure(
    csv_path: Union[str, Path], csv_delimiter: str = ";"
) -> None:
    """
    Checks if the CSV file structure is valid and contains a non-empty "name" column with no duplicates and no empty
    values.

    Args:
        csv_path (Union[str, Path]): The path to the CSV file to validate.
        csv_delimiter (str): The delimiter used in the CSV file. Defaults to ";".

    Raises:
        CSVStructureError: If the CSV file does not contain a "name" column, contains duplicate names, or contains empty
        values.
    """
    # Check if the CSV file contains a "name" column
    with open(csv_path, "r") as f:
        reader = csv.DictReader(f, delimiter=csv_delimiter)
        if "name" not in reader.fieldnames:
            raise CSVStructureError(
                f"{csv_path} should have a header with a 'name' column."
            )

        # Check if the "name" column contains duplicates or empty values
        names = set()
        for row in reader:
            name = row["name"].strip()
            if not name:
                raise CSVStructureError(
                    f"'{csv_path}' contains an empty value in the 'name' column."
                )
            if name in names:
                raise CSVStructureError(
                    f"'{csv_path}' contains duplicate names in the 'name' column."
                )

            names.add(name)
