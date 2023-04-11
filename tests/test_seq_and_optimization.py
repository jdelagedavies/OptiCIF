"""
This script demonstrates how to use the ragraph and opticif packages to analyze
and optimize CIF models. The script follows these steps:

1. Loads nodes and edges from CSV files.
2. Computes and prints initial metrics (feedback distance, feedback marks, and cycles).
3. Creates a design structure matrix (DSM) and saves it as an SVG image.
4. Performs a genetic algorithm-based sequencing to optimize the system.
5. Computes and prints metrics for the sequenced system.
6. Creates a sequenced DSM and saves it as an SVG image.
7. Writes the new sequence to a CSV file.
8. Performs global optimization using the opticif package.

To customize the script for your own system, modify the input file paths and adjust
the parameters as needed.
"""
from pathlib import Path

from ragraph import plot
from ragraph.analysis.heuristics import johnson
from ragraph.analysis.sequence._genetic import genetic
from ragraph.analysis.sequence.metrics import feedback_distance, feedback_marks
from ragraph.io.csv import from_csv

from opticif import write_to_csv, do_global_optimization

# Define input files and output directory
input_dir = "./models/simple_lock"
output_dir = "./models/simple_lock/generated"

test_nodes = f"{input_dir}/simple_lock.nodes.csv"  # Requires at least a name column
test_edges = f"{input_dir}/simple_lock.edges.csv"  # Requires at least a source and target column
test_cif_path = f"{input_dir}/simple_lock.plants_and_requirements.cif"

# Define parameters
n_chromosomes = 1000
n_generations = 10000
evaluator = "feedback_distance"
csv_delimiter = ";"

# Create graph object from nodes and edges
print("Initializing: Loading nodes and edges from CSV files...")
g = from_csv(test_nodes, test_edges)

# Compute penalty scores and contribution of each cell in the matrix to the penalty scores
score_dist, contrib_dist = feedback_distance(g.get_adjacency_matrix())
score_marks, contrib_marks = feedback_marks(g.get_adjacency_matrix())

# Detect cycles
cycles = list(johnson(g, names=True))
n_cycles = len(cycles)
print(
    f"Initialization complete.\n"
    f"Initial feedback distance: {score_dist}\n"
    f"Initial feedback marks: {score_marks}\n"
    f"Initial contribution to feedback distance:\n{contrib_dist}\n"
    f"Initial contribution to feedback marks:\n{contrib_marks}\n"
    f"Initial number of cycles: {n_cycles}\n"
    f"Initial cycles: {cycles}\n"
)

# Create the 'generated' directory if it doesn't exist
generated_dir = Path(output_dir)
generated_dir.mkdir(exist_ok=True)

# Plot DSM
fig = plot.dsm(
    leafs=g.leafs,
    edges=g.edges,
)
fig.write_image(f"{generated_dir}/dsm.svg")

# Sequence using genetic algorithm
print("Sequencing: Running genetic sequencing algorithm...")
g, seq = genetic(g, n_chromosomes=1000, n_generations=10000, evaluator=evaluator)

# Compute penalty scores and contribution of each cell in the matrix to the penalty scores
score_dist_seq, contrib_dist_seq = feedback_distance(g.get_adjacency_matrix(nodes=seq))
score_marks_seq, contrib_marks_seq = feedback_marks(g.get_adjacency_matrix(nodes=seq))

# Detect cycles
cycles_seq = list(johnson(g, names=True, nodes=seq))
n_cycles_seq = len(cycles_seq)
print(
    f"Sequencing complete.\n"
    f"Sequenced feedback distance: {score_dist_seq:.2f}\n"
    f"Sequenced feedback marks: {score_marks_seq}\n"
    f"Sequenced contribution to feedback distance:\n{contrib_dist_seq}\n"
    f"Sequenced contribution to feedback marks:\n{contrib_marks_seq}\n"
    f"Sequenced number of cycles: {n_cycles_seq}\n"
    f"Sequenced cycles: {cycles_seq}\n"
)

# Plot sequenced DSM
fig = plot.dsm(
    leafs=seq,
    edges=g.edges,
)
fig.write_image(f"{generated_dir}/dsm_sequenced.svg")

# Write new sequence to CSV
write_to_csv(seq, "output", output_dir, csv_delimiter)

# Perform global optimization
print("Optimizing: Performing global optimization...")
do_global_optimization(
    f"{generated_dir}/output.nodes.seq.csv", test_cif_path, output_dir, csv_delimiter
)
print("Optimization complete.")
