"""
Created on Wed Oct 05 15:48:53 2016

@author: Sebastien Popoff
"""

import ctypes as ct
import sys
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
        self._ALPLib = ct.CDLL("./x64/alp4395.dll")   
            


        
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
        # Temperatures. Data format: signed long with 1 LSB=1/256 °C */
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
        

        
        
    def _raiseError(self, errorString):
        raise Exception(errorString)
        
    def Initialize(self, DeviceNum = None, InitFlag = None):
        
        if DeviceNum == None:
            DeviceNum = ct.c_long(self._ALP_DEFAULT)
        if InitFlag == None:
            InitFlag = ct.c_long(self._ALP_DEFAULT)
        

        if not (self._AlpDevAlloc(DeviceNum,InitFlag,ct.byref(self.ALP_ID)) == self._ALP_OK):
            self._raiseError('Cannot open DMD.')
            
        if not (self._ALPLib.AlpDevInquire(self.ALP_ID, self._ALP_DEV_DMDTYPE, ct.byref(self.DMDType)) == self._ALP_OK):
            self._raiseError('Inquery fails.')      

            
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
            
       
    def AllocateSequence(self, imgData = None, nbImg = 1, bitDepth = 1):
        '''
        Allocate memory on the DDR RAM for the sequence of image.
        '''

        data = ''.join(chr(int(x)) for x in imgData)
        pImageData = ct.cast(ct.create_string_buffer(data,self.nSizeX*self.nSizeY),ct.c_void_p)    

        DDRseq_pointer = ct.c_long(0)
        # Allocate memory on the DDR RAM for the sequence of image.
        self._ALPLib.AlpSeqAlloc(self.ALP_ID, ct.c_long(bitDepth), ct.c_long(nbImg), ct.byref(DDRseq_pointer))
        
        # Load the data into memory, here we load everythong, so we start at image 0 for nbImg images.
        if not (self._ALPLib.AlpSeqPut(self.ALP_ID, DDRseq_pointer, 0, nbImg, pImageData) == self._ALP_OK):
            self._raiseError('Cannot allocate image sequence.')
        # AlpProjStartCont(self.ALP_ID, nSeqId )) 
        self._lastDDRseq = DDRseq_pointer
        return DDRseq_pointer
        
    def SetTiming(self, nPictureTime, DDRseq_pointer = None, synchDelay = None, synchPulseWidth = None, triggerInDelay = None):
        
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
            
        
        
        if not (self._ALPLib.AlpSeqTiming(self.ALP_ID, DDRseq_pointer, self._ALP_DEFAULT, nPictureTime, synchDelay, synchPulseWidth, triggerInDelay)  == self._ALP_OK):
            self._raiseError('Cannot set timing.')
        
        
    def Run(self, DDRseq_pointer = None):
        '''
        Display a sequenc loaded into the DDR memory. If not sequence pointer is given, display the last sequence stored.
        '''
        if (DDRseq_pointer == None) and (self._lastDDRseq):
            DDRseq_pointer = self._lastDDRseq
        if (DDRseq_pointer == None):
            self._raiseError('No sequence to display.')
        
        if not (self._ALPLib.AlpProjStartCont(self.ALP_ID, DDRseq_pointer) == self._ALP_OK):
            self._raiseError('Cannot launch sequence.')
        
    def Stop(self):
        self._ALPLib.AlpDevHalt(self.ALP_ID)

    def Free(self):
        self._ALPLib.AlpDevFree(self.ALP_ID)
