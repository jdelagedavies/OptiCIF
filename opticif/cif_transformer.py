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
    csv_delimiter: str = ";",
) -> None:
    """
    Performs global optimization on a CIF specification by reordering plant instantiations according to an input
    sequence. Reordered instantiations are placed at the end of the output file.

    Args:
        csv_path (Union[str, Path]): The path to a CSV file containing the node sequence. The file should have a
                        header with a "name" column containing the nodes to be reordered.
        cif_path (Union[str, Path]): The path to the CIF specification containing the plant instantiations to be
                        reordered.
        csv_delimiter (str): The delimiter used in the CSV file. Defaults to ";".

    Returns:
        None. The reordered CIF file is saved with ".seq" appended to the input file's name.
    """
    # Convert inputs to Path objects
    csv_path = Path(csv_path)
    cif_path = Path(cif_path)

    # Validate the CSV file structure
    validate_csv_structure(csv_path, csv_delimiter)

    # Read the CSV file and get the sequence
    with open(csv_path, "r") as f:
        seq = [row["name"] for row in csv.DictReader(f, delimiter=csv_delimiter)]

    # Read the CIF file
    with open(cif_path, "r") as f:
        cif_lines = f.readlines()

    # Create a dictionary mapping the target lines to their contents and catch duplicates
    line_dict = {}
    unmatched_lines = []
    duplicates = set()
    for line in cif_lines:
        item = next(
            (
                item
                for item in seq
                if line.startswith(item + ":") or line.startswith(item + " :")
            ),
            None,
        )
        if item is not None:
            if item in line_dict:
                duplicates.add(item)
            else:
                line_dict[item] = line
        else:
            unmatched_lines.append(line)

    if duplicates:
        raise ValueError(
            f"Duplicate instantiations found for nodes: {', '.join(sorted(duplicates))}"
        )

    # Reorder the target lines according to the sequence
    missing_nodes = set(seq) - set(line_dict.keys())
    if missing_nodes:
        raise KeyError(
            f"Nodes not found in the CIF specification '{cif_path}': {', '.join(sorted(missing_nodes))}"
        )

    reordered_lines = [line_dict[item] for item in seq]

    # Check if the last line in unmatched_lines is empty
    if unmatched_lines and not unmatched_lines[-1].rstrip():
        # The last line is already an empty line
        pass
    else:
        # Add an empty padding line
        unmatched_lines.append("\n")

    # Combine unmatched lines with reordered lines and add a marker
    output_lines = (
        unmatched_lines + ["// Reordered plant instantiations\n"] + reordered_lines
    )

    # Create the 'generated' directory if it doesn't exist
    generated_dir = Path("generated")
    generated_dir.mkdir(exist_ok=True)

    # Write the output lines to the output file
    output_file = generated_dir / f"{cif_path.stem}.seq.cif"

    with open(output_file, "w") as f:
        f.writelines(output_lines)
