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
    mat_data = sio.loadmat(matrix_path)
    matrix = mat_data[list(mat_data.keys())[-1]]

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
    prod_sys_map_path: Union[str, Path],
    schedule_order_path: Union[str, Path],
    group_info_path: Union[str, Path],
    stem_path: str,
    output_dir: Union[str, Path] = "generated",
    csv_delimiter: str = ";",
) -> None:
    """
    Reads plant group information from a product system map, a schedule order, and a partition information output by
    the MATLAB sequencing script from De Jong (2019), and generates two CSV files: one containing the ordered list of
    node names based on the plant group sequence, and another containing the ordered list of plant group IDs. It also
    appends a "kind" column to both the ordered node and plant groups files with the iteration block they are part of
    (Delage-Davies, 2023).

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
                                       Defaults to "generated".
        csv_delimiter (str): The csv_delimiter used in the CSV files. Defaults to ";".

    Returns: None. The ordered node names and plant group IDs are saved to two separate CSV files in the specified
             output directory. The output files' names are created by appending ".nodes.seq.csv" and
             ".groups.nodes.seq.csv" to the stem_path.
    """
    # Read the plant group information from the file
    with open(prod_sys_map_path, "r") as f:
        plant_group_lines = f.readlines()

    # Process the plant group information to create a dictionary mapping plant group IDs to plant elements
    plant_group_map = {}
    for line in plant_group_lines:
        plant_group_data = line.strip().split(",")
        plant_group_id = int(plant_group_data[0][1:])
        plant_elements = [elem.strip() for elem in plant_group_data[1:]]
        plant_group_map[plant_group_id] = plant_elements

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

    # Determine the iteration groups (kinds)
    plant_group_blocks = _determine_iteration_blocks(
        ordered_plant_group_names, partition_info
    )

    # Create the output directory if it doesn't exist
    generated_dir = Path(output_dir)
    generated_dir.mkdir(exist_ok=True)

    # Append extension to the stem path to create the filename
    output_file_nodes = generated_dir / f"{stem_path}.nodes.seq.csv"
    output_file_groups = generated_dir / f"{stem_path}.groups.nodes.seq.csv"

    # Write the ordered node names and their iteration blocks to a CSV file with the headers "name;kind"
    with open(output_file_nodes, "w") as f:
        writer = csv.writer(f, delimiter=csv_delimiter)
        writer.writerow(["name", "kind"])
        for plant_group_id in ordered_plant_group_names:
            block_id = plant_group_blocks[plant_group_id]
            for node_name in plant_group_map[plant_group_id]:
                writer.writerow([node_name, f"B{block_id}"])

    # Write the ordered plant group IDs and their iteration blocks to a CSV file with the headers "name;kind"
    with open(output_file_groups, "w") as f:
        writer = csv.writer(f, delimiter=csv_delimiter)
        writer.writerow(["name", "kind"])
        for plant_group_id, block_id in plant_group_blocks.items():
            writer.writerow([f"G{plant_group_id}", f"B{block_id}"])


def _determine_iteration_blocks(ordered_items, group_info):
    """
    Assigns a block ID (node "kind" attribute) to each item in ordered_items, where each block represents a group
    of items that are processed together in one iteration. Each partition represents a block, and items in the spaces
    between partitions form blocks.

    Args:
        ordered_items (list): A list of items ordered by the sequence in which they are processed.
        group_info (2D list): A list containing the starting indices and sizes of each partition.

    Returns:
        block_assignments (dict): A dictionary mapping each item in ordered_items to its block ID.
    """
    # Convert group_info into a list of (start, end) tuples
    partitions = [
        (start - 1, start + size - 1)
        for start, size in zip(group_info[0], group_info[1])
    ]

    # Sort the partitions by their starting index
    partitions.sort()

    block_assignments = {}
    current_block = 0
    partition_end = -1

    for i, item in enumerate(ordered_items):
        # Start a new block at the beginning of the sequence, after the end of each partition,
        # and at the start of each new partition
        if i == 0 or i == partition_end + 1 or (partitions and i == partitions[0][0]):
            current_block += 1
            if partitions and i == partitions[0][0]:  # We've reached a new partition
                partition_end = partitions[0][1]
                partitions.pop(0)
            else:  # We've moved past the current partition
                partition_end = -1  # Reset partition_end

        block_assignments[item] = current_block

    return block_assignments
