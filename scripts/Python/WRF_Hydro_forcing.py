import os
import errno
import logging
import re
import time
import numpy as np
from ConfigParser import SafeConfigParser



# -----------------------------------------------------
#             WRF_Hydro_forcing.py
# -----------------------------------------------------

#  Overview:
#  This is a forcing engine for WRF Hydro. It serves as a wrapper
#  to the regridding and other processing scripts written in NCL.  
#  This script was created to conform with NCEP Central Operations
#  WCOSS implementation standards and as part of the workflow for
#  operating at the National Water Center (NWC).  Input variables 
#  to the NCL scripts are defined in a parm/config file: 
#  wrf_hydro_forcing.parm to reduce the requirement to set environment
#  variables for input file directories, output file directories,
#  etc. which are not always conducive in an operational setting.



def regrid_data( product_name, parser ):
    """Provides a wrapper to the regridding scripts originally
    written in NCL.  For HRRR data regridding, the
    HRRR-2-WRF_Hydro_ESMF_forcing.ncl script is invoked.
    For MRMS data MRMS-2-WRF_Hydro_ESMF_forcing.ncl is invoked.
    Finally, for NAM212 data, NAM-2-WRF_Hydro_ESMF_forcing.ncl 
    is invoked.  All product files (HRRR, MRMS, NAM, RAP etc.) are
    retrieved and stored in a list. The appropriate regridding
    script is invoked for each file in the list.  The regridded
    files are stored in an output directory defined in the
    parm/config file.

    Args:
        product_name (string):  The name of the product 
                                e.g. HRRR, MRMS, NAM
        parser (ConfigParser):  The parser to the config/parm
                                file containing all defined values
                                necessary for running the regridding.
    Returns:
        elapsed_times (numpy array):  A Numpy array containing the 
                                      elapsed time in seconds for 
                                      regridding each file.

    """


    # Retrieve the values from the parm/config file
    # which are needed to invoke the regridding 
    # scripts.
    product = product_name.upper()
    dst_grid_name = parser.get('regridding','dst_grid_name')
    ncl_exec = parser.get('exe', 'ncl_exe')

    # Create an array to store the elapsed times for
    # regridding each file.
    elapsed_array = []

    if product == 'HRRR':
       logging.info("Regridding HRRR")
       wgt_file = parser.get('regridding', 'HRRR_wgt_bilinear')
       data_dir =  parser.get('data_dir', 'HRRR_data')
       regridding_exec = parser.get('exe', 'HRRR_regridding_exe')
       data_files_to_process = get_filepaths(data_dir)   
       #Values needed for running the regridding script
       wgt_file = parser.get('regridding','HRRR_wgt_bilinear')
       output_dir_root = parser.get('output_dir','HRRR_output_dir')
    elif product == 'MRMS':
       logging.info("Regridding MRMS")
       wgt_file = parser.get('regridding', 'MRMS_wgt_bilinear')
       data_dir =  parser.get('data_dir', 'MRMS_data')
       regridding_exec = parser.get('exe', 'MRMS_regridding_exe')
       data_files_to_process = get_filepaths(data_dir)   
       #Values needed for running the regridding script
       wgt_file = parser.get('regridding','MRMS_wgt_bilinear')
       output_dir_root = parser.get('output_dir','MRMS_output_dir')
    elif product == 'NAM':
       logging.info("Regridding NAM")
       wgt_file = parser.get('regridding', 'NAM_wgt_bilinear')
       data_dir =  parser.get('data_dir', 'NAM_data')
       regridding_exec = parser.get('exe', 'NAM_regridding_exe')
       data_files_to_process = get_filepaths(data_dir)
       #Values needed for running the regridding script
       wgt_file = parser.get('regridding','NAM_wgt_bilinear')
       output_dir_root = parser.get('output_dir','NAM_output_dir')
    elif product == 'GFS':
       logging.info("Regridding GFS")
       wgt_file = parser.get('regridding', 'GFS_wgt_bilinear')
       data_dir =  parser.get('data_dir', 'GFS_data')
       regridding_exec = parser.get('exe', 'GFS_regridding_exe')
       data_files_to_process = get_filepaths(data_dir)
       #Values needed for running the regridding script
       wgt_file = parser.get('regridding','GFS_wgt_bilinear')
       output_dir_root = parser.get('output_dir','GFS_output_dir')
    elif product == 'RAP':
       logging.info("Regridding RAP")
       wgt_file = parser.get('regridding', 'RAP_wgt_bilinear')
       data_dir =  parser.get('data_dir', 'RAP_data')
       regridding_exec = parser.get('exe', 'RAP_regridding_exe')
       data_files_to_process = get_filepaths(data_dir)
       #Values needed for running the regridding script
       wgt_file = parser.get('regridding','RAP_wgt_bilinear')
       output_dir_root = parser.get('output_dir','RAP_output_dir')



    # For each file in the data directory,
    # generate the key-value pairs for 
    # input to the regridding script.
    # The key-value pairs for the input should look like: 
    #    'srcfilename="/d4/hydro-dm/IOC/data/HRRR/20150723_i23_f010_HRRR.grb2"' 
    #    'wgtFileName_in = "/d4/hydro-dm/IOC/weighting/HRRR1km/HRRR2HYDRO_d01_weight_bilinear.nc"'
    #    'dstGridName="/d4/hydro-dm/IOC/data/geo_dst.nc"' 
    #    'outdir="/d4/hydro-dm/IOC/regridded/HRRR/20150723/i09"'
    #    'outFile="20150724_i09_f010_HRRR.nc"' 

    for data_file_to_process in data_files_to_process:
        #input_filename = data_dir + '/' + data_file_to_process
        input_filename =  data_file_to_process
        srcfilename_param =  "'srcfilename=" + '"' + input_filename +  \
                             '"' + "' "
        logging.info("input data file: %s", data_file_to_process)
        wgtFileName_in_param =  "'wgtFileName_in = " + '"' + wgt_file + \
                                '"' + "' "
        dstGridName_param =  "'dstGridName=" + '"' + dst_grid_name + '"' + "' "

        # Create the output filename following the RAL 
        # naming convention: 
        (subdir_file_path,hydro_filename) = create_output_name_and_subdir(product,data_file_to_process, data_dir)
   
        # Create the full path to the output directory and assigning
        # this to the output directory parameter. 
        output_file_dir = output_dir_root + "/" + subdir_file_path
        outdir_param = "'outdir=" + '"' + output_file_dir + '"' + "' " 

        if product == "HRRR" or product == "NAM" \
           or product == "GFS" or product == "RAP":
           full_output_file = output_file_dir + "/"  + subdir_file_path
           #logging.info("Full output filename for %s: %s", product, full_output_file)
           # Create the new output file subdirectory
           mkdir_p(output_file_dir)
           outFile_param = "'outFile=" + '"' + hydro_filename+ '"' + "' "
           
        elif product == "MRMS":
           # !!!!!!NOTE!!!!!
           # MRMS regridding script differs from the HRRR and NAM scripts in that it does not
           # accept an outdir variable.  Incorporate the output directory (outdir)
           # into the outFile variable.
           full_output_file = output_file_dir + "/"  + hydro_filename
           #logging.info("Full output filename for %s: %s", product, full_output_file)
           mkdir_p(output_file_dir)
           outFile_param = "'outFile=" + '"' + full_output_file + '"' + "' "
   
        regrid_params = srcfilename_param + wgtFileName_in_param + \
                        dstGridName_param + outdir_param + \
                        outFile_param
        regrid_prod_cmd = ncl_exec + " "  + regrid_params + " " + \
                          regridding_exec
        
        #logging.debug(regrid_prod_cmd)
        # Measure how long it takes to run the NCL script for regridding.
        start_NCL_regridding = time.time()
        return_value = os.system(regrid_prod_cmd)
        end_NCL_regridding = time.time()
        elapsed_time_sec = end_NCL_regridding - start_NCL_regridding
        elapsed_array.append(elapsed_time_sec)
     

        if return_value != 0:
            logging.info('ERROR: The regridding of %s was unsuccessful, \
                          return value of %s', product,return_value)
            #TO DO: Determine the proper action to take when the NCL file h
            #fails. For now, exit.
            exit()
        
    return elapsed_array



def get_filepaths(dir):
    """ Generates the file names in a directory tree
    by walking the tree either top-down or bottom-up.
    For each directory in the tree rooted at 
    the directory top (including top itself), it
    produces a 3-tuple: (dirpath, dirnames, filenames).
    
    Args:
        dir (string): The base directory from which we 
                      begin the search for filenames.
    Returns:
        file_paths (list): A list of the full filepaths 
                           of the data to be processed.

        
    """

    # Create an empty list which will eventually store 
    # all the full filenames
    file_paths = []

    # Walk the tree
    for root, directories, files in os.walk(dir):
        for filename in files:
            # Join the two strings to form the full
            # filepath.
            filepath = os.path.join(root,filename)
            # add it to the list
            file_paths.append(filepath)
    return file_paths



def create_output_name_and_subdir(product, filename, input_data_file):
    """ Creates the full filename for the regridded data which follows 
    the RAL standard:  
       basedir/YYYYMMDD/i_hh/YYMMDD_ihh_fnnnn_<product>.nc
    Where the i_hh is the model run time/init time in hours
    fnnn is the forecast time in hours and <product> is the
    name of the model/data product:
       e.g. HRRR, NAM, MRMS, GFS, etc.

    Args:
        product (string):  The product name: HRRR, MRMS, or NAM.

        filename (string): The name of the data file:
                           YYYYMMDD_ihh_fnnn_product.nc

        input_data_file (string):  The full path and name
                                  of the (input) data 
                                  files:
                                  /d4/hydro-dm/IOC/data/product/...
                                  This is used to create the output
                                  data dir and filename from the
                                  datetime, init, and forecast
                                  portions of the filename.

        output_dir_root (string): The root directory for output:
                                  /d4/hydro-dm/IOC/regridded/<product>
                                  Used to create the full path.

    Returns:
        
        year_month_day_subdir (string): The subdirectory under which the 
                                        processed files will be stored:
                                        YYYYMMDD/i_hh

        hydro_filename (string):  The name of the processed output
                                  file.      
 
    """

    # Convert product to uppercase for an easy, consistent 
    # comparison.
    product_name = product.upper() 

    if product == 'HRRR' or product == 'GFS' \
       or product == "NAM" or product == 'RAP':
        match = re.match(r'.*([0-9]{8})_(i[0-9]{2})_(f[0-9]{2,4})',filename)
        if match:
            year_month_day = match.group(1)
            init_hr = match.group(2)
            fcst_hr = match.group(3)
            year_month_day_subdir = year_month_day + "/" + init_hr 
        else:
            logging.error("ERROR: %s data filename %s has an unexpected name.", \
                           product_name,filename) 
            exit()

    elif product == 'MRMS':
        match = re.match(r'.*([0-9]{8})_([0-9]{2}).*',filename) 
        if match:
           year_month_day = match.group(1)
           init_hr = "i" + match.group(2)
           # Radar data- not a model, therefore no forecast
           fcst_hr = "f000"
           year_month_day_subdir = year_month_day + "/" + init_hr 
        else:
           logging.error("ERROR: MRMS data filename %s \
                          has an unexpected file name.",\
                          filename) 
           exit()

    # Assemble the filename and the full output directory path
    hydro_filename = year_month_day + "_" + init_hr + \
                      "_" + fcst_hr + "_" + product_name + ".nc"
    #logging.debug("Generated the output filename for %s: %s",product, hydro_filename)

    return (year_month_day_subdir, hydro_filename)




def mkdir_p(dir):
    """Provides mkdir -p functionality.
    
       Args:
          dir (string):  Full directory path to be created if it
                         doesn't exist.
       Returns:
          None:  Creates nested subdirs if they don't already 
                 exist.

    """
    #logging.info("Directory to be made: %s",dir)
#    if not os.path.exists(os.path.dirname(dir)):
#       logging.info("inside mkdir_p...creating directory: %s", dir)
#       os.makedirs(os.path.dirname(dir))
#    else:
#       logging.info("Directory path %s already exists", dir)
    try:
       os.makedirs(dir)
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(dir):
            pass
        else: raise            


def downscale_data(product_name, parser, shortwave=False):
    """
    Performs downscaling of data by calling the necessary
    NCL or Fortran code.  


    Args:
        product_name (string):  The product name: ie HRRR, NAM, GFS, etc. 

        parser (ConfigParser) : The ConfigParser which can access the
                                Python config file wrf_hydro_forcing.parm
                                and retrieve the file names and locations
                                of input.

        shortwave (boolean) :   True if downscaling of shortwave 
                                radiation (SWDOWN) is necessary, in which
                                case invoke the NCL wrapper to the Fortan
                                code that performs the downscaling.
                                False by default, don't downscale
                                the shortwave radiation.
    Returns:
        elapsed_array (List):  A list of the elapsed time for
                               performing the downscaling. Each entry 
                               represents the time to downscale a file.  

                               In addition, the output files are saved
                               with the name and location (both 
                               specified in the config file).
                               
                              
        
    """

    # Read in all the relevant input parameters based on the product: 
    # HRRR, NAM, GFS, etc.
    product = product_name.upper() 
    lapse_rate_file = parser.get('downscaling','lapse_rate_file')
 
 
    # Create an array to store the elapsed times for
    # downscaling each file.
    elapsed_array = []
    downscale_exe = parser.get('exe', 'downscaling_exe')
    ncl_exec = parser.get('exe', 'ncl_exe')

    if product  == 'HRRR':
        logging.info("Downscaling HRRR")
        data_to_downscale_dir = parser.get('downscaling','HRRR_data_to_downscale')
        hgt_data_file = parser.get('downscaling','HRRR_hgt_data')
        geo_data_file = parser.get('downscaling','HRRR_geo_data')
        downscale_output_dir = parser.get('downscaling', 'HRRR_downscale_output_dir')
    elif product == 'NAM':
        logging.info("Downscaling NAM")
        data_to_downscale_dir = parser.get('downscaling','NAM_data_to_downscale')
        hgt_data_file = parser.get('downscaling','NAM_hgt_data')
        geo_data_file = parser.get('downscaling','NAM_geo_data')
        downscale_output_dir = parser.get('downscaling', 'NAM_downscale_output_dir')
    elif product == 'GFS':
        logging.info("Downscaling GFS")
        data_to_downscale_dir = parser.get('downscaling','GFS_data_to_downscale')
        hgt_data_file = parser.get('downscaling','GFS_hgt_data')
        geo_data_file = parser.get('downscaling','GFS_geo_data')
        downscale_output_dir = parser.get('downscaling', 'GFS_downscale_output_dir')

        # Retrieve the executable for downscaling SWDOWN, shortwave radiation.
        if shortwave:
            downscale_swdown_exe = parser.get('downscaling', 'RAP_downscaling_fortran_exe') 

    elif product == 'RAP':
        logging.info("Downscaling RAP")
        data_to_downscale_dir = parser.get('downscaling','RAP_data_to_downscale')
        hgt_data_file = parser.get('downscaling','RAP_hgt_data')
        geo_data_file = parser.get('downscaling','RAP_geo_data')
        downscale_output_dir = parser.get('downscaling', 'RAP_downscale_output_dir')
  
  
    
    # Get the data to downscale, and for each file, call the 
    # corresponding downscale script
    #logging.info("dir with downscaled data: %s", data_to_downscale_dir)
    data_to_downscale = get_filepaths(data_to_downscale_dir)
    
    for data in data_to_downscale:
        #logging.info("data to downscale: %s", data)

        # Create the full output filename by replacing the 
        # 'regridded' subdirectory with the 'downscaled' 
        # subdirectory, thus maintaining the same 
        # structure and naming format.
        p = re.compile('regridded')
        full_output_filename = p.sub('downscaled',data)        
        logging.debug("Full output filename: %s" , full_output_filename)
       
        match = re.match(r'(.*)/[0-9]{8}_i[0-9]{2}_f.*',full_output_filename)
        if match:
            subdir = match.group(1)
        else:
            logging.error("ERROR: regridded file's name: %s is an unexpected format",\
                           data)
        # Make the nested subdirectories.
        mkdir_p(subdir) 
 
        # Create the key-value pairs that make up the
        # input for the NCL script responsible for
        # the downscaling.
        input_file1_param = "'inputFile1=" + '"' + hgt_data_file + '"' + "' "
        input_file2_param = "'inputFile2=" + '"' + geo_data_file + '"' + "' "
        input_file3_param = "'inputFile3=" + '"' + data + '"' + "' "
        lapse_file_param = "'lapseFile=" + '"' + lapse_rate_file + '"' + "' "
        output_file_param = "'outFile=" + '"' + full_output_filename + '"' + "' "
        downscale_params =  input_file1_param + input_file2_param + \
                            input_file3_param + lapse_file_param + \
                            output_file_param 
        downscale_cmd = ncl_exe + " " + downscale_params + " " + downscale_exe

        # Key-value pairs for downscaling SWDOWN, shortwave radiation.
        swdown_output_file_param = "'outFile=" + '"' + full_output_filename + '"' + "' "
        swdown_geo_file_param = "'inputGeo=" + '"' + geo_data_file + '"' + "' "
        swdown_params = swdown_geo_file_param + " " + swdown_output_file_param
        downscale_shortwave = ncl_exe + " " + swdown_params + " " + downscale_swdown_exe 
        #logging.debug("Downscale command: %s", downscale_cmd)
        start = time.time()
        return_value = os.system(downscale_cmd)
        swdown_return_value = os.system(swdown_downscale_cmd)
        end = time.time()
        elapsed = end - start
        elapsed_array.append(elapsed)
    
        if return_value != 0 or swdown_return_value != 0:
            logging.info('ERROR: The downscaling of %s was unsuccessful, \
                          return value of %s', product,return_value)
       
            #TO DO: Determine the proper action to take when the NCL file h
            #fails. For now, exit.
            exit()

    return elapsed_array


def create_benchmark_summary(product, activity, elapsed_times):
    
    """ Create a summary of the min, max, and mean
        time to perform a processing activity for 
        each data file. The information is placed 
        in the log file.

        Args:
           product (string):  The name of the product under
                              consideration.
           activity (string): The processing activity: 
                              regridding, downscaling, etc.
           elapsed_times (ndarray): Numpy ndarray of elapsed 
                                   times (wall clock time 
                                   for now) for each of the
                                   files that were processed.
       
       Output:
           None:  Generates an entry in the log file, as
                  an "info" entry, which states the min,
                  max, and average time in seconds.
     
    """
    elapsed_array = np.array(elapsed_times)
    min_time = np.min(elapsed_array)
    max_time = np.max(elapsed_array)
    avg_time = np.mean(elapsed_array)
    med_time = np.median(elapsed_array) 

    logging.info("=========================================")
    logging.info("SUMMARY for %s %s ", activity,product) 
    logging.info("=========================================")
    logging.info("Average elapsed time (sec): %s", avg_time)
    logging.info("Median elapsed time (sec): %s", med_time)
    logging.info("Min elapsed time (sec): %s ", min_time)
    logging.info("Max elapsedtime (sec): %s ", max_time)
    

#--------------------Define the Workflow -------------------------

if __name__ == "__main__":
    # Replace pass with anything you wish if you want to
    # run this as a standalone program.
    pass
