#!/bin/csh

#rm State.LongRangeRegrid.txt
while 1
python LongRangeRegridDriver.py ../../parm/wrf_hydro_forcing.parm
sleep 60
end
exit 0
