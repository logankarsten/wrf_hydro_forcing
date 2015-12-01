import WRF_Hydro_forcing as whf
import logging
import os
import sys
import re
from ConfigParser import SafeConfigParser
import optparse
import shutil

"""Short_Range_Forcing
Performs regridding,downscaling, bias
correction (if needed), and layering/mixing 
of data products associated with the Short Range
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
                            (HRRR or RAP)
           file (string):  The file name (full path not necessary,
                            this is derived from the Python config/
                            param file and the YYYMMDD portion of 
                            the file name.

          prod2 (string):   The second product (RAP or HRRR), default
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
    forcing_config_label = "Short_Range"
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
        # Get the finished directory locations for the relevant product.
        if prod == 'RAP':
            regridded_dir = parser.get('regridding', 'RAP_output_dir')
            downscale_dir = parser.get('downscaling', 'RAP_downscale_output_dir')
            finished_downscale_dir = parser.get('downscaling', 'RAP_finished_output_dir')
            downscale_input_dir = parser.get('downscaling',  'RAP_data_to_downscale')
      
        elif prod == 'HRRR':
            regridded_dir = parser.get('regridding', 'HRRR_output_dir')
            downscale_dir = parser.get('downscaling', 'HRRR_downscale_output_dir')
            finished_downscale_dir = parser.get('downscaling', 'HRRR_finished_output_dir')
            downscale_input_dir = parser.get('downscaling',  'HRRR_data_to_downscale')


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
            # some variables for 0hr forecast, but GFS is not used for Short Range
            # forcing). We will need to substitute this file for the downscaled
            # file from a previous model run with the same valid time.  
            # We only need to do this for downscaled files, as the Short Range 
            # forcing files that are regridded always get downscaled and we don't want
            # to do this for both the regridding and downscaling.
            if fcsthr == 0 and prod == 'RAP':
                logging.info("Regridding, ignoring f0 RAP files " )
                regridded_file = whf.regrid_data(product_data_name, file, parser, True)

                # Downscaling...
                whf.downscale_data(product_data_name,regridded_file, parser, True, True)                

                # Move the finished downscaled file to the "finished" area so the triggering
                # script can determine when to layer with other data.
                match = re.match(r'.*/([0-9]{10})/([0-9]{12}.LDASIN_DOMAIN1.nc)',regridded_file)
                if match:
                    ymd_dir = match.group(1) 
                    file_only = match.group(2)
                    downscaled_dir = downscale_dir + "/" + ymd_dir
                    if not os.path.exists(downscaled_dir):
                        mkdir_p(downscaled_dir)
                    downscaled_file = downscaled_dir + "/" + file_only 
                    whf.move_to_finished_area(parser, prod, downscaled_file) 
                else:
                    print ("Can't get filename only from the finished regridded file") 

            else:
                regridded_file = whf.regrid_data(product_data_name, file, parser, False)
                # Downscaling...
                whf.downscale_data(product_data_name,regridded_file, parser,True, False)                
                # Move the downscaled file to the finished area.
                # Move the downscaled file to the finished location 
                match = re.match(r'.*/([0-9]{10})/([0-9]{12}.LDASIN_DOMAIN1.nc)',regridded_file)
                if match:
                    full_dir = downscale_dir + "/" + match.group(1)
                    full_finished_file = full_dir + "/" + match.group(2)
                    if not os.path.exists(full_dir):
                        logging.info("finished dir doesn't exist, creating it now...")
                        whf.mkdir_p(full_dir)
                    whf.move_to_finished_area(parser, prod,full_finished_file)
                else:
                    print ("Can't get filename only from the finished regridded file") 

        else:
            # Skip processing this file, exiting...
            logging.info("INFO [Short_Range_Forcing]- Skip processing, requested file is outside max fcst")
    elif action_requested == 'layer':
        logging.info("Layering requested for %s and %s", prod, prod2)
        # Do some checking to make sure that there are two data products 
        # and two files indicated.
        if prod2 is None:
            logger.error("ERROR [Short_Range_Forcing]: layering requires two products")
        elif file2 is None:
            logger.error("ERROR [Short_Range_Forcing]: layering requires two input files")
        else:
            # We have everything we need, request layering
            whf.layer_data(parser,prod,file, prod2,file2, 'Short_Range')
            whf.rename_final_files(parser,'Short_Range')
             
    elif action_requested == 'bias':
        logging.info("Bias correction requested for %s", file)
        logging.info("Bias correction not yet suppoted for Short Range Forcing")
            



 
        
#--------------------------    
    
   
if __name__ == "__main__":
    forcing()
    

