============
Installation
============

This guide will walk you through the process of installing the DRAGONWIND simulation platform.

System Requirements
------------------

* Python 3.8 or higher
* 4GB RAM minimum (8GB recommended)
* Windows, macOS, or Linux operating system

Dependencies
-----------

DRAGONWIND requires the following Python packages:

* numpy
* pandas
* matplotlib
* seaborn
* pyyaml
* tqdm
* dash (for web UI)
* dash-bootstrap-components (for web UI)
* plotly
* jsonschema (for configuration validation)
* pytest (for testing)

Basic Installation
-----------------

1. Clone the repository from GitHub:

   .. code-block:: bash

      git clone https://github.com/deluair/DRAGONWIND.git
      cd DRAGONWIND

2. Create and activate a virtual environment (recommended):

   .. code-block:: bash

      # On Windows
      python -m venv venv
      venv\Scripts\activate

      # On macOS/Linux
      python -m venv venv
      source venv/bin/activate

3. Install the required packages:

   .. code-block:: bash

      pip install -r requirements.txt

4. Verify the installation:

   .. code-block:: bash

      python -m dragonwind_simulator.tests.run_basic_test

Development Installation
-----------------------

For development, you'll need additional packages for testing, documentation, and code quality:

1. Install development dependencies:

   .. code-block:: bash

      pip install -r requirements-dev.txt

2. Set up pre-commit hooks:

   .. code-block:: bash

      pre-commit install

Web Dashboard Installation
-------------------------

To use the web dashboard, make sure you have the required packages:

.. code-block:: bash

   pip install dash dash-bootstrap-components plotly

Starting the Web Dashboard
------------------------

To launch the web dashboard:

.. code-block:: bash

   python -m dragonwind_simulator.web_dashboard

Then open your web browser and navigate to http://127.0.0.1:8050/ to access the dashboard.

Troubleshooting
--------------

**ImportError: DLL load failed**
   On Windows, this may be due to missing Visual C++ Redistributable. Install the latest version from the Microsoft website.

**ModuleNotFoundError**
   Ensure that you've activated the virtual environment and installed all dependencies.

**SyntaxError: source code string cannot contain null bytes**
   If you encounter this error, the file may contain null bytes. Fix by opening the file in a text editor, saving it with proper encoding, or using a utility to remove null bytes.

For more help, please open an issue on our GitHub repository.
