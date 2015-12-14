#!/bin/csh

#rm State.*Regrid.txt
while 1
python Regrid_Driver.py MRMS ../../parm/wrf_hydro_forcing.parm
sleep 10
end
exit 0
