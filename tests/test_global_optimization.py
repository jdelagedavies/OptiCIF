"""This script demonstrates how to use the opticif package to perform global optimization on a CIF specification.

1. Loads the sequenced node names from a CSV file.
2. Reads the original CIF specification containing the plant instantiations.
3. Performs global optimization by reordering plant instantiations according to the sequenced node names.
4. Writes the reordered instantiations to a new CIF file.

To customize the script for your own system, modify the file paths, directories, and adjust the
parameters as needed."""
import time

from opticif import do_global_optimization

# Define input files and directories
input_dir = "models/simple_lock"
test_cif_path = f"{input_dir}/simple_lock.plants_and_requirements.cif"
test_sequenced_nodes = f"{input_dir}/generated/simple_lock.nodes.seq.csv"

# Define output files and directories
output_dir = f"{input_dir}/generated"

# Define parameters
csv_delimiter = ";"

# Perform global optimization
print("Optimizing: Performing global optimization...")
start_time = time.time()
do_global_optimization(test_sequenced_nodes, test_cif_path, output_dir, csv_delimiter)
end_time = time.time()

time_elapsed_ms = (end_time - start_time) * 1000
print(f"Optimization complete. Execution time: {time_elapsed_ms:.2f} milliseconds.")
