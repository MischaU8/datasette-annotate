# datasette-annotate

[![PyPI](https://img.shields.io/pypi/v/datasette-annotate.svg)](https://pypi.org/project/datasette-annotate/)
[![Changelog](https://img.shields.io/github/v/release/MischaU8/datasette-annotate?include_prereleases&label=changelog)](https://github.com/MischaU8/datasette-annotate/releases)
[![Tests](https://github.com/MischaU8/datasette-annotate/workflows/Test/badge.svg)](https://github.com/MischaU8/datasette-annotate/actions?query=workflow%3ATest)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](https://github.com/MischaU8/datasette-annotate/blob/main/LICENSE)

Datasette plugin for annotating / labelling your training data.

## Installation

Install this plugin in the same environment as Datasette.

    datasette install datasette-annotate

## Usage

Usage instructions go here.

## Development

To set up this plugin locally, first checkout the code. Then create a new virtual environment:

    cd datasette-annotate
    python3 -m venv venv
    source venv/bin/activate

Now install the dependencies and test dependencies:

    pip install -e '.[test]'

To run the tests:

    pytest
