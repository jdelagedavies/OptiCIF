"""
This module provides functionality for working with CSV files in the context of the CIF optimization process and
DSM matrix conversion. It contains functions for converting a list of sequenced RaGraph node objects to a CSV file
and for converting a binary DSM matrix in CSV format to an edge list in CSV format, using node names from a
separate CSV file.
"""

import csv
from pathlib import Path
from typing import List, Union

from ragraph.graph import Node

from opticif import validate_node_csv_structure, validate_matrix_csv_structure


def node_to_csv(
    nodes: List[Node],
    stem_path: str,
    output_dir: Union[str, Path] = "generated",
    csv_delimiter: str = ";",
) -> None:
    """
    Write a list of sequenced node names to a CSV file with the given stem path. The node objects are from the
    RaGraph package.

    Args:
        nodes (List[Node]): A list of sequenced RaGraph node objects. Each node object must have a 'name' attribute
            that is a string.
        stem_path (str): The stem path for the CSV file, without the '.csv' extension.
        output_dir (Union[str, Path]): The path to the directory where the output files will be saved.
                        Defaults to "generated".
        csv_delimiter (str): The delimiter used in the CSV file. Defaults to ";".

    Returns:
        None. The CSV file is saved with ".nodes.seq.csv" appended to the stem path in the specified output
        directory.
    """
    # Extracting only the names of each node using list comprehension
    node_names = [node.name for node in nodes]

    # Create the 'generated' directory if it doesn't exist
    generated_dir = Path(output_dir)
    generated_dir.mkdir(exist_ok=True)

    # Append "_nodes.csv" to the stem path to create the filename
    filename = generated_dir / f"{stem_path}.nodes.seq.csv"

    # Writing the node names to a CSV file
    with open(filename, mode="w", newline="") as f:
        writer = csv.writer(f, delimiter=csv_delimiter)
        writer.writerow(["name"])
        for name in node_names:
            writer.writerow([name])


def mat_to_csv(
    matrix_path: Union[str, Path],
    node_path: Union[str, Path],
    stem_path: str,
    output_dir: Union[str, Path] = "generated",
    delimiter: str = ";",
) -> None:
    """
    Convert a binary DSM matrix in CSV format to an edge list in CSV format, using node names from a separate CSV file.

    The matrix is binary, with a '1' representing a mark (an edge between nodes) and a '0' representing an empty cell
    (no edge between nodes).

    Args:
        matrix_path (Union[str, Path]): The path to the CSV file containing the binary DSM matrix.
        node_path (Union[str, Path]): The path to the CSV file containing node names with a header "name".
        stem_path (str): The stem path for the CSV file, without the '.csv' extension.
        output_dir (Union[str, Path]): The path to the directory where the output files will be saved.
                        Defaults to "generated".
        delimiter (str): The delimiter used in the CSV files. Defaults to ";".

    Returns:
        None. The edge list in CSV format is saved with ".edges.csv" appended to the stem path in the specified output
        directory.
    """
    # Convert inputs to Path objects
    matrix_path = Path(matrix_path)
    node_path = Path(node_path)

    # Validate the node CSV structure
    validate_node_csv_structure(node_path, delimiter)

    # Read node names from the CSV file
    with open(node_path, "r") as f:
        nodes = [row["name"] for row in csv.DictReader(f, delimiter=delimiter)]

    # Validate the matrix CSV structure
    validate_matrix_csv_structure(matrix_path, delimiter)

    # Read the matrix from the CSV file
    with open(matrix_path, "r") as f:
        matrix = list(csv.reader(f, delimiter=delimiter))

    # Create the 'generated' directory if it doesn't exist
    generated_dir = Path(output_dir)
    generated_dir.mkdir(exist_ok=True)

    # Append ".edges.csv" to the stem path to create the filename
    output_file = generated_dir / f"{stem_path}.edges.csv"

    # Convert the matrix to edges in CSV format
    with open(output_file, "w", newline="") as f:
        writer = csv.writer(f, delimiter=delimiter)
        writer.writerow(["source", "target"])

        for i, row in enumerate(matrix):
            for j, mark in enumerate(row):
                if mark == "1":
                    writer.writerow([nodes[i], nodes[j]])
