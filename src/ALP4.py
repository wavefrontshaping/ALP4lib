#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Wed Oct 05 15:48:53 2016

@author: Sebastien Popoff
"""

import ctypes as ct
import platform
import numpy as np
import six
if six.PY3:
    import winreg as _winreg
else:
    import _winreg

from header import *


class ALPError(Exception):
    def __init__(self, error_code):
        super(ALPError, self).__init__(ALP_ERRORS[error_code])


def afficheur(bitPlane):
    nSizeX = 2560
    nSizeY = 1600
    display = np.zeros((nSizeY, nSizeX))
    for jj in range(nSizeY):
        for ii in range(nSizeX // 8):
            Q = bitPlane[jj * nSizeX // 8 + ii]
            R = [0, 0, 0, 0, 0, 0, 0, 0]
            k = 7
            while Q != 0:
                R[k] = (Q % 2)
                Q = Q // 2
                k -= 1
            for ll in range(8):
                display[jj, ii * 8 + ll] = R[ll]
    return display


def img_to_bitplane(imgArray, bitShift):
    """
    Convert a binary image into a bitplane.
    """
    bitPlane = np.packbits(imgArray).tolist()
    return bitPlane

class ALP4(object):
    """
    This class controls a Vialux DMD board based on the Vialux ALP 4.X API.
    """

    def __init__(self, version='4.3', libDir=None):

        os_type = platform.system()

        if libDir is None:
            try:
                reg = _winreg.ConnectRegistry(None, _winreg.HKEY_LOCAL_MACHINE)
                key = _winreg.OpenKey(reg, r"SOFTWARE\ViALUX\ALP-" + version)
                libDir = (_winreg.QueryValueEx(key, "Path"))[0] + "/ALP-{0} API/".format(version)
            except EnvironmentError:
                raise ValueError("Cannot auto detect libDir! Please specify it manually.")

        if libDir.endswith('/'):
            libPath = libDir
        else:
            libPath = libDir + '/'
            ## Load the ALP dll
        if (os_type == 'Windows'):
            if (ct.sizeof(ct.c_voidp) == 8):  ## 64bit
                libPath += 'x64/'
            elif not (ct.sizeof(ct.c_voidp) == 4):  ## 32bit
                raise OSError('System not supported.')
        else:
            raise OSError('System not supported.')

        if (version == '4.1'):
            libPath += 'alpD41.dll'
        elif (version == '4.2'):
            libPath += 'alpD41.dll'
        elif (version == '4.3'):
            libPath += 'alp4395.dll'

        print('Loading library: ' + libPath)

        self._ALPLib = ct.CDLL(libPath)

        ## Class parameters
        # ID of the current ALP device
        self.ALP_ID = ct.c_ulong(0)
        # Type of DMD found
        self.DMDType = ct.c_long(0)
        # Pointer to the last stored image sequence
        self._lastDDRseq = None
        # List of all Sequences
        self.Seqs = []

    def _checkError(self, returnValue, errorString, warning=False):
        if not (returnValue == ALP_OK):
            if not warning:
                raise ALPError(returnValue)
            else:
                print(errorString + '\n' + ALP_ERRORS[returnValue])

    def Initialize(self, DeviceNum=None):
        """
        Initialize the communication with the DMD.

        Usage:
        Initialize(DeviceNum = None)

        PARAMETERS
        ----------
        DeviceNum : int
                    Serial number of the DMD to initialize, useful for multiple DMD control.
                    If not specify, open the first available DMD.
        """
        if DeviceNum is None:
            DeviceNum = ct.c_long(ALP_DEFAULT)

        self._checkError(self._ALPLib.AlpDevAlloc(DeviceNum, ALP_DEFAULT, ct.byref(self.ALP_ID)), 'Cannot open DMD.')
        self._checkError(self._ALPLib.AlpDevInquire(self.ALP_ID, ALP_DEV_DMDTYPE, ct.byref(self.DMDType)),
                         'Inquery fails.')

        nSizeX = ct.c_long(0)
        self._checkError(self._ALPLib.AlpDevInquire(self.ALP_ID, ALP_DEV_DISPLAY_WIDTH, ct.byref(nSizeX)),
                         'Inquery ALP_DEV_DISPLAY_WIDTH fails.')
        self.nSizeX = nSizeX.value

        nSizeY = ct.c_long(0)
        self._checkError(self._ALPLib.AlpDevInquire(self.ALP_ID, ALP_DEV_DISPLAY_HEIGHT, ct.byref(nSizeY)),
                         'Inquery ALP_DEV_DISPLAY_HEIGHT fails.')
        self.nSizeY = nSizeY.value

        print('DMD found, resolution = ' + str(self.nSizeX) + ' x ' + str(self.nSizeY) + '.')

    def SeqAlloc(self, nbImg=1, bitDepth=1):
        """
        This function provides ALP memory for a sequence of pictures. All pictures of a sequence have the
        same  bit  depth.  The  function  allocates  memory  from  the  ALP  board  RAM. The  user  has  no  direct
        read/write  access.  ALP  functions  provide  data  transfer  using  the  sequence  memory  identifier
        (SequenceId) of type ALP_ID.
        Pictures can be loaded into the ALP RAM using the SeqPut function.
        The availability of ALP memory can be tested using the DevInquire function.
        When a sequence is no longer required, release it using SeqFree.


        Usage:
        SeqAlloc(nbImg = 1, bitDepth = 1)

        PARAMETERS
        ----------
        nbImg : int
                Number of images in the sequence.
        bitDepth : int
                   Quantization of the image between 1 (on/off) and 8 (256 pwm grayscale levels).

        See ALPLib.AlpSeqAlloc in the ALP API description for more information.

        RETURNS
        -------
        SequenceID : ctypes c_ulong
                     Id of the created sequence.
                     This id is stored internally as the last created sequence and
                     erase the previous one. When a sequence relasted function is used without
                     specifying a SequenceId, it will use the stored SequenceId.

        """

        SequenceId = ct.c_long(0)
        self.Seqs.append(SequenceId)  # Put SequenceId in list of all Sequences to keep track of them
        # Allocate memory on the DDR RAM for the sequence of image.
        self._checkError(
            self._ALPLib.AlpSeqAlloc(self.ALP_ID, ct.c_long(bitDepth), ct.c_long(nbImg), ct.byref(SequenceId)),
            'Cannot allocate image sequence.')

        self._lastDDRseq = SequenceId
        return SequenceId

    def SeqPutEx(self, imgData, LineOffset, LineLoad, SequenceId=None, PicOffset=0, PicLoad=0, dataFormat='Python'):
        """
        Image data transfer using AlpSeqPut is based on whole DMD frames. Applications that only
        update small regions inside a frame suffer from overhead of this default behavior. An extended
        ALP API function is available to reduce this overhead.

        The AlpSeqPutEx function offers the same functionality as the standard function (AlpSeqPut),
        but in addition, it is possible to select a section within a sequence frame using the
        LineOffset and LineLoad parameters of the tAlpLinePut data-structure (see below) and update
        only this section of the SDRAM-memory associated with the sequence for a range of
        sequence-pictures (selected via the PicOffset and PicLoad parameters of tAlpLinePut in
        similarity to AlpSeqPut).

        This results in accelerated transfer-time of small image data updates (due to the fact that the
        amount of transferred data is reduced).

        Therefore, the user only passes the lines of the pictures he wants to update via the UserArrayPtr
        (that would be PicLoad*LineLoad lines in total).

        PARAMETERS
        ----------

        imgData : list, 1D array or 1D ndarray
                  Data stream corresponding to a sequence of nSizeX by nSizeX images.
                  Values has to be between 0 and 255.
        LineOffset : int
                     Defines the offset of the frame-section. The frame-data of this section is transferred
                     for each of the frames selected with PicOffset and PicLoad. The value of this
                     parameter must be greater or equal to zero, otherwise ALP_PARM_INVALID is returned.
        LineLoad : int
                   Defines the size of the frame-section. If the value of the parameter is
                   less than zero or if LineOffset+LineLoad exceeds the number of lines
                   per sequence-frame, ALP_PARM_INVALID is returned. If LineLoad is
                   zero, this value is adjusted to include all lines of the frame, starting at
                   line LineOffset
        SequenceId : ctypes c_long
                     Sequence identifier. If not specified, set the last sequence allocated in the DMD board memory
        PicOffset : int, optional
                    Picture number in the sequence (starting at 0) where the data upload is
                    started; the meaning depends upon ALP_DATA_FORMAT.
                    By default, PifOffset = 0.
        PicLoad : int, optional
                 number of pictures that are to be loaded into the sequence memory.
                 Depends on ALP_DATA_FORMAT.
                 PicLoad = 0 correspond to a complete sequence.
                 By default, PicLoad = 0.
        dataFormat : string, optional
                 Specify the type of data sent as image.
                 Should be ' Python' or 'C'.
                 If the data is of Python format, it is converted into a C array before sending to the DMD via the dll.
                 By default dataFormat = 'Python'
        """

        if not SequenceId:
            SequenceId = self._lastDDRseq

        LinePutParam = tAlpLinePut(ALP_PUT_LINES,
                                   ct.c_long(PicOffset),
                                   ct.c_long(PicLoad),
                                   ct.c_long(LineOffset),
                                   ct.c_long(LineLoad))

        if dataFormat not in ['Python', 'C']:
            raise ValueError('dataFormat must be one of "Python" or "C"')

        if dataFormat == 'Python':
            pImageData = imgData.astype(np.uint8).ctypes.data_as(ct.c_void_p)
        elif dataFormat == 'C':
            pImageData = ct.cast(imgData, ct.c_void_p)

        self._checkError(self._ALPLib.AlpSeqPutEx(self.ALP_ID, SequenceId, LinePutParam, pImageData),
                         'Cannot send image sequence to device.')

    def SeqPut(self, imgData, SequenceId=None, PicOffset=0, PicLoad=0, dataFormat='Python'):
        """
        This  function  allows  loading user  supplied  data  via  the  USB  connection  into  the  ALP  memory  of  a
        previously allocated sequence (AlpSeqAlloc) or a part of such a sequence. The loading operation can
        run  concurrently to  the  display  of  other sequences.  Data  cannot be  loaded  into  sequences that  are
        currently started for display. Note: This protection can be disabled by ALP_SEQ_PUT_LOCK.

        The function loads PicNum pictures into the ALP memory reserved for the specified sequence starting
        at picture PicOffset. The calling program is suspended until the loading operation is completed.

        The  ALP  API  compresses  image  data  before  sending  it  over  USB.  This  results  in  a  virtual
        improvement of data transfer speed. Compression ratio is expected to vary depending on image data.
        Incompressible data do not cause overhead delays.

        Usage:
        SeqPut(imgData, nbImg = 1, bitDepth = 1)

        PARAMETERS
        ----------

        imgData : list, 1D array or 1D ndarray
                  Data stream corresponding to a sequence of nSizeX by nSizeX images.
                  Values has to be between 0 and 255.
        SequenceId : ctypes c_long
                     Sequence identifier. If not specified, set the last sequence allocated in the DMD board memory
        PicOffset : int, optional
                    Picture number in the sequence (starting at 0) where the data upload is
                    started; the meaning depends upon ALP_DATA_FORMAT.
                    By default, PifOffset = 0.
        PicLoad : int, optional
                 number of pictures that are to be loaded into the sequence memory.
                 Depends on ALP_DATA_FORMAT.
                 PicLoad = 0 correspond to a complete sequence.
                 By default, PicLoad = 0.
        dataFormat : string, optional
                 Specify the type of data sent as image.
                 Should be ' Python' or 'C'.
                 If the data is of Python format, it is converted into a C array before sending to the DMD via the dll.
                 By default dataFormat = 'Python'

        SEE ALSO
        --------

        See ALPLib.AlpSeqPut in the ALP API description for more information.
        """

        if not SequenceId:
            SequenceId = self._lastDDRseq

        if dataFormat == 'Python':
            pImageData = imgData.astype(np.uint8).ctypes.data_as(ct.c_void_p)
        elif dataFormat == 'C':
            pImageData = ct.cast(imgData, ct.c_void_p)
        else:
            raise ValueError('dataFormat must be one of "Python" or "C"')

        self._checkError(
            self._ALPLib.AlpSeqPut(self.ALP_ID, SequenceId, ct.c_long(PicOffset), ct.c_long(PicLoad), pImageData),
            'Cannot send image sequence to device.')

    def ImgToBitPlane(self, imgArray, bitShift=0):
        """
        Create a bit plane from the imgArray.
        The bit plane is an (nSizeX x nSizeY / 8) array containing only the bit values
        corresponding to the bit number bitShift.
        For a bit depth = 8, 8 bit planes can be extracted from the imgArray by iterating ImgToBitPlane.

        WARNING: It is recommended to directly generate images as bitplanes for better performances.

        Usage:

        ImgToBitPlane(imgArray,bitShift = 0)

        PARAMETERS
        ----------

        imgArray: 1D array or list
                  An image of the same resolution as the DMD (nSizeX by nSizeY).

        bitShift: int, optional
                  Bit plane to extract form the imgArray (0 to 8),
                  Has to be <= bit depth.

        RETURNS
        -------

        bitPlane: list
                  Array (nSizeX x nSizeY)/8


        """
        return img_to_bitplane(imgArray, bitShift)


    def SetTiming(self, SequenceId=None, illuminationTime=None, pictureTime=None, synchDelay=None,
                  synchPulseWidth=None, triggerInDelay=None):
        """
        Set the timing properties of the sequence to display.

        Usage:

        SetTiming( SequenceId = None, illuminationTime = None, pictureTime = None, synchDelay = None, \
                  synchPulseWidth = None, triggerInDelay = None)

        PARAMETERS
        ----------

        SequenceId : c_ulong, optional
                       Identified of the sequence. If not specified, set the last sequence allocated in the DMD board memory
        illuminationTime: c_ulong, optional
                           Display time of a single image of the sequence in microseconds.
                           If not specified, use the highest possible value compatible with pictureTime.
        pictureTime : int, optional
                        Time between the start of two consecutive picture, up to 10^7 microseconds = 10 seconds.
                        With illuminationTime, it sets the display rate.
                        If not specified, the value is set to minimize the dark time according illuminationTime.
                        If illuminationTime is also not specified, set to a frame rate of 30Hz.
        synchDelay : Specifies the time delay between the start of the output sync pulse and the start of the display (master mode).
                       Value between 0 and 130,000 microseconds. Set to 0 if not specified.
        synchPulseWidth : Duration of the sync output pulse.
                         By default equals synchDelay + illuminationTime in normal mode.
                         By default equals ALP_ILLUMINATION_TIME in binary uninterrupted mode.
        triggerInDelay : Length of the trigger signal in microseconds, set to 0 by default.


        SEE ALSO
        --------
        See ALPLib.AlpSeqAlloc in the ALP API description for more information.
        """
        if (SequenceId is None) and (self._lastDDRseq):
            SequenceId = self._lastDDRseq
        if (SequenceId is None):
            raise ValueError('No sequence to display.')

        if (synchDelay is None):
            synchDelay = ALP_DEFAULT
        if (synchPulseWidth is None):
            synchPulseWidth = ALP_DEFAULT
        if (triggerInDelay is None):
            triggerInDelay = ALP_DEFAULT
        if (illuminationTime is None):
            illuminationTime = ALP_DEFAULT
        if (pictureTime is None):
            pictureTime = ALP_DEFAULT

        self._checkError(
            self._ALPLib.AlpSeqTiming(self.ALP_ID, SequenceId, ct.c_long(illuminationTime), ct.c_long(pictureTime),
                                      ct.c_long(synchDelay), ct.c_long(synchPulseWidth), ct.c_long(triggerInDelay)),
            'Cannot set timing.')

    def DevInquire(self, inquireType):
        """
        Ask the controller board the value of a specified parameter about the ALP device.

        Usage: Inquire(request)

        PARAMETERS
        ----------

        inquireType : ctypes c_ulong
                      Sepcifies the type of value to return.


        RETURNS
        -------

        value : c_double
                Value of the requested parameter.

        SEE ALSO
        --------

        See AlpDevInquire in the ALP API description for request types.

        """

        ret = ct.c_double(0)

        self._checkError(self._ALPLib.AlpDevInquire(self.ALP_ID, inquireType, ct.byref(ret)), 'Error sending request.')
        return ret.value()

    def SeqInquire(self, inquireType, SequenceId=None):
        """
        Ask the controller board the value of a specified parameter about an image sequence.


        Usage: Inquire(self, inquireType,  SequenceId = None)

        PARAMETERS
        ----------

        inquireType : ctypes c_ulong
                  Sepcifies the type of value to return.
        SequenceId : ctyles c_long, optional
                     Identified of the sequence. If not specified, set the last sequence allocated in the DMD board memory

        RETURNS
        -------

        value : int
                Value of the requested parameter.


        SEE ALSO
        --------
        See AlpSeqInquire in the ALP API description for request types.
        """
        ret = ct.c_long(0)

        if (SequenceId is None) and (self._lastDDRseq):
            SequenceId = self._lastDDRseq

        self._checkError(self._ALPLib.AlpSeqInquire(self.ALP_ID, SequenceId, inquireType, ct.byref(ret)),
                         'Error sending request.')
        return ret.value

    def ProjInquire(self, inquireType, SequenceId=None):
        """
        Usage: ProjInquire(self, inquireType, SequenceId = None)

        PARAMETERS
        ----------

        request : ctypes c_ulong
                  Sepcifies the type of value to return.
        SequenceId : ctyles c_long, optional
                     Identified of the sequence. If not specified, set the last sequence allocated in the DMD board memory

        RETURNS
        -------

        value : int
                Value of the requested parameter.


        SEE ALSO
        --------
        See AlpProjInquire in the ALP API description for request types.
        """
        ret = ct.c_long(0)

        if (SequenceId is None) and (self._lastDDRseq):
            SequenceId = self._lastDDRseq

        self._checkError(self._ALPLib.AlpProjInquire(self.ALP_ID, SequenceId, inquireType, ct.byref(ret)),
                         'Error sending request.')
        return ret.value

    def ProjInquireEx(self, inquireType, SequenceId=None):
        """
        Data objects that do not fit into a simple 32-bit number can be inquired using this function.
        Meaning and layout of the data depend on the InquireType.

        Usage: ProjInquireEx(self, inquireType, UserStructPtr, SequenceId = None)

        PARAMETERS
        ----------

        inquireType : ctypes c_ulong
                      Sepcifies the type of value to return.
        SequenceId : ctypes c_long, optional
                     Identified of the sequence. If not specified, set the last sequence allocated in the DMD board memory

        RETURNS
        -------

        UserStructPtr : ctypes POINTER
                        Pointer to a data structure which shall be filled out by AlpSeqInquireEx.


        SEE ALSO
        --------
        See AlpProjInquireEx in the ALP API description for request types.
        """
        UserStructPtr = ct.c_double(0)

        if (SequenceId is None) and (self._lastDDRseq):
            SequenceId = self._lastDDRseq

        self._checkError(self._ALPLib.AlpProjInquire(self.ALP_ID, SequenceId, inquireType, ct.byref(UserStructPtr)),
                         'Error sending request.')
        return UserStructPtr

    def DevControl(self, controlType, value):
        """
        This  function  is used to  change  the  display  properties  of  the  ALP.
        The  default  values  are  assigned during device allocation by AllocateSequence.

        Usage: Control(self, controlType, value)

        PARAMETERS
        ----------

        controlType: ctypes c_ulong
                     Specifies the type of value to set.

        SEE ALSO
        --------
        See AlpDevControl in the ALP API description for control types.
        """
        self._checkError(self._ALPLib.AlpDevControl(self.ALP_ID, controlType, ct.c_long(value)),
                         'Error sending request.')

    def DevControlEx(self, controlType, userStruct):
        """
        Data objects that do not fit into a simple 32-bit number can be written using this function. Meaning and
        layout of the data depend on the ControlType.

        Usage: Control(self, controlType, value)

        PARAMETERS
        ----------

        controlType : ctypes c_ulong
                      Specifies the type of value to set.
        userStruct : tAlpDynSynchOutGate structure
                     It contains synch parameters.


        SEE ALSO
        --------

        See AlpDevControlEx in the ALP API description for control types.
        """
        self._checkError(self._ALPLib.AlpDevControlEx(self.ALP_ID, controlType, userStruct.byref()),
                         'Error sending request.')

    def ProjControl(self, controlType, value):
        """
        This function controls the system parameters that are in effect for all sequences. These parameters
        are maintained until they are modified again or until the ALP is freed. Default values are in effect after
        ALP allocation. All parameters can be read out using the AlpProjInquire function.
        This function is only allowed if the ALP is in idle wait state (ALP_PROJ_IDLE), which can be enforced
        by the AlpProjHalt function.

        Usage: Control(self, controlType, value)

        PARAMETERS
        ----------
        controlType : attribute flag (ctypes c_ulong)
                      Specify the paramter to set.

        value : c_double
                Value of the parameter to set.

        SEE ALSO
        --------

        See AlpProjControl in the ALP API description for control types.
        """
        self._checkError(self._ALPLib.AlpProjControl(self.ALP_ID, controlType, ct.c_long(value)),
                         'Error sending request.')

    def ProjControlEx(self, controlType, pointerToStruct):
        """
        Data  objects  that  do  not  fit  into  a  simple  32-bit  number  can  be  written  using  this  function.  These
        objects are unique to the ALP device, so they may affect display of all sequences.
        Meaning and layout of the data depend on the ControlType.

        Usage: Control(self, controlType, value)

        PARAMETERS
        ----------
        controlType : attribute flag (ctypes c_ulong)
            Specify the paramter to set.

        pointerToStruct : ctypes POINTER
            Pointer to a tFlutWrite structure. Create a tFlutWrite object and pass it to the function using ctypes.byref
            (Requires importing ctypes)


        SEE ALSO
        --------
        See AlpProjControlEx in the ALP API description for control types.
        """
        self._checkError(self._ALPLib.AlpProjContro(self.ALP_ID, controlType, pointerToStruct),
                         'Error sending request.')

    def SeqControl(self, controlType, value, SequenceId=None):
        """
        This function is used to change the display properties of a sequence.
        The default values are assigned during sequence allocation by AlpSeqAlloc.
        It  is  allowed  to  change  settings  of  sequences  that  are  currently  in  use.
        However  the  new  settings become effective after restart using AlpProjStart or AlpProjStartCont.

        Usage: SeqControl(self, controlType, value,  SequenceId = None)

        PARAMETERS
        ----------

        controlType : attribute flag (ctypes c_ulong)
            Specify the paramter to set.

        value : ctypes c_double
                Value of the parameter to set.

        SequenceId : ctypes c_long, optional
                     Identified of the sequence. If not specified, set the last sequence allocated in the DMD board memory


        SEE ALSO
        --------

        See AlpSeqControl in the ALP API description for control types.
        """

        if (SequenceId is None) and (self._lastDDRseq):
            SequenceId = self._lastDDRseq

        self._checkError(self._ALPLib.AlpSeqControl(self.ALP_ID, SequenceId, controlType, ct.c_long(value)),
                         'Error sending request.')

    def FreeSeq(self, SequenceId=None):
        """
        Frees a previously allocated sequence. The ALP memory reserved for the specified sequence in the device DeviceId is released.


        Usage: FreeSeq(SequenceId = None)

        PARAMETERS
        ----------

        SequenceId : ctypes c_long, optional
                     Identified of the sequence. If not specified, free the last sequence allocated in the DMD board memory
        """

        if (SequenceId is None) and (self._lastDDRseq):
            SequenceId = self._lastDDRseq

        self.Seqs.remove(SequenceId)  # Removes the last SequenceId from sequence list
        self._checkError(self._ALPLib.AlpSeqFree(self.ALP_ID, SequenceId), 'Unable to free the image sequence.',
                         warning=True)

    def Run(self, SequenceId=None, loop=True):
        """
        Display a sequence loaded into the DDR memory.

        Usage: Run( SequenceId = None, loop = True)

        PARAMETERS
        ----------

        SequenceId : ctypes c_ulong
                     Id of the sequence to run.
                     If no sequence pointer is given, display the last sequence stored.
        loop : bool
               If True, display the sequence continuously using ALPLib.AlpProjStartCont.
               If False, display it once using ALPLib.AlpProjStart. Set to True by default.

        SEE ALSO
        --------
        See ALPLib.AlpProjStart and ALPLib.AlpProjStartCont in the ALP API description for more information.
        """
        if (SequenceId is None) and (self._lastDDRseq):
            SequenceId = self._lastDDRseq
        if (SequenceId is None):
            self._raiseError('No sequence to display.')

        if loop:
            self._checkError(self._ALPLib.AlpProjStartCont(self.ALP_ID, SequenceId), 'Cannot launch sequence.')
        else:
            self._checkError(self._ALPLib.AlpProjStart(self.ALP_ID, SequenceId), 'Cannot launch sequence.')

    def Wait(self):
        """
        This function is used to wait for the completion of the running sequence display.

        Usage: Wait()
        """
        self._checkError(self._ALPLib.AlpProjWait(self.ALP_ID), 'Cannot go in wait mode.')

    def Halt(self):
        """
        This   function   puts   the   ALP   in   an   idle   wait   state.   Current   sequence   display   is   canceled
        (ALP_PROJ_IDLE) and the loading of sequences is aborted (AlpSeqPut).

        Usage: Halt()
        """
        self._checkError(self._ALPLib.AlpDevHalt(self.ALP_ID), 'Cannot stop device.')

    def Free(self):
        """
        This  function  de-allocates  a  previously  allocated  ALP  device.  The  memory  reserved  by  calling
        AlpSeqAlloc is also released.
        The ALP has to be in idle wait state, see also AlpDevHalt.

        Usage: Free()
        """
        self._checkError(self._ALPLib.AlpDevFree(self.ALP_ID), 'Cannot free device.')
        del self._ALPLib
