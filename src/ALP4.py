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

## Standard parameter
ALP_DEFAULT = 0

## Return codes
ALP_OK = 0x00000000  # Successfull execution
ALP_NOT_ONLINE = 1001  # The specified ALP has not been found or is not ready.

##	parameters ##

## AlpDevInquire 

ALP_DEVICE_NUMBER = 2000  # Serial number of the ALP device
ALP_VERSION = 2001  # Version number of the ALP device
ALP_DEV_STATE = 2002  # current ALP status, see above
ALP_AVAIL_MEMORY = 2003  # ALP on-board sequence memory available for further sequence
#	allocation (AlpSeqAlloc); number of binary pictures
# Temperatures. Data format: signed long with 1 LSB=1/256 degrees C 
ALP_DDC_FPGA_TEMPERATURE = 2050  # V4100 Rev B: LM95231. External channel: DDC FPGAs Temperature Diode
ALP_APPS_FPGA_TEMPERATURE = 2051  # V4100 Rev B: LM95231. External channel: Application FPGAs Temperature Diode
ALP_PCB_TEMPERATURE = 2052  # V4100 Rev B: LM95231. Internal channel. "Board temperature"

#	AlpDevControl - ControlTypes & ControlValues 
ALP_SYNCH_POLARITY = 2004  # Select frame synch output signal polarity
ALP_TRIGGER_EDGE = 2005  # Select active input trigger edge (slave mode)
ALP_LEVEL_HIGH = 2006  # Active high synch output
ALP_LEVEL_LOW = 2007  # Active low synch output
ALP_EDGE_FALLING = 2008  # High to low signal transition
ALP_EDGE_RISING = 2009  # Low to high signal transition

ALP_TRIGGER_TIME_OUT = 2014  # trigger time-out (slave mode)
ALP_TIME_OUT_ENABLE = 0  # Time-out enabled (default)
ALP_TIME_OUT_DISABLE = 1  # Time-out disabled */

ALP_USB_CONNECTION = 2016  # Re-connect after a USB interruption

ALP_DEV_DMDTYPE = 2021  # Select DMD type; only allowed for a new allocated ALP-3 device
ALP_DMDTYPE_XGA = 1  # 1024*768 mirror pixels (0.7" Type A, D3000)
ALP_DMDTYPE_SXGA_PLUS = 2  # 1400*1050 mirror pixels (0.95" Type A, D3000)
ALP_DMDTYPE_1080P_095A = 3  # 1920*1080 mirror pixels (0.95" Type A, D4x00)
ALP_DMDTYPE_XGA_07A = 4  # 1024*768 mirror pixels (0.7" Type A, D4x00)
ALP_DMDTYPE_XGA_055A = 5  # 1024*768 mirror pixels (0.55" Type A, D4x00)
ALP_DMDTYPE_XGA_055X = 6  # 1024*768 mirror pixels (0.55" Type X, D4x00)
ALP_DMDTYPE_WUXGA_096A = 7  # 1920*1200 mirror pixels (0.96" Type A, D4100)
ALP_DMDTYPE_WQXGA_400MHZ_090A = 8  # 2560*1600 mirror pixels (0.90" Type A, DLPC910) at standard clock rate (400 MHz)
ALP_DMDTYPE_WQXGA_480MHZ_090A = 9  # WQXGA at extended clock rate (480 MHz); WARNING: This mode requires temperature control of DMD
ALP_DMDTYPE_WXGA_S450 = 12  # # 1280x800 (DLP650LNIR WXGA S450)
ALP_DMDTYPE_DISCONNECT = 255  # behaves like 1080p (D4100)

ALP_DEV_DISPLAY_HEIGHT = 2057  # number of mirror rows on the DMD
ALP_DEV_DISPLAY_WIDTH = 2058  # number of mirror columns on the DMD

ALP_DEV_DMD_MODE = 2064  # query/set DMD PWR_FLOAT mode, valid options: ALP_DMD_RESUME (normal operation: "wake up DMD"), ALP_DMD_POWER_FLOAT
ALP_DMD_RESUME = 0  # default mode, Wake up DMD; Auto-Shutdown on loss of supply voltage safely switches off DMD
ALP_DMD_POWER_FLOAT = 1  # power down, release micro mirrors from deflected state

ALP_PWM_LEVEL = 2063  # PWM pin duty-cycle as percentage: 0..100%; after AlpDevAlloc: 0%

# AlpDevControlEx 
ALP_DEV_DYN_SYNCH_OUT1_GATE = 2023
ALP_DEV_DYN_SYNCH_OUT2_GATE = 2024
ALP_DEV_DYN_SYNCH_OUT3_GATE = 2025


class tAlpDynSynchOutGate(ct.Structure):
    # For ControlType ALP_DEV_DYN_TRIG_OUT[1..3]_GATE of function AlpDevControlEx
    # Configure compiler to not insert padding bytes! (e.g. #pragma pack)
    _fields_ = [("Period", ct.c_ubyte),  # Period=1..16 enables output; 0: tri-state
                ("Polarity", ct.c_ubyte),  # 0: active pulse is low, 1: high
                ("Gate", ct.c_ubyte * 16)]  # #Period number of bytes; each one is 0 or 1
    # Period bytes are used!


# AlpSeqControl - ControlTypes
ALP_SEQ_REPEAT = 2100  # Non-continuous display of a sequence (AlpProjStart) allows
#	for configuring the number of sequence iterations.
ALP_SEQ_REPETE = ALP_SEQ_REPEAT  # According to the typo made in primary documentation (ALP API description)
ALP_FIRSTFRAME = 2101  # First image of this sequence to be displayed.
ALP_LASTFRAME = 2102  # Last image of this sequence to be displayed.

ALP_BITNUM = 2103  # A sequence can be displayed with reduced bit depth for faster speed.
ALP_BIN_MODE = 2104  # Binary mode: select from ALP_BIN_NORMAL and ALP_BIN_UNINTERRUPTED (AlpSeqControl)

ALP_BIN_NORMAL = 2105  # Normal operation with progammable dark phase
ALP_BIN_UNINTERRUPTED = 2106  # Operation without dark phase

ALP_PWM_MODE = 2107  # ALP_DEFAULT, ALP_FLEX_PWM
ALP_FLEX_PWM = 3  # ALP_PWM_MODE: all bit planes of the sequence are displayed as
#	fast as possible in binary uninterrupted mode;
#	use ALP_SLAVE mode to achieve a custom pulse-width modulation timing for generating gray-scale 

ALP_DATA_FORMAT = 2110  # Data format and alignment
ALP_DATA_MSB_ALIGN = 0  # Data is MSB aligned (default)
ALP_DATA_LSB_ALIGN = 1  # Data is LSB aligned
ALP_DATA_BINARY_TOPDOWN = 2  # Data is packed binary, top row first; bit7 of a byte = leftmost of 8 pixels
ALP_DATA_BINARY_BOTTOMUP = 3  # Data is packed binary, bottom row first
# XGA:   one pixel row occupies 128 byte of binary data.
#        Byte0.Bit7 = top left pixel (TOPDOWN format)
# 1080p and WUXGA: one pixel row occupies 256 byte of binary data.
#        Byte0.Bit7 = top left pixel (TOPDOWN format)
# SXGA+: one pixel row occupies 176 byte of binary data. First byte ignored.
#        Byte1.Bit7 = top left pixel (TOPDOWN format)

ALP_SEQ_PUT_LOCK = 2119  # ALP_DEFAULT: Lock Sequence Memory in AlpSeqPut;
#	Not ALP_DEFAULT: do not lock, instead allow writing sequence image data even currently displayed 


ALP_FIRSTLINE = 2111  # Start line position at the first image
ALP_LASTLINE = 2112  # Stop line position at the last image
ALP_LINE_INC = 2113  # Line shift value for the next frame
ALP_SCROLL_FROM_ROW = 2123  # combined value from ALP_FIRSTFRAME and ALP_FIRSTLINE
ALP_SCROLL_TO_ROW = 2124  # combined value from ALP_LASTFRAME and ALP_LASTLINE

#	Frame Look Up Table (FLUT): sequence settings select how to use the FLUT.
#	The look-up table itself is shared across all sequences.
#	(use ALP_FLUT_SET_MEMORY controls for accessing it) 
ALP_FLUT_MODE = 2118  # Select Frame LookUp Table usage mode:
ALP_FLUT_NONE = 0  # linear addressing, do not use FLUT (default)
ALP_FLUT_9BIT = 1  # Use FLUT for frame addressing: 9-bit entries
ALP_FLUT_18BIT = 2  # Use FLUT for frame addressing: 18-bit entries

ALP_FLUT_ENTRIES9 = 2120  # Determine number of FLUT entries; default=1
#	Entries: supports all values from 1 to ALP_FLUT_MAX_ENTRIES9 
ALP_FLUT_OFFSET9 = 2122  # Determine offset of FLUT index; default=0
#	Offset supports multiples of 256;
#	For ALP_FLUT_18BIT, the effective index is half of the 9-bit index.
#	--> "ALP_FLUT_ENTRIES18" and "ALP_FLUT_FRAME_OFFSET18" are 9-bit settings divided by 2 
#	The API does not reject overflow! (FRAME_OFFSET+ENTRIES > MAX_ENTRIES).
#	The user is responsible for correct settings. 

ALP_SEQ_DMD_LINES = 2125  # Area of Interest: Value = MAKELONG(StartRow, RowCount)


def MAKELONG(StartRow, RowCount):
    return StartRow + RowCount << 16


#  AlpSeqInquire
ALP_BITPLANES = 2200  # Bit depth of the pictures in the sequence
ALP_PICNUM = 2201  # Number of pictures in the sequence
ALP_PICTURE_TIME = 2203  # Time between the start of consecutive pictures in the sequence in microseconds,
#	the corresponding in frames per second is
#	picture rate [fps] = 1 000 000 / ALP_PICTURE_TIME [µs]
ALP_ILLUMINATE_TIME = 2204  # Duration of the display of one picture in microseconds
ALP_SYNCH_DELAY = 2205  # Delay of the start of picture display with respect
#	to the frame synch output (master mode) in microseconds
ALP_SYNCH_PULSEWIDTH = 2206  # Duration of the active frame synch output pulse in microseconds
ALP_TRIGGER_IN_DELAY = 2207  # Delay of the start of picture display with respect to the
#	active trigger input edge in microseconds
ALP_MAX_SYNCH_DELAY = 2209  # Maximal duration of frame synch output to projection delay in microseconds
ALP_MAX_TRIGGER_IN_DELAY = 2210  # Maximal duration of trigger input to projection delay in microseconds

ALP_MIN_PICTURE_TIME = 2211  # Minimum time between the start of consecutive pictures in microseconds
ALP_MIN_ILLUMINATE_TIME = 2212  # Minimum duration of the display of one picture in microseconds
#	depends on ALP_BITNUM and ALP_BIN_MODE
ALP_MAX_PICTURE_TIME = 2213  # Maximum value of ALP_PICTURE_TIME

#	ALP_PICTURE_TIME = ALP_ON_TIME + ALP_OFF_TIME
#	ALP_ON_TIME may be smaller than ALP_ILLUMINATE_TIME
ALP_ON_TIME = 2214  # Total active projection time
ALP_OFF_TIME = 2215  # Total inactive projection time

#  AlpProjInquire & AlpProjControl & ...Ex - InquireTypes, ControlTypes & Values */
ALP_PROJ_MODE = 2300  # Select from ALP_MASTER and ALP_SLAVE mode */
ALP_MASTER = 2301  # The ALP operation is controlled by internal */
#	timing, a synch signal is sent out for any */
#	picture displayed */
ALP_SLAVE = 2302  # The ALP operation is controlled by external */
#	trigger, the next picture in a sequence is */
#	displayed after the detection of an external */
#	input trigger signal. */
ALP_PROJ_STEP = 2329  # ALP operation should run in ALP_MASTER mode,
#											but each frame is repeatedly displayed
#											until a trigger event is received.
#											Values (conditions): ALP_LEVEL_HIGH |
#											LOW, ALP_EDGE_RISING | FALLING.
#											ALP_DEFAULT disables the trigger and
#											makes the sequence progress "as usual".
#											If an event is "stored" in edge mode due
#											to a past edge, then it will be
#											discarded during
#											AlpProjControl(ALP_PROJ_STEP). */
ALP_PROJ_SYNC = 2303  # Select from ALP_SYNCHRONOUS and ALP_ASYNCHRONOUS mode */
ALP_SYNCHRONOUS = 2304  # The calling program gets control back after completion */
#	of sequence display. */
ALP_ASYNCHRONOUS = 2305  # The calling program gets control back immediatelly. */

ALP_PROJ_INVERSION = 2306  # Reverse dark into bright */
ALP_PROJ_UPSIDE_DOWN = 2307  # Turn the pictures upside down */

ALP_PROJ_STATE = 2400  # Inquire only */

ALP_FLUT_MAX_ENTRIES9 = 2324  # Inquire FLUT size */
# Transfer FLUT memory to ALP. Use AlpProjControlEx and pUserStructPtr of type tFlutWrite. */
ALP_FLUT_WRITE_9BIT = 2325  # 9-bit look-up table entries */
ALP_FLUT_WRITE_18BIT = 2326  # 18-bit look-up table entries  */


# for ALP_FLUT_WRITE_9BIT, ALP_FLUT_WRITE_18BIT (both versions share the same data type),
# to be used with AlpProjControlEx */
class tFlutWrite(ct.Structure):
    _fields_ = [("nOffset", ct.c_long),  # first LUT entry to transfer (write FrameNumbers[0] to LUT[nOffset]):
                # number of 9-bit or 18-bit entries to transfer;
                # For nSize=ALP_DEFAULT(0) the API sets nSize to its maximum value. This
                # requires nOffset=0
                ("nSize", ct.c_long),
                # nOffset+nSize must not exceed ALP_FLUT_MAX_ENTRIES9 (ALP_FLUT_WRITE_9BIT)
                # or ALP_FLUT_MAX_ENTRIES9/2 (ALP_FLUT_WRITE_18BIT).

                # The ALP API reads only the first nSize entries from this array. It
                # extracts 9 or 18 least significant bits from each entry.
                ("FrameNumbers", ct.c_ulong * 4096)]


## Sequence Queue API Extension:
ALP_PROJ_QUEUE_MODE = 2314
ALP_PROJ_LEGACY = 0  # ALP_DEFAULT: emulate legacy mode: 1 waiting position. AlpProjStart replaces enqueued and still waiting sequences */
ALP_PROJ_SEQUENCE_QUEUE = 1  # manage active sequences in a queue */

ALP_PROJ_QUEUE_ID = 2315  # provide the QueueID (ALP_ID) of the most recently enqueued sequence (or ALP_INVALID_ID) */
ALP_PROJ_QUEUE_MAX_AVAIL = 2316  # total number of waiting positions in the sequence queue */
ALP_PROJ_QUEUE_AVAIL = 2317  # number of available waiting positions in the queue */
#	   bear in mind that when a sequence runs, it is already dequeued and does not consume a waiting position any more */
ALP_PROJ_PROGRESS = 2318  # (AlpProjInquireEx) inquire detailled progress of the running sequence and the queue */
ALP_PROJ_RESET_QUEUE = 2319  # Remove all enqueued sequences from the queue. The currently running sequence is not affected. ControlValue must be ALP_DEFAULT */
ALP_PROJ_ABORT_SEQUENCE = 2320  # abort the current sequence (ControlValue=ALP_DEFAULT) or a specific sequence (ControlValue=QueueID); abort after last frame of current iteration */
ALP_PROJ_ABORT_FRAME = 2321  # similar, but abort after next frame */
#	  	Only one abort request can be active at a time. If it is requested to
#		abort another sequence before the old request is completed, then
#		AlpProjControl returns ALP_NOT_IDLE. (Please note, that AlpProjHalt
#		and AlpDevHalt work anyway.) If the QueueID points to a sequence
#		behind an indefinitely started one (AlpProjStartCont) then it returns
#		ALP_PARM_INVALID in order to prevent dead-locks. */
ALP_PROJ_WAIT_UNTIL = 2323  # When does AlpProjWait complete regarding the last frame? or after picture time of last frame */
ALP_PROJ_WAIT_PIC_TIME = 0  # ALP_DEFAULT: AlpProjWait returns after picture time */
ALP_PROJ_WAIT_ILLU_TIME = 1  # AlpProjWait returns after illuminate time (except binary uninterrupted sequences, because an "illuminate time" is not applicable there) */


# for AlpProjInquireEx(ALP_PROJ_PROGRESS):
class tAlpProjProgress(ct.Structure):
    _fields_ = [("CurrentQueueId", ct.c_ulong),
                ("SequenceId", ct.c_ulong),  # Consider that a sequence can be enqueued multiple times!
                ("nWaitingSequences", ct.c_ulong),  # number of sequences waiting in the queue
                # track iterations and frames: device-internal counters are incompletely
                # reported; The API description contains more details on that.
                ("nSequenceCounter", ct.c_ulong),  # Number of iterations to be done
                ("nSequenceCounterUnderflow", ct.c_ulong),  # nSequenceCounter can
                # underflow (for indefinitely long Sequences: AlpProjStartCont);
                # nSequenceCounterUnderflow is 0 before, and non-null afterwards
                ("nFrameCounter", ct.c_ulong),  # Frames left inside current iteration
                ("nPictureTime", ct.c_ulong),  # micro seconds of each frame; this is
                # reported, because the picture time of the original sequence could
                # already have changed in between
                ("nFramesPerSubSequence", ct.c_ulong),  # Each sequence iteration
                # displays this number of frames. It is reported to the user just for
                # convenience, because it depends on different parameters. */
                ("nFlagse", ct.c_ulong)]
    # may be a combination of ALP_FLAG_SEQUENCE_ABORTING | SEQUENCE_INDEFINITE | QUEUE_IDLE | FRAME_FINISHED


ALP_FLAG_QUEUE_IDLE = ct.c_ulong(1)
ALP_FLAG_SEQUENCE_ABORTING = ct.c_ulong(2)
ALP_FLAG_SEQUENCE_INDEFINITE = ct.c_ulong(4)  # AlpProjStartCont: this sequence runs indefinitely long, until aborted
ALP_FLAG_FRAME_FINISHED = ct.c_ulong(8)  # illumination of last frame finished, picture time still progressing
ALP_FLAG_RSVD0 = ct.c_ulong(16)  # reserved


# for AlpSeqPutEx():
class tAlpLinePut(ct.Structure):
    _fields_ = [("TransferMode", ct.c_long),  # common first member of AlpSeqPutEx' UserStructPtr argument
                ("PicOffset", ct.c_long),
                ("PicLoad", ct.c_long),
                ("LineOffset", ct.c_long),
                ("LineLoad", ct.c_long)]


ALP_PUT_LINES = ct.c_long(1)  # not ulong; need to be long in the tAlpLinePut struct

ALP_ERRORS = {1001: 'The specified ALP device has not been found or is not ready.',
              1002: 'The ALP device is not in idle state.',
              1003: 'The specified ALP device identifier is not valid.',
              1004: 'The specified ALP device is already allocated.',
              1005: 'One of the parameters is invalid.',
              1006: 'Error accessing user data.',
              1007: 'The requested memory is not available (full?).',
              1008: 'The sequence specified is currently in use.',
              1009: 'The ALP device has been stopped while image data transfer was active.',
              1010: 'Initialization error.',
              1011: 'Communication error.',
              1012: 'The specified ALP has been removed.',
              1013: 'The onboard FPGA is unconfigured.',
              1014: 'The function is not supported by this version of the driver file VlxUsbLd.sys.',
              1018: 'Waking up the DMD from PWR_FLOAT did not work (ALP_DMD_POWER_FLOAT)',
              1019: 'Support in ALP drivers missing. Update drivers and power-cycle device.',
              1020: 'SDRAM Initialization failed.'}


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

        if (self.DMDType.value == ALP_DMDTYPE_XGA or self.DMDType.value == ALP_DMDTYPE_XGA_055A or self.DMDType.value == ALP_DMDTYPE_XGA_055X or self.DMDType.value == ALP_DMDTYPE_XGA_07A):
            self.nSizeX = 1024
            self.nSizeY = 768
        elif (self.DMDType.value == ALP_DMDTYPE_SXGA_PLUS):
            self.nSizeX = 1400
            self.nSizeY = 1050
        elif (self.DMDType.value == ALP_DMDTYPE_DISCONNECT or self.DMDType.value == ALP_DMDTYPE_1080P_095A):
            self.nSizeX = 1920
            self.nSizeY = 1080
        elif (self.DMDType.value == ALP_DMDTYPE_WUXGA_096A):
            self.nSizeX = 1920
            self.nSizeY = 1200
        elif (self.DMDType.value == ALP_DMDTYPE_WQXGA_400MHZ_090A or self.DMDType.value == ALP_DMDTYPE_WQXGA_480MHZ_090A):
            self.nSizeX = 2560
            self.nSizeY = 1600
        elif (self.DMDType.value == ALP_DMDTYPE_WXGA_S450):
            self.nSizeX = 1280
            self.nSizeY = 800
        else:
            print("Unknown DMDtype with value ", self.DMDType.value)
            raise EnvironmentError("DMD Type not supported or unknown.")

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
        For a bit depth = 8, 8 bit planes can be extracted from the imgArray bu iterating ImgToBitPlane.

        WARNING: This function is slow. It is advised not to use it in a loop to convert a sequence
        of image arrays to bit planes. Use for tests only. It is recommended to directly generate images
        as bitplanes.

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
        bitPlane = [0] * (self.nSizeX * self.nSizeY // 8)
        for ind, value in enumerate(imgArray):
            bitPlane[(ind - ind % 8) // 8] += (2 ** (7 - ind % 8)) * ((int(value) >> bitShift) % 2)
        return bitPlane

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
