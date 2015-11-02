import os
import errno
import logging
import re
import time
import numpy as np
import sys
import argparse
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
       output_dir_root = parser.get('regridding','HRRR_output_dir')
    elif product == 'MRMS':
       logging.info("Regridding MRMS")
       wgt_file = parser.get('regridding', 'MRMS_wgt_bilinear')
       data_dir =  parser.get('data_dir', 'MRMS_data')
       regridding_exec = parser.get('exe', 'MRMS_regridding_exe')
       data_files_to_process = get_filepaths(data_dir)   
       #Values needed for running the regridding script
       output_dir_root = parser.get('regridding','MRMS_output_dir')
    elif product == 'NAM':
       logging.info("Regridding NAM")
       wgt_file = parser.get('regridding', 'NAM_wgt_bilinear')
       data_dir =  parser.get('data_dir', 'NAM_data')
       regridding_exec = parser.get('exe', 'NAM_regridding_exe')
       data_files_to_process = get_filepaths(data_dir)
       #Values needed for running the regridding script
       output_dir_root = parser.get('regridding','NAM_output_dir')
    elif product == 'GFS':
       logging.info("Regridding GFS")
       wgt_file = parser.get('regridding', 'GFS_wgt_bilinear')
       data_dir =  parser.get('data_dir', 'GFS_data')
       regridding_exec = parser.get('exe', 'GFS_regridding_exe')
       data_files_to_process = get_filepaths(data_dir)
       #Values needed for running the regridding script
       output_dir_root = parser.get('regridding','GFS_output_dir')
    elif product == 'RAP':
       logging.info("Regridding RAP")
       wgt_file = parser.get('regridding', 'RAP_wgt_bilinear')
       data_dir =  parser.get('data_dir', 'RAP_data')
       regridding_exec = parser.get('exe', 'RAP_regridding_exe')
       data_files_to_process = get_filepaths(data_dir)
       #Values needed for running the regridding script
       output_dir_root = parser.get('regridding','RAP_output_dir')



    # For each file in the data directory,
    # generate the key-value pairs for 
    # input to the regridding script.
    # The key-value pairs for the input should look like: 
    #  'srcfilename="/d4/hydro-dm/IOC/data/HRRR/20150723_i23_f010_HRRR.grb2"' 
    #  'wgtFileName_in=
    #     "d4/hydro-dm/IOC/weighting/HRRR1km/HRRR2HYDRO_d01_weight_bilinear.nc"'
    #  'dstGridName="/d4/hydro-dm/IOC/data/geo_dst.nc"' 
    #  'outdir="/d4/hydro-dm/IOC/regridded/HRRR/20150723/i09"'
    #  'outFile="20150724_i09_f010_HRRR.nc"' 

    for data_file_to_process in data_files_to_process:
        #input_filename = data_dir + '/' + data_file_to_process
        input_filename =  data_file_to_process
        srcfilename_param =  "'srcfilename=" + '"' + input_filename +  \
                             '"' + "' "
       # logging.info("input data file: %s", data_file_to_process)
        wgtFileName_in_param =  "'wgtFileName_in = " + '"' + wgt_file + \
                                '"' + "' "
        dstGridName_param =  "'dstGridName=" + '"' + dst_grid_name + '"' + "' "

        # Create the output filename following the RAL 
        # naming convention: 
        (subdir_file_path,hydro_filename) = \
            create_output_name_and_subdir(product,data_file_to_process,data_dir)
   
        #logging.info("hydro filename: %s", hydro_filename)
        # Create the full path to the output directory
        # and assign it to the output directory parameter
        output_file_dir = output_dir_root + "/" + subdir_file_path
        outdir_param = "'outdir=" + '"' + output_file_dir + '"' + "' " 
        #logging.info("outdir_param: %s", outdir_param)

        if product == "HRRR" or product == "NAM" \
           or product == "GFS" or product == "RAP":
           #full_output_file = output_file_dir + "/"  + subdir_file_path
           full_output_file = output_file_dir + "/"  
           # Create the new output file subdirectory
           mkdir_p(output_file_dir)
           outFile_param = "'outFile=" + '"' + hydro_filename+ '"' + "' "
        elif product == "MRMS":
           # !!!!!!NOTE!!!!!
           # MRMS regridding script differs from the HRRR and NAM scripts in that it does not
           # accept an outdir variable.  Incorporate the output directory (outdir)
           # into the outFile variable.
           full_output_file = output_file_dir + "/"  + hydro_filename
           mkdir_p(output_file_dir)
           outFile_param = "'outFile=" + '"' + full_output_file + '"' + "' "
   
        regrid_params = srcfilename_param + wgtFileName_in_param + \
                        dstGridName_param + outdir_param + \
                        outFile_param
        regrid_prod_cmd = ncl_exec + " "  + regrid_params + " " + \
                          regridding_exec
        
        logging.debug("regridding command: %s",regrid_prod_cmd)
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
    try:
       os.makedirs(dir)
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(dir):
            pass
        else: raise            


def downscale_data(product_name, parser, downscale_shortwave=False):
    """
    Performs downscaling of data by calling the necessary
    NCL code (specific to the model/product).  There is an
    additional option to downscale the short wave radiation, SWDOWN.  
    If downscaling SWDOWN (shortwave radiation) is requested  
    then a second NCL script is invoked (topo_adj.ncl).  This second 
    NCL script invokes a Fortran application (topo_adjf90.so, 
    built from topo_adj.f90). 

    NOTE:  If the additional downscaling
    (of shortwave radiation) is requested, the adj_topo.ncl script
    will "clobber" the previously created downscaled files.


    Args:
        product_name (string):  The product name: ie HRRR, NAM, GFS, etc. 

        parser (ConfigParser) : The ConfigParser which can access the
                                Python config file wrf_hydro_forcing.parm
                                and retrieve the file names and locations
                                of input.

        downscale_shortwave (boolean) : 'True' if downscaling of 
                                shortwave radiation (SWDOWN) is 
                                requested; invoke topo_adj.ncl, 
                                the NCL wrapper to the Fortan
                                code.
                                Set to 'False' by default.
    Returns:
        elapsed_array (List):  A list of the elapsed time for
                               performing the downscaling. Each entry 
                               represents the time to downscale a file.  

                               
                              
        
    """

    # Read in all the relevant input parameters based on the product: 
    # HRRR, NAM, GFS, etc.
    product = product_name.upper() 
    lapse_rate_file = parser.get('downscaling','lapse_rate_file')
    ncl_exec = parser.get('exe', 'ncl_exe')
    
 
    # Create an array to store the elapsed times for
    # downscaling each file.
    elapsed_array = []

    if product  == 'HRRR':
        logging.info("Downscaling HRRR")
        data_to_downscale_dir = parser.get('downscaling','HRRR_data_to_downscale')
        hgt_data_file = parser.get('downscaling','HRRR_hgt_data')
        geo_data_file = parser.get('downscaling','HRRR_geo_data')
        downscale_output_dir = parser.get('downscaling', 'HRRR_downscale_output_dir')
        downscale_exe = parser.get('exe', 'HRRR_downscaling_exe')
    elif product == 'NAM':
        logging.info("Downscaling NAM")
        data_to_downscale_dir = parser.get('downscaling','NAM_data_to_downscale')
        hgt_data_file = parser.get('downscaling','NAM_hgt_data')
        geo_data_file = parser.get('downscaling','NAM_geo_data')
        downscale_output_dir = parser.get('downscaling', 'NAM_downscale_output_dir')
        downscale_exe = parser.get('exe', 'NAM_downscaling_exe')
    elif product == 'GFS':
        logging.info("Downscaling GFS")
        data_to_downscale_dir = parser.get('downscaling','GFS_data_to_downscale')
        hgt_data_file = parser.get('downscaling','GFS_hgt_data')
        geo_data_file = parser.get('downscaling','GFS_geo_data')
        downscale_output_dir = parser.get('downscaling', 'GFS_downscale_output_dir')
        logging.info("GFS data to downscale: %s ", downscale_output_dir)
        downscale_exe = parser.get('exe', 'GFS_downscaling_exe')
    elif product == 'RAP':
        logging.info("Downscaling RAP")
        data_to_downscale_dir = parser.get('downscaling','RAP_data_to_downscale')
        hgt_data_file = parser.get('downscaling','RAP_hgt_data')
        geo_data_file = parser.get('downscaling','RAP_geo_data')
        downscale_output_dir = parser.get('downscaling', 'RAP_downscale_output_dir')
        #DEBUGXXX
        logging.info("output dir for downscaled data %s", downscale_output_dir)
        downscale_exe = parser.get('exe', 'RAP_downscaling_exe')
 
    
    # Get the data to downscale, and for each file, call the 
    # corresponding downscaling script
    #logging.info("dir with downscaled data: %s", data_to_downscale_dir)
    data_to_downscale = get_filepaths(data_to_downscale_dir)
    
    for data in data_to_downscale:
        match = re.match(r'(.*)/(([0-9]{8})_(i[0-9]{2})_f.*)',data)
        if match:
            yr_month_day = match.group(3)
            downscaled_file = match.group(2)
            init_hr = match.group(4)
        else:
            logging.error("ERROR: regridded file's name: %s is an unexpected format",\
                           data)
        
       
        full_downscaled_dir = downscale_output_dir + "/" + yr_month_day + "/"\
                                + init_hr  
        full_downscaled_file = full_downscaled_dir + "/" +  downscaled_file
        # Create the full output directory for the downscaled data if it doesn't 
        # already exist. 
        mkdir_p(full_downscaled_dir) 
        #mkdir_p(downscale_output_dir) 

        logging.info("full_downscaled_file: %s", full_downscaled_file)
        logging.debug("Full output filename for second downscaling: %s" , full_downscaled_file)
 
        # Create the key-value pairs that make up the
        # input for the NCL script responsible for
        # the downscaling.
        input_file1_param = "'inputFile1=" + '"' + hgt_data_file + '"' + "' "
        input_file2_param = "'inputFile2=" + '"' + geo_data_file + '"' + "' "
        input_file3_param = "'inputFile3=" + '"' + data + '"' + "' "
        lapse_file_param =  "'lapseFile=" + '"' + lapse_rate_file + '"' + "' "
        output_file_param = "'outFile=" + '"' + full_downscaled_file + '"' + "' "
        downscale_params =  input_file1_param + input_file2_param + \
                  input_file3_param + lapse_file_param +  output_file_param 
        downscale_cmd = ncl_exec + " " + downscale_params + " " + downscale_exe
        logging.debug("Downscale command : %s", downscale_cmd)

        # Downscale the shortwave radiation, if requested...
        # Key-value pairs for downscaling SWDOWN, shortwave radiation.
        if downscale_shortwave:
            logging.info("Shortwave downscaling requested...")
            downscale_swdown_exe = parser.get('exe', 'shortwave_downscaling_exe') 
            swdown_output_file_param = "'outFile=" + '"' + \
                                       full_downscaled_file + '"' + "' "

            swdown_geo_file_param = "'inputGeo=" + '"' + geo_data_file + '"' + "' "
            swdown_params = swdown_geo_file_param + " " + swdown_output_file_param
            downscale_shortwave_cmd = ncl_exec + " " + swdown_params + " " \
                                      + downscale_swdown_exe 
            logging.info("SWDOWN downscale command: %s", downscale_shortwave_cmd)

            # Crude measurement of performance for downscaling.
            # Wall clock time used to determine the elapsed time
            # for downscaling each file.
            start = time.time()

            #Invoke the NCL script for performing a single downscaling.
            return_value = os.system(downscale_cmd)
            swdown_return_value = os.system(downscale_shortwave_cmd)
            end = time.time()
            elapsed = end - start
            elapsed_array.append(elapsed)

            # Check for successful or unsuccessful downscaling
            # of the required and shortwave radiation
            if return_value != 0 or swdown_return_value != 0:
                logging.info('ERROR: The downscaling of %s was unsuccessful, \
                             return value of %s', product,return_value)
                exit()

        else:
            # Only one downscaling, no additional downscaling of
            # the short wave radiation.

            # Crude measurement of performance for downscaling.
            start = time.time()

            #Invoke the NCL script for performing the generic downscaling.
            return_value = os.system(downscale_cmd)
            end = time.time()
            elapsed = end - start
            elapsed_array.append(elapsed)

            # Check for successful or unsuccessful downscaling
            if return_value != 0:
                logging.info('ERROR: The downscaling of %s was unsuccessful, \
                             return value of %s', product,return_value)
                #TO DO: Determine the proper action to take when the NCL file 
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
    if len(elapsed_times) > 0:
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
    else:
        logging.error("ERROR: Nothing was returned....")
    



# STUB for BIAS CORRECTION, TO BE
# IMPLEMENTED LATER...
def bias_correction(parser):
    """ STUB TO BE IMPLEMENTED
    """
#
#



def layer_data(parser, primary_data, secondary_data):
    """ Invokes the NCL script, combine.ncl
        to layer/combine two files:  a primary and secondary
        file (with identical date/time, model run time, and
        forecast time) are found by iterating through a list
        of primary files and determining if the corresponding
        secondary file exists.


        Args:
              parser (ConfigParser):  The parser to the config/parm
                                      file containing all the defined
                                      values.
              primary_data (string):  The name of the primary product
 
              secondary_data (string): The name of the secondary product

        Output:
              None:  For each primary and secondary file that is
                     combined/layered, create a file
                     (name and location defined in the config/parm 
                     file).
    """

    # Retrieve any necessary parameters from the wrf_hydro_forcing config/parm
    # file...
    # 1) directory where HRRR and RAP downscaled data reside
    # 2) output directory where layered files will be saved
    # 3) location of any executables/scripts
    ncl_exe = parser.get('exe', 'ncl_exe')
    layering_exe = parser.get('exe','Analysis_Assimilation_layering')
    downscaled_primary_dir = parser.get('layering','analysis_assimilation_primary')
    downscaled_secondary_dir = parser.get('layering','analysis_assimilation_secondary')
    layered_output_dir = parser.get('layering','output_dir')


    # Loop through any available files in
    # the directory that defines the first choice/priority data.
    # Assemble the name of the corresponding secondary filename
    # by deriving the date (YYYYMMDD), modelrun (ihh), and 
    # forecast time (_fhhh) from the primary filename and path.
    # Then check if this file exists, if so, then pass this pair into
    # a list of tuples comprised of (primary file, secondary file).
    # After a list of paired files has been completed, these files
    # will be layered/combined by invoking the NCL script, combine.ncl.
    primary_files = get_filepaths(downscaled_primary_dir)
    
    # Determine which primary and secondary files we can layer, based on
    # matching dates, model runs, and forecast times.
    list_paired_files = find_layering_files(primary_files, downscaled_secondary_dir)
    
    # Now we have all the paired files to layer, create the key-value pair of
    # input needed to run the NCL layering script.
    num_matched_pairs = len(list_paired_files)
    for pair in list_paired_files:
        hrrrFile_param = "'hrrrFile=" + '"' + pair[0] + '"' + "' "
        rapFile_param =  "'rapFile="  + '"' + pair[1] + '"' + "' "
        full_layered_outfile = layered_output_dir + "/" + pair[2]
        outFile_param = "'outFile=" + '"' + full_layered_outfile + '"' + "' "
        mkdir_p(full_layered_outfile)
        init_indexFlag = "false"
        indexFlag = "true"
        init_indexFlag_param = "'indexFlag=" + '"' +  init_indexFlag + '"' + "' "
        indexFlag_param = "'indexFlag=" + '"' + indexFlag + '"' + "' "
        init_layering_params = hrrrFile_param + rapFile_param + init_indexFlag_param\
                               + outFile_param 
        layering_params = hrrrFile_param + rapFile_param + indexFlag_param\
                          + outFile_param
        init_layering_cmd = ncl_exe + " " + init_layering_params + " " + \
                            layering_exe
        layering_cmd = ncl_exe + " " + layering_params + " " + \
                            layering_exe
         
        init_return_value = os.system(init_layering_cmd)
        return_value = os.system(layering_cmd) 
    
    
def find_layering_files(primary_files,downscaled_secondary_dir):
    """Given a list of the primary files (full path + filename),
    retrieve the corresponding secondary file if it exists.  
    Create and return a list of tuples: (primary file, secondary file, 
    layered file). 

    Args:
        primary_files(list):  A list of the primary files
                              which we are trying to find
                              a corresponding "match" in
                              the secondary file directory
        downscaled_secondary_dir(string): The name of the
                                          directory for the
                                          secondary data.
    Output:
        list_paired_files (list): A list of tuples, where 
                                  the tuple consists of 
                                  (primary file, secondary
                                   file, and layered file name)
        
 
    """
    secondary_product = "RAP"
    list_paired_files = []
    paired_files = ()

    for primary_file in primary_files:
        match = re.match(r'.*/downscaled/([A-Za-z]{3,4})/([0-9]{8})/i([0-9]{2})/[0-9]{8}_i[0-9]{2}_f([0-9]{3})_[A-Za-z]{3,4}.nc',primary_file)
        if match:
            product = match.group(1)
            date = match.group(2)
            modelrun_str = match.group(3)
            fcst_hr_str = match.group(4)
            # Assemble the corresponding secondary file based on the date, modelrun, 
            # and forecast hour. 
            secondary_file = downscaled_secondary_dir +  \
                             "/" + date + "/i" + modelrun_str + "/" + date +\
                             "_i"+ modelrun_str + "_f" + fcst_hr_str + "_" +\
                             secondary_product + ".nc"  
            layered_filename = date + "_i" + modelrun_str + "_f" + \
                               fcst_hr_str + "_Analysis-Assimilation.nc"
               
        
            # Determine if this "manufactured" secondary file exists, if so, then 
            # create a tuple to represent this pair: (primary file, 
            # secondary file, layered file) then add this tuple of 
            # files to the list and continue. If not, then continue 
            # with the next primary file in the primary_files list.
            if os.path.isfile(secondary_file):
                paired_files = (primary_file, secondary_file,layered_filename)
                list_paired_files.append(paired_files)
                num = len(list_paired_files)
            else:
                logging.info("No matching date, or model run or forecast time for\
                             #secondary file")
                continue
        else:
            logging.error('ERROR: filename structure is not what was expected')



    return list_paired_files


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
    if len(elapsed_times) > 0:
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
    else:
        logging.error("ERROR: Nothing was returned....")
    

def read_input():
    parser = argparse.ArgumentParser(description='Forcing Configurations for WRF-Hydro')
    # Actions
    parser.add_argument('--regrid_downscale', action='store_true', help='regrid and downscale')
    parser.add_argument('--bias', action='store_true', help='bias correction')
    parser.add_argument('--layer', action='store_true', help='layer')

    # Model name of input data
    parser.add_argument('--InputDataName', required = True, choices=['MRMS','RAP','HRRR','GFS','CFS'],help='input data name: MRMS, RAP, HRRR, GFS, CFS')


    # Input file
    parser.add_argument('InputFileName', nargs=1, type=argparse.FileType('r'))
    args = parser.parse_args()
    if not (args.regrid_downscale or args.layer or args.bias) :
        parser.error('No action was requested, request regridding/downscaling, bias-correction, or layering')

    return args




#--------------------Define the Workflow -------------------------

if __name__ == "__main__":
    # Replace pass with anything you wish if you want to
    # run this as a standalone program.
    pass
