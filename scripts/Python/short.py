#!/usr/bin/python

import Short_Range_Forcing as srf

# Regrid and downscale RAP
#srf.forcing('regrid','RAP','20151201_i12_f001_WRF-RR.grb2')
##srf.forcing('regrid','RAP','20151124_i12_f002_WRF-RR.grb2')
##srf.forcing('regrid','RAP','20151124_i18_f001_WRF-RR.grb2')
#srf.forcing('regrid','RAP','20151124_i13_f001_WRF-RR.grb2')
#srf.forcing('regrid','RAP','20151124_i23_f001_WRF-RR.grb2')
#srf.forcing('regrid','RAP','20151117_i00_f000_WRF-RR.grb2')


# Regrid and downscale HRRR
#srf.forcing('regrid','HRRR','20151201_i12_f001_HRRR.grb2')
#srf.forcing('regrid','HRRR','20151124_i12_f002_HRRR.grb2')
#srf.forcing('regrid','HRRR','20151124_i18_f001_HRRR.grb2')
#srf.forcing('regrid','HRRR','20151124_i13_f001_HRRR.grb2')
#srf.forcing('regrid','HRRR','20151124_i23_f001_HRRR.grb2')
#srf.forcing('regrid','HRRR','20151117_i00_f000_HRRR.grb2')

# Layer HRRR and RAP
srf.forcing('layer','RAP','2015120112/201512011300.LDASIN_DOMAIN1.nc','HRRR','2015120112/201512011300.LDASIN_DOMAIN1.nc')






