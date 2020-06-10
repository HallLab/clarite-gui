# CLARITE-GUI

[![Documentation Status](https://readthedocs.org/projects/clarite-gui/badge/?version=latest)](https://clarite-gui.readthedocs.io/en/latest/?badge=latest)

A GUI Version of CLARITE

![alt text][logo]

[logo]: gui/resources/images/clarite_logo.png "CLARITE Logo"

Full documentation on [ReadTheDocs.io](https://clarite-gui.readthedocs.io/en/stable/)

*NOTE*: Update resources with `pyrcc -o gui/resources/app_resources.py gui/resources/app_resources.qrc`

## Install using Conda

Requires Python v3.6 or higher

1. Create a conda environment
    
       conda create -n clarite-gui python=3.7
    
2. (OSX Only) - Install numpy and (assuming you are using homebrew) install omp

       conda install numpy
       brew install libomp
       
3.  Install requirements

        conda install pyqt
        pip install clarite

## Citing CLARITE

1. Lucas AM, et al (2019)
[CLARITE facilitates the quality control and analysis process for EWAS of metabolic-related traits.](https://www.frontiersin.org/article/10.3389/fgene.2019.01240)
*Frontiers in Genetics*: 10, 1240

2. Passero K, et al (2020)
[Phenome-wide association studies on cardiovascular health and fatty acids considering phenotype quality control practices for epidemiological data.](https://www.worldscientific.com/doi/abs/10.1142/9789811215636_0058)
*Pacific Symposium on Biocomputing*: 25, 659