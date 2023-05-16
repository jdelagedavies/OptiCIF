"""This module provides functionality for working with CSV files related to the CIF optimization process, DSM matrix
conversion, and plant group sequence handling.
"""

import csv
from pathlib import Path
from typing import Dict, List, Union

import scipy.io as sio
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
                        Defaults to 'generated'.
        csv_delimiter (str): The csv_delimiter used in the CSV file. Defaults to ';'.

    Returns:
        None. The CSV file is saved with '.nodes.seq.csv' appended to the stem path in the specified output
        directory.
    """
    # Extracting only the names of each node using list comprehension
    node_names = [node.name for node in nodes]

    # Create the output directory if it doesn't exist
    generated_dir = _create_output_directory(output_dir)

    # Append "_nodes.csv" to the stem path to create the filename
    filename = generated_dir / f"{stem_path}.nodes.seq.csv"

    # Writing the node names to a CSV file
    _write_csv_file(filename, ["name"], [[name] for name in node_names], csv_delimiter)


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
        node_path (Union[str, Path]): The path to the CSV file containing node names with a header 'name'.
        stem_path (str): The stem path for the CSV file, without the '.csv' extension.
        output_dir (Union[str, Path]): The path to the directory where the output files will be saved.
                        Defaults to 'generated'.
        csv_delimiter (str): The csv_delimiter used in the CSV files. Defaults to ';'.

    Returns:
        None. The edge list in CSV format is saved with '.edges.csv' appended to the stem path in the specified output
        directory.
    """
    # Validate the node CSV structure
    validate_node_csv_structure(node_path, csv_delimiter)

    # Read node names from the CSV file
    nodes = [row["name"] for row in _read_csv_file(node_path, csv_delimiter)]

    # Validate the matrix file structure
    validate_matrix_file_structure(matrix_path)

    # Read the matrix from the .mat file
    mat_data = sio.loadmat(matrix_path)
    matrix = mat_data[list(mat_data.keys())[-1]]

    # Check if the length of both files matches
    if len(matrix) != len(nodes):
        raise ValueError(
            f"The length of '{matrix_path}' does not match the length of '{node_path}'."
        )

    # Create the output directory if it doesn't exist
    generated_dir = _create_output_directory(output_dir)

    # Append ".edges.csv" to the stem path to create the filename
    output_file = generated_dir / f"{stem_path}.edges.csv"

    # Convert the matrix to edges in CSV format
    edges = [
        [nodes[i], nodes[j]]
        for i, row in enumerate(matrix)
        for j, mark in enumerate(row)
        if mark == 1
    ]

    _write_csv_file(output_file, ["source", "target"], edges, csv_delimiter)


def plant_groups_to_csv(
    prod_sys_map_path: Union[str, Path],
    schedule_order_path: Union[str, Path],
    group_info_path: Union[str, Path],
    stem_path: str,
    output_dir: Union[str, Path] = "generated",
    csv_delimiter: str = ";",
) -> None:
    """
    Reads plant group information from a product system map, a schedule order, and a partition information output by
    the MATLAB sequencing script from De Jong (2019). Generates two CSV files: one containing the ordered list of
    node names based on the plant group sequence, and another containing the ordered list of plant group IDs. It also
    appends a 'labels' column to both the ordered node and plant groups files with the partition ID they are part of
    (Delage-Davies, 2023), if they belong to a partition.

    Args:
        prod_sys_map_path (Union[str, Path]): The path to a file containing the product system map. Each line should
                                              contain a plant group ID followed by a comma-separated list of plant
                                              elements (node names) belonging to the plant group.
                                              For example:
                                              G1,NodeA,NodeB
                                              G2,NodeC,NodeD
        schedule_order_path (Union[str, Path]): The path to a .mat file containing the ordered sequence of group IDs.
        group_info_path (Union[str, Path]): The path to the .mat file containing the information about partitions:
                                               the starting position and the size of each partition.
        stem_path (str): A string used as the base of the output files' names.
        output_dir (Union[str, Path]): The path to the directory where the output files will be saved.
                                       Defaults to 'generated'.
        csv_delimiter (str): The csv_delimiter used in the CSV files. Defaults to ';'.

    Returns: None. The ordered node names and plant group IDs are saved to two separate CSV files in the specified
             output directory. The output files' names are created by appending '.nodes.seq.csv' and
             '.groups.nodes.seq.csv' to the stem_path.
    """
    # Read the plant group information from the file
    with open(prod_sys_map_path, "r") as f:
        plant_group_lines = f.readlines()

    # Process the plant group information to create a dictionary mapping plant group IDs to plant elements
    plant_group_map = _build_plant_group_map(plant_group_lines)

    # Load the plant_group_sequence from the scheduleorder file
    plant_group_sequence = sio.loadmat(schedule_order_path)["scheduleorder"][0]

    # Load the partition_info from the groupinfo file
    partition_info = sio.loadmat(group_info_path)["groupinfo"]

    # Check if the length of both files matches
    if len(plant_group_map) != len(plant_group_sequence):
        raise ValueError(
            f"The length of '{prod_sys_map_path}' does not match the length of '{schedule_order_path}'."
        )

    # Create the ordered lists of node and plant group names based on the plant_group_sequence
    ordered_node_names = []
    ordered_plant_group_names = []
    for plant_group_id in plant_group_sequence:
        ordered_node_names.extend(plant_group_map[plant_group_id])
        ordered_plant_group_names.append(plant_group_id)

    # Determine the partition IDs (labels)
    plant_group_partitions = _assign_partition_ids(
        ordered_plant_group_names, partition_info
    )

    # Create the output directory if it doesn't exist
    generated_dir = _create_output_directory(output_dir)

    # Append extension to the stem path to create the filename
    output_file_nodes = generated_dir / f"{stem_path}.nodes.seq.csv"
    output_file_groups = generated_dir / f"{stem_path}.groups.nodes.seq.csv"

    # Write the ordered node names and their partition IDs (if they belong to a partition) to a CSV file
    # with the headers "name;labels"
    node_rows = []
    for plant_group_id in ordered_plant_group_names:
        partition_id = plant_group_partitions.get(plant_group_id, "")
        partition_label = f"partition{partition_id}" if partition_id else ""
        for node_name in plant_group_map[plant_group_id]:
            node_rows.append([node_name, partition_label])

    _write_csv_file(output_file_nodes, ["name", "labels"], node_rows, csv_delimiter)

    # Write the ordered plant group IDs and their partition IDs (if they belong to a partition) to a CSV file
    # with the headers "name;labels"
    group_rows = []
    for plant_group_id in ordered_plant_group_names:
        partition_id = plant_group_partitions.get(plant_group_id, "")
        partition_label = f"partition{partition_id}" if partition_id else ""
        group_rows.append([f"G{plant_group_id}", partition_label])

    _write_csv_file(output_file_groups, ["name", "labels"], group_rows, csv_delimiter)


def _assign_partition_ids(ordered_items, group_info):
    """
    Assigns a partition ID to each item in ordered_items that is part of a partition. Each partition represents
    a group of items that are processed together in one iteration loop.

    Args:
        ordered_items (list): A list of items ordered by the sequence in which they are processed.
        group_info (2D list): A list containing the starting indices and sizes of each partition.

    Returns:
        partition_assignments (dict): A dictionary mapping each item in a partition to its partition ID.
    """
    # Convert group_info into a list of (start, end, partition_id) tuples
    partitions = [
        (start - 1, start + size - 1, partition_id)
        for partition_id, (start, size) in enumerate(
            zip(group_info[0], group_info[1]), start=1
        )
    ]

    # Create a dictionary mapping each item to its partition ID
    partition_assignments = {
        item: partition_id
        for start, end, partition_id in partitions
        for item in ordered_items[start : end + 1]
    }

    return partition_assignments


def _write_csv_file(
    filename: Union[str, Path],
    headers: List[str],
    rows: List[List[str]],
    csv_delimiter: str = ";",
) -> None:
    """
    Writes data to a CSV file.

    Args:
        filename (Union[str, Path]): The path to the CSV file.
        headers (List[str]): The column headers for the CSV file.
        rows (List[List[str]]): The rows of data to write to the CSV file. Each inner list represents a row.
        csv_delimiter (str): The csv_delimiter used in the CSV file. Defaults to ';'.
    """
    with open(filename, mode="w", newline="") as f:
        writer = csv.writer(f, delimiter=csv_delimiter)
        if headers:
            writer.writerow(headers)
        writer.writerows(rows)


def _read_csv_file(
    filename: Union[str, Path], csv_delimiter: str = ";"
) -> List[Dict[str, str]]:
    """
    Reads data from a CSV file.

    Args:
        filename (Union[str, Path]): The path to the CSV file.
        csv_delimiter (str): The csv_delimiter used in the CSV file. Defaults to ';'.

    Returns:
        List[Dict[str, str]]: A list of dictionaries representing the rows in the CSV file. Each dictionary has keys
        corresponding to the column headers and values corresponding to the values in each column.
    """
    with open(filename, "r") as f:
        return list(csv.DictReader(f, delimiter=csv_delimiter))


def _create_output_directory(output_dir: Union[str, Path]) -> Path:
    """
    Creates the output directory if it doesn't exist.

    Args:
        output_dir (Union[str, Path]): The path to the directory.

    Returns:
        Path: The path to the directory.
    """
    generated_dir = Path(output_dir)
    generated_dir.mkdir(exist_ok=True)
    return generated_dir


def _build_plant_group_map(plant_group_lines: List[str]) -> Dict[int, List[str]]:
    plant_group_map = {}
    for line in plant_group_lines:
        plant_group_data = line.strip().split(",")
        plant_group_id = int(plant_group_data[0][1:])
        plant_elements = [elem.strip() for elem in plant_group_data[1:]]
        plant_group_map[plant_group_id] = plant_elements
    return plant_group_map
