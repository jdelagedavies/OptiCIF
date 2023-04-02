"""
This module contains the CSV converter used to translate a list of RaGraph Node objects to a CSV list.
"""

import csv
from pathlib import Path

from ragraph.graph import Node


def write_to_csv(nodes: list[Node], stem_path: str, csv_delimiter: str = ";") -> None:
    """
    Write a list of node names to a CSV file with the given stem path. The node objects are from the RaGraph package.

    Args:
        nodes (list): A list of RaGraph Node objects. Each node object must have a 'name' attribute
            that is a string.
        stem_path (str): The stem path for the CSV file, without the '.csv' extension.
        csv_delimiter (str): The delimiter used in the CSV file. Defaults to ";".

    Returns:
        None. The CSV file is saved with "_nodes.csv" appended to the stem path in the "generated" directory.
    """
    # Extracting only the names of each node using list comprehension
    node_names = [node.name for node in nodes]

    # Create the 'generated' directory if it doesn't exist
    generated_dir = Path("generated")
    generated_dir.mkdir(exist_ok=True)

    # Append "_nodes.csv" to the stem path to create the filename
    filename = generated_dir / f"{stem_path}_nodes.csv"

    # Writing the node names to a CSV file
    with open(filename, mode="w", newline="") as file:
        writer = csv.writer(file, delimiter=csv_delimiter)
        writer.writerow(["name"])
        for name in node_names:
            writer.writerow([name])

    print(f"Node names written to CSV file {filename}")
