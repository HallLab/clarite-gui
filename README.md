# CLARITE-GUI

[![Documentation Status](https://readthedocs.org/projects/clarite-gui/badge/?version=latest)](https://clarite-gui.readthedocs.io/en/latest/?badge=latest)

A GUI Version of CLARITE

![alt text][logo]

[logo]: src/main/resources/base/images/clarite_logo.png "CLARITE Logo"

Full documentation on [ReadTheDocs.io](https://clarite-gui.readthedocs.io/en/stable/)

## Install

Requires Python v3.6

1. Download the repository and navigate to the main folder
2. Create a python venv

        python -m venv venv
    
3. Activate the environment

    On Mac/Linux:

        source venv/bin/activate

    On Windows:

        call venv\scripts\activate.bat
    
4. Install the requirements

    On Mac/Linux:

        source src\requirements\base.txt

    On Windows:

        pip install -r src\requirements\windows.txt


## Running

1. Activate the environment (if not already activated)

    On Mac/Linux:

        source venv/bin/activate

    On Windows:

        call venv\scripts\activate.bat

2. Run

        fbs run

## Creating an executable (currently not working)

    python -m fbs freeze
