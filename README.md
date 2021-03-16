# CLARITE-GUI

[![Documentation Status](https://readthedocs.org/projects/clarite-gui/badge/?version=latest)](https://clarite-gui.readthedocs.io/en/latest/?badge=latest)

A GUI Version of CLARITE

![alt text][logo]

[logo]: gui/resources/images/clarite_logo.png "CLARITE Logo"

Full documentation on [ReadTheDocs.io](https://clarite-gui.readthedocs.io/en/stable/)

*NOTE*: Update resources with `pyrcc -o gui/resources/app_resources.py gui/resources/app_resources.qrc`

## Running

1. Download or clone this repository and enter the folder
2. Ensure pipenv is installed

    ``pip install pipenv``

3. Create/update the pipenv

    ``pipenv update``

4. Run:

    ``pipenv run python main.py``
    
## Using the 'r_survey' regression method in 'ewas'

This will currently raise an error "signal only works in main thread".
This should be resolved when [this pull request](https://github.com/rpy2/rpy2/pull/780) is merged into rpy2

Executables will be provided for future releases.

## Build Notes

### Windows

pipenv run pyinstaller -F --name=CLARITE --icon=clarite_logo.ico main.py
./dist/CLARITE.exe

### Mac

pipenv run pyinstaller -F --name=CLARITE --icon=clarite_logo.ico --hidden-import cmath --windowed main.py
./dist/CLARITE

## Citing CLARITE

1. Lucas AM, et al (2019)
[CLARITE facilitates the quality control and analysis process for EWAS of metabolic-related traits.](https://www.frontiersin.org/article/10.3389/fgene.2019.01240)
*Frontiers in Genetics*: 10, 1240

2. Passero K, et al (2020)
[Phenome-wide association studies on cardiovascular health and fatty acids considering phenotype quality control practices for epidemiological data.](https://www.worldscientific.com/doi/abs/10.1142/9789811215636_0058)
*Pacific Symposium on Biocomputing*: 25, 659