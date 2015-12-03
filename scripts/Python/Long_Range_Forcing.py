import WRF_Hydro_forcing as whf
import logging
import os
import sys
import datetime
import getopt
from ConfigParser import SafeConfigParser

"""Long_Range_Forcing
Performs multi-step process of applying bias-correction to CFSv2 using
NLDAS cdf matching, combine the bias-corrected NetCDF files into one
NetCDF file which is then regridded to the conus IOC domain. A final
step of downscaling the data using high-resolution topography data
takes place.
"""

#-----------------------------------
# Logan Karsten
# National Center for Atmospheric Research
# Research Applications Laboratory
# karsten@ucar.edu
# 303-497-2693
#-----------------------------------

# Inputs to wrapper configuration are as follows:
# 1.) CFSv2 file 

def forcing(argv):
    """ Args:
        1.) file (string): The file name. The full path is 
            not necessary as full paths will be derived from
            parameter directory paths and datetime information.
        Returns:
        1.) Status (integer): Integer value indicating whether
            downscaling was successful (0), or failed (1). All
            errors will be written to the log file. 
    """

    file_in = ''
    try:
        opts, args = getopt.getopt(argv,"hi:",["file_in="])
    except getopt.GetoptErr:
        print 'Long_Range_Forcing.py -i <file_in>'
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print 'Long_Range_Forcing.py -i <file_in>'
            sys.exit(0)
        elif opt in ("-i", "--ifile"):
            file_in = arg

    # Obtain CFSv2 forcing engine parameters.
    parser = SafeConfigParser()
    configFile = '/d4/karsten/DFE/wrf_hydro_forcing/parm/wrf_hydro_forcing.parm'
    parser.read(configFile)
    logging_level = parser.get('log_level', 'forcing_engine_log_level')
    out_dir = parser.get('downscaling','CFS_downscale_out_dir') 
    tmp_dir = parser.get('bias_correction','CFS_tmp_dir')

    # Define CFSv2 cycle date and valid time based on file name.
    (cycleYYYYMMDD,cycleHH,fcsthr,em) = whf.extract_file_info_cfs(file_in)
    em_str = str(em)

    # Establish datetime objects
    dateCurrent = datetime.datetime.today()
    dateCycleYYYYMMDDHH = datetime.datetime(year=int(cycleYYYYMMDD[0:4]),
                          month=int(cycleYYYYMMDD[4:6]),
                          day=int(cycleYYYYMMDD[6:8]),
                          hour=cycleHH)
    dateFcstYYYYMMDDHH = dateCycleYYYYMMDDHH + \
                         datetime.timedelta(seconds=fcsthr*3600)
 
    # Establish final output directories to hold 'LDASIN' files used for
    # WRF-Hydro long-range forecasting. If the directory does not exist,
    # create it.
    out_path = out_dir + "/Member_" + em_str.zfill(2) + "/" + \
               dateCycleYYYYMMDDHH.strftime("%Y%m%d%H")

    whf.mkdir_p(out_path)

    # Establish log file unique to model cycle, time, and current time
    # This will make it possible to diagnose potential issues that 
    # arise with data forcing engine. 
    log_path = out_path + "/" + dateCycleYYYYMMDDHH.strftime('%Y%m%d%H') + \
               "_" + dateFcstYYYYMMDDHH.strftime('%Y%m%d%H') + \
               "_" + dateCurrent.strftime('%Y%m%d%H%M%S') + '_Long_Range.log' 

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

    in_fcst_range = whf.is_in_fcst_range("CFSv2",fcsthr,parser)

    if in_fcst_range:
        # First, bias-correct CFSv2 data and generate hourly files 
        # from six-hour forecast
        logging.info("Bias correcting for CFSv2 cycle: " + \
                     dateCycleYYYYMMDDHH.strftime('%Y%m%d%H') + \
                     " CFSv2 forecast time: " + dateFcstYYYYMMDDHH.strftime('%Y%m%d%H'))
        whf.bias_correction('CFSv2',file_in,dateCycleYYYYMMDDHH,
                            dateFcstYYYYMMDDHH,parser, em = em)
        # Second, regrid to the conus IOC domain
        # Loop through each hour in a six-hour CFSv2 forecast time step, compose temporary filename 
        # generated from bias-correction and call the regridding to go to the conus domain.
        for hour in range(1, 7):
  	    dateTempYYYYMMDDHH = dateFcstYYYYMMDDHH - datetime.timedelta(seconds=(6-hour)*3600)
               
            fileBiasCorrected = tmp_dir + "/CFSv2_bias_corrected_TMP_" + \
                                dateCycleYYYYMMDDHH.strftime('%Y%m%d%H') + "_" + \
                                dateTempYYYYMMDDHH.strftime('%Y%m%d%H') + ".M" + \
                                em_str.zfill(2) + ".nc"
            logging.info("Regridding CFSv2 to conus domain for cycle: " + \
                         dateCycleYYYYMMDDHH.strftime('%Y%m%d%H') + \
                         " forecast time: " + dateTempYYYYMMDDHH.strftime('%Y%m%d%H'))
            fileRegridded = whf.regrid_data("CFSv2",fileBiasCorrected,parser)
            # Double check to make sure file was created, delete temporary bias-corrected file
            whf.file_exists(fileRegridded)
            cmd = "rm -rf " + fileBiasCorrected
            status = os.system(cmd)
            if status != 0:
                logging.error("Failure to remove " + fileBiasCorrected)
                sys.exit(1)

  
        # Third, perform topography downscaling to generate final
        # Loop through each hour in a six-hour CFSv2 forecast time step, compose temporary filename
        # generated from regridding and call the downscaling function.
        for hour in range(1,7):
            dateTempYYYYMMDDHH = dateFcstYYYYMMDDHH - datetime.timedelta(seconds=(6-hour)*3600)

            logging.info("Downscaling CFSv2 for cycle: " +
                         dateCycleYYYYMMDDHH.strftime('%Y%m%d%H') +
                         " forecast time: " + dateTempYYYYMMDDHH.strftime('%Y%m%d%H'))
            fileRegridded = tmp_dir + "/CFSv2_bias_corrected_TMP_" + \
                            dateCycleYYYYMMDDHH.strftime('%Y%m%d%H') + "_" + \
                                dateTempYYYYMMDDHH.strftime('%Y%m%d%H') + \
                                "_regridded.M" + em_str.zfill(2) + ".nc"
            LDASIN_path_tmp = tmp_dir + "/" + dateTempYYYYMMDDHH.strftime('%Y%m%d%H') + "00.LDASIN_DOMAIN1.nc"
            LDASIN_path_final = out_path + "/" + dateTempYYYYMMDDHH.strftime('%Y%m%d%H') + "00.LDASIN_DOMAIN1"
            # Check to see if final file already exists. If it does, this implies something went wrong and it 
            # needs to be removed
            if os.path.exists(LDASIN_path_final):
                cmd = "rm -rf " + LDASIN_path_final
                status = os.system(cmd)
                if status != 0:
                    logging.error("Failure to remove old file " + LDASIN_path_final)
                    sys.exit(1)
                
            whf.downscale_data("CFSv2",fileRegridded,parser, out_path=LDASIN_path_tmp, \
                               verYYYYMMDDHH=dateTempYYYYMMDDHH)
            # Double check to make sure file was created, delete temporary regridded file
            whf.file_exists(LDASIN_path_tmp)
            # Rename file to conform to WRF-Hydro expectations
            cmd = "mv " + LDASIN_path_tmp + " " + LDASIN_path_final
            status = os.system(cmd)
            if status != 0:
                logging.error("Failure to rename " + LDASIN_path_tmp)
                sys.exit(1)
            whf.file_exists(LDASIN_path_final)
            cmd = "rm -rf " + fileRegridded
            status = os.system(cmd)
            if status != 0:
                logging.error("Failure to remove " + fileRegridded)
                sys.exit(1)
        
        # Exit gracefully with an exit status of 0
        sys.exit(0)
    else:
        # Skip processing this file. Exit gracefully with a 0 exit status.
        logging.info('Requested file is outside max fcst for CFSv2')
        sys.exit(0)

if __name__ == "__main__":
    forcing(sys.argv[1:])
