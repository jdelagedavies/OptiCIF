"""
This module provides functionality for global optimization on CIF specifications.
"""

import csv
from pathlib import Path
from typing import Union

from opticif.validator import validate_csv_structure


def do_global_optimization(
    csv_path: Union[str, Path],
    cif_path: Union[str, Path],
    output_dir: Union[str, Path] = "generated",
    csv_delimiter: str = ";",
) -> None:
    """
    Performs global optimization on a CIF specification by reordering plant instantiations according to an input
    sequence. Reordered instantiations are placed at the end of the output file, preserving multiline instantiations.
    Note that this code assumes that indented lines are part of the previous instantiation, and instantiations are
    not nested.

    Args:
        csv_path (Union[str, Path]): The path to a CSV file containing the node sequence. The file should have a
                        header with a "name" column containing the nodes to be reordered.
        cif_path (Union[str, Path]): The path to the CIF specification containing the plant instantiations to be
                        reordered. Multiline instantiations are supported.
        output_dir (Union[str, Path]): The path to the directory where the output files will be saved.
                        Defaults to "generated".
        csv_delimiter (str): The delimiter used in the CSV file. Defaults to ";".

    Returns:
        None. The reordered CIF file is saved with ".seq" appended to the input file's name in the specified
        output directory.
    """
    # Convert inputs to Path objects
    csv_path = Path(csv_path)
    cif_path = Path(cif_path)

    # Validate the CSV file structure
    validate_csv_structure(csv_path, csv_delimiter)

    # Read the CSV file and get the sequence
    with open(csv_path, "r") as f:
        node_sequence = [
            row["name"] for row in csv.DictReader(f, delimiter=csv_delimiter)
        ]

    # Read the CIF file
    with open(cif_path, "r") as f:
        cif_lines = f.readlines()

    # Create a dictionary mapping the target lines to their contents and catch duplicates
    instantiations_dict = {}
    non_instantiation_lines = []
    duplicates = set()
    current_item = None
    current_item_lines = []

    for line in cif_lines:
        stripped_line = line.strip()

        node_name = next(
            (
                name
                for name in node_sequence
                if line.startswith(name + ":") or line.startswith(name + " :")
            ),
            None,
        )

        if node_name is not None:
            # Found a new instantiation, save the previous one if any
            if current_item is not None:
                instantiations_dict[current_item] = current_item_lines

            # Start a new instantiation
            current_item = node_name
            current_item_lines = [line]

            if node_name in instantiations_dict:
                duplicates.add(node_name)
        else:
            if current_item is not None and stripped_line and line.startswith(" "):
                # Continue the current instantiation
                current_item_lines.append(line)
            else:
                if current_item is not None:
                    # Save the current instantiation before moving to a non-instantiation line
                    instantiations_dict[current_item] = current_item_lines
                    current_item = None
                    current_item_lines = []

                non_instantiation_lines.append(line)

    # Save the last instantiation if any
    if current_item is not None:
        instantiations_dict[current_item] = current_item_lines

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
