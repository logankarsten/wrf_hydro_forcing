"""RegridDriver
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
def parmRead(fname):
   """Read in the main config file, return needed parameters

   Parameters
   ----------
   fname: str
      name of parameter file to read in

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

   forcing_config_label = "RegridDriver"
   logging_filename =  forcing_config_label + ".log" 
   logging.basicConfig(format='%(asctime)s %(message)s',
                       filename=logging_filename, level=set_level)

   hrrrDir = parser.get('data_dir', 'HRRR_data')
   mrmsDir = parser.get('data_dir', 'MRMS_data')
   rapDir = parser.get('data_dir', 'RAP_data')
   gfsDir = parser.get('data_dir', 'GFS_data')
    
   maxFcstHourHrrr = int(parser.get('fcsthr_max', 'HRRR_fcsthr_max'))
   maxFcstHourRap = int(parser.get('fcsthr_max', 'RAP_fcsthr_max'))
   maxFcstHourGfs = int(parser.get('fcsthr_max', 'GFS_fcsthr_max'))

   hoursBackHrrr = int(parser.get('triggering', 'HRRR_hours_back'))
   hoursBackRap = int(parser.get('triggering', 'RAP_hours_back'))
   hoursBackGfs = int(parser.get('triggering', 'GFS_hours_back'))
   hoursBackMrms = int(parser.get('triggering', 'MRMS_hours_back'))

   stateFile = parser.get('triggering', 'regrid_state_file')
    

   parms = Parms(hrrrDir, mrmsDir, rapDir, gfsDir, 
                 maxFcstHourHrrr, maxFcstHourRap, maxFcstHourGfs,
                 hoursBackHrrr, hoursBackRap, hoursBackGfs,
                 hoursBackMrms, stateFile)
   return parms

#----------------------------------------------------------------------------
def regridHRRR(fname):
   """Invoke HRRR regridding/downscaling (see Short_Range_Forcing.py)
       
   Parameters
   ----------
   fname: str
      name of file to regrid and downscale, with yyyymmdd parent dir

   Returns
   -------
   None

   """
   logging.info("REGRIDDING HRRR DATA, file=%s", fname)
   #srf.forcing('regrid', 'HRRR', fname[9:])
   logging.info("DONE REGRIDDING HRRR DATA, file=%s", fname)
    
#----------------------------------------------------------------------------
def regridRAP(fname):
   """Invoke RAP regridding/downscaling (see Short_Range_Forcing.py)
       
   Parameters
   ----------
   fname: str
      name of file to regrid and downscale, with yyyymmdd parent dir

   Returns
   -------
   None

   """
   logging.info("REGRIDDING RAP DATA, file=%s", fname)
   #srf.forcing('regrid', 'RAP', fname[9:])
   logging.info("DONE REGRIDDING RAP DATA, file=%s", fname)
    
#----------------------------------------------------------------------------
def regridMRMS(mrmsFname):
   """Invoke MRMS regridding (see Analysis_Assimilation.py)
       
   Parameters
   ----------
   fname: str
      name of file to regrid and downscale, with yyyymmdd parent dir

   Returns
   -------
   None

   """
   logging.info("REGRIDDING MRMS DATA, file=%s", mrmsFname)
   #aaf.forcing('regrid', 'MRMS', mrmsFname[9:])
   logging.info("DONE REGRIDDING MRMS DATA, file=%s", mrmsFname)

#----------------------------------------------------------------------------
def regridGFS(gfsFname):
   """Invoke GFS regridding (see Medium_Range_Forcing.py)

   Parameters
   ----------
   fname: str
      name of file to regrid and downscale, with yyyymmdd parent dir

   Returns
   -------
   None

   """
   logging.info("REGRIDDING GFS DATA, file=%s", gfsFname)
   #mrf.forcing('regrid', 'GFS', gfsFname[9:])
   logging.info("DONE REGRIDDING GFS DATA, file=%s", gfsFname)

#----------------------------------------------------------------------------
class Parms:
   """Parameters from the main wrf_hydro param file that are needed 

   Attributes
   ----------
   _hrrrDir: str
      Topdir for HRRR
   _mrmsDir: str  
      Topdir for MRMS
   _rapDir: str
      Topdir for RAP
   _gfsDir: str
      Topdir for GFS
   _maxFcstHourHrrr: int
      Maximum forecast hour to process, HRRR
   _maxFcstHourRap: int
      Maximum forecast hour to process, RAP
   _maxFcstHourGfs: int
      Maximum forecast hour to process, GFS
   _hoursBackHrrr: int
      Hours back to maintain state, HRRR
   _hoursBackRap: int
      Hours back to maintain state, RAP
   _hoursBackGfs: int
      Hours back to maintain state, GFS
   _hoursBackMrms: int
      Hours back to maintain state, MRMS
   _stateFile: str
      Name of file with state information that is read/written
   """

   def __init__(self, hrrrDir, mrmsDir, rapDir, gfsDir, 
                maxFcstHourHrrr,maxFcstHourRap,
                maxFcstHourGfs, hoursBackHrrr, hoursBackRap, 
                hoursBackGfs, hoursBackMrms, stateFile):
      """Initialization using input args

      Parameters
      ----------
      One to one with attributes, self explanatory
      """
      self._hrrrDir = hrrrDir
      self._mrmsDir = mrmsDir
      self._rapDir = rapDir
      self._gfsDir = gfsDir
      self._maxFcstHourHrrr = maxFcstHourHrrr
      self._maxFcstHourRap = maxFcstHourRap
      self._maxFcstHourGfs = maxFcstHourGfs
      self._hoursBackHrrr = hoursBackHrrr
      self._hoursBackRap = hoursBackRap
      self._hoursBackGfs = hoursBackGfs
      self._hoursBackMrms = hoursBackMrms
      self._stateFile = stateFile

   def debugPrint(self):
      """ Debug logging of content
      """
      logging.debug("Parms: HRRR_data = %s", self._hrrrDir)
      logging.debug("Parms: MRMS_data = %s", self._mrmsDir)
      logging.debug("Parms: RAP_data = %s", self._rapDir)
      logging.debug("Parms: GFS_data = %s", self._gfsDir)
      logging.debug("Parms: MaxFcstHourHrrr = %d", self._maxFcstHourHrrr)
      logging.debug("Parms: MaxFcstHourRap = %d", self._maxFcstHourRap)
      logging.debug("Parms: MaxFcstHourGfs = %d", self._maxFcstHourGfs)
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
   _hrrr
      HRRR file names with yyyymmdd parent directory
   _mrms
      MRMS file names with yyyymmdd parent directory
   _rap
      RAP file names with yyyymmdd parent directory
   _gfs
      GFS file names with yyyymmdd parent directory
   """

   def __init__(self, parmFile):
      """Initialize using parameters read in from a file

      Parameters
      ----------
      parmFile: str
         Name of param file to read
      """

      if (not parmFile):
         self._empty = 1
         self._hrrr = []
         self._mrms = []
         self._rap = []
         self._gfs = []
      else:
         self._empty = 0
         cf = SafeConfigParser()
         cf.read(parmFile)
         self._hrrr = [name for name in cf.get("latest", "hrrr").split()]
         self._mrms = [name for name in cf.get("latest", "mrms").split()]
         self._rap = [name for name in cf.get("latest", "rap").split()]
         self._gfs = [name for name in cf.get("latest", "gfs").split()]

   def isEmpty(self):
      """Check if state is set or not

      Parameters
      ----------
         none
    
      Returns
      -------
         true if state is not set
      """
      return self._empty == 1

   def isEmptyTyped(self, dataType):
      """Check if a particular type is empty or not

      Parameters
      ----------
         dataType:str
            'HRRR', 'RAP', etc
    
      Returns
      -------
         true if this type is empty
      """
      if (dataType == 'HRRR'):
         return (not self._hrrr)
      elif (dataType == 'RAP'):
         return (not self._rap)
      elif (dataType == 'MRMS'):
         return (not self._mrms)
      elif (dataType == 'GFS'):
         return (not self._gfs)
      else:
         logging.error("Unknown dataType %s", dataType)
         return 1
      

   def newestTyped(self, dataType):
      """return newest file of a particular type 

      Parameters
      ----------
         dataType:str
            'HRRR', 'RAP', etc
    
      Returns
      -------
      str
         File name (newest) of this type, or empty string if none
         
      """
      if (self.isEmptyTyped(dataType)):
         return ""
      if (dataType == 'HRRR'):
         return (self._hrrr[-1])
      elif (dataType == 'RAP'):
         return (self._rap[-1])
      elif (dataType == 'MRMS'):
         return (self._mrms[-1])
      elif (dataType == 'GFS'):
         return (self._gfs[-1])
      else:
         logging.error("Unknown dataType %s", dataType)
         return 1
      

   def initialize(self, hrrr, rap, mrms, gfs):
      """Initialize from DataFiles inputs

      Parameters
      ----------
         hrrr: DataFiles
            HRRR data
         rap: DataFiles
            RAP data
         mrms: DataFiles
            MRMS data
         gfs: DataFiles
            GFS data
    
      Returns
      -------
         None
      """
      self._empty = 0
      self._hrrr = hrrr.getFnames()
      self._rap = rap.getFnames()
      self._mrms = mrms.getFnames()
      self._gfs = gfs.getFnames()

   def debugPrint(self):
      """ logging debug of contents
      """
      for f in self._rap:
         logging.debug("State:RAP:%s", f)
      for f in self._mrms:
         logging.debug("State:MRMS:%s", f)
      for f in self._hrrr:
         logging.debug("State:HRRR:%s", f)
      for f in self._gfs:
         logging.debug("State:GFS:%s", f)
        
   def updateTyped(self, dataType, time, hoursBack):
      """Update typed state so that input time is newest one

       Parameters
       ----------
       dataType:str
          'HRRR', 'RAP', etc
       time: ForecastTime
          The newest time
       hoursBack:
          Maximum issue time hours back compared to time
       
       Returns
       -------
       none
       """
      if (dataType == 'HRRR'):
         self._hrrr = df.filterWithinNHours(self._hrrr, dataType, time,
                                            hoursBack)
      elif (dataType == 'RAP'):
         self._rap = df.filterWithinNHours(self._rap, dataType, time, hoursBack)
      elif (dataType == 'MRMS'):
         self._mrms = df.filterWithinNHours(self._mrms, dataType, time,
                                            hoursBack)
      elif (dataType == 'GFS'):
         self._gfs = df.filterWithinNHours(self._gfs, dataType, time, hoursBack)
      else:
         logging.error("Unknown dataType %s", dataType)
      

   def addFileIfNew(self, f, dataType):
      """ If input file is not in state, add it

      Parameters
      ----------
      f:str
         File name
      dataType:str
         'HRRR', 'RAP', etc

      Returns
      -------
      bool
         True if added, false if already in the state

      """
      ret = 0
      if (dataType == 'HRRR'):
         if (not f in self._hrrr):
            self._hrrr.append(f)
            ret = 1
      elif (dataType == 'RAP'):
         if (not f in self._rap):
            self._rap.append(f)
            ret = 1
      elif (dataType == 'MRMS'):
         if (not f in self._mrms):
            self._mrms.append(f)
            ret = 1
      elif (dataType == 'GFS'):
         if (not f in self._gfs):
            self._gfs.append(f)
            ret = 1
      else:
         logging.error("Unknown dataType %s", dataType)
      return ret
   
   def sortFiles(self, dataType):
      """ Sort the files into ascending order for a type

      Note: sort depends on naming being 'nice'

      Parameters
      ----------
      dataType:str
      'HRRR', 'RAP', etc
    
      Returns
      -------
      none

      """
      if (dataType == 'HRRR'):
         self._hrrr.sort()
      elif (dataType == 'RAP'):
         self._rap.sort()
      elif (dataType == 'MRMS'):
         self._mrms.sort()
      elif (dataType == 'GFS'):
         self._gfs.sort()
      else:
         logging.error("Unknown dataType %s", dataType)


   def updateWithNew(self, data, dataType, hoursBack):
      """ Update internal state with new data

      The dataType is used to determine which part of state to update

      Parameters
      ----------
      data: DataFiles
         The newest data
      dataType: str
         'HRRR', 'RAP', etc.
      hoursBack: int
         Maximum number of hours back to keep data in state

      Returns
      -------
      list[str]
          The data file names that are are newly added to state
      """
         
      ret = []
      fnames = data.getFnames()
      if (not fnames):
         return ret

      if (self.isEmptyTyped(dataType)):
         logging.debug("Adding to empty %s list", dataType);
      else:
         sname = self.newestTyped(dataType)
         if (not sname):
            logging.error("Expected file, got none")
            return ret
         if (fnames[-1] > sname):
            logging.debug("%s Newer time encountered", dataType)
            # see if issue time has increased and if so, purge old stuff
            # create DataFile objects
            df0 = df.DataFile(sname[0:8], sname[9:], dataType)
            df1 = df.DataFile(fnames[-1][0:8], fnames[-1][9:], dataType)
            if (df0._ok and df1._ok):
               if (df0._time.inputIsNewerIssueHour(df1._time)):
                  logging.debug("%s Issue hour has increased, purge now",
                                dataType)
                  self.updateTyped(dataType, df1._time, hoursBack)
            else:
               logging.error("Constructing DataFile objects")

      for f in fnames:
         if (self.addFileIfNew(f, dataType)):
            ret.append(f)

      self.sortFiles(dataType)
      return ret
        
   def write(self, parmFile):
      """ Write state to param file

      Parameters
      ----------
         parmFile: Name of file to write to 
            
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
      for f in self._mrms:
         s += f
         s += "\n"
      config.set('latest', 'mrms', s)

      s = ""

      for f in self._hrrr:
         s += f
         s += "\n"
      config.set('latest', 'hrrr', s)

      s = ""
      for f in self._rap:
         s += f
         s += "\n"
      config.set('latest', 'rap', s)

      s = ""
      for f in self._gfs:
         s += f
         s += "\n"
      config.set('latest', 'gfs', s)

      # Write it out
      with open(parmFile, 'wb') as configfile:
         config.write(configfile)

#----------------------------------------------------------------------------
def createStateFile(parms):
   """  Called if there is no state file, look at data dirs and create state

   Parameters
   ----------
   parms: Parms
      Parameter settings

   Returns
   -------
   none

   Writes out the state file after creating it
   """

   logging.info("Initializing")


   # query each directory and get newest model run file for each, then
   # get all for that and previous issue time
   hrrr = df.DataFiles(parms._hrrrDir, parms._maxFcstHourHrrr, "HRRR")
   hrrr.setNewestFiles(parms._hoursBackHrrr)
   for f in hrrr._content:
      f.debugPrint("Newest files: HRRR")

   rap = df.DataFiles(parms._rapDir, parms._maxFcstHourRap, "RAP")
   rap.setNewestFiles(parms._hoursBackRap)
   for f in rap._content:
      f.debugPrint("Newest files: RAP")
    
   gfs = df.DataFiles(parms._gfsDir, parms._maxFcstHourGfs, "GFS")
   gfs.setNewestFiles(parms._hoursBackGfs)
   for f in gfs._content:
      f.debugPrint("Newest files: GFS")
    
   mrms = df.DataFiles(parms._mrmsDir, 0, "MRMS")
   mrms.setNewestFiles(parms._hoursBackMrms)
   for f in mrms._content:
      f.debugPrint("Newest files: MRMS")


   state = State("")
   state.initialize(hrrr, rap, mrms, gfs)

   # maybe back up  and regrid that entire issue time
   # maybe redo this exact set of inputs only
   # maybe do nothing
   # maybe do all of them..for now do nothing as its easiest, just move on
   #files = hrrr.getFnames()
   #for f in files:
   #  regridHRRR(f)
   #files = rap.getFnames()
   #for f in files:
   #    regridRAP(f)
   #files = mrms.getFnames()
   #for f in files:
   #    regridMRMS(f)

   # write out file
   state.write(parms._stateFile)

#----------------------------------------------------------------------------
def main(argv):

    # read in fixed main params
    parms = parmRead("wrf_hydro_forcing.parm")
    parms.debugPrint()

    #if there is not a state file, create one now using newest
    if (not os.path.exists(parms._stateFile)):
        parms.debugPrint()
        createStateFile(parms)
        
    # begin normal processing situation
    logging.debug("....Check for new input data to regid")
    
    # read in state
    state = State(parms._stateFile)
    if state.isEmpty():
        # error return here
        return 0
    #state.debugPrint()
    
    # query each directory and get newest model run file for each, then
    # get all for that and previous issue time
    hrrr = df.DataFiles(parms._hrrrDir, parms._maxFcstHourHrrr, "HRRR")
    hrrr.setNewestFiles(parms._hoursBackHrrr)
    #for f in hrrr._content:
    #    f.debugPrint("Newest files: HRRR")
    rap = df.DataFiles(parms._rapDir, parms._maxFcstHourRap, "RAP")
    rap.setNewestFiles(parms._hoursBackRap)
    #for f in rap._content:
    #    f.debugPrint("Newest files: RAP")
    
    gfs = df.DataFiles(parms._gfsDir, parms._maxFcstHourGfs, "GFS")
    gfs.setNewestFiles(parms._hoursBackGfs)

    mrms = df.DataFiles(parms._mrmsDir, 0, "MRMS")
    mrms.setNewestFiles(parms._hoursBackMrms)
    #for f in mrms._content:
    #    f.debugPrint("Newest files: MRMS")


    # Update the state to reflect changes, returning those files to regrid
    # Regrid 'em
    toProcess = state.updateWithNew(hrrr, 'HRRR', parms._hoursBackHrrr)
    for f in toProcess:
        regridHRRR(f)

    # Same with RAP
    toProcess = state.updateWithNew(rap, 'RAP', parms._hoursBackRap)
    for f in toProcess:
        regridRAP(f)

    # Same with GFS
    toProcess = state.updateWithNew(gfs, 'GFS', parms._hoursBackGfs)
    for f in toProcess:
        regridGFS(f)

    # Same with MRMS
    toProcess = state.updateWithNew(mrms, 'MRMS', parms._hoursBackMrms)
    for f in toProcess:
        regridMRMS(f)

    # write out state and exit
    #state.debugPrint()
    state.write(parms._stateFile)
    return 0

#----------------------------------------------

if __name__ == "__main__":
    main(sys.argv[1:])
