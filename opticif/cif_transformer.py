"""This module provides functionality for global optimization on CIF specifications."""

import csv
import re
from pathlib import Path
from typing import Union
from collections import defaultdict

from opticif._validators import validate_node_csv_structure


def do_global_optimization(
    csv_path: Union[str, Path],
    cif_path: Union[str, Path],
    output_dir: Union[str, Path] = "generated",
    csv_delimiter: str = ";",
) -> None:
    """
    Performs global optimization on a CIF specification by reordering explicit plant automaton declarations according
    to an input sequence. Reordered items are grouped by their kind if a kind column exists in the CSV. Reordered items
    are placed at the end of the output file.

    Args:
        csv_path (Union[str, Path]): The path to a CSV file containing the node sequence. The file should have a
                        header with a "name" column containing the nodes to be reordered. Optionally, it may also have
                        a "kind" column to group reordered nodes by plant groups.
        cif_path (Union[str, Path]): The path to the CIF specification containing the explicit
                        plant automaton declarations to be reordered.
        output_dir (Union[str, Path]): The path to the directory where the output files will be saved.
                        Defaults to "generated".
        csv_delimiter (str): The csv_delimiter used in the CSV file. Defaults to ";".

    Returns:
        None. The reordered CIF file is saved with ".seq" appended to the input file's name in the specified
        output directory.
    """
    # Convert to Path object
    output_dir = Path(output_dir)
    cif_path = Path(cif_path)

    # Validate the CSV file structure
    validate_node_csv_structure(csv_path, csv_delimiter)

    # Read the CSV file and get the sequence and kinds
    with open(csv_path, "r") as f:
        csv_reader = csv.DictReader(f, delimiter=csv_delimiter)
        has_kind_column = "kind" in csv_reader.fieldnames
        node_sequence = []
        kind_sequence = [] if has_kind_column else None
        for row in csv_reader:
            node_sequence.append(row["name"])
            if has_kind_column:
                kind_sequence.append(row["kind"])

    # Prepare a regex pattern for matching node names
    pattern = (
            r"^\s*plant\s+automaton\s+("
            + "|".join(re.escape(name) for name in node_sequence)
            + r")\s*:"
        )
    node_name_pattern = re.compile(pattern)

    # Read the CIF file
    with open(cif_path, "r") as f:
        cif_lines = f.readlines()

    # Initialize dictionaries and sets for tracking lines and duplicates
    items_dict = {}
    non_item_lines = []
    duplicates = set()

    # Initialize variables for capturing multiline items
    capturing_item = False
    node_name = None
    current_item_lines = []

    # Iterate through CIF lines, separating target lines and non-target lines
    for line in cif_lines:
        # Skip empty lines and comments
        if not line.strip() or line.strip().startswith("//"):
            continue

        # If not capturing an item, check if the line starts a new item
        if not capturing_item:
            match = node_name_pattern.match(line)
            if match:
                node_name = match.group(1)
                capturing_item = True
                current_item_lines = [line]

                # Check for duplicates
                if node_name in items_dict:
                    duplicates.add(node_name)
            else:
                non_item_lines.append(line)
        # If capturing an item, append the line to the current item lines
        else:
            current_item_lines.append(line)

        # If item ends, store the captured lines and reset capturing state
        if capturing_item and line.strip().split()[-1] == "end":
            items_dict[node_name] = current_item_lines
            capturing_item = False

    # Check for unclosed items or duplicates and raise appropriate exceptions
    if capturing_item:
        raise SyntaxError(f"Unclosed automaton detected")

    if duplicates:
        raise ValueError(
            f"Duplicate automatons found for nodes: {', '.join(sorted(duplicates))}"
        )

    # Reorder the target lines according to the sequence
    missing_nodes = set(node_sequence) - set(items_dict.keys())
    if missing_nodes:
        raise KeyError(
            f"Nodes not found in the CIF specification '{cif_path}': {', '.join(sorted(missing_nodes))}"
        )

    output_lines = non_item_lines
    if has_kind_column:
        kind_grouped_lines = defaultdict(list)
        for node_name, kind in zip(node_sequence, kind_sequence):
            kind_grouped_lines[kind].extend(items_dict[node_name])

        for kind, lines in kind_grouped_lines.items():
            output_lines.append(f"group {kind}:\n")
            output_lines.extend(["    " + line for line in lines])
            output_lines.append("end\n")
    else:
        for node_name in node_sequence:
            output_lines += items_dict[node_name]

    # Create the output directory if it doesn't exist
    generated_dir = Path(output_dir)
    generated_dir.mkdir(exist_ok=True)

    # Write the output lines to the output file
    output_file = generated_dir / f"{cif_path.stem}.seq.cif"

    with open(output_file, "w") as f:
        f.writelines(output_lines)
