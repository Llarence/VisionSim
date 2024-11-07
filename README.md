# Vision Sim

This is a simple repo to test different vision algorithms on a rover.
It uses Unity to run the simulation and [PyVirtualDisplay](https://github.com/ponty/PyVirtualDisplay) to connect to the simulated enivroment.

## Requirements

PyVirtualDisplay is uses the X Window System so that is required to run this program.
PyVirtualDisplay uses Xvfb, Xephyr or Xvnc so you may have to install one that works for you.

To run the simulator the Python requirements are:
 - easyprocess
 - pyvirtualdisplay
 - cv2
 - numpy

To run the sample algorithm you further need:
 - PIL
 - transformers
 - torch
 - matplotlib

## Running

First you must build the Unity project. I just like to create a ```Build``` directory in the Unity project and build there. It is already in the .gitignore.

To run the project you go to the ```Python``` directory and run ```python3 main.py your/path/to/executable```.
