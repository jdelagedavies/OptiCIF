from opticif import plant_groups_to_csv

# Define input files and directories
input_dir = "../models/swalmen_tunnel"
test_prod_sys_map = f"{input_dir}/swalmen_tunnel.prodsysmap.txt"
test_schedule_order = f"{input_dir}/swalmen_tunnel.scheduleorder.mat"
test_group_info = f"{input_dir}/swalmen_tunnel.groupinfo.mat"

# Define output files and directories
output_dir = f"{input_dir}/generated"
output_csv_stem_path = "swalmen_tunnel"

# Convert
plant_groups_to_csv(
    test_prod_sys_map,
    test_schedule_order,
    test_group_info,
    output_csv_stem_path,
    output_dir,
)
