# ALP4lib
A Python module to control Vialux DMDs based on ALP4.X API. It uses the .ddl files provided by Vialux. This module comes with no warranty and does not currently supports all the basic ALP API functions.

## What is it?

This module wraps the basic function of the Vialux dlls to control a digitial micro-mirror device with a Vialux board. Vialux provide dlls and modules for Matlab and Labview but not for Python. This code is tested with a device using the 4.3 version of the ALP API, other version may have issues.

## Requirements

* Windows 32 or 64,
* Vialux drivers and the ALP4.X dll files available for download on [Vialux website](http://www.vialux.de/en/).

## Installation

Just copy the ALP4.py file in the working directory. The win32 ALPX.dll files should be directly in the working directory and the win64 dll with the same name in a /x64 subfolder. Alternatively, a different dll directory can be set at the initialization of the DMD handler object. The dlls have the following names respectively for the 4.1, 4.2 and 4.3 versions of the ALP API: 'alp41.dll', 'alp42.dll' and 'alp4395.dll'. 

## Examples

Please note that these examples use numpy array for convenience but for speed sakes, I recommend using lists or array types that can also be sent through the **AllocateSequence** function. 

### A simple example

```python
import numpy as np
import scipy.misc, scipy.ndimage

DMD = ALP4(version = '4.3')
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

## A more advanced example
```python

import numpy as np
import scipy.misc, scipy.ndimage

# Instantiate the ALP4 object with specifying the dll directory and API version.
DMD = ALP4(version = '4.3', libDir = 'C:\Program Files\ALP-4.3\ALP-4.3 API')

# Initialize communication with the DMD having the serial number myDMD_serial (useful for multiple DMD used on the same computer).
DMD.Initialize(self, DeviceNum = myDMD_serial)  

# We will send a sequence of 4 8bit grayscale images.
bitDepth = 8
nbImg = 4

# We create the sequences of images concatenated in a long 1D numpy array.

# First sequence: moving fringes
imgData = np.array([])
[X,Y] = np.meshgrid(np.arange(DMD.nSizeX),np.arange(DMD.nSizeY))
for i in range(nbImg)
  imgData = np.append(imgData,(np.sin((1.*X)/50+(i-1.)/nbImg*np.Pi*2)*2**bitDepth).ravel())

# Allocate the memory specifying the number of images and the bit depth.
seq1 = DMD.AllocateSequence( imgData = img.ravel(), nbImg = nbImg, bitDepth = bitDepth)

# We create a second sequence of images: white to black screen
imgData = []
for i in range(nbImg)
  imgData = np.append(imgData,(np.ones([DMD.nSizeY,DMD.nSizeX])*(1.*i)/(nbImg-1)*2**bitDepth).ravel())
  
# Allocate the second sequence
seq2 = DMD.AllocateSequence(imgData = img.ravel(), nbImg = nbImg, bitDepth = bitDepth)

#
SetTiming(self, nPictureTime, DDRseq_pointer = None, synchDelay = None, synchPulseWidth = None, triggerInDelay = None):
```
