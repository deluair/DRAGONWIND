# Setting up Sphinx Documentation for DRAGONWIND

This guide explains how to set up and build the API documentation for the DRAGONWIND simulation platform using Sphinx.

## Prerequisites

- Python 3.7 or higher
- pip package manager

## Installation

Install Sphinx and related packages:

```bash
pip install sphinx sphinx-rtd-theme sphinx-autodoc-typehints myst-parser
```

## Project Structure

The documentation will be organized as follows:

```
docs/
├── api/              # Auto-generated API documentation
├── _build/           # Built HTML documentation
├── _static/          # Static files (CSS, JavaScript, images)
├── _templates/       # Customized templates for Sphinx
├── conf.py           # Sphinx configuration file
├── index.rst         # Main documentation index
├── installation.rst  # Installation guide
├── usage.rst         # Usage instructions
└── examples.rst      # Examples and tutorials
```

## Building the Documentation

To build the documentation:

1. Navigate to the `docs` directory
2. Run `sphinx-build -b html . _build/html`
3. Open `_build/html/index.html` in a web browser to view the documentation

## Automating Documentation Updates

Add the following script to automatically update the documentation when the code changes:

```bash
# update_docs.bat for Windows
cd /d %~dp0
sphinx-build -b html . _build/html
```

## Integrating with Read the Docs

1. Create a `.readthedocs.yml` file in the project root:

```yaml
version: 2

sphinx:
  configuration: docs/conf.py

python:
  version: 3.8
  install:
    - requirements: requirements.txt
    - method: pip
      path: .
```

2. Create a `requirements-docs.txt` file with documentation dependencies:

```
sphinx>=4.3.0
sphinx-rtd-theme>=1.0.0
sphinx-autodoc-typehints>=1.12.0
myst-parser>=0.15.2
```
