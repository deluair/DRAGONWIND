@echo off
echo Building DRAGONWIND documentation...

REM Create directories if they don't exist
if not exist "_static\images" mkdir "_static\images"
if not exist "_build" mkdir "_build"
if not exist "_build\html" mkdir "_build\html"

REM Install required packages if needed
pip install sphinx sphinx-rtd-theme sphinx-autodoc-typehints myst-parser

REM Build the HTML documentation
sphinx-build -b html . _build/html

echo Documentation build complete.
echo You can view the documentation by opening _build/html/index.html in your web browser.
