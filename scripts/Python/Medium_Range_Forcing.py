import WRF_Hydro_forcing as whf
import logging
import os
import sys
from ConfigParser import SafeConfigParser
import optparse

"""Medium_Range_Forcing
Performs regridding,downscaling, bias
correction (if needed), and layering/mixing 
of data products associated with the Medium Range
forcing configuration.  Invokes methods in the
WRF_Hydro_forcing module and input parameters
that are defined in the wrf_hydro_forcing.parm
parameter/configuration file.  Logs to a log
file that is created in the same directory
from where this script is executed.

"""
def forcing(action, prod, file, prod2=None, file2=None):
    """Peforms the action on the given data
       product and corresponding input file.

       Args:
           action (string):  Supported actions are:
                             'regrid' - regrid and downscale
                             'bias'   - bias correction 
                                        (requires two 
                                        products and two files)
                             'layer'  - layer (requires two
                                        products and two files)
           prod (string):  The first product [mandatory option]:
                            (GFS)
           file (string):  The file name (full path not necessary,
                            this is derived from the Python config/
                            param file and the YYYMMDD portion of 
                            the file name.

          prod2 (string):   The second product (????), default
                            is None. Required for layering.
          file2 (string):   The second file name, required for 
                            layering, default is None.
       Returns:
           None           Performs the indicated action on the
                          files based on the type of product and
                          any other relevant information provided
                          by the Python config/param file,
                          wrf_hydro_forcing.parm
 
 
    """


    # Read the parameters from the config/param file.
    parser = SafeConfigParser()
    parser.read('wrf_hydro_forcing.parm')

    # Set up logging, environments, etc.
    forcing_config_label = 'Medium_Range'
    logging = whf.initial_setup(parser,forcing_config_label)


    # Extract the date, model run time, and forecast hour from the file name
    # Use the fcsthr to process only the files that have a fcst hour less than
    # the max fcst hr defined in the param/config file.
    
    
    # Convert the action to lower case 
    # and the product name to upper case
    # for consistent checking
    action_requested = action.lower()
    product_data_name = prod.upper()
    if action == 'regrid': 
        (date,modelrun,fcsthr) = whf.extract_file_info(file)
        # Determine whether this current file lies within the forecast range
        # for the data product (e.g. if processing RAP, use only the 0hr-18hr forecasts).
        # Skip if this file has a forecast hour greater than the max indicated in the 
        # parm/config file.
        in_fcst_range = whf.is_in_fcst_range(prod, fcsthr, parser)

        if in_fcst_range:
            # Check for RAP or GFS data products.  If this file is
            # a 0 hr fcst and is RAP or GFS, substitute each 0hr forecast
            # with the file from the previous model run and the same valid
            # time.  This is necessary because there are missing variables
            # in the 0hr forecasts (e.g. precip rate for RAP and radiation
            # in GFS).
    
            logging.info("Regridding and Downscaling for %s", product_data_name)
            # Determine if this is a 0hr forecast for RAP data (GFS is also missing
            # some variables for 0hr forecast, but GFS is not used for Medium Range
            # forcing). We will need to substitute this file for the downscaled
            # file from a previous model run with the same valid time.  
            # We only need to do this for downscaled files, as the Medium Range 
            # forcing files that are regridded always get downscaled and we don't want
            # to do this for both the regridding and downscaling.
            if fcsthr == 0 and prod == 'GFS':
                logging.info("Regridding (ignoring f0 RAP files) %s: ", file )
                regridded_file = whf.regrid_data(product_data_name, file, parser, True)
                whf.downscale_data(product_data_name,regridded_file, parser, True, True)                
            else:
                logging.info("Regridding %s: ", file )
                regridded_file = whf.regrid_data(product_data_name, file, parser, False)
                whf.downscale_data(product_data_name,regridded_file, parser,True, False)                
                whf.move_to_final_location(parser,"Medium_Range")
                
        else:
            # Skip processing this file, exiting...
            logging.info("INFO [Medium_Range_Forcing]- Skip processing, requested file is outside max fcst")
    elif action_requested == 'layer':
        logging.info("Layering requested for medium range")
    elif action_requested == 'bias':
        logging.info("Bias correction requested for %s", file)
        logging.info("Bias correction not yet suppoted for Medium Range Forcing")
            


 
        
#--------------------------    
    
   
if __name__ == "__main__":
    forcing()
    

