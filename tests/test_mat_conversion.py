from opticif import mat_to_csv

# Define input files and directories
input_dir = "./models/swalmen_tunnel"
test_matrix = f"{input_dir}/DSM_Swalmen_Unsequenced.csv"
test_nodes = f"{input_dir}/swalmen_tunnel.nodes.csv"

# Define output files and directories
output_dir = f"{input_dir}/generated"
output_csv_stem_path = "swalmen_tunnel"

# Define parameters
delimiter = ";"

# Convert binary matrix in CSV format to edge list in CSV format
mat_to_csv(test_matrix, test_nodes, output_csv_stem_path, output_dir, delimiter)
