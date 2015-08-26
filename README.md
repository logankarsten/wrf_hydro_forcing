# wrf_hydro_forcing
This repository contains any script (NCL, Python) used in the WRF-Hydro forcing engine, which will account for the following configurations:
    Analysis & assimilation
    Short Range Forcing 
    Medium Range Forcing
    Long Range Forcing
    Retrospective Forcing
    
USAGE:
Check out the regridding and downscaling scripts from the scripts/NCL directory, the WRF-Hydro forcing engine, WRF-Hydro_forcing.py from the scripts/Python directory, and the config/parm file wrf_hydro_forcing.parm from the parm directory.  Indicate the directory where your input data is located, where you wish the output data to reside, and where the regridding and downscaling scripts are located.  In the main section of the WRF-Hydro_forcing.py, indicate your logging level, the name of your logging file, the product to process, the location of the weighting files, and indicate which action you wish to perform (ie regridding, downscaling).  To run, do the following at the command line:

    python WRF-Hydro_forcing.py
    
*Note: The weightings files should be available for every model type.  These will usually reside on the test host.  Currently, they are found in hydro-c1:/d4/hydro-dm/IOC/weightings.
    
    
