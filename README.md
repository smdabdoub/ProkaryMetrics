ProkaryMetrics (v0.3.1)
=======================
This software is designed to enable basic 3D visualization of 8/16-bit B&W 
2D stacks of microscopy data, as well as allow users to manually designate the
location of bacteria within the image data. Currently the software also 
provides the users with some basic statistics such as the number of recorded 
bacteria and the size and volume of the marked bacteria within a fitted 
ellipsoid.

Requirements
------------
The software is written in Python (2.7) and requires (minimum version) the 
following libraries:

* VTK (5.6)
* wxPython (2.8.10)
* PIL (1.1.7)

The simplest means to getting the appropriate Python environment with the 
appropriate libraries is to install the Enthought Python Distribution (free 
for Academic users) which can be found at:

http://enthought.com/products/epd.php

The current version (7.2) would be best to for running ProkaryMetrics, 
but you will need at least the 7.0 release of the EPD due to the requirement 
of Python 2.7.

In the near future, I hope to provide a self-contained app package for Mac/Win 
that will not require any installations.

Running
-------
Once you have the appropriate Python environment and libraries installed, use 
a console to navigate to the ProkaryMetrics folder contained with this file in 
the downloaded archive and type:

> $> python pkMetrics.py

This command will launch the program, and everything else is done through 
interacting with the GUI.

- - -
Version 0.3.1 of ProkaryMetrics is released under the GPLv3.

Please address any comments or questions to:

Shareef M. Dabdoub, Ph.D.
dabdoub.2@osu.edu
