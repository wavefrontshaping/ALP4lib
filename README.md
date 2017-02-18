# ALP4lib
ALP4lib is a Python module to control Vialux DMDs based on ALP4.X API.
This is not an independant open source module, it uses the .ddl files provided by [Vialux](http://www.vialux.de/en/).
This software is still experimental, use it at your own risk.

## What is it?

This module wraps the basic function of the Vialux dlls to control a digitial micro-mirror device with a Vialux board. 
Vialux provides dlls and also modules for Matlab and Labview but not for Python. 
This code is tested with a device using the 4.3 version of the ALP API, other versions may have issues.
LED control related functions are not implemented.
Please read the ALP API description provided with the [Vialux](http://www.vialux.de/en/) ALP installation.

## Requirements

* Windows 32 or 64,
* Vialux drivers and the ALP4.X dll files available for download on [Vialux website](http://www.vialux.de/en/).

**Warning:** Still display issues with Python 3.X, a fix is on its way. 

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

or 

```shell
easy_install ALP4lib
```

## Copy the .dll

The win32 ALPX.dll files should be directly in the working directory and the win64 dll with the same name in a /x64 subfolder. Alternatively, a different dll directory can be set at the initialization of the DMD handler object. 
The dlls have the following names respectively for the 4.1, 4.2 and 4.3 versions of the ALP API: 'alp41.dll', 'alp42.dll' and 'alp4395.dll'. 

## A simple example

```python
import numpy as np
from ALP4 import *
import time

# Load the Vialux .dll
DMD = ALP4(version = '4.3', libDir = 'C:/Program Files/ALP-4.3/ALP-4.3 API')
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
DMD.SetTiming(illuminationTime = 20000)

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
