# ALP4lib
A Python module to control Vialux DMDs based on ALP4.X API. It uses the .ddl files provided by Vialux.

## What is it?

This module wraps the basic function of the Vialux dlls to control a digitial micro-mirror device with a Vialux board. This code is tested with a device using the 4.3 version of the ALP API, other version may have issues.

## Requirements

* Windows 32 or 64,
* Vialux drivers and the ALP4.X dll files available for download on [Vialux website](http://www.vialux.de/en/).

## A simple example

```python
import numpy as np
import scipy.misc, scipy.ndimage

DMD = ALP4()
DMD.Initialize()

bitDepth = 1    # binary amplitude image (0 or 1)
imgBlack = np.zeros([DMD.nSizeY,DMD.nSizeX])
imgWhite = np.ones([DMD.nSizeY,DMD.nSizeX])
imgSeq  = np.concatenate([imgB.ravel(),imgW.ravel()])

DMD.AllocateSequence( imgData = imgSeq, nbImg = 2, bitDepth = bitDepth)
DMD.SetTiming(20000) # 50 Hz

DMD.Stop()
DMD.Free()
``` 
