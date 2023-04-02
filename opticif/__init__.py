"""
OptiCIF: A package for global optimization of CIF specifications in Python.

OptiCIF provides tools to perform global optimization on CIF specifications
by reordering plant instantiations according to a specified sequence.
It includes a CIF transformer, a CSV validator, and a CSV converter.
"""

from .cif_transformer import do_global_optimization
from .validator import validate_csv_structure
from .csv_converter import write_to_csv
