"""WhfLog
Handles log file creation
"""

import os
import datetime
import logging
import DataFiles as df
from ConfigParser import SafeConfigParser
#from inspect import getframeinfo, stack
import inspect

# global var always length 7  'Short   ', 'Medium ', 'Long   ', 'AA     '
WhfConfigType = '      '
WhfConfigTypeLen = 7

# global variable always length 7  'Regrid ', 'Layer  '
WhfAction = '       '
WhfActionLen = 7

# global variable always length 14  'RAP,HRRR/MRMS ', ...
WhfData = '              '
WhfDataLen = 14


def init(parser, logFileName, configType, action, data):
    """Initialize log file using configFile content, and a log file name

    Parameters
    ----------
    parser : SafeConfigParser
        parser that has parsed the file on entry
    logFileName : str
        Name of the log file, without a .log suffix
    """

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
    logging_path = parser.get('log_level', 'forcing_engine_log_dir')
    df.makeDirIfNeeded(logging_path)
    logging_path += "/"
    now = datetime.datetime.utcnow()
    logging_path += now.strftime("%Y%m%d")
    df.makeDirIfNeeded(logging_path)

    logging_filename =  logging_path + "/" + logFileName + ".log" 
#    logging.basicConfig(format='%(asctime)s %(levelname)s [[%(filename)s:%(lineno)d],%(funcName)s]   %(message)s',
#                        filename=logging_filename, level=set_level)
    logging.basicConfig(format='%(asctime)s  %(message)s',
                        filename=logging_filename, level=set_level)

    global WhfConfigType
    WhfConfigType = configType
    WhfConfigType = WhfConfigType.ljust(WhfConfigTypeLen)

    global WhfAction
    WhfAction = action
    WhfAction = WhfAction.ljust(WhfActionLen)
    
    global WhfData
    WhfData = data
    WhfData = WhfData.ljust(WhfDataLen)
    
def setConfigType(ctype):
    global WhfConfigType
    WhfConfigType = ctype
    WhfConfigType = WhfConfigType.ljust(WhfConfigTypeLen)

def setData(data):
    global WhfData
    WhfData = data
    WhfData = WhfData.ljust(WhfDataLen)

def debug(fmt, *argv):
    lineno = inspect.stack()[1][2]
    funcname = inspect.stack()[1][3]
    filename = os.path.basename(inspect.stack()[1][1])
    linestr = '%d' % (lineno)
    formatStr = 'OK      ' + WhfConfigType + WhfAction + WhfData + " [" + filename + ":" + linestr + "," + funcname + "] " + fmt
    logging.debug(formatStr, *argv)
    
def info(fmt, *argv):
    lineno = inspect.stack()[1][2]
    funcname = inspect.stack()[1][3]
    filename = os.path.basename(inspect.stack()[1][1])
    linestr = '%d' % (lineno)
    formatStr = 'OK      ' + WhfConfigType + WhfAction + WhfData + " [" + filename + ":" + linestr + "," + funcname + "] " + fmt
    logging.info(formatStr, *argv)
    
def warning(fmt, *argv):
    lineno = inspect.stack()[1][2]
    funcname = inspect.stack()[1][3]
    filename = os.path.basename(inspect.stack()[1][1])
    linestr = '%d' % (lineno)
    formatStr = 'WARNING ' + WhfConfigType + WhfAction + WhfData + " [" + filename + ":" + linestr + "," + funcname + "] " + fmt
    logging.warning(formatStr, *argv)
    
def error(fmt, *argv):
    lineno = inspect.stack()[1][2]
    funcname = inspect.stack()[1][3]
    filename = os.path.basename(inspect.stack()[1][1])
    linestr = '%d' % (lineno)
    formatStr = 'ERROR   ' + WhfConfigType + WhfAction + WhfData + " [" + filename + ":" + linestr + "," + funcname + "] " + fmt
    logging.error(formatStr, *argv)
    
def critical(fmt, *argv):
    lineno = inspect.stack()[1][2]
    funcname = inspect.stack()[1][3]
    filename = os.path.basename(inspect.stack()[1][1])
    linestr = '%d' % (lineno)
    formatStr = 'CRITICL ' + WhfConfigType + WhfAction + WhfData + " [" + filename + ":" + linestr + "," + funcname + "] " + fmt
    logging.critical(formatStr, *argv)
    
