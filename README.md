# 2D/3D Seismic Survey Design

<!-- Optional badges -->
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-%3E3.11-blue.svg)](https://www.python.org/)

## Introduction

The 2D/3D Seismic Survey Design tool is a Python project to support geophysicists in planning 2D and 3D seismic surveys including Pre-Plot planning and Pre-Permit planning. [`GeoPandas`](https://geopandas.org/) and
[`Shapely`](https://shapely.readthedocs.io/) packages. 

## Installation

To install the package, clone it from Github using 

`git clone https://github.com/AlexanderJuestel/seismic_survey_design.git`

The main requirements are `python>3.11`, `geopandas` and `matplotlib` which will also install subpackages like `shapely`, `numpy`, and others and can be installed in an environment with `python>3.11` using

`pip install geopandas matplotlib` 

## Features

- Creating a nominal survey design including target zone (line for 2D, area for 3D), migration aperture, fold taper, and nominal fold calculations within a dedicated SurveyDesign class based on a predefined `config.yaml` file.
- Creating a preplot survey design projecting source and receiver points onto roads or offroad and fold calculations
- Definition and classification of source points based on no-permit areas (e.g. protected areas) or distances to buildings


