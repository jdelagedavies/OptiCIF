import time
from pathlib import Path

from ragraph import plot
from ragraph.analysis.sequence import markov
from ragraph.analysis.sequence.metrics import feedback_distance, feedback_marks
from ragraph.io.csv import from_csv

from opticif import node_to_csv

# Define input files and directories
input_dir = "./models/swalmen_tunnel"
test_nodes = (
    f"{input_dir}/generated/markov.nodes.seq.csv"  # Requires at least a name column
)
test_edges = f"{input_dir}/generated/swalmen_tunnel.edges.csv"  # Requires at least a source and target column

# Define output files and directories
output_dir = "./models/swalmen_tunnel/generated"
output_csv_stem_path = "markov"  # Stem path of the CSV list of sequenced node names
output_sequenced_dsm_name = "dsm_markov"

# Define parameters
inf = 0  # Weight of relative node influence when sorting
dep = 10  # Weight of relative node dependency when sorting
csv_delimiter = ";"

# Create graph object from nodes and edges
print("Initializing: Loading nodes and edges from CSV files...")
g = from_csv(test_nodes, test_edges)

# Compute penalty scores and contribution of each cell in the matrix to the penalty scores
score_dist, contrib_dist = feedback_distance(g.get_adjacency_matrix())
score_marks, contrib_marks = feedback_marks(g.get_adjacency_matrix())
print(
    f"Initialization complete.\n"
    f"Initial feedback distance: {score_dist}\n"
    f"Initial feedback marks: {score_marks}\n"
    f"Initial contribution to feedback distance:\n{contrib_dist}\n"
    f"Initial contribution to feedback marks:\n{contrib_marks}\n"
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
print("Sequencing: Running Markov sequencing algorithm...")
start_time = time.time()
g, seq = markov(g, inf=inf, dep=dep)
end_time = time.time()

time_elapsed = end_time - start_time

# Compute penalty scores and contribution of each cell in the matrix to the penalty scores
score_dist_seq, contrib_dist_seq = feedback_distance(g.get_adjacency_matrix(nodes=seq))
score_marks_seq, contrib_marks_seq = feedback_marks(g.get_adjacency_matrix(nodes=seq))
print(
    f"Sequencing complete. Execution time: {time_elapsed:.2f} seconds.\n"
    f"Sequenced feedback distance: {score_dist_seq:.2f}\n"
    f"Sequenced feedback marks: {score_marks_seq}\n"
    f"Sequenced contribution to feedback distance:\n{contrib_dist_seq}\n"
    f"Sequenced contribution to feedback marks:\n{contrib_marks_seq}\n"
)

# Plot sequenced DSM
fig = plot.dsm(
    leafs=seq,
    edges=g.edges,
)
fig.write_image(f"{generated_dir}/{output_sequenced_dsm_name}.seq.svg")

# Write new sequence to CSV
node_to_csv(seq, output_csv_stem_path, output_dir, csv_delimiter)
