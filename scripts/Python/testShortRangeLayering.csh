#!/bin/csh

rm State.ShortRangeLayering.txt
while 1
python ShortRangeLayeringDriver.py ../../parm/wrf_hydro_forcing.parm
sleep 60
end
exit 0
