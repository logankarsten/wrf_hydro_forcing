#!/bin/csh

rm State.AnalysisAssimLayering.txt
while 1
python AnalysisAssimLayeringDriver.py ../../parm/wrf_hydro_forcing.parm
sleep 60
end
exit 0
