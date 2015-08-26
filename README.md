# wrf_hydro_forcing
This repository contains any script (NCL, Python) used in the WRF-Hydro forcing engine, which will account for the following configurations:
    Analysis & assimilation
    Short Range Forcing 
    Medium Range Forcing
    Long Range Forcing
    Retrospective Forcing
    
USAGE:
Check out the regridding and downscaling scripts from the scripts/NCL directory, the WRF-Hydro forcing engine, WRF-Hydro_forcing.py from the scripts/Python directory, and the config/parm file wrf_hydro_forcing.parm from the parm directory.  Indicate the directory where your input data is located, where you wish the output data to reside, and where the regridding and downscaling scripts are located.  In the main section of the WRF-Hydro_forcing.py, indicate your logging level, the name of your logging file, the product to process, and which action you wish to perform.  To run, simply do the following:

    python WRF-Hydro_forcing.py
    

    
    
