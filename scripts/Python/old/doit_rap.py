import Short_Range_Forcing as srf
import Analysis_Assimilation_Forcing as aac
# 18z AAC cycle hour -3 to -2
srf.forcing('regrid','RAP','20151207_i07_f003_WRF-RR.grb2')
aac.forcing('regrid','RAP','20151207_i10_f000_WRF-RR.grb2')
# 18z AAC cycle hour -2 to -1
srf.forcing('regrid','RAP','20151207_i08_f003_WRF-RR.grb2')
aac.forcing('regrid','RAP','20151207_i11_f000_WRF-RR.grb2')
# 18z AAC cycle hour -1 to 0
srf.forcing('regrid','RAP','20151207_i09_f003_WRF-RR.grb2')
aac.forcing('regrid','RAP','20151207_i12_f000_WRF-RR.grb2')
