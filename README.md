# CLARITE-GUI

[![Documentation Status](https://readthedocs.org/projects/clarite-gui/badge/?version=latest)](https://clarite-gui.readthedocs.io/en/latest/?badge=latest)

A GUI Version of CLARITE

![alt text][logo]

[logo]: gui/resources/images/clarite_logo.png "CLARITE Logo"

Full documentation on [ReadTheDocs.io](https://clarite-gui.readthedocs.io/en/stable/)

## Running
Executables are [available under releases](https://github.com/HallLab/clarite-gui/releases).

To run using python:

1. Download or clone this repository and enter the folder
2. Ensure pipenv is installed

    ``pip install pipenv``

3. Create/update the pipenv

    ``pipenv update``

4. Run:

    ``pipenv run python main.py``
    
## Known Issues

* Using the 'r_survey' regression method in 'ewas'
  * This will currently raise an error "signal only works in main thread". This should be resolved when [this pull request](https://github.com/rpy2/rpy2/pull/780) is merged into rpy2
* Build not available for MacOS
   * Due to Big Sur difficulties, which may be resolved in a future version of PyInstaller
* Statsmodels/PyInstaller incompatibility
    * Will be fixed in the next release of PyInstaller due to a new hook for statsmodels

## Build Notes

### Windows

pipenv run pyinstaller -F --name=CLARITE --icon=clarite_logo.ico main.py
./dist/CLARITE.exe

### Mac - Currently broken on Big Sur

pipenv run pyinstaller -F --name=CLARITE --icon=clarite_logo.ico --hidden-import cmath --windowed main.py
open ./dist/CLARITE.app

## Citing CLARITE

1. Lucas AM, et al (2019)
[CLARITE facilitates the quality control and analysis process for EWAS of metabolic-related traits.](https://www.frontiersin.org/article/10.3389/fgene.2019.01240)
*Frontiers in Genetics*: 10, 1240

2. Passero K, et al (2020)
[Phenome-wide association studies on cardiovascular health and fatty acids considering phenotype quality control practices for epidemiological data.](https://www.worldscientific.com/doi/abs/10.1142/9789811215636_0058)
*Pacific Symposium on Biocomputing*: 25, 659