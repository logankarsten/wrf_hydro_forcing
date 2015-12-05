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
             
            
    dateCurrent = datetime.datetime.today()  
    cycleDate = datetime.datetime(year=yearCycle,month=monthCycle,day=dayCycle, \
                hour=hourCycle)
    validDate = cycleDate + datetime.timedelta(seconds=fhr*3600)
    fcstWindowDate = validDate + datetime.timedelta(seconds=-3*3600) # Used for 3-hr forecast
                     # HRRR/RAP files necessary for fluxes and precipitation data.
  
    # Obtain analysis and assimiltation configuration parameters.
    parser = SafeConfigParser()
    configFile = '/d4/karsten/DFE/wrf_hydro_forcing/parm/wrf_hydro_forcing.parm'
    parser.read(configFile)
    out_dir = parser.get('layering','analysis_assimilation_output')
    tmp_dir = parser.get('layering','analysis_assimilation_tmp')
    qpe_parm_dir = parser.get('layering','qpe_combine_parm_dir')
    hrrr_ds_dir_3hr = parser.get('downscaling','HRRR_finished_output_dir')
    hrrr_ds_dir_0hr = parser.get('downscaling','HRRR_finished_output_dir_0hr')
    rap_ds_dir_3hr = parser.get('downscaling','RAP_finished_output_dir')
    rap_ds_dir_0hr = parser.get('downscaling','RAP_finished_output_dir_0hr')
    mrms_ds_dir = parser.get('regridding','MRMS_finished_output_dir')
    layer_exe = parser.get('exe','Analysis_Assimilation_layering')
    ncl_exec = parser.get('exe', 'ncl_exe')

    # Sanity checking
    whf.dir_exists(out_dir)
    whf.dir_exists(tmp_dir)
    whf.dir_exists(qpe_parm_dir)
    whf.dir_exists(hrrr_ds_dir_3hr)
    whf.dir_exists(hrrr_ds_dir_0hr)
    whf.dir_exists(rap_ds_dir_3hr)
    whf.dir_exists(rap_ds_dir_0hr)
    whf.dir_exists(mrms_ds_dir)
    whf.file_exists(layer_exe)

    # Establish final output directories to hold 'LDASIN' files used for
    # WRF-Hydro long-range forecasting. If the directory does not exist,
    # create it.
    out_path = out_dir + "/" + cycleDate.strftime("%Y%m%d%H")

    whf.mkdir_p(out_path)

    # Establish log file unique to model cycle, time, and current time
    # This will make it possible to diagnose potential issues that
    # arise with data forcing engine.
    log_path = out_path + "/" + cycleDate.strftime('%Y%m%d%H') + \
               "_" + validDate.strftime('%Y%m%d%H') + \
               "_" + dateCurrent.strftime('%Y%m%d%H%M%S') + '_Anal_Assim.log'
    logging_level = parser.get('log_level', 'forcing_engine_log_level') 

    # Open log file
    if logging_level == 'DEBUG':
        set_level = logging.DEBUG
    elif logging_level == 'INFO':
        set_level = logging.INFO
    elif logging_level == 'WARNING':
        set_level = logging.WARNING
    elif logging_level == 'ERROR':
        set_level = logging.ERROR
    else:
        set_level = logging.CRITICAL

    logging.basicConfig(format='%(asctime)s %(message)s',
                        filename=log_path, level=set_level)

    # Compose necessary file paths  
    hrrr0Path = hrrr_ds_dir_0hr + "/" + validDate.strftime("%Y%m%d%H") + \
                "/" + validDate.strftime("%Y%m%d%H") + "00.LDASIN_DOMAIN1.nc"
    hrrr3Path = hrrr_ds_dir_3hr + "/" + fcstWindowDate.strftime("%Y%m%d%H") + \
                "/" + validDate.strftime("%Y%m%d%H") + "00.LDASIN_DOMAIN1.nc"     
    rap0Path = rap_ds_dir_0hr + "/" + validDate.strftime("%Y%m%d%H") + \
                "/" + validDate.strftime("%Y%m%d%H") + "00.LDASIN_DOMAIN1.nc"
    rap3Path = rap_ds_dir_3hr + "/" + fcstWindowDate.strftime("%Y%m%d%H") + \
                "/" + validDate.strftime("%Y%m%d%H") + "00.LDASIN_DOMAIN1.nc"
    mrmsPath = mrms_ds_dir + "/" + validDate.strftime("%Y%m%d%H") + \
                "/" + validDate.strftime("%Y%m%d%H") + "00.LDASIN_DOMAIN1.nc"
    hrrrBiasPath = qpe_parm_dir + "/HRRR_CMC-CPC_bias-corr_m" + \
                   validDate.strftime("%m") + "_v8_wrf1km.grb2"
    hrrrWgtPath = qpe_parm_dir + "/HRRR_wgt_m" + \
                  validDate.strftime("%m") + "_v7_wrf1km.grb2"
    mrmsBiasPath = qpe_parm_dir + "/MRMS_radonly_CMC-CPC_bias-corr_m" + \
                   validDate.strftime("%m") + "_v8_wrf1km.grb2"
    mrmsWgtPath = qpe_parm_dir + "/MRMS_radonly_wgt_m" + \
                  validDate.strftime("%m") + "_v7_wrf1km.grb2"
    rapBiasPath = qpe_parm_dir + "/RAPD_CMC-CPC_bias-corr_m" + \
                  validDate.strftime("%m") + "_v8_wrf1km.grb2"
    rapWgtPath = qpe_parm_dir + "/RAPD_wgt_m" + \
                 validDate.strftime("%m") + "_v7_wrf1km.grb2"

    # Sanity checking on parameter data
    whf.file_exists(hrrrBiasPath)
    whf.file_exists(hrrrWgtPath)
    whf.file_exists(mrmsBiasPath)
    whf.file_exists(mrmsWgtPath)
    whf.file_exists(rapBiasPath)
    whf.file_exists(rapWgtPath) 

    # Compose output file paths
    LDASIN_path_tmp = tmp_dir + "/" + validDate.strftime('%Y%m%d%H') + "00.LDASIN_DOMAIN1_TMP.nc"
    LDASIN_path_final = out_path + "/" + validDate.strftime('%Y%m%d%H') + "00.LDASIN_DOMAIN1"
    # Perform layering/combining depending on processing path.
    if process == 1:    # RAP only
        logging.info("Layering and Combining RAP only for cycle date: " + \
                     cycleDate.strftime("%Y%m%d%H") + " valid date: " + \
                     validDate.strftime("%Y%m%d%H"))
        # Check for existence of input files
        whf.file_exists(rap0Path)
        whf.file_exists(rap3Path)
    elif process == 2:  # HRRR and RAP only 
        logging.info("Layering and Combining RAP and HRRR for cycle date: " + \
                     cycleDate.strftime("%Y%m%d%H") + " valid date: " + \
                     validDate.strftime("%Y%m%d%H"))
        # Check for existence of input files
        whf.file_exists(rap0Path)
        whf.file_exists(rap3Path)
        whf.file_exists(hrrr0Path)
        whf.file_exists(hrrr3Path)
    elif process == 3:  # HRRR, RAP, and MRMS
        logging.info("Layering and Combining RAP/HRRR/MRMS for cycle date: " + \
                     cycleDate.strftime("%Y%m%d%H") + " valid date: " + \
                     validDate.strftime("%Y%m%d%H"))
        # Check for existence of input files
        whf.file_exists(rap0Path)
        whf.file_exists(rap3Path)
        whf.file_exists(hrrr0Path)
        whf.file_exists(hrrr3Path)
        whf.file_exists(mrmsPath)
    else:  # Error out
        logging.error("Invalid input action selected")
        return(1)

    print process
    hrrrB_param = "'hrrrBFile=" + '"' + hrrrBiasPath + '"' + "' "
    mrmsB_param = "'mrmsBFile=" + '"' + mrmsBiasPath + '"' + "' "
    rapB_param = "'rapBFile=" + '"' + rapBiasPath + '"' + "' "
    hrrrW_param = "'hrrrWFile=" + '"' + hrrrWgtPath + '"' + "' "
    mrmsW_param = "'mrmsWFile=" + '"' + mrmsWgtPath + '"' + "' "
    rapW_param = "'rapWFile=" + '"' + rapWgtPath + '"' + "' "
    hrrr0_param = "'hrrr0File=" + '"' + hrrr0Path + '"' + "' "
    hrrr3_param = "'hrrr3File=" + '"' + hrrr3Path + '"' + "' "
    rap0_param = "'rap0File=" + '"' + rap0Path + '"' + "' "
    rap3_param = "'rap3File=" + '"' + rap3Path + '"' + "' "
    mrms_param = "'mrmsFile=" + '"' + mrmsPath + '"' + "' "
    process_param = "'process=" + '"' + str(process) + '"' + "' "
    out_param = "'outPath=" + '"' + LDASIN_path_tmp + '"' + "' "
     
    cmd_params = hrrrB_param + mrmsB_param + rapB_param + \
                 hrrrW_param + mrmsW_param + rapW_param + \
                 hrrr0_param + hrrr3_param + rap0_param + rap3_param + \
                 mrms_param + process_param + out_param
    cmd = ncl_exec + " -Q " + cmd_params + " " + layer_exe
    status = os.system(cmd)

    if status != 0:
        logging.error("Error in combinining NCL program")
        return(1)
   

#----------------------------------------------
if __name__ == "__main__":
    forcing()
