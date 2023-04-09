# OptiCIF

OptiCIF is a Python package for performing global optimization on CIF specifications by reordering plant instantiations
according to a provided input sequence. Global optimization is formally defined in
Reijnen, [2020](https://www.persistent-identifier.nl/urn:nbn:nl:ui:25-115168de-878f-4f5f-9c55-126f20f845fe). It
integrates in the
[synthesis-based engineering](https://www.eclipse.org/escet/cif/synthesis-based-engineering/approaches/synthesis-based-engineering.html)
development process. This package was developed as part of a bachelor thesis

## Installation

To use OptiCIF, clone the repository:

```bash
git clone https://github.com/jdelagedavies/opticif.git
```

The project is managed using Poetry. Ensure that you have Poetry installed and then install the dependencies:

```bash
cd opticif
poetry install
```

Alternatively, install the dependencies manually. You can find the list of dependencies in the `pyproject.toml file`,
under the `[tool.poetry.dependencies]` section.

## Usage

OptiCIF can be used as a standalone, but can also be used in combination with
the [RaGraph](https://ragraph.ratio-case.nl/) package to analyze and
optimize CIF models.

Here's a basic example of using OptiCIF to perform global optimization on a CIF specification:

```python
from opticif import do_global_optimization

# Define input files
cif_path = "path/to/your/cif/specification.cif"
csv_path = "path/to/your/sequence.csv"  # CSV file containing the node sequence

# Perform global optimization
do_global_optimization(csv_path, cif_path)

```

For more advanced usage and integration with RaGraph, see the test scripts provided in the repository.

## License

[MIT](LICENSE)
