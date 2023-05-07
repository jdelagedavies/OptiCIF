"""This module provides functionality for working with CSV files related to the CIF optimization process, DSM matrix
conversion, and plant group sequence handling. It includes functions for:

- Converting a list of sequenced RaGraph node objects to a CSV file;
- Converting a binary DSM matrix in .mat to an edge list in CSV format, using node names from a separate CSV file;
- Generating a CSV file with ordered node names based on plant group information from a product system map and a group
  sequence .mat file.
"""

import csv
import scipy.io as sio
from pathlib import Path
from typing import List, Union

from ragraph.graph import Node

from opticif import validate_node_csv_structure, validate_matrix_file_structure


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
        csv_delimiter (str): The csv_delimiter used in the CSV file. Defaults to ";".

    Returns:
        None. The CSV file is saved with ".nodes.seq.csv" appended to the stem path in the specified output
        directory.
    """
    # Extracting only the names of each node using list comprehension
    node_names = [node.name for node in nodes]

    # Create the output directory if it doesn't exist
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
    csv_delimiter: str = ";",
) -> None:
    """
    Convert a binary DSM matrix in .mat format to an edge list in CSV format, using node names from a separate CSV file.

    The matrix is binary, with a '1' representing a mark (an edge between nodes) and a '0' representing an empty cell
    (no edge between nodes).

    Args:
        matrix_path (Union[str, Path]): The path to the .mat file containing the binary DSM matrix.
        node_path (Union[str, Path]): The path to the CSV file containing node names with a header "name".
        stem_path (str): The stem path for the CSV file, without the '.csv' extension.
        output_dir (Union[str, Path]): The path to the directory where the output files will be saved.
                        Defaults to "generated".
        csv_delimiter (str): The csv_delimiter used in the CSV files. Defaults to ";".

    Returns:
        None. The edge list in CSV format is saved with ".edges.csv" appended to the stem path in the specified output
        directory.
    """
    # Validate the node CSV structure
    validate_node_csv_structure(node_path, csv_delimiter)

    # Read node names from the CSV file
    with open(node_path, "r") as f:
        nodes = [row["name"] for row in csv.DictReader(f, delimiter=csv_delimiter)]

    # Validate the matrix file structure
    validate_matrix_file_structure(matrix_path)

    # Read the matrix from the .mat file
    with open(matrix_path, "r", encoding="utf-8-sig") as f:
        matrix = [list(map(int, row.strip().split())) for row in f]

    # Check if the length of both files matches
    if len(matrix) != len(nodes):
        raise ValueError(
            f"The length of '{matrix_path}' does not match the length of '{node_path}'."
        )

    # Create the output directory if it doesn't exist
    generated_dir = Path(output_dir)
    generated_dir.mkdir(exist_ok=True)

    # Append ".edges.csv" to the stem path to create the filename
    output_file = generated_dir / f"{stem_path}.edges.csv"

    # Convert the matrix to edges in CSV format
    with open(output_file, "w", newline="") as f:
        writer = csv.writer(f, delimiter=csv_delimiter)
        writer.writerow(["source", "target"])

        for i, row in enumerate(matrix):
            for j, mark in enumerate(row):
                if mark == 1:
                    writer.writerow([nodes[i], nodes[j]])


def plant_groups_to_csv(
    group_map_path: Union[str, Path],
    group_sequence_path: Union[str, Path],
    stem_path: str,
    output_dir: Union[str, Path] = "generated",
) -> None:
    """
    Reads plant group information from a product system map file and a group sequence file output by the MATLAB
    sequencing script from de Jong (2020), and generates a CSV file containing the ordered list of node names based on
    the group sequence.

    Args:
        group_map_path (Union[str, Path]): The path to a file containing plant group information, also known as the
                                           product system map. Each line should contain a group ID followed by a
                                           comma-separated list of plant elements (node names) belonging to the group.
                                           For example:
                                           G1,NodeA,NodeB
                                           G2,NodeC,NodeD
        group_sequence_path (Union[str, Path]): The path to a .mat file containing a 'scheduleorder' variable, which
                                                represents the ordered sequence of group IDs. This file is output by the
                                                MATLAB sequencing script from de Jong (2020).
        stem_path (str): A string used as the base of the output file's name.
        output_dir (Union[str, Path]): The path to the directory where the output files will be saved.
                                       Defaults to "generated".

    Returns:
        None. The ordered node names are saved to a CSV file with the header "name" in the specified output directory.
              The output file's name is created by appending ".nodes.seq.csv" to the stem_path.
    """
    # Read the group information from the file
    with open(group_map_path, "r") as f:
        group_lines = f.readlines()

    # Process the group information to create a dictionary mapping group IDs to plant elements
    group_map = {}
    for line in group_lines:
        group_data = line.strip().split(",")
        group_id = int(group_data[0][1:])
        plant_elements = [elem.strip() for elem in group_data[1:]]
        group_map[group_id] = plant_elements

    # Load the group_sequence from the scheduleorder file
    mat_data = sio.loadmat(group_sequence_path)
    group_sequence = mat_data["scheduleorder"][0]

    # Check if the length of both files matches
    if len(group_map) != len(group_sequence):
        raise ValueError(
            f"The length of '{group_map_path}' does not match the length of '{group_sequence_path}'."
        )

    # Create the ordered list of node names based on the group_sequence
    ordered_node_names = []
    for group_id in group_sequence:
        ordered_node_names.extend(group_map[group_id])

    # Create the output directory if it doesn't exist
    generated_dir = Path(output_dir)
    generated_dir.mkdir(exist_ok=True)

    # Append ".nodes.seq.csv" to the stem path to create the filename
    output_file = generated_dir / f"{stem_path}.nodes.seq.csv"

    # Write the ordered node names to a CSV file with the header "name"
    with open(output_file, "w") as f:
        f.write("name\n")
        for node_name in ordered_node_names:
            f.write(node_name + "\n")
