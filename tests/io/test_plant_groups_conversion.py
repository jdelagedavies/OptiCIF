from opticif import plant_groups_to_csv

# Define input files and directories
input_dir = "../models/swalmen_tunnel"
test_group_map = f"{input_dir}/swalmen_tunnel.prodsysmap.txt"
test_group_seq = f"{input_dir}/swalmen_tunnel.scheduleorder.mat"

# Define output files and directories
output_dir = f"{input_dir}/generated"
output_csv_stem_path = "swalmen_tunnel"

# Convert sequence of plant groups to plant elements list in CSV format
plant_groups_to_csv(test_group_map, test_group_seq, output_csv_stem_path, output_dir)
