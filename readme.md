[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/xpdlines)](https://pypi.org/project/xpdlines/)
[![PyPI](https://img.shields.io/pypi/v/xpdlines.svg?style=flat)](https://pypi.org/project/xpdlines/)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.4715880.svg)](https://doi.org/10.5281/zenodo.4715880)


# Lines

Lines is a program for plotting powder diffraction patterns, and was initially developed for interactively modifying the background during the course of a Rietveld refinement with XRS-82 (Baerlocher, 1982). The modern way of removing backgrounds is by fitting a Chebyshev polynomial during the course of the Rietveld refinement. In practice, this method is unreliable when doing a Pawley or Le Bail fit, and offers little control over the shape of the background during a Rietveld refinement. 

## Background correction

The background of any pattern (.xy or .xye format) can be corrected with:

    lines pattern.xye --bgcorrect 1

Then by clicking on the figure, the background can be specified. By closing the program, a list of X and Y coordinates is printed to console and written to the file lines.out. The command line option --bgcorrect 1 tells the program to perform a linear background correction, and print the corrected file to pattern_corr.xy. Lines respects your standard deviations and never overwrites the original data. The background points are by default written to the file lines.out. In case this file exists, the original is backed up to lines.out~.

It is then possible to continue the background correction process by loading in the points from the file lines.out  like this:

	lines pattern.xye --bgcorrect 1 --bgin lines.out

It is also possible to perform the background correction while doing a refinement with TOPAS. In order to do so, the observed, calculated and difference plot should be output from TOPAS with the following commands:

    Out_X_Yobs(x_yobs.xy)
    Out_X_Ycalc(x_ycalc.xy)
    Out_X_Difference(x_ydiff.xy)

Then, to start the background correct prodecure:

    lines pattern.xye --bgcorrect 1 --bgin lines.out --topasbg

The option --topasbg will tell the program to read the observed, calculated and difference plots and --bg_in lines.out will load previously saved background points from the file lines.out.

![background](https://cloud.githubusercontent.com/assets/873520/14958064/02be1a30-1089-11e6-8f2d-61b458e4cc0d.png)

Since its inception, many functions for operations performed on powder diffraction data have been implemented. A number of different file formats can be read and visualized in numerous ways. Further options for diffraction pattern manipulation include the options to adjust the wavelength of the diffraction data, or to re-bin, normalize, and smooth them. All the functions are documented in the help file, which can be accessed via lines --help.

## GUI

On Windows, a GUI for the background subtraction is available. It is accessible via the `lines_bg.bat` file  in the `bin` directory or by typing `lines gui`.

Pressing run opens an instance of lines where the background can be modified. By closing the plot window, and the corrected and background patterns will be written.

![gui](https://cloud.githubusercontent.com/assets/873520/14958063/029e912e-1089-11e6-9ffc-976ddbf1f992.png)

## Requirements

In brackets are known working versions.

- Python 3.9+
- numpy (1.24.1)
- scipy (1.10.0)
- matplotlib (3.6.3)

## Installation

```bash
pip install xpdlines
```

Or, to install the latest version from this repository:


```bash
pip install git+https://github.com/stefsmeets/lines
```