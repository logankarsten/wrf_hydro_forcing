import Analysis_Assimilation_Forcing as aac
# 18z AAC cycle hour -3 to -2
aac.forcing('regrid','MRMS', 'GaugeCorr_QPE_00.00_20151207_100000.grib2')
# 18z AAC cycle hour -2 to -1
aac.forcing('regrid','MRMS', 'GaugeCorr_QPE_00.00_20151207_110000.grib2')
# 18z AAC cycle hour -1 to 0
aac.forcing('regrid','MRMS', 'GaugeCorr_QPE_00.00_20151207_120000.grib2')
