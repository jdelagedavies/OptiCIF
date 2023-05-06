"""This module provides functionality for global optimization on CIF specifications."""

import csv
import re
from pathlib import Path
from typing import Union

from opticif._validators import validate_node_csv_structure


def do_global_optimization(
    csv_path: Union[str, Path],
    cif_path: Union[str, Path],
    output_dir: Union[str, Path] = "generated",
    csv_delimiter: str = ";",
    mode: str = "automaton",
) -> None:
    """
    Performs global optimization on a CIF specification by reordering explicit plant automaton declarations or plant
    instantiations or  according to an input sequence. Reordered items are placed at the end of the output file,
    preserving multiline automaton declarations or instantiations.

    Args:
        csv_path (Union[str, Path]): The path to a CSV file containing the node sequence. The file should have a
                        header with a "name" column containing the nodes to be reordered.
        cif_path (Union[str, Path]): The path to the CIF specification containing the plant instantiations or explicit
                        plant automaton declarations to be reordered. Multiline items are supported.
        output_dir (Union[str, Path]): The path to the directory where the output files will be saved.
                        Defaults to "generated".
        csv_delimiter (str): The csv_delimiter used in the CSV file. Defaults to ";".
        mode (str): The optimization mode, either "instantiation" or "automaton". Defaults to "automaton".
            - "automaton": Reorder explicit plant automaton declarations (e.g., "plant automaton Node1: ... end").
            - "instantiation": Reorder plant instantiations (e.g., "Node1: Plant;").

    Returns:
        None. The reordered CIF file is saved with ".seq" appended to the input file's name in the specified
        output directory.
    """
    if mode not in ["automaton", "instantiation"]:
        raise ValueError(
            "Invalid mode specified. Choose either 'automaton' or 'instantiation'"
        )

    # Convert to Path object
    output_dir = Path(output_dir)
    cif_path = Path(cif_path)

    # Validate the CSV file structure
    validate_node_csv_structure(csv_path, csv_delimiter)

    # Read the CSV file and get the sequence
    with open(csv_path, "r") as f:
        csv_reader = csv.DictReader(f, delimiter=csv_delimiter)
        node_sequence = [row["name"] for row in csv_reader]

    # Prepare a regex pattern for matching node names
    pattern = ""
    if mode == "automaton":
        pattern = (
            r"^\s*plant\s+automaton\s+("
            + "|".join(re.escape(name) for name in node_sequence)
            + r")\s*:"
        )
    elif mode == "instantiation":
        pattern = (
            r"^\s*(" + "|".join(re.escape(name) for name in node_sequence) + r")\s*:"
        )

    node_name_pattern = re.compile(pattern)

    # Read the CIF file
    with open(cif_path, "r") as f:
        cif_lines = f.readlines()

    # Create a dictionary mapping the target lines to their contents and catch duplicates
    items_dict = {}
    non_item_lines = []
    duplicates = set()

    capturing_item = False
    node_name = None
    current_item_lines = []

    for line in cif_lines:
        if not line.strip() or line.strip().startswith(
            "//"
        ):  # Skip empty lines and comments
            continue

        if not capturing_item:
            match = node_name_pattern.match(line)
            if match:
                node_name = match.group(1)
                capturing_item = True
                current_item_lines = [line]

                if node_name in items_dict:
                    duplicates.add(node_name)
            else:
                non_item_lines.append(line)
        else:
            current_item_lines.append(line)

        closing_condition = (
            capturing_item and ";" in line
            if mode == "instantiation"
            else capturing_item and line.strip().split()[-1] == "end"
        )
        if closing_condition:
            items_dict[node_name] = current_item_lines
            capturing_item = False

    if capturing_item:
        raise ValueError(f"Unclosed {mode} detected")

    if duplicates:
        raise ValueError(
            f"Duplicate {mode}s found for nodes: {', '.join(sorted(duplicates))}"
        )

    # Reorder the target lines according to the sequence
    missing_nodes = set(node_sequence) - set(items_dict.keys())
    if missing_nodes:
        raise KeyError(
            f"Nodes not found in the CIF specification '{cif_path}': {', '.join(sorted(missing_nodes))}"
        )

    output_lines = non_item_lines
    for node_name in node_sequence:
        output_lines += items_dict[node_name]

    # Create the 'generated' directory if it doesn't exist
    generated_dir = Path(output_dir)
    generated_dir.mkdir(exist_ok=True)

    # Write the output lines to the output file
    output_file = generated_dir / f"{cif_path.stem}.seq.cif"

    with open(output_file, "w") as f:
        f.writelines(output_lines)
