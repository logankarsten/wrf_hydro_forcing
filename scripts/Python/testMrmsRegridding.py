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

def main(argv):
   aaf.forcing('regrid', 'MRMS', 'GaugeCorr_QPE_00.00_20151203_190000.grib2')

#----------------------------------------------

if __name__ == "__main__":
    main(sys.argv[1:])
