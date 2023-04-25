from opticif import mat_to_csv

# Define input files and directories
input_dir = "../models/simple_lock"
test_matrix = f"{input_dir}/simple_lock_DSM.csv"
test_nodes = f"{input_dir}/simple_lock.nodes.csv"

# Define output files and directories
output_dir = f"{input_dir}/generated"
output_csv_stem_path = "simple_lock"

# Define parameters
delimiter = ";"

# Convert binary matrix in CSV format to edge list in CSV format
mat_to_csv(test_matrix, test_nodes, output_csv_stem_path, output_dir, delimiter)
