#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Wed Oct 05 15:48:53 2016

@author: Sebastien Popoff
"""

import ctypes as ct
import platform

class ALP4():
    """
    This class controls a Vialux DMD board based on the Vialux ALP 4.X API.
    """    
    
    def __init__(self, version = '4.3', pathDir = './'):
        
        os_type = platform.system()
        libPath = pathDir
        ## Load the ALP dll
        if (os_type == 'Windows'):
            if (ct.sizeof(ct.c_voidp) == 8):     ## 64bit    
                libPath += 'x64/'
            elif not (ct.sizeof(ct.c_voidp) == 4):  ## 32bit
                self._raiseError('System not supported.')
        else:
            self._raiseError('System not supported.')
            
        if (version == '4.1'):
            libPath += 'alpD41.dll'
        elif (version == '4.2'):
            libPath += 'alpD41.dll'
        elif (version == '4.3'):
            libPath += 'alp4395.dll'
            
        print('Loading linrary: ' + libPath)
        self._ALPLib = ct.CDLL(libPath)   
            


        
        ## Standard parameter
        self._ALP_DEFAULT       = 0L  
        
        ## Return codes
        self._ALP_OK = 0x00000000L       # Successfull execution 
        self._ALP_NOT_ONLINE         = 1001L		#	The specified ALP has not been found or is not ready. 
        
        ##	parameters ##

        ## AlpDevInquire 
        
        self._ALP_DEVICE_NUMBER = 2000L	#	Serial number of the ALP device */
        self._ALP_VERSION = 2001L	#	Version number of the ALP device */
        self._ALP_DEV_STATE =			2002L	#	current ALP status, see above */
        self._ALP_AVAIL_MEMORY =		2003L	#	ALP on-board sequence memory available for further sequence */
        										#	allocation (AlpSeqAlloc); number of binary pictures */
        # Temperatures. Data format: signed long with 1 LSB=1/256 degrees C */
        self._ALP_DDC_FPGA_TEMPERATURE =	2050L	# V4100 Rev B: LM95231. External channel: DDC FPGAs Temperature Diode */
        self._ALP_APPS_FPGA_TEMPERATURE	 = 2051L	# V4100 Rev B: LM95231. External channel: Application FPGAs Temperature Diode */
        self._ALP_PCB_TEMPERATURE = 		2052L	# V4100 Rev B: LM95231. Internal channel. "Board temperature" */
        
        #	AlpDevControl - ControlTypes & ControlValues */
        self._ALP_SYNCH_POLARITY	= 2004L	#  Select frame synch output signal polarity */
        self._ALP_TRIGGER_EDGE =		2005L	#  Select active input trigger edge (slave mode) */
        self._ALP_LEVEL_HIGH	 =		2006L	#  Active high synch output */
        self._ALP_LEVEL_LOW	=		2007L	#  Active low synch output */
        self._ALP_EDGE_FALLING =		2008L	#  High to low signal transition */
        self._ALP_EDGE_RISING =		2009L	#  Low to high signal transition */
        
        self._ALP_TRIGGER_TIME_OUT =	2014L	#	trigger time-out (slave mode) */
        self._ALP_TIME_OUT_ENABLE 	=   0L	#	Time-out enabled (default) */
        self._ALP_TIME_OUT_DISABLE =	   1L	#	Time-out disabled */
        
        self._ALP_USB_CONNECTION =		2016L	#	Re-connect after a USB interruption */
        
        self._ALP_DEV_DMDTYPE =			2021L	#	Select DMD type; only allowed for a new allocated ALP-3 device */
        self._ALP_DMDTYPE_XGA =			   1L	#	1024*768 mirror pixels (0.7" Type A, D3000) */
        self._ALP_DMDTYPE_SXGA_PLUS =	   2L	#	1400*1050 mirror pixels (0.95" Type A, D3000) */
        self._ALP_DMDTYPE_1080P_095A =	   3L	#	1920*1080 mirror pixels (0.95" Type A, D4x00) */
        self._ALP_DMDTYPE_XGA_07A	=	   4L	#	1024*768 mirror pixels (0.7" Type A, D4x00) */
        self._ALP_DMDTYPE_XGA_055A	 =  5L	#	1024*768 mirror pixels (0.55" Type A, D4x00) */
        self._ALP_DMDTYPE_XGA_055X	 =  6L	#	1024*768 mirror pixels (0.55" Type X, D4x00) */
        self._ALP_DMDTYPE_WUXGA_096A =	   7L	#	1920*1200 mirror pixels (0.96" Type A, D4100) */
        self._ALP_DMDTYPE_WQXGA_400MHZ_090A = 8L #	2560*1600 mirror pixels (0.90" Type A, DLPC910) at standard clock rate (400 MHz) */
        self._ALP_DMDTYPE_WQXGA_480MHZ_090A = 9L #	WQXGA at extended clock rate (480 MHz); WARNING: This mode requires temperature control of DMD */
        self._ALP_DMDTYPE_DISCONNECT = 255L	#	behaves like 1080p (D4100) */
        
        self._ALP_DEV_DISPLAY_HEIGHT = 2057L	# number of mirror rows on the DMD */
        self._ALP_DEV_DISPLAY_WIDTH = 2058L	# number of mirror columns on the DMD */
        
        self._ALP_DEV_DMD_MODE = 2064L	# query/set DMD PWR_FLOAT mode, valid options: ALP_DMD_RESUME (normal operation: "wake up DMD"), ALP_DMD_POWER_FLOAT */
        self._ALP_DMD_RESUME	=         0L	# default mode, Wake up DMD; Auto-Shutdown on loss of supply voltage safely switches off DMD */
        self._ALP_DMD_POWER_FLOAT =         1L	# power down, release micro mirrors from deflected state */
        
        self._ALP_PWM_LEVEL = 		2063L	# PWM pin duty-cycle as percentage: 0..100%; after AlpDevAlloc: 0% */

        #  AlpSeqInquire */
        self._ALP_BITPLANES =			2200L	#	Bit depth of the pictures in the sequence */
        self._ALP_PICNUM	=			2201L	#	Number of pictures in the sequence */
        self._ALP_PICTURE_TIME =		2203L	#	Time between the start of consecutive pictures in the sequence in microseconds, */
        										#	the corresponding in frames per second is */
        										#	picture rate [fps] = 1 000 000 / ALP_PICTURE_TIME [µs] */
        self._ALP_ILLUMINATE_TIME =		2204L	#	Duration of the display of one picture in microseconds */
        self._ALP_SYNCH_DELAY =			2205L	#	Delay of the start of picture display with respect */
        										#	to the frame synch output (master mode) in microseconds */
        self._ALP_SYNCH_PULSEWIDTH =	2206L	#	Duration of the active frame synch output pulse in microseconds */
        self._ALP_TRIGGER_IN_DELAY =	2207L	#	Delay of the start of picture display with respect to the */
        										#	active trigger input edge in microseconds */
        self._ALP_MAX_SYNCH_DELAY =		2209L	#	Maximal duration of frame synch output to projection delay in microseconds */
        self._ALP_MAX_TRIGGER_IN_DELAY =	2210L	#	Maximal duration of trigger input to projection delay in microseconds */
        
        self._ALP_MIN_PICTURE_TIME =	2211L	#	Minimum time between the start of consecutive pictures in microseconds */
        self._ALP_MIN_ILLUMINATE_TIME =	2212L	#	Minimum duration of the display of one picture in microseconds */
        										#	depends on ALP_BITNUM and ALP_BIN_MODE */
        self._ALP_MAX_PICTURE_TIME =	2213L	#	Maximum value of ALP_PICTURE_TIME */
        
        										#	ALP_PICTURE_TIME = ALP_ON_TIME + ALP_OFF_TIME */
        										#	ALP_ON_TIME may be smaller than ALP_ILLUMINATE_TIME */
        self._ALP_ON_TIME =				2214L	#	Total active projection time */
        self._ALP_OFF_TIME =			2215L	#	Total inactive projection time */

        self._ALP_ERRORS = {1001L:'The specified ALP device has not been found or is not ready.',
                            1002L:'The ALP device is not in idle state.',
                            1003L:'The specified ALP device identifier is not valid.',
                            1004L:'The specified ALP device is already allocated.',
                            1005L:'One of the parameters is invalid.',
                            1006L:'Error accessing user data.',
                            1007L:'The requested memory is not available (full?).',
                            1008L:'The sequence specified is currently in use.',
                            1009L:'The ALP device has been stopped while image data transfer was active.',
                            1010L:'Initialization error.',
                            1011L:'Communication error.',
                            1012L:'The specified ALP has been removed.',
                            1013L:'The onboard FPGA is unconfigured.',
                            1014L:'The function is not supported by this version of the driver file VlxUsbLd.sys.',
                            1018L:'Waking up the DMD from PWR_FLOAT did not work (ALP_DMD_POWER_FLOAT)',
                            1019L:'Support in ALP drivers missing. Update drivers and power-cycle device.',
                            1020L:'SDRAM Initialization failed.'}
        
        ## Class parameters
        # ID of the current ALP device
        self.ALP_ID = ct.c_long(0)
        # Type of DMD found
        self.DMDType = ct.c_long(0)
        # Pointer to the last stored image sequence
        self._lastDDRseq = None
        # Delay sync
        self._synchDelay = self._ALP_DEFAULT 
        # Duration of the pulse for output trigger
        self._synchPulseWidth = self._ALP_DEFAULT
        # Time between the incoming trigger edge and the start of the display (slave mode)
        self._triggerInDelay = self._ALP_DEFAULT
        
        
    def _checkError(self, returnValue, errorString):
        if not (returnValue == self._ALP_OK):
            raise Exception(errorString+'\n'+self._ALP_ERRORS[returnValue])
        
    def Initialize(self, DeviceNum = None):
        '''
        Initialize the communication with the DMD.        
        
        Usage:
        Initialize(DeviceNum = None)
        DeviceNum:  Serial number of the DMD to initialize, useful for multiple DMD control.
                    If not specify, open the first available DMD.
        '''
        if DeviceNum == None:
            DeviceNum = ct.c_long(self._ALP_DEFAULT)       
 
        self._checkError(self._ALPLib.AlpDevAlloc(DeviceNum,self._ALP_DEFAULT,ct.byref(self.ALP_ID)),'Cannot open DMD.')
        
        self._checkError(self._ALPLib.AlpDevInquire(self.ALP_ID, self._ALP_DEV_DMDTYPE, ct.byref(self.DMDType)),'Inquery fails.')
            
        if (self.DMDType.value == self._ALP_DMDTYPE_XGA or self.DMDType.value == self._ALP_DMDTYPE_XGA_055A or self.DMDType.value == self._ALP_DMDTYPE_XGA_055X or self.DMDType.value == self._ALP_DMDTYPE_XGA_07A):
            self.nSizeX = 1024; self.nSizeY = 768
        elif (self.DMDType.value ==  self._ALP_DMDTYPE_SXGA_PLUS):
		self.nSizeX = 1400; self.nSizeY = 1050
        elif (self.DMDType.value == self._ALP_DMDTYPE_DISCONNECT or self.DMDType.value == self._ALP_DMDTYPE_1080P_095A):
		self.nSizeX = 1920; self.nSizeY = 1080
        elif (self.DMDType.value == self._ALP_DMDTYPE_WUXGA_096A):
		self.nSizeX = 1920; self.nSizeY = 1200
        elif (self.DMDType.value == self._ALP_DMDTYPE_WQXGA_400MHZ_090A or self.DMDType.value == self._ALP_DMDTYPE_WQXGA_480MHZ_090A):
           self.nSizeX = 2560; self.nSizeY = 1600
        else:
            self._raiseError("DMD Type not supported or unknown.")

        print 'DMD found, resolution = ', self.nSizeX, 'x', self.nSizeY, '.'
            
       
    def AllocateSequence(self, imgData, nbImg = 1, bitDepth = 1):
        '''
        Allocate memory on the DDR RAM for the sequence of image. 
        Data values has to be between 0 and 128(?).
        
        Usage:
        AllocateSequence(imgData, nbImg = 1, bitDepth = 1)
        imgData: Data stream (list, 1D array or 1D numpyarray) corresponding to a sequence of nSizeX by nSizeX images.
        nbImg: Number of images in the sequence
        bitDepth: Quantization of the image between 1 (on/off) and 8 (256 pwm levels).
        '''

        data = ''.join(chr(int(x)) for x in imgData)
        pImageData = ct.cast(ct.create_string_buffer(data,nbImg*self.nSizeX*self.nSizeY),ct.c_void_p)    

        DDRseq_pointer = ct.c_long(0)
        # Allocate memory on the DDR RAM for the sequence of image.
        self._ALPLib.AlpSeqAlloc(self.ALP_ID, ct.c_long(bitDepth), ct.c_long(nbImg), ct.byref(DDRseq_pointer))
        
        # Load the data into memory, here we load everythong, so we start at image 0 for nbImg images.
#        if not (self._ALPLib.AlpSeqPut(self.ALP_ID, DDRseq_pointer, 0, nbImg, pImageData) == self._ALP_OK):
#            self._raiseError('Cannot allocate image sequence.')

        self._checkError(self._ALPLib.AlpSeqPut(self.ALP_ID, DDRseq_pointer, 0, nbImg, pImageData),'Cannot allocate image sequence.')

        self._lastDDRseq = DDRseq_pointer
        return DDRseq_pointer
        
    def SetTiming(self, DDRseq_pointer = None, illuminationTime = None, pictureTime = None, synchDelay = None,
                  synchPulseWidth = None, triggerInDelay = None):
        '''
        Set the timing properties of the sequence to display.

        Usage:
        SetTiming(DDRseq_pointer = None, illuminationTime = None, pictureTime = None, synchDelay = None, 
                  synchPulseWidth = None, triggerInDelay = None)
                  
        DDRseq_pointer: Identified of the sequence. If not specified, set the last sequence allocated in the DMD board memory
        illuminationTime: Display time of a single image of the sequence in microseconds. 
                          If not specified, use the highest possible value compatible with pictureTime.
        pictureTime: Time between the start of two consecutive picture, up to 10^7 microseconds = 10 seconds.
                     With illuminationTime, it sets the display rate.
                     If not specified, the value is set to minimize the dark time according illuminationTime.
                     If illuminationTime is also not specified, set to a frame rate of 30Hz.
        synchDelay: Specifies the time delay between the start of the output sync pulse and the start of the display (master mode).
                    Value between 0 and 130,000 microseconds. Set to 0 if not specified.
        synchPulseWidth: Duration of the sync output pulse. 
                         By default equals synchDelay + illuminationTime in normal mode.
                         By default equals ALP_ILLUMINATION_TIME in binary uninterrupted mode.
        triggerInDelay: Length of the trigger signal in microseconds, set to 0 by default.
        
        
        '''
        if (DDRseq_pointer == None) and (self._lastDDRseq):
            DDRseq_pointer = self._lastDDRseq
        if (DDRseq_pointer == None):
            self._raiseError('No sequence to display.')
            
        if (synchDelay == None):
            synchDelay = self._synchDelay
        if (synchPulseWidth == None):
            synchPulseWidth = self._synchPulseWidth
        if (triggerInDelay == None):
            triggerInDelay = self._triggerInDelay
        if (illuminationTime == None):
            illuminationTime = self._ALP_DEFAULT
        if (pictureTime == None):
            pictureTime = self._ALP_DEFAULT
            
        
          
#        if not (self._ALPLib.AlpSeqTiming(self.ALP_ID, DDRseq_pointer, illuminationTime, pictureTime, synchDelay, synchPulseWidth, triggerInDelay)  == self._ALP_OK):
#            self._raiseError('Cannot set timing.')
        self._checkError(self._ALPLib.AlpSeqTiming(self.ALP_ID, DDRseq_pointer, illuminationTime, pictureTime, synchDelay, synchPulseWidth, triggerInDelay),'Cannot set timing.')

    def DevInquire(self, request):
        '''
        Ask the controller board the value of a specified parameter about the ALP device.
        
        Usage: Inquire(self, request)
        
        request: type of value to return:
            'deviceNumber': Serial number of the ALP device
            'version': Version number of the ALP device, e.g. 0x0401 for ALP-4.1
            'availableMemory': ALP on-board sequence memory available for further sequence 
                    allocation (AlpSeqAlloc) – number of binary pictures;
                    The returned number of binary pictures represents the largest free 
                    memory area available for sequence allocation. If ALP memory is 
                    fragmented because of repeated calls of AlpSeqAlloc and AlpSeqFree
                    then this value may differ from the total non-allocated memory.
            'synchPolarity': Frame synch output signal polarity:
                             _ALP_LEVEL_HIGH or _ALP_LEVEL_LOW 
            'triggerEdge':   trigger input signal slope:
                             _ALP_EDGE_FALLING or _ALP_EDGE_RISING
            'DMDType':  Return the type of DMD If no DMD is detected (ALP_DMDTYPE_DISCONNECT), 
                        then the API emulates a 1080p DMD.
            'displayHeight': Number of mirror rows on the DMD, according to 'DMDType'
            'displayWidth': number of mirror columns on the DMD, according to 'DMDType'
            'USBConnection':  Check, if the USB connection is ok 
            'DDCFPGATemp':  Returns FPGA temperature. 
                            The value is written as 1/256 °C to *UserVarPtr. It ranges from -128 °C to +127.96875 °C.
            'AppsFPGATemp': Returns FPGA temperature. The value is written as 1/256 °C to *UserVarPtr. 
                            It ranges from -128 °C to +127.96875 °C.
            'PCBTemp':  Returns PCB temperature.                
                        The value is written as 1/256 °C to *UserVarPtr. It ranges from -128 °C to +127.75 °C. Accuracy: +/- 3 °C
            'PWMLevelp':    Percentage: duty cycle of the PWM pin, see PWM Output below
        '''
        
        if (request == 'deviceNumber'):
            query = self._ALP_DEVICE_NUMBER
        if (request == 'version'):
            query = self._ALP_VERSION
        if (request == 'availableMemory'):
            query = self._ALP_AVAIL_MEMORY 
        if (request == 'synchPolarity'):
            query = self._ALP_SYNCH_POLARITY
        if (request == 'triggerEdge'):
            query = self._ALP_TRIGGER_EDGE     
        if (request == 'DMDType'):
            query = self._ALP_DEV_DMDTYPE 
        if (request == 'DMDMode'):
            query = self._ALP_DEV_DMD_MODE 
        if (request == 'displayHeight'):
            query = self._ALP_DEV_DISPLAY_HEIGHT
        if (request == 'displayWidth'):
            query = self._ALP_DEV_DISPLAY_WIDTH
        if (request == 'USBConnection'):
            query = self._ALP_USB_CONNECTION  
        if (request == 'DDCFPGATemp'):
            query = self._ALP_DDC_FPGA_TEMPERATURE,
        if (request == 'AppsFPGATemp'):
            query = self._ALP_APPS_FPGA_TEMPERATURE
        if (request == 'PCBTemp'):
            query = self._ALP_PCB_TEMPERATURE
        if (request == 'PWMLevelp'):
            query = self._ALP_PWM_LEVEL 
        else:
            self._raiseError('Unknown request')
            
        ret = ct.c_double(0)
        
        self._checkError(self._ALPLib.AlpDevInquire(self.ALP_ID, query, ct.byref(ret)),'Error sending request.')
        return ret.value()
        
            
    def SeqInquire(self, request,  DDRseq_pointer = None):
        '''
        Ask the controller board the value of a specified parameter about an image sequence.
        
        
        Usage: Inquire(self, request, DDRseq_pointer = None)

            request: type of value to return:
                    'bitDepthPic': bit depth of the pictures in the sequence
                    'bitDepthDisplay': bit depth for display
                    'binMode': sequence display in binary mode
                    'nbPic' : number of pictures in the sequence
                    'firstFrame': number of the first picture in the sequence selected for display
                    'lastFrame': number of the last picture in the sequence selected for display
                    'nbSeqRepeat': number of automatically repeated displays of the sequence
                    'minPicTime': Minimum time between the start of consecutive pictures
                    'maxPicTime': Maximum time between the start of consecutive pictures
                    'illuminationTime': Duration of the display of one picture in µs
                    'minIlluminationTime': Minimum duration of the display of one picture in µs
                    'onTime': Total active projection time
                    'offTime': Total inactive projection time
                    'synchDelay': Delay of the start of picture display with respect 
                                  to the trigger output (master mode) in µs 
                    'maxSynchDelay':  Maximal duration of trigger delay in µs 
                    'synchPulseWidth': Duration of the output trigger in µs
                    'triggerInDelay':  Delay of the start of picture display with respect to the trigger input in µs 
                    'maxTriggerInDelay': Maximal duration of trigger delay in µs
                    'dataFormat': Currently selected image data format (see also AlpSeqControl, AlpSeqPut)
                    'seqPutLock': Protect sequence data against writing (AlpSeqPut) during display.
                    'PWMMode': See section Flexible PWM Mode in user manual.       
        '''
        
        if (request == 'bitDepthPic'):
            inquireType = self._ALP_BITPLANES
        elif (request == 'bitDepthDisplay'):
            inquireType = self._ALP_BITNUM
        elif (request == 'binMode'):
            inquireType = self._ALP_BIN_MODE
        elif (request == 'nbPic'):
            inquireType = self._ALP_PICNUM
        elif (request == 'firstFrame'):
            inquireType = self._ALP_FIRSTFRAME
        elif (request == 'lastFrame'):
            inquireType = self._ALP_LASTFRAME
        elif (request == 'nbSeqRepeat'):
            inquireType = self._ALP_SEQ_REPEAT
        elif (request == 'minPicTime'):
            inquireType = self._ALP_MIN_PICTURE_TIME
        elif (request == 'maxPicTime'):
            inquireType = self._ALP_MAX_PICTURE_TIME
        elif (request == 'illuminationTime'):
            inquireType = self._ALP_ILLUMINATE_TIME   
        elif (request == 'minIlluminationTime'):
            inquireType = self._ALP_MIN_ILLUMINATE_TIME
        elif (request == 'onTime'):
            inquireType = self._ALP_ON_TIME
        elif (request == 'offTime'):
            inquireType = self._ALP_OFF_TIME
        elif (request == 'synchDelay'):
            inquireType = self._ALP_SYNCH_DELAY
        elif (request == 'maxSynchDelay'):
            inquireType = self._ALP_MAX_SYNCH_DELAY 
        elif (request == 'synchPulseWidth'):
            inquireType = self._ALP_SYNCH_PULSEWIDTH
        elif (request == 'triggerInDelay'):
            inquireType = self._ALP_TRIGGER_IN_DELAY 
        elif (request == 'maxTriggerInDelay'):
            inquireType = self._ALP_MAX_TRIGGER_IN_DELAY
        elif (request == 'dataFormat'):
            inquireType = self._ALP_DATA_FORMAT
        elif (request == 'seqPutLock'):
            inquireType = self._ALP_SEQ_PUT_LOCK
        elif (request == 'PWMMode'):
            inquireType = self._ALP_PWM_MODE 
        else:
            self._raiseError('Unknown request')
    
        ret = ct.c_double(0)
        
        if (DDRseq_pointer == None) and (self._lastDDRseq):
            DDRseq_pointer = self._lastDDRseq
            
        self._checkError(self._ALPLib.AlpSeqInquire(self.ALP_ID,  DDRseq_pointer, inquireType, ct.byref(ret)),'Error sending request.')
        return ret.value()
        
    def FreeSeq(self,DDRseq_pointer = None):
        '''
        Frees a previously allocated sequence. The ALP memory reserved for the specified sequence in the device DeviceId is released.
        
        
        Usage: FreeSeq(DDRseq_pointer = None)
        
            DDRseq_pointer: Id of the sequence to free. If not specified, free the last uploaded sequence.
        '''
        if (DDRseq_pointer == None) and (self._lastDDRseq):
            DDRseq_pointer = self._lastDDRseq
            
            
        self._checkError(self._ALPLib.AlpSeqFree(self.ALP_ID,DDRseq_pointer),'Unable to free the image sequence.')
        
    def Run(self, DDRseq_pointer = None):
        '''
        Display a sequenc loaded into the DDR memory. If not sequence pointer is given, display the last sequence stored.
        '''
        if (DDRseq_pointer == None) and (self._lastDDRseq):
            DDRseq_pointer = self._lastDDRseq
        if (DDRseq_pointer == None):
            self._raiseError('No sequence to display.')
        
#        if not (self._ALPLib.AlpProjStartCont(self.ALP_ID, DDRseq_pointer) == self._ALP_OK):
#            self._raiseError('Cannot launch sequence.')
        self._checkError(self._ALPLib.AlpProjStartCont(self.ALP_ID, DDRseq_pointer),'Cannot launch sequence.')
        
    def DiscretizeArray(self,arr):
        maxValue = max(arr)
        
        
    def Stop(self):
        self._ALPLib.AlpDevHalt(self.ALP_ID)

    def Free(self):
        self._ALPLib.AlpDevFree(self.ALP_ID)
