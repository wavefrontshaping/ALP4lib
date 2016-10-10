# ALP4lib
A Python module to control Vialux DMDs based on ALP4.X API. It uses the .ddl files provided by Vialux.

## What is it?

This module wraps the basic function of the Vialux dlls to control a digitial micro-mirror device with a Vialux board. Vialux provide dlls and modules for Matlab and Labview but not for Python. This code is tested with a device using the 4.3 version of the ALP API, other version may have issues.

## Requirements

* Windows 32 or 64,
* Vialux drivers and the ALP4.X dll files available for download on [Vialux website](http://www.vialux.de/en/).

## Installation

Just copy the ALP4.py file in the working directory. The win32 ALPX.dll files should be directly in the working directory and the win64 dll with the same name in a /x64 subfolder. Alternatively, a different dll directory can be set at the initialization of the DMD handler object. The dlls have the following names respectively for the 4.1, 4.2 and 4.3 versions of the ALP API: 'alp41.dll', 'alp42.dll' and 'alp4395.dll'. 

## A simple example

```python
import numpy as np
import scipy.misc, scipy.ndimage
from ALP4 import *

DMD = ALP4(version = '4.3')
DMD.Initialize()

bitDepth = 1    # binary amplitude image (0 or 1)
imgBlack = np.zeros([DMD.nSizeY,DMD.nSizeX])
imgWhite = np.ones([DMD.nSizeY,DMD.nSizeX])
imgSeq  = np.concatenate([imgBlack.ravel(),imgWhite.ravel()])

DMD.AllocateSequence( imgData = imgSeq, nbImg = 2, bitDepth = bitDepth)
DMD.SetTiming(20000) # 50 Hz

DMD.Stop()
DMD.Free()
``` 
