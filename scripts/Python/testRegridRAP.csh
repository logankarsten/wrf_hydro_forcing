#!/bin/csh

#rm State.*Regrid.txt
while 1
#python Regrid_Driver.py MRMS ../../parm/wrf_hydro_forcing.parm
#python Regrid_Driver.py HRRR ../../parm/wrf_hydro_forcing.parm
python Regrid_Driver.py RAP ../../parm/wrf_hydro_forcing.parm
#python Regrid_Driver.py GFS ../../parm/wrf_hydro_forcing.parm
sleep 10
end
exit 0
