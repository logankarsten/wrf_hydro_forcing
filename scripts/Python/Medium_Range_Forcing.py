import WRF_Hydro_forcing as whf
import logging
import os
from ConfigParser import SafeConfigParser
import sys
import getopt

"""Medium_Range_Forcing
Performs regridding and downscaling, then bias
correction, and layering/mixing of data products 
associated with the Medium Range forcing configuration. 
Invokes methods in the WRF_Hydro_forcing module and 
input parameters that are defined in the wrf_hydro_forcing.parm
parameter/configuration file.  Logs to a log
file that is created in the same directory
from where this script is executed.  

"""


def usage():
    print (' -h --help:  Usage/help\n -r --regrid: Regrid data\n -d --downscale: Downscale\n -l --layer: Layer data\n -b --bias:  Bias correction' )


def main(argv):
    # Read the parameters from the config/param file.
    parser = SafeConfigParser()
    parser.read('wrf_hydro_forcing.parm')
    ncl_exec = parser.get('exe', 'ncl_exe')
    ncarg_root = parser.get('default_env_vars', 'ncarg_root')
    logging_level = parser.get('log_level', 'forcing_engine_log_level')
    forcing_config_label = "Analysis_Assimilation"

    # Check for the NCARG_ROOT environment variable. If it is not set,
    # use an appropriate default, defined in the configuration file.
    ncarg_root_found = os.getenv("NCARG_ROOT")
    if ncarg_root_found is None:
        ncarg_root = os.environ["NCARG_ROOT"] = ncarg_root
   
    # Set the NCL_DEF_LIB_DIR to indicate where ALL shared objects
    # reside.
    ncl_def_lib_dir = parser.get('default_env_vars','ncl_def_lib_dir')
    ncl_def_lib_dir = os.environ["NCL_DEF_LIB_DIR"] = ncl_def_lib_dir
    
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

    logging_filename =  forcing_config_label + ".log" 
    logging.basicConfig(format='%(asctime)s %(message)s',
                         filename=logging_filename, level=set_level)

    try:
        (opts, args) = getopt.getopt(argv,"hrdlb",['help','regrid','downscale','layer','bias'])
    except getopt.GetoptError:
        usage()
        sys.exit(2)
    for opt, arg in opts:
        if opt in ('-h','--help'):
            usage()
            sys.exit()
        elif opt == '-r' or opt == '--regrid':
            print 'regridding data...'
            GFS_regrids = whf.regrid_data("GFS", parser)
            whf.create_benchmark("GFS","Regridding", RAP_regrids)
            HRRR_regrids = whf.regrid_data("GFS", parser)
        elif opt == '-d' or opt == '--downscale':
            print 'downscaling data...'
            GFS_downscalings = whf.downscale_data("GFS",parser, True)
            whf.create_benchmark("GFS","Downscaling", RAP_downscalings)
        elif opt == '-l' or opt == '--layer':
            print 'layering data...'
        elif opt == '-b' or opt == '--bias':
            print 'bias correcting...'
            # TO BE IMPLEMENTED in WRF_Hydro_forcing.py
            # Perform bias correction on any necessary input data.
            # 
            # bias_correction("GFS")
    


   

#----------------------------------------------

if __name__ == "__main__":
    main(sys.argv[1:])
