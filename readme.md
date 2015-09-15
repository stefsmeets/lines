# Lines

Lines is a program for plotting powder diffraction patterns, and was initially developed for interactively modifying the background during the course of a Rietveld refinement with XRS-82 (Baerlocher, 1982). The modern way of removing backgrounds is by fitting a Chebyshev polynomial during the course of the Rietveld refinement. In practice, this method is unreliable when doing a Pawley or Le Bail fit, and offers little control over the shape of the background during a Rietveld refinement.

The background of any file can be corrected with:

    lines pattern.xye --bg_correct 1

Then by clicking on the figure, the background can be specified. By closing the program, a list of X and Y coordinates is printed to console and written to the file lines.out. The command line option --bgcorrect 1 tells the program to perform a linear background correction, and print the corrected file to pattern_corr.xy. In this way, the original file is never modified.

It is also possible to perform the background correction while doing a refinement with TOPAS. In order to do so, the observed, calculated and difference plot should be output from TOPAS with the following commands:

    Out_X_Yobs(x_yobs.xy)
    Out_X_Ycalc(x_ycalc.xy)
    Out_X_Difference(x_ydiff.xy)

Then, to start the background correct prodecure:

    lines pattern.xye --topasbg --bg_correct 1 --bgin lines.out

The option --topasbg will tell the program to read the observed, calculated and difference plots and --bg_in lines.out will load previously saved background points from the file lines.out.

Since its inception, many functions for operations performed on powder diffraction data have been implemented. A number of different file formats can be read and visualized in numerous ways. Further options for diffraction pattern manipulation include the options to adjust the wavelength of the diffraction data, or to re-bin, normalize, and smooth them. All the functions are documented in the help file, which can be accessed via luke --help.

## Requirements

- Python2.7
- numpy
- scipy
- matplotlib
- CCTBX (optional)

## Installation

Download and extract:

    https://github.com/stefsmeets/lines/archive/master.zip

Install:

    python setup.py install

Uninstall:

    pip uninstall lines



