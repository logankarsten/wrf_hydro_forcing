import WRF-Hydro_forcing as whf
import logging
import os
from ConfigParser import SafeConfigParser

#----------------------------------------------

if __name__ == "__main__":
    parser = SafeConfigParser()
    parser.read('wrf_hydro_forcing.parm')

    ncl_exec = parser.get('exe', 'ncl_exe')
    ncarg_root = parser.get('default_env_vars', 'ncarg_root')
    logging_level = parser.get('log_level', 'forcing_engine_log_level')
    log_file_dir = parser.get('log_level', 'output_log_directory')
    forcing_config_label = "Medium-Range"

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

    logging_filename = forcing_config_label + "_forcing.log" 
    logging.basicConfig(format='%(asctime)s %(message)s',
                         filename=logging_filename, level=set_level)

    # Regrid the GFS data.
    GFS_regrids = whf.regrid_data("GFS",parser, ncl_exec)     
    
    # Downscale the GFS data.
    GFS_downscalings = whr.downscale_data("GFS", parser, ncl_exec)
   
    # Generate the metrics for regridding and downscaling and write to the
    # logfile, which by default is saved to the directory from which this
    # script in invoked.
    whf.create_benchmark("GFS","Regridding", GFS_regrids)
    whf.create_benchmark("GFS","Downscaling", GFS_downscalings)
