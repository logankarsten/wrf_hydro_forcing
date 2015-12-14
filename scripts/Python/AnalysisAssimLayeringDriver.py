""" ShortRangeLayeringDriver.py
Checks regrid/rescale data directories for new content, and if 
found and time to do so, initiate layering scripts.
Keeps state in a state file that is read/written
each time this script is invoked.  The state
file shows the most recent issue times status as regards inputs and layering.
Logs to a log file that is created in the
same directory from where this script is executed.  
"""

import os
import sys
import logging
import datetime
import time
from ConfigParser import SafeConfigParser
import Analysis_Assimilation_Forcing as aaf


def layer(parms, itime, step, which):
    """ Perform layering

    NOTE: here is where returns status will be added and used

    Parameters
    ----------
    parms : Parms
        parameters

    """        
    logging.debug("LAYERING: %s  %d %s", itime.strftime("%Y%m%d%H"),
                  step, which)
    aaf.anal_assim_layer(itime.strftime('%Y%m%d%H'), '-%01d'%(step), which)
    logging.debug("DONE LAYERING: %s  %d %s", itime.strftime("%Y%m%d%H"),
                  step, which)

    #path = self._issue.strftime("%Y%m%d%H") + "/"
    #path += self._valid.strftime("%Y%m%d%H%M") + ".LDASIN_DOMAIN1.nc"
    #logging.info("LAYERING %s ", path)
    #srf.forcing('layer', 'HRRR', path, 'RAP', path)
    #logging.info("DONE LAYERING file=%s", path)

#----------------------------------------------------------------------------
def stepStaticName(index):
    ret = 'step%01d' %(index)
    return ret

#----------------------------------------------------------------------------
def isYyyymmddhh(name):
    """Check if a string is of format yyyymmddhh

    Parameters
    ----------
    name : str
       Name to check

    Returns
    -------
    bool
        true if name has that format
    """
    if (len(name) == 10):
        if (datetime.datetime.strptime(name, '%Y%m%d%H')):
            return 1
    return 0

#----------------------------------------------------------------------------
def isYyyymmddhhmmss(name):
    """Check if a string is of format yyyymmddhhmmss

    Parameters
    ----------
    name : str
       Name to check

    Returns
    -------
    bool
        true if name has that format
    """
    if (len(name) == 14):
        if (datetime.datetime.strptime(name, '%Y%m%d%H%M%S')):
            return 1
    return 0

#----------------------------------------------------------------------------
#
# filter a list of names to those that are dates of format yyyymmddhh
#
# names = list of names
#
# return filtered list
#
def datesWithHour(names):
    """Filter a list down to elements that have format yyyymmdd

    Parameters
    ----------
    names : list[str]
        The names to filter

    Returns
    -------
    list[str]
        The filtered names
    """
    return [name for name in names if (isYyyymmddhh(name)==1)]

    
#----------------------------------------------------------------------------
def getFileNames(aDir):
   """Return the files in a directory that are not themselves subdirectories

   Parameters
   ----------
   aDir: str
      Full path directory name

   Returns
   -------
   List[str]
      the data files in the directory
   """
   return [name for name in os.listdir(aDir)
           if not os.path.isdir(os.path.join(aDir, name))]

#----------------------------------------------------------------------------
def getImmediateSubdirectories(aDir):
   """return the subdirectories of a directory

   Parameters
   ----------
   aDir: str
      Full path directory name

   Returns
   -------
   list[str]
      All subdirectories of the aDir

   """

   # does the dir exist?
   if (not os.path.exists(aDir)):
       return []

   return [name for name in os.listdir(aDir)
           if os.path.isdir(os.path.join(aDir, name))]

#---------------------------------------------------------------------------
def getYyyymmddhhSubdirectories(dir):
   """return the 'yyyymmddhh' subdirectories of a directory

   Parameters
   ----------
   aDir: str
      Full path directory name

   Returns
   -------
   list[str]
      All subdirectories of the aDir that are of format 'yyyymmddhh'

   """
   names = getImmediateSubdirectories(dir)
   return datesWithHour(names)

#----------------------------------------------------------------------------
def newestIssueTime(dir):
    """return the subdirectory (yyyymmddhh) that is for the newest issue time

    Parameters
    ----------
    dir : str
       Directory with subdirectories

    Returns
    -------
    str
       The subdirectory with biggest issue time, or empty string
    """       
    names = getYyyymmddhhSubdirectories(dir)
    if (not names):
        return ""

    names = sorted(names)
    ret = names[-1]
    return ret
    
#----------------------------------------------------------------------------
def forecastExists(dir, issueTime, fcstHour):
    """ Check if forecast exists

    Parameters
    ----------
    dir : str
       Full path to the issue time directories
    issueTime : datetime
       The issue time (y,m,d,h)       
    fcstHour:  int
       should be 0 or 3

    Returns
    -------
    bool
    True if the forecast does exist on disk
    """
           
    path = dir + "/"
    path += issueTime.strftime("%Y%m%d%H")
    if (os.path.isdir(path)):
        validTime = issueTime + datetime.timedelta(hours=fcstHour)
        fname = validTime.strftime("%Y%m%d%H%M") + ".LDASIN_DOMAIN1.nc"
        names = getFileNames(path)
        for n in names:
            if (n == fname):
                logging.debug("Found %s in %s",  fname, path)
                return 1
    return 0

#----------------------------------------------------------------------------
def obsExists(dir, issueTime):
    """ Check if obs exists

    Parameters
    ----------
    dir : str
       Full path to the MRMS directories
    issueTime : datetime
       The issue time (y,m,d,h)       

    Returns
    -------
    bool
    True if the data does exist on disk
    """
           
    path = dir + "/"
    path += issueTime.strftime("%Y%m%d%H")
    if (os.path.isdir(path)):
        fname = issueTime.strftime("%Y%m%d%H%M") + ".LDASIN_DOMAIN1.nc"
        names = getFileNames(path)
        for n in names:
            if (n == fname):
                logging.debug("Found %s in %s",  fname, path)
                return 1
    return 0

#----------------------------------------------------------------------------
def parmRead(fname):
    """ Read in a param file

    Parameters
    ---------
    fname : str
       Name of the file to read
    Returns
    -------
    Parms
        The parameters that were read in
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

    forcing_config_label = "AnalysisAssimLayeringDriver"
    logging_filename =  forcing_config_label + ".log" 
    logging.basicConfig(format='%(asctime)s %(message)s',
                        filename=logging_filename, level=set_level)

    hrrrDir = parser.get('downscaling', 'HRRR_finished_output_dir')
    hrrr0hrDir = parser.get('downscaling', 'HRRR_finished_output_dir_0hr') # placeholder
    mrmsDir = parser.get('regridding', 'MRMS_finished_output_dir')  # maybe incorrect
    rapDir = parser.get('downscaling', 'RAP_finished_output_dir')
    rap0hrDir = parser.get('downscaling', 'RAP_finished_output_dir_0hr') # placeholder
    layerDir = parser.get('layering', 'analysis_assimilation_output')
    maxFcstHour = 3

    hoursBack = 5   # 3 hours back at 0, -1, and -2    (-2 -3 = -5)

    maxWaitMinutes=15 #int(parser.get('triggering',
                      #           'short_range_fcst_max_wait_minutes'))
    veryLateMinutes=20 #int(parser.get('triggering',
                       #            'short_range_fcst_very_late_minutes'))
    stateFile = parser.get('triggering', 'analysis_assim_layering_state_file')

    parms = Parms(hrrrDir, hrrr0hrDir, rapDir, rap0hrDir, mrmsDir, layerDir,
                  maxFcstHour, hoursBack, maxWaitMinutes, veryLateMinutes, stateFile)

    return parms

#----------------------------------------------------------------------------
class Parms:
    """ Parameters from the main wrf_hydro param file that are used for layering

    Attributes
    ----------
    _hrrrDir : str
       HRRR top input directory
    _hrrr0hrDir : str
       HRRR top input directory, 0 hour forecasts
    _rapDir : str
       RAP top input directory
    _rap0hrDir : str
       RAP top input directory, 0 hour forecasts
    _mrmsDir : str
       MRMS top input directory
    _layerDir : str
       output top directory
    _maxFcstHour : int
       maximum forecast hour for layered output
    _hoursBack : int
       Hours back to maintain state, issue time
    _maxWaitSeconds
       Maximum number of sec. to wait for additional inputs after first arrives
    _veryLateSeconds
       Maximum number of sec. before declaring a forecast very late
    _stateFile : str
        Name of file with state information
    """
    def __init__(self, hrrrDir, hrrr0hrDir, rapDir, rap0hrDir, mrmsDir,
                 layerDir, maxFcstHour, hoursBack,
                 maxWaitMinutes, veryLateMinutes, stateFile) :
        """ Initialize from input args
        
        Parameters
        ----------
        Inputs are 1 to 1 with attributes
        """
        self._hrrrDir = hrrrDir
        self._hrrr0hrDir = hrrr0hrDir
        self._rapDir = rapDir
        self._rap0hrDir = rap0hrDir
        self._mrmsDir = mrmsDir
        self._layerDir = layerDir
        self._maxFcstHour = maxFcstHour
        self._hoursBack = hoursBack
        self._maxWaitSeconds = maxWaitMinutes*60
        self._veryLateSeconds = veryLateMinutes*60
        self._stateFile = stateFile


    def debugPrint(self):
        """ logging debug of content
        """
        logging.debug("Parms: HRRR_data = %s", self._hrrrDir)
        logging.debug("Parms: HRRR_0_data = %s", self._hrrr0hrDir)
        logging.debug("Parms: RAP_data = %s", self._rapDir)
        logging.debug("Parms: RAP_0_data = %s", self._rap0hrDir)
        logging.debug("Parms: MRMSdata = %s", self._mrmsDir)
        logging.debug("Parms: Layer_data = %s", self._layerDir)
        logging.debug("Parms: MaxFcstHour = %d", self._maxFcstHour)
        logging.debug("Parms: HoursBack = %d", self._hoursBack)
        logging.debug("Parms: maxWaitSeconds = %d", self._maxWaitSeconds)
        logging.debug("Parms: veryLateSeconds = %d", self._veryLateSeconds)
        logging.debug("Parms: StateFile = %s", self._stateFile)


#----------------------------------------------------------------------------
class ForecastStep:
    """ Internal state that is read in and saved out, individual time step relative to an issue time
    
    Assumes there is an issue time at a higher level

    Attributes
    ----------
    _empty : bool
       true if contents not set
    _step : int
       0, 1, or 2
    _hrrr0 : bool
       true if HRRR input is available at issue - _step, hour 0
    _hrrr3 : bool
       true if HRRR input is available at issue - _step - 3, hour 3
    _rap0 : bool
       true if RAP input is available at issue - _step, hour 0
    _rap3 : bool
       true if RAP input is available at issue - _step - 3, hour 3
    _mrms : bool
       true if MRMS input is available at issue - _step
    _layered : bool
       true if this step has been layered (sent to Analysis/Assimilation)
    """
    def __init__(self, configString=""):
        """ Initialize by parsing a a config file  line

        Parameters
        ----------
        configString : str
           Config file line, or empty
        """

        # init to empty
        self._empty = 1
        self._step = 0
        self._hrrr0 = 0
        self._hrrr3 = 0
        self._rap0 = 0
        self._rap3 = 0
        self._mrms = 0
        self._layered = 0
        if not configString:
            return

        # parse
        self._empty = 0
        self._step = int(configString[0:1])
        self._hrrr0 = int(configString[2:3])
        self._hrrr3 = int(configString[4:5])
        self._rap0 = int(configString[6:7])
        self._rap3 = int(configString[8:9])
        self._mrms = int(configString[10:11])
        self._layered = int(configString[12:13])
    def debugPrint(self):
        """ logging debug of content
        """
        logging.debug("FcstStep: empty=%d", self._empty)
        if (self._empty):
            return
        logging.debug("FcstStep[%d] hrrr0:%d hrrr3:%d rap0:%d rap3:%d mrms:%d lay:%d",
                      self._step, self._hrrr0, self._hrrr3, self._rap0,
                      self._rap3, self._mrms, self._layered)

    def debugPrintString(self):
        """ logging debug of content
        Returns
        -------
        str
        """
        if (self._empty):
            return ""
        ret = 's[%d] hr0[%d] hr3[%d] rp0[%d] rp3[%d] mrms[%d] lay[%d]' %(self._step,
          self._hrrr0,
          self._hrrr3,
          self._rap0,
          self._rap3,
          self._mrms,
          self._layered)
        return ret
    
    def initializeContent(self, step):
        """ Set content using inputs

        Parameters
        ----------
        step : int
           Step 0, 1, 2
        """
        self._empty = 0
        self._step = step
        self._hrrr0 = 0
        self._hrrr3 = 0
        self._rap0 = 0
        self._rap3 = 0
        self._mrms = 0
        self._layred = 0
        
    def stepName(self):
        ret = stepStaticName(self._step)
        return ret

    def writeConfigString(self):
        """ Write local content as a one line string
        Returns
        -------
        str
        """
        if (self._empty):
            # write fake stuff out
            ret = "0 0 0 0 0 0 0"
        else:
            ret = '%01d %01d %01d %01d %01d %01d %01d' %(self._step,
                                                         self._hrrr0,
                                                         self._hrrr3,
                                                         self._rap0,
                                                         self._rap3,
                                                         self._mrms,
                                                         self._layered)
        return ret
    
    def setAvailability(self, parms, issueTime):
        """ Change availability status when appropriate by looking at disk

        Parameters
        ----------
        parms : Parms
            parameters
        issueTime : datetime
            time of this assimilation

        Returns
        -------
        none
        """

        if (self._layered):
            return
        
        time0 = issueTime - datetime.timedelta(hours=self._step)
        time3 = issueTime - datetime.timedelta(hours=(self._step + 3))

        if (self._hrrr0 == 0):
            self._hrrr0 = forecastExists(parms._hrrr0hrDir, time0, 0)
        if (self._hrrr3 == 0):
            self._hrrr3 = forecastExists(parms._hrrrDir, time3, 3)
        if (self._rap0 == 0):
            self._rap0 = forecastExists(parms._rap0hrDir, time0, 0)
        if (self._rap3 == 0):
            self._rap3 = forecastExists(parms._rapDir, time3, 3)
        if (self._mrms == 0):
            self._mrms = obsExists(parms._mrmsDir, time0)


    def layerIfReady(self, parms, itime):
        """  Perform layering if state is fully ready

        Parameters
        ----------
        parms : Parms
           Parameters
        itime : datetime
        Returns
        -------
        bool
           True if layering was done, or had previously been done
        """
        
        if (self._layered == 1):
            return 1
        self.setAvailability(parms, itime)
        if (self._hrrr0 == 1 and self._rap0 == 1 and
            self._hrrr3 == 1 and self._rap3 == 1 and self._mrms == 1):
            self._layered = 1
            layer(parms, itime, self._step, "RAP_HRRR_MRMS")
            return 0
        return 0
    
    def forceLayer(self, parms, itime):
        """  Perform layering if state is partially ready enough

        Parameters
        ----------
        parms : Parms
           Parameters
        itime : datetime
        Returns
        -------
        bool
           True if layering was done, or had previously been done
        """
        
        if (self._layered == 1):
            return 1
        self.setAvailability(parms, itime)
        if (self._rap0 == 1 and self._rap3 == 1):
            if (self._hrrr0 == 1 and self._hrrr3 == 1):
                self._layered = 1
                if (self._mrms == 1):
                    layer(parms, itime, self._step, "RAP_HRRR_MRMS")
                else:
                    layer(parms, itime, self._step, "RAP_HRRR")
            else:
                self._layered = 1
                layer(parms, itime, self._step, "RAP")
        else:
            self._layered = 1
            logging.warning("WARNING, no layering of %s, step=-%d",
                            itime.strftime("%Y%m%d%h"), self._step)
    
#----------------------------------------------------------------------------
class State:
    """ Internal state that is read in and saved out

    Attributes

    _empty : bool
       true if contents not set
    _issue : datetime
       Issue time (y, m, d, h, 0, 0)
    _step : list[ForecastStep]
       The 3 steps 0, 1, 2 hours back
    _layered : bool
       true if this forecast has been layered
    _clockTime : datetime
       time at which the first forecast input was available
    """
    def __init__(self):
        """ Initialize

        Parameters
        ----------
        """

        # init to empty
        self._empty = 1
        self._first = 1
        self._issue = datetime.datetime
        self._step = []
        self._layered = 0
        self._clockTime = datetime.datetime

    def initFromStateFile(self, confFile):

        # parse
        cf = SafeConfigParser()
        cf.read(confFile)
        self._step = []
        self._first = 1
        self._empty = 1
        status = int(cf.get('status', 'first'))
        if (status == 1):
            return
        self._empty = 0
        self._first = int(cf.get('forecast', 'first'))
        stime = cf.get('forecast', 'issue_time')
        self._issue = datetime.datetime.strptime(stime, "%Y%m%d%H")

        cf.get('forecast', 'layered', self._layered)
        fs0 = ForecastStep(cf.get('forecast', stepStaticName(0)))
        fs1 = ForecastStep(cf.get('forecast', stepStaticName(1)))
        fs2 = ForecastStep(cf.get('forecast', stepStaticName(2)))
        self._step.append(fs0)
        self._step.append(fs1)
        self._step.append(fs2)
        stime = cf.get('forecast', 'clock_time')
        self._clockTime = datetime.datetime.strptime(stime, '%Y-%m-%d_%H:%M:%S')
        
    def debugPrint(self):
        """ logging debug of content
        """
        logging.debug("Fcst: empty=%d first=%d", self._empty, self._first)
        if (self._empty):
            return
        logging.debug("Fcst: I:%s step[0]:%s step[1]:%s step[2]:%s layered:%d clockTime=%s",
                      self._issue.strftime("%Y%m%d%H"),
                      self._step[0].debugPrintString(),
                      self._step[1].debugPrintString(),
                      self._step[2].debugPrintString(),
                      self._layered, 
                      self._clockTime.strftime("%Y-%m-%d_%H:%M:%S"))

    def initialize(self, parms, newest):
        """  Initialize state using inputs. Called when issue time changes.

        Parameters
        ----------
        parms : Parms
           Parameteres
        newest : str
           yyyymmddhh string for the new issue time
        """

        # convert to datetime
        itime = datetime.datetime.strptime(newest, '%Y%m%d%H')

        self._empty = 0
        self._step = []
        self._first = 1
        self.setContent(itime)
        
    def write(self, parmFile):
        """ Write contents to a state file

        Parameters
        ----------
        parmFile : str
           Name of file to write to 
        """

        config = SafeConfigParser()

        config.add_section('status')
        if (self._empty == 1):
            config.set('status', 'first', '1')
        else:
            config.set('status', 'first', '0')

        # When adding sections or items, add them in the reverse order of
        # how you want them to be displayed in the actual file.
        # In addition, please note that using RawConfigParser's and the raw
        # mode of ConfigParser's respective set functions, you can assign
        # non-string values to keys internally, but will receive an error
        # when attempting to write to a file or when you get it in non-raw
        # mode. SafeConfigParser does not allow such assignments to take place.
        config.add_section('forecast')

        if (self._first == 1):
            config.set('forecast', 'first', '1')
        else:
            config.set('forecast', 'first', '0')
        config.set('forecast', 'issue_time', self._issue.strftime("%Y%m%d%H"))
        if (self._layered == 1):
            config.set('forecast', 'layered', '1')
        else:
            config.set('forecast', 'layered', '0')
        for f in self._step:
            s = f.writeConfigString()
            stepName = f.stepName()
            config.set('forecast', stepName, s)
        config.set('forecast', 'clock_time',
                   self._clockTime.strftime("%Y-%m-%d_%H:%M:%S"))
        
        # Write it out
        with open(parmFile, 'wb') as configfile:
            config.write(configfile)


    def setContent(self, issueTime):
        """ Set content using inputs

        Parameters
        ----------
        issueTime : datetime
            Model run time
        lt : int
            Forecast time seconds
        """
        self._empty = 0
        self._issue = issueTime
        self._step = []
        self._first = 1
        fs0 = ForecastStep()
        fs0.initializeContent(0)
        self._step.append(fs0)
        fs1 = ForecastStep()
        fs1.initializeContent(1)
        self._step.append(fs1)
        fs2 = ForecastStep()
        fs2.initializeContent(2)
        self._step.append(fs2)
        self._layered = 0
        self._clockTime = datetime.datetime.utcnow()
        #self.debugPrint()
        
    def isNewModelIssueTime(self, issueTime):
        """ Check if input is a new model issue time or not

        Parameters
        ----------
        issueTime: str
            yyyymmddhh string
        Returns
        -------
        bool
            true if the input issue time is not in the state
        
        """
        if (self._empty):
            return 1
        else:
            itime = datetime.datetime.strptime(issueTime, '%Y%m%d%H')
            return (itime > self._issue)
    

    def setCurrentModelAvailability(self, parms):
        """ Change availability status when appropriate by looking at disk

        Parameters
        ----------
        parms : Parms
            parameters
        model : Model
            overall status for this model run, used for clock time

        Returns
        -------
        none
        """

        if (self._layered):
            # no need to do more, already layered
            return
        if (self._empty):
            logging.error("Empty when not expected")
            return
        
        # make note if going from nothing to something
        nothing = 1
        for f in self._step:
            if (f._layered):
                nothing = 0


        #if (nothing):
            #logging.debug("Nothing, so trying to get stuff")

        # first time only, try the -1 and -2 steps, force with what we have
        if (self._first):
            self._step[2].forceLayer(parms, self._issue)
            self._step[1].forceLayer(parms, self._issue)
            self._first = 0
            
        self._step[0].layerIfReady(parms, self._issue)
        self._layered = self._step[0]._layered
        if (not self._layered):
            tnow = datetime.datetime.utcnow()
            diff = tnow - self._clockTime
            idiff = diff.total_seconds()
            if (idiff > parms._veryLateSeconds):
                logging.warning("WARNING: Inputs for layering timeout Issue:%s",
                                self._issue.strftime("%Y%m%d%H"))
                self._step[0].forceLayer(parms, self._issue)
                self._layered = 1
                
#----------------------------------------------------------------------------
def main(argv):

    # User must pass the config file into the main driver.
    configFile = argv[0]
    if not os.path.exists(configFile):
        print 'ERROR forcing engine config file not found.'
        return 1

    # read in fixed main params
    parms = parmRead(configFile)

    newestT = ""
    newestT1 = newestIssueTime(parms._hrrrDir)
    if (newestT):
        if (newestT1):
            if (newestT1 > newestT):
                newestT = newestT1
    else:
        newestT = newestT1
        
    newestT1 = newestIssueTime(parms._rapDir)
    if (newestT):
        if (newestT1):
            if (newestT1 > newestT):
                newestT = newestT1
    else:
        newestT = newestT1
    newestT1 = newestIssueTime(parms._hrrr0hrDir)
    if (newestT):
        if (newestT1):
            if (newestT1 > newestT):
                newestT = newestT1
    else:
        newestT = newestT1
        
    newestT1 = newestIssueTime(parms._rap0hrDir)
    if (newestT):
        if (newestT1):
            if (newestT1 > newestT):
                newestT = newestT1
    else:
        newestT = newestT1
        
    newestT1 = newestIssueTime(parms._mrmsDir)
    if (newestT):
        if (newestT1):
            if (newestT1 > newestT):
                newestT = newestT1
    else:
        newestT = newestT1
        

    if (not newestT):
        logging.debug("No data")
        return 0

    # if there is not a state file, create one now using newest
    if (not os.path.exists(parms._stateFile)):
        state = State()
        logging.info("Initializing")
        state.initialize(parms, newestT)
        state.write(parms._stateFile)

    # Normal processing situation
    logging.debug("Look for Layering....")
    
    # read in state
    state2 = State()
    state2.initFromStateFile(parms._stateFile)
    #state2.debugPrint()
    if state2._empty:
        # error return here
        return 0
    
    # check for new issue time
    if (state2.isNewModelIssueTime(newestT)):
        logging.info("Re-Initializing state, new model issue time %s", newestT)
        state2.initialize(parms, newestT)

    # update availability
    state2.setCurrentModelAvailability(parms)

    # write out final state
    state2.write(parms._stateFile)
    return 0

#----------------------------------------------

if __name__ == "__main__":
    main(sys.argv[1:])
