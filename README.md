# Track-o-tron

![GitHub Tag](https://img.shields.io/github/v/tag/bendabir/trackotron?sort=semver&label=version)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/trackotron)
![PyPI - Implementation](https://img.shields.io/pypi/implementation/trackotron)
![PyPI - License](https://img.shields.io/pypi/l/trackotron)
![Libraries.io dependency status for latest release](https://img.shields.io/librariesio/release/pypi/trackotron)
![GitHub deployments](https://img.shields.io/github/deployments/bendabir/trackotron/release?label=release)

Improved decorator for Langfuse.

## Installation

First, install the package with your favorie package manager (`pip`, `poetry`, etc.).

```python
pip install trackotron
```

## Usage

**TODO**

## Development

The whole project relies on Poetry for setup. It has been developed with Python 3.9 for backward compatibility. Python 3.8 is not supported as it will reach end-of-life in October 2024.

### Environment

```bash
poetry env use python3.9
poetry lock
poetry install --with dev
poetry run pre-commit install
```

### Quality

```bash
poetry run black . # Format code
poetry run ruff check --fix --force-exclude . # Lint code
poetry run mypy --ignore-missing-imports --scripts-are-modules . # Type check code
```

```bash
poetry run python -m pytest --cov=src/trackotron tests # Run all tests
```

### Build

```bash
poetry build -f wheel
```
