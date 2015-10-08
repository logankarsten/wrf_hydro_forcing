import WRF_Hydro_forcing as whf
import logging
import os
from ConfigParser import SafeConfigParser

"""Analysis_Assimilation_Forcing
Performs the regridding and downscaling 
associated with the Analysis and Assimilation
forcing configuration.  Uses methods in the
WRF_Hydro_forcing module and input parameters
that are defined in the wrf_hydro_forcing.parm
parameter/configuration file.
"""

#----------------------------------------------

if __name__ == "__main__":
    parser = SafeConfigParser()
    parser.read('wrf_hydro_forcing.parm')

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

    logging_filename =  forcing_config_label + ".log" 
    logging.basicConfig(format='%(asctime)s %(message)s',
                         filename=logging_filename, level=set_level)
    # STUB- TO BE IMPLEMENTED  
    # Bias correction 
    # MRMS_<prod>  = whf.bias_corr("<prod>", parser)

    # Regrid the MRMS, RAP, and HRRR data.
    MRMS_regrids = whf.regrid_data("MRMS",parser)     
    RAP_regrids = whf.regrid_data("RAP", parser)
    HRRR_regrids = whf.regrid_data("HRRR", parser)
    
    # Downscale the RAP and HRRR data; the MRMS data does not require
    # downscaling. 
    RAP_downscalings = whf.downscale_data("RAP",parser)
    HRRR_downscalings = whf.downscale_data("HRRR", parser)

    # Layering the HRRR (primary) and RAP (secondary) data.
    Analysis_Assimilation_Layering = whf.layer_data(parser, "HRRR","RAP")
   
    # Generate the metrics for regridding, downscaling and layering. 
    # Write to the logfile, which by default is saved to the directory 
    # from which this application is run.
    # 
    whf.create_benchmark("MRMS","Regridding", MRMS_regrids)
    whf.create_benchmark("MRMS","Downscaling", MRMS_downscalings)
    whf.create_benchmark("RAP","Regridding", RAP_regrids)
    whf.create_benchmark("RAP","Downscaling", RAP_downscalings)
    whf.create_benchmark("HRRR","Regridding", HRRR_regrids)
    whf.create_benchmark("HRRR","Downscaling", HRRR_downscalings)
    whf.create_benchmark("HRRR-RAP", "Layering", Analysis_Assimilation_Layering)
