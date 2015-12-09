"""Regrid_Driver
Checks data directories for new content, and if 
found initiates regrid/rescaling python scripts.
Keeps state in a state file that is read/written
each time this script is invoked.  The state
file contains the most recent data files.
Logs to a log file that is created in the
same directory from where this script is executed.  
"""

import os
import sys
import logging
import datetime
import time
from ConfigParser import SafeConfigParser
import DataFiles as df
import Short_Range_Forcing as srf
import Analysis_Assimilation_Forcing as aaf
import Medium_Range_Forcing as mrf

#----------------------------------------------------------------------------
def parmRead(fname, fileType):
   """Read in the main config file, return needed parameters

   Parameters
   ----------
   fname: str
      name of parameter file to read in
   fileType: str
      'RAP', 'HRRR', 'MRMS', 'GFS'

   Returns
   -------
   Parms
      values as pulled from the file

   """
    
   parser = SafeConfigParser()
   parser.read(fname)
   logging_level = parser.get('log_level', 'forcing_engine_log_level')
   # Set the logging level based on what was defined in the parm/config file
   if logging_level == 'DEBUG':
      set_level = logging.DEBUG
   elif logging_level == 'INFO':
      set_level = logging.INFO
   elif logging_level == 'WARNING':
      set_level = logging.WARNING
   elif logging_level == 'ERROR':
      set_level = logging.ERROR
   else:
      set_level = logging.CRITICAL

   forcing_config_label = "RegridDriver" + fileType
   logging_filename =  forcing_config_label + ".log" 
   logging.basicConfig(format='%(asctime)s %(message)s',
                       filename=logging_filename, level=set_level)

   dataDir = parser.get('data_dir', fileType + '_data')
   maxFcstHour = int(parser.get('fcsthr_max', fileType + '_fcsthr_max'))
   hoursBack = int(parser.get('triggering', fileType + '_hours_back'))
   stateFile = parser.get('triggering', fileType + '_regrid_state_file')
   
   parms = Parms(dataDir, maxFcstHour, hoursBack, stateFile)
   return parms

#----------------------------------------------------------------------------
def regrid(fname, fileType):
   """Invoke HRRR regridding/downscaling (see Short_Range_Forcing.py)
       
   Parameters
   ----------
   fname: str
      name of file to regrid and downscale, with yyyymmdd parent dir
   fileType: str
      HRRR, RAP, ... string

   Returns
   -------
   None

   """

   logging.info("REGRIDDING %s DATA, file=%s", fileType, fname)
   if (fileType == 'HRRR'):
       srf.forcing('regrid', 'HRRR', fname[9:])
       # special case, if it is a 0 hour forecast, do double regrid
       f = df.DataFile(fname[0:8], fname[9:], 'HRRR')
       if (f._ok):
          if (f._time._forecastHour == 0):
             logging.debug("SPECIAL 0 hour case %s", fname[9:0])
             aaf.forcing('regrid', 'HRRR', fname[9:])
       else:
          logging.error("Regrid error checking for 0 hour data")
   elif (fileType == 'RAP'):
       srf.forcing('regrid', 'RAP', fname[9:])
       # special case, if it is a 0 hour forecast, do double regrid
       f = df.DataFile(fname[0:8], fname[9:], 'RAP')
       if (f._ok):
          if (f._time._forecastHour == 0):
             logging.debug("SPECIAL 0 hour case %s", fname[9:0])
             aaf.forcing('regrid', 'RAP', fname[9:])
       else:
          logging.error("Regrid error checking for 0 hour data")
   elif (fileType == 'GFS'):
       mrf.forcing('regrid', 'GFS', fname[9:])
   elif (fileType == 'MRMS'):
       print fname[9:]
       aaf.forcing('regrid', 'MRMS', fname[9:])
   else:
       logging.error("Unknown file type %s", fileType)

   logging.info("DONE REGRIDDING %s DATA, file=%s", fileType, fname)
    
#----------------------------------------------------------------------------
class Parms:
   """Parameters from the main wrf_hydro param file that are needed 

   Attributes
   ----------
   _dataDir: str
      Topdir for data
   _maxFcstHour: int
      Maximum forecast hour to process
   _hoursBack: int
      Hours back to maintain state
   _stateFile: str
      Name of file with state information that is read/written
   """

   def __init__(self, dataDir, maxFcstHour, hoursBack, stateFile):
      """Initialization using input args

      Parameters
      ----------
      One to one with attributes, self explanatory
      """
      self._dataDir = dataDir
      self._maxFcstHour = maxFcstHour
      self._hoursBack = hoursBack
      self._stateFile = stateFile

   def debugPrint(self):
      """ Debug logging of content
      """
      logging.debug("Parms: data = %s", self._dataDir)
      logging.debug("Parms: MaxFcstHour = %d", self._maxFcstHour)
      logging.debug("Parms: StateFile = %s", self._stateFile)


#----------------------------------------------------------------------------

# Internal state that is read in and saved out
# The state
#
class State:
   """Internal state that is read in and saved out

   Attributes
   ----------
   _empty: bool
      True if state is not set
   _data
      data file names with yyyymmdd parent directory
   """

   def __init__(self, parmFile="", fileType=""):
      """Initialize using parameters read in from a file

      Parameters
      ----------
      parmFile: str
         Name of param file to read
      fileType: str
         'HRRR', 'RAP', ...
      """

      if (not parmFile):
         self._empty = 1
         self._data = []
      else:
         self._empty = 0
         cf = SafeConfigParser()
         cf.read(parmFile)
         self._data = [name for name in cf.get("latest", fileType).split()]

   def isEmpty(self):
      """Check if state is set or not

      Parameters
      ----------
         none
    
      Returns
      -------
         true if state is not set
      """
      if (self._empty == 1):
         return 1
      return (not self._data)

   def newest(self):
      """return newest file

      Returns
      -------
      str
         File name (newest), or empty string if none
         
      """
      if (self.isEmpty()):
         return ""
      return (self._data[-1])
      

   def initialize(self, data, fileType):
      """Initialize from DataFiles inputs

      Parameters
      ----------
      data: DataFiles
         data
      fileType : str
         'HRRR', etc
    
      Returns
      -------
         None
      """
      self._empty = 0
      self._data = data.getFnames()

   def debugPrint(self):
      """ logging debug of contents
      """
      for f in self._data:
         logging.debug("State:%s", f)
        
   def update(self, time, hoursBack, fileType):
      """Update typed state so that input time is newest one

       Parameters
       ----------
       time: ForecastTime
          The newest time
       hoursBack:
          Maximum issue time hours back compared to time
       fileType: str
          'HRRR', ...
       
       Returns
       -------
       none
       """
      self._data = df.filterWithinNHours(self._data, fileType, time, hoursBack)
      

   def addFileIfNew(self, f):
      """ If input file is not in state, add it

      Parameters
      ----------
      f:str
         File name

      Returns
      -------
      bool
         True if added, false if already in the state

      """
      ret = 0
      if (not f in self._data):
          self._data.append(f)
          ret = 1
      return ret
   
   def sortFiles(self):
      """ Sort the files into ascending order for a type

      Note: sort depends on naming being 'nice'

      Returns
      -------
      none

      """
      self._data.sort()

   def updateWithNew(self, data, hoursBack, fileType):
      """ Update internal state with new data

      Parameters
      ----------
      data: DataFiles
         The newest data
      hoursBack: int
         Maximum number of hours back to keep data in state
      fileType : str
         'HRRR', 'RAP', ...
      Returns
      -------
      list[str]
          The data file names that are are newly added to state
      """
         
      ret = []
      fnames = data.getFnames()
      if (not fnames):
         return ret

      if (self.isEmpty()):
         logging.debug("Adding to empty list")
      else:
         sname = self.newest()
         if (not sname):
            logging.error("Expected file, got none")
            return ret
         if (fnames[-1] > sname):
            logging.debug("Newer time encountered")
            # see if issue time has increased and if so, purge old stuff
            # create DataFile objects
            df0 = df.DataFile(sname[0:8], sname[9:], fileType)
            df1 = df.DataFile(fnames[-1][0:8], fnames[-1][9:], fileType)
            if (df0._ok and df1._ok):
               if (df0._time.inputIsNewerIssueHour(df1._time)):
                  logging.debug("%s Issue hour has increased, purge now",
                                fileType)
                  self.update(df1._time, hoursBack, fileType)
            else:
               logging.error("Constructing DataFile objects")

      for f in fnames:
         if (self.addFileIfNew(f)):
            ret.append(f)

      self.sortFiles()
      return ret
        
   def write(self, parmFile, fileType):
      """ Write state to param file

      Parameters
      ----------
      parmFile: Name of file to write to 
      fileType: str
          'HRRR', etc
            
      Returns
      -------
      None
      """
         
      config = SafeConfigParser()

      # When adding sections or items, add them in the reverse order of
      # how you want them to be displayed in the actual file.
      # In addition, please note that using RawConfigParser's and the raw
      # mode of ConfigParser's respective set functions, you can assign
      # non-string values to keys internally, but will receive an error
      # when attempting to write to a file or when you get it in non-raw
      # mode. SafeConfigParser does not allow such assignments to take place.

      config.add_section('latest')

      s = ""
      for f in self._data:
         s += f
         s += "\n"
      config.set('latest', fileType, s)

      # Write it out
      with open(parmFile, 'wb') as configfile:
         config.write(configfile)

#----------------------------------------------------------------------------
def createStateFile(parms, fileType):
   """  Called if there is no state file, look at data dirs and create state

   Parameters
   ----------
   parms: Parms
      Parameter settings
   fileType: str
      'HRRR', ...

   Returns
   -------
   none

   Writes out the state file after creating it
   """

   logging.info("Initializing")


   # query each directory and get newest model run file for each, then
   # get all for that and previous issue time
   data = df.DataFiles(parms._dataDir, parms._maxFcstHour, fileType)
   data.setNewestFiles(parms._hoursBack)
   for f in data._content:
      f.debugPrint("Newest files: " + fileType)

   state = State("")
   state.initialize(data, fileType)

   # maybe back up  and regrid that entire issue time
   # maybe redo this exact set of inputs only
   # maybe do nothing
   # maybe do all of them..for now do nothing as its easiest, just move on

   # write out file
   state.write(parms._stateFile, fileType)

#----------------------------------------------------------------------------
def main(argv):

    fileType = argv[0]
    good = 0
    if (fileType == 'HRRR' or fileType == 'RAP' or fileType == 'MRMS' or
        fileType == 'GFS'):
       good = 1
    if (good == 0):
       print 'ERROR unknown file type command arg ', fileType
       return 1

    # User must pass the config file into the main driver.
    configFile = argv[1]
    if not os.path.exists(configFile):
        print 'ERROR forcing engine config file not found.'
        return 1
    
    # read in fixed main params
    parms = parmRead(configFile, fileType)
    parms.debugPrint()

    #if there is not a state file, create one now using newest
    if (not os.path.exists(parms._stateFile)):
        parms.debugPrint()
        createStateFile(parms, fileType)
        
    # begin normal processing situation
    logging.debug("....Check for new input data to regid")
    
    # read in state
    state = State(parms._stateFile, fileType)
    if state.isEmpty():
        # error return here
        return 0
    #state.debugPrint()
    
    # query each directory and get newest model run file for each, then
    # get all for that and previous issue time
    data = df.DataFiles(parms._dataDir, parms._maxFcstHour, fileType)
    data.setNewestFiles(parms._hoursBack)

    # Update the state to reflect changes, returning those files to regrid
    # Regrid 'em
    toProcess = state.updateWithNew(data, parms._hoursBack, fileType)
    for f in toProcess:
        regrid(f, fileType)

    # write out state and exit
    #state.debugPrint()
    state.write(parms._stateFile, fileType)
    return 0

#----------------------------------------------

if __name__ == "__main__":
    main(sys.argv[1:])
