# wrf_hydro_forcing
This repository contains all scripts (NCL, Python) used in the WRF-Hydro forcing engine, which will account for the following configurations:
    Analysis & assimilation
    Short Range Forcing 
    Medium Range Forcing
    Long Range Forcing
    Retrospective Forcing
    
USAGE:
Check out the regridding and downscaling scripts from the scripts/NCL directory, the WRF-Hydro forcing engine, WRF-Hydro_forcing.py from the scripts/Python directory, and the config/parm file wrf_hydro_forcing.parm from the parm directory.  Indicate the directory where your input data is located, where you wish the output data to reside, and where the regridding and downscaling scripts are located.  In the main section of the <forcing config>.py, indicate your logging level, the name of your logging file, the product to process, the location of the weighting files, and indicate which action you wish to perform (ie regridding, downscaling).  To run, do the following at the command line:

    python <forcing config name>.py
    
    where the forcing config name = Analysis_Assimilation_Forcing, Short_Range_Forcing, Long_Range_Forcing, etc.
    Make sure you have the config/parm file, the forcing config file and the WRF_Hydro_forcing.py file in the same 
    directory from which you are invoking.
    
*Note: The weightings files should be available for every model type.  These will usually reside on the test host.  Currently, they are found in hydro-c1:/d4/hydro-dm/IOC/weightings.
    
    
