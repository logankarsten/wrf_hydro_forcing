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
   print "REGRIDDING RAP DATA, file=", fname
   srf.forcing('regrid', 'RAP', fname[9:])
    

if __name__ == "__main__":
    regridRAP('20151203/20151203_i17_f000_WRF-RR.grb2')
    
