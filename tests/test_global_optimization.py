"""This script demonstrates how to use the opticif package to perform global optimization on a CIF specification.

1. Loads the sequenced node names from a CSV file.
2. Reads the original CIF specification containing the plant instantiations.
3. Performs global optimization by reordering plant instantiations according to the sequenced node names.
4. Writes the reordered instantiations to a new CIF file.

To customize the script for your own system, modify the file paths, directories, and adjust the
parameters as needed."""
from opticif import do_global_optimization

# Define input files and directories
input_dir = "./models/simple_lock"
test_cif_path = f"{input_dir}/simple_lock.plants_and_requirements.cif"
test_sequenced_nodes = f"{input_dir}/generated/genetic.nodes.seq.csv"

# Define output files and directories
output_dir = "./models/simple_lock/generated"

# Define parameters
csv_delimiter = ";"

# Perform global optimization
print("Optimizing: Performing global optimization...")
do_global_optimization(test_sequenced_nodes, test_cif_path, output_dir, csv_delimiter)
print("Optimization complete.")
