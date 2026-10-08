# ALP4lib
ALP4lib is a Python module to control Vialux DMDs based on ALP4.X and ALP5.X API.
This is not an independant open source module, it uses the .dll (Windows) or .so (Linux) files provided by [Vialux](http://www.vialux.de/en/).
This software is experimental, use it at your own risk.

## What is it?

This module wraps the basic function of the Vialux libraries to control a digitial micro-mirror device with a Vialux board. 
Vialux provides dlls (Windows) and shared libraries (Linux), and also modules for Matlab and Labview but not for Python. 
This code is tested with a device using the 4.3 version of the ALP API on Windows and Linux, other versions may have issues.
LED control related functions are not implemented.
Please read the ALP API description provided with the [Vialux](http://www.vialux.de/en/) ALP installation.

## Requirements

* Windows 32 or 64, or Linux x86_64,
* Vialux drivers and the ALP4.X or ALP5.X dll files (Windows) or the ALP shared libraries (Linux) available for download on [Vialux website](http://www.vialux.de/en/),
* Compatible Python 2.7 and 3.X.

## Citing the code

If the code was helpful to your work, please consider citing it:

[![DOI](https://zenodo.org/badge/70229567.svg)](https://zenodo.org/badge/latestdoi/70229567)


## Installation

### Manual installation 
Just copy the ALP4.py file in the working directory. 

### Automatic installation

To automatically download and copy the module in the python directory (so it can be available from anywhere), run the command:

```shell
pip install ALP4lib
```

### Installation from source (Github)
To install the latest version directly from Github without cloning, run:
```shell script
pip install git+https://github.com/wavefrontshaping/ALP4lib.git
```
Alternatively, clone the repository and install the package with the following command.
```shell script
pip install .
```
Instead of the normal installation, if you want to install ALP4lib in [development mode](https://setuptools.pypa.io/en/latest/userguide/development_mode.html), use:
```shell script
pip install -e .
```


## Copy the .dll/.so

### Windows

The win32 ALPX.dll files could be directly in the working directory and the win64 dll with the same name in a /x64 subfolder. 
If no directory is given, the module reads the ALP installation path from the Windows registry and looks for the API folder
(`ALP-4.X high-speed API` for ALP 4.X, `ALP-5.X API` for ALP 5.X, e.g. `C:\Program Files\ALP-5.0\ALP-5.0 API\`).
Alternatively, a different dll directory can be set at the initialization of the DMD handler object with the `libDir` argument. 
The dlls have the following names respectively for the 4.1, 4.2, 4.3, 4.4, 5.0 and 5.1 versions of the ALP API: 'alpD41.dll', 'alpV42.dll', 'alp4395.dll', 'Alp44.dll', 'alp50.dll' and 'alp51.dll'. 

### Linux

Install the Vialux Linux drivers and ALP shared libraries following the Vialux documentation.
By default, the module looks for the library in `/usr/lib/x86_64-linux-gnu/`.
A different directory can be set at the initialization of the DMD handler object with the `libDir` argument.
The shared libraries have the following names for the 4.1, 4.2, 4.3, 4.4, 5.0 and 5.1 versions of the ALP API: 'libalp41.so', 'libalp42.so', 'libalp43.so', 'libalp44.so', 'libalp50.so' and 'libalp51.so'.

```python
from ALP4 import *

# Default library directory (/usr/lib/x86_64-linux-gnu/ on Linux)
DMD = ALP4(version = '4.3')

# Custom library directory
DMD = ALP4(version = '4.3', libDir = '/opt/vialux/lib/')
```

## A simple example

```python
import numpy as np
from ALP4 import *
import time

# Load the Vialux library (.dll on Windows, .so on Linux)
DMD = ALP4(version = '4.3')
# Initialize the device
DMD.Initialize()

# Binary amplitude image (0 or 1)
bitDepth = 1    
imgBlack = np.zeros([DMD.nSizeY,DMD.nSizeX])
imgWhite = np.ones([DMD.nSizeY,DMD.nSizeX])*(2**8-1)
imgSeq  = np.concatenate([imgBlack.ravel(),imgWhite.ravel()])

# Allocate the onboard memory for the image sequence
DMD.SeqAlloc(nbImg = 2, bitDepth = bitDepth)
# Send the image sequence as a 1D list/array/numpy array
DMD.SeqPut(imgData = imgSeq)
# Set image rate to 50 Hz
DMD.SetTiming(pictureTime = 20000)

# Run the sequence in an infinite loop
DMD.Run()

time.sleep(10)

# Stop the sequence display
DMD.Halt()
# Free the sequence from the onboard memory
DMD.FreeSeq()
# De-allocate the device
DMD.Free()
``` 
