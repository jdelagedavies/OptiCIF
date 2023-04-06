"""
OptiCIF: A package for global optimization of CIF specifications in Python.

OptiCIF provides tools to perform global optimization on CIF specifications
by reordering plant instantiations according to a specified sequence.
It includes a CIF transformer, a CSV validator, and a CSV converter.
"""

from opticif.cif_transformer import do_global_optimization
from opticif.validator import validate_csv_structure
from opticif.csv_converter import write_to_csv
