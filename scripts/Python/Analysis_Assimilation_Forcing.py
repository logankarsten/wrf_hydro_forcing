import Test as whf
import logging
import os
from ConfigParser import SafeConfigParser
#import WRF-Hydro_forcing

#----------------------------------------------

if __name__ == "__main__":
    parser = SafeConfigParser()
    parser.read('test.parm')

    ncl_exec = parser.get('exe', 'ncl_exe')
    ncarg_root = parser.get('default_env_vars', 'ncarg_root')
    logging_level = parser.get('log_level', 'forcing_engine_log_level')
    log_file_dir = parser.get('log_level', 'output_log_directory')
    forcing_config_label = "Analysis_Assimilation"

    # Check for the NCARG_ROOT environment variable. If it is not set,
    # use an appropriate default, defined in the configuration file.
    ncarg_root_found = os.getenv("NCARG_ROOT")
    if ncarg_root_found is None:
        ncarg_root = os.environ["NCARG_ROOT"] = ncarg_root
    
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

    logging_filename = forcing_config_label + ".log" 
    logging.basicConfig(format='%(asctime)s %(message)s',
                         filename=logging_filename, level=set_level)

    # Regrid the MRMS, NAM, and HRRR data.
    MRMS_regrids = whf.regrid_data("MRMS",parser)     
    NAM_regrids = whf.regrid_data("NAM", parser)
    HRRR_regrids = whf.regrid_data("HRRR", parser)
    
    # Downscale the NAM and HRRR data; the MRMS data does not require
    # downscaling. 
    NAM_downscalings = whf.downscale_data("NAM",parser)
    HRRR_downscalings = whf.downscale_data("HRRR", parser)
   
    # Generate the metrics for regridding and downscaling and write to the
    # logfile, which by default is saved to the directory from which this
    # 
    whf.create_benchmark("MRMS","Regridding", MRMS_regrids)
    whf.create_benchmark("MRMS","Downscaling", MRMS_downscalings)
    whf.create_benchmark("NAM","Regridding", NAM_regrids)
    whf.create_benchmark("NAM","Downscaling", NAM_downscalings)
    whf.create_benchmark("HRRR","Regridding", HRRR_regrids)
    whf.create_benchmark("HRRR","Downscaling", HRRR_downscalings)
