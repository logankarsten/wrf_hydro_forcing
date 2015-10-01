# wrf_hydro_forcing
This repository contains all scripts (NCL, Python) and shared objects (from Fortran) used in the WRF-Hydro forcing engine.  The following forcing configurations will be supported:
    Analysis & assimilation
    Short Range Forcing 
    Medium Range Forcing
    Long Range Forcing
    Retrospective Forcing (omit for now, not included for IOC)
    
How to run:
1) Check out the regridding, downscaling and layering/combining scripts from the scripts/NCL directory.
2) Check out the WRF-Hydro forcing engine, WRF-Hydro_forcing.py from the scripts/Python directory.
3) Check out the config/parm file wrf_hydro_forcing.parm from the parm directory.  
4) Check out the Fortran shared object sorc/Fortran/adj_topof90.so and save it to the directory where you define
   the NCL shared object directory, NCL_DEF_LIB_DIR.  Note: this is the directory where ALL shared objects will
   be placed.
5) In the wrf_hydro_forcing.parm file, indicate things such as: a)the directory where your input data is located, b) where you wish the output data to reside, and c) the location of the regridding and downscaling scripts, and d) the location of all the shared objects (NCL_DEF_LIB_DIR)
6) In the main section of the <forcing config>.py, indicate information such as your logging level, the name of your logging file, the product to process, the location of the weighting files, and indicate which action you wish to perform (ie regridding, downscaling).  To run, do the following at the command line:

    python <forcing config name>.py
    
    where the forcing config name = Analysis_Assimilation_Forcing, Short_Range_Forcing, Long_Range_Forcing, etc.
    Make sure you have the config/parm file, the forcing config file and the WRF_Hydro_forcing.py file in the same 
    directory from which you are invoking.
    
*Note: The weightings files should be available for every model type.  These will usually reside on the test host.  Currently, they are found in hydro-c1:/d4/hydro-dm/IOC/weightings.
    
    
