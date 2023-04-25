"""
This module provides functionality for global optimization on CIF specifications.
"""

import csv
import re
from pathlib import Path
from typing import Union

from opticif.validators import validate_node_csv_structure


def do_global_optimization(
    csv_path: Union[str, Path],
    cif_path: Union[str, Path],
    output_dir: Union[str, Path] = "generated",
    csv_delimiter: str = ";",
) -> None:
    """
    Performs global optimization on a CIF specification by reordering plant instantiations according to an input
    sequence. Reordered instantiations are placed at the end of the output file, preserving multiline instantiations.

    Args:
        csv_path (Union[str, Path]): The path to a CSV file containing the node sequence. The file should have a
                        header with a "name" column containing the nodes to be reordered.
        cif_path (Union[str, Path]): The path to the CIF specification containing the plant instantiations to be
                        reordered. Multiline instantiations are supported.
        output_dir (Union[str, Path]): The path to the directory where the output files will be saved.
                        Defaults to "generated".
        csv_delimiter (str): The csv_delimiter used in the CSV file. Defaults to ";".

    Returns:
        None. The reordered CIF file is saved with ".seq" appended to the input file's name in the specified
        output directory.
    """
    # Convert output_dir to Path object
    output_dir = Path(output_dir)

    # Validate the CSV file structure
    validate_node_csv_structure(csv_path, csv_delimiter)

    # Read the CSV file and get the sequence
    with open(csv_path, "r") as f:
        node_sequence = [
            row["name"] for row in csv.DictReader(f, delimiter=csv_delimiter)
        ]

    # Prepare a regex pattern for matching node names
    node_name_pattern = re.compile(
        r"^\s*(" + "|".join(re.escape(name) for name in node_sequence) + r")\s*:"
    )

    # Read the CIF file
    with open(cif_path, "r") as f:
        cif_lines = f.readlines()

    # Create a dictionary mapping the target lines to their contents and catch duplicates
    instantiations_dict = {}
    non_instantiation_lines = []
    duplicates = set()

    capturing_instantiation = False
    current_item = None
    current_item_lines = []

    for line in cif_lines:
        if not line.strip():  # Skip empty lines
            continue

        if not capturing_instantiation:
            match = node_name_pattern.match(line)
            if match:
                node_name = match.group(1)
                capturing_instantiation = True
                current_item = node_name
                current_item_lines = [line]

                if node_name in instantiations_dict:
                    duplicates.add(node_name)
            else:
                non_instantiation_lines.append(line)
        else:
            if line.strip():  # Skip empty lines
                current_item_lines.append(line)

        if capturing_instantiation and ";" in line:
            instantiations_dict[current_item] = current_item_lines
            capturing_instantiation = False

    # Store the last instantiation if any
    if capturing_instantiation:
        instantiations_dict[current_item] = current_item_lines

    if capturing_instantiation:
        raise ValueError("Unclosed instantiation detected")

    if duplicates:
        raise ValueError(
            f"Duplicate instantiations found for nodes: {', '.join(sorted(duplicates))}"
        )

    # Reorder the target lines according to the sequence
    missing_nodes = set(node_sequence) - set(instantiations_dict.keys())
    if missing_nodes:
        raise KeyError(
            f"Nodes not found in the CIF specification '{cif_path}': {', '.join(sorted(missing_nodes))}"
        )

    reordered_lines = [
        line for node_name in node_sequence for line in instantiations_dict[node_name]
    ]

    # Check if the last line in non_instantiation_lines is empty
    if non_instantiation_lines and not non_instantiation_lines[-1].rstrip():
        # The last line is already an empty line
        pass
    else:
        # Add an empty padding line
        non_instantiation_lines.append("\n")

    # Combine unmatched lines with reordered lines and add a marker
    output_lines = (
        non_instantiation_lines
        + ["// Reordered plant instantiations\n"]
        + reordered_lines
    )

    # Create the 'generated' directory if it doesn't exist
    generated_dir = Path(output_dir)
    generated_dir.mkdir(exist_ok=True)

    # Write the output lines to the output file
    output_file = generated_dir / f"{cif_path.stem}.seq.cif"

    with open(output_file, "w") as f:
        f.writelines(output_lines)
