import WRF_Hydro_forcing as whf
import logging
import os
import sys
from ConfigParser import SafeConfigParser
import optparse

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


def main():
    # Initialize anything that is specific to this
    # forcing configuration...
    forcing_config_label = 'Short_Range'

    # Read the parameters from the config/param file.
    parser = SafeConfigParser()
    parser.read('wrf_hydro_forcing.parm')

    # Set up logging, environments, etc.
    forcing_config_label = "Short_Range"
    logging = whf.initial_setup(parser,forcing_config_label)

    # Retrieve the information from the input args
    opt_parser = optparse.OptionParser()
    opt_parser.add_option('--regrid', help='regrid and downscale',\
                  dest='r_d_bool', default=False, action='store_true')
    opt_parser.add_option('--bias', help='bias correction', dest='bias_bool',\
                  default=False, action='store_true')
    opt_parser.add_option('--layer', help='layer', dest='layer_bool',\
                  default=False, action='store_true')

    # tell optparse to store option's arg in specified destination
    # member of opts
    opt_parser.add_option('--prod', help='data product', dest='data_prod',\
                       action='store')
    opt_parser.add_option('--prod2', help='second data product \
                      (for layering and bias correction)', dest='data_prod2',\
                       action='store')
    opt_parser.add_option('--File', help='file name',dest='file_name',\
                      action='store', nargs=1)
    opt_parser.add_option('--File2', help='second file name \
                       (for layering and bias correction)',dest='file_name2',\
                        action='store', nargs=1)
    (opts,args) = opt_parser.parse_args()

    curr_data_file = opts.file_name
    product_data_name = opts.data_prod

    # Making sure all necessary options appeared
    if opts.layer_bool:
        if (opts.data_prod and not opts.data_prod2):
            print "Layering requires two data products"
            parser.print_help()
        elif (opts.file_name and not opts.file_name2) :
            print "Layering requires two input files"
            parser.print_help()

    if opts.r_d_bool:
        print "Regrid and downscale requested"
        if(not opts.data_prod or not opts.file_name):
            print "Regrid (& downscale) requires one data product \
                   and one file name"
            parser.print_help()
        else:
            print "data prod: %s"%opts.data_prod
            print "filename: %s"%opts.file_name



    # Extract the date, model run time, and forecast hour from the file name
    # Use the fcsthr to process only the files that have a fcst hour less than
    # the max fcst hr defined in the param/config file.
    (date,modelrun,fcsthr) = whf.extract_file_info(curr_data_file)
    
    
    # Determine whether this current file lies within the forecast range
    # for the data product (e.g. if processing RAP, use only the 0hr-18hr forecasts).
    # Skip if this file has a forecast hour greater than the max indicated in the 
    # parm/config file.
    in_fcst_range = whf.is_in_fcst_range(product_data_name, fcsthr, parser)

    if in_fcst_range:
        # Check for RAP or GFS data products.  If this file is
        # a 0 hr fcst and is RAP or GFS, substitute each 0hr forecast
        # with the file from the previous model run and the same valid
        # time.  This is necessary because there are missing variables
        # in the 0hr forecasts (e.g. precip rate for RAP and radiation
        # in GFS).

        if opts.r_d_bool:
            logging.info("Regridding and Downscaling for %s", opts.data_prod)
            # Determine if this is a 0hr forecast for RAP data (GFS is also missing
            # some variables for 0hr forecast, but GFS is not used for Short Range
            # forcing). We will need to substitute this file for the downscaled
            # file from a previous model run with the same valid time.  
            # We only need to do this for downscaled files, as the Short Range 
            # forcing files that are regridded always get downscaled and we don't want
            # to do this for both the regridding and downscaling.
            if fcsthr == 0 and product_data_name == 'RAP':
                logging.info("Regridding, ignoring f0 RAP files " )
                regridded_file = whf.regrid_data(product_data_name, curr_data_file, parser, True)
                whf.downscale_data(product_data_name,regridded_file, parser, True, True)                
            else:
                regridded_file = whf.regrid_data(product_data_name, curr_data_file, parser, False)
                whf.downscale_data(product_data_name,regridded_file, parser,True, False)                
            
        elif args.layer_bool:
            logging.info("Layering requested for %s", args.InputFileName)
     
        elif args.bias_bool:
            logging.info("Bias correction requested for %s", args.InputFileName)

    else:
        # Skip processing this file, exiting...
        logging.info("INFO [Short_Range_Forcing]- Skip processing, requested file is outside max fcst")
        return

 
    
    
#--------------------------    
    
   
if __name__ == "__main__":
    main()
    

