import WRF_Hydro_forcing as whf
import logging
import os
from ConfigParser import SafeConfigParser
import sys
import getopt

"""Analysis_Assimilation_Forcing
Performs regridding and downscaling, then bias
correction, and layering/mixing of data products 
associated with the Analysis and Assimilation
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
                            (MRMS, HRRR or RAP)
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
    parser.read('aa_wrf_hydro_forcing.parm')

    # Set up logging, environments, etc.
    forcing_config_label = "Anal_Assim"
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
        # Usually check for forecast range, but only 0, 3 hr forecast/analysis data used
   
        # Check for HRRR, RAP, MRMS products. 
        logging.info("Regridding and Downscaling for %s", product_data_name)

        if fcsthr == 0 and prod == "HRRR":
            downscale_dir = parser.get('downscaling', 'HRRR_downscale_output_dir_0hr')
            regridded_file = whf.regrid_data(product_data_name,file,parser,False, \
                             zero_process=True)
            whf.downscale_data(product_data_name,regridded_file, parser,False, False, \
                               zero_process=True)

            # Move downscaled file to staging area where triggering will monitor
            match = re.match(r'.*/([0-9]{10})/([0-9]{12}.LDASIN_DOMAIN1.nc)',regridded_file)
            if match:
                full_dir = downscale_dir + "/" + match.group(1)
                full_finished_file = full_dir + "/" + match.group(2)
                # File should have been created in downscale_data step.
                whf.file_exists(full_finished_file)
                whf.move_to_finished_area(parser, prod, full_finished_file, zero_move=True)
        elif fcsthr == 0 and prod == "RAP":
            downscale_dir = parser.get('downscaling', 'RAP_downscale_output_dir_0hr')
            regridded_file = whf.regrid_data(product_data_name,file,parser,False, \
                             zero_process=True)
            whf.downscale_data(product_data_name,regridded_file, parser,False, False, \
                               zero_process=True)
            # Move downscaled file to staging area where triggering will monitor
            match = re.match(r'.*/([0-9]{10})/([0-9]{12}.LDASIN_DOMAIN1.nc)',regridded_file)
            if match:
                full_dir = downscale_dir + "/" + match.group(1)
                full_finished_file = full_dir + "/" + match.group(2)
                # File should have been created in downscale_data step.
                whf.file_exists(full_finished_file)
                whf.move_to_finished_area(parser, prod, full_finished_file, zero_move=True) 
        elif prod == "MRMS":
            regridded_file = whf.regrid_data(product_data_name,file,parser,False)
  
            # Move regridded file to staging area where triggering will monitor
            # First make sure file exists
            whf.file_exists(regridded_file)
            whf.move_to_finished_area(parser, prod, regridded_file, zero_move=False)
        else:
            # We have everything we need, request layering, since layering is the last step,
            # move/rename all finished data (MRMS included) to the final Anal_Assim directory.
            whf.layer_data(parser,prod,file, prod2,file2, 'Anal_Assim')
            whf.rename_final_files(parser,'Anal_Assim')
             
    elif action_requested == 'bias':
        logging.info("Bias correction requested for the Analysis and Assimilation Forcing on file: %s", file)
            



    
   
    

 
   

#----------------------------------------------
if __name__ == "__main__":
    forcing()
