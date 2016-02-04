#!/bin/bash

rm State.AnalysisAssimLayering.txt
while true
do
    python AnalysisAssimLayeringDriver.py ../../parm/wrf_hydro_forcing.parm
    sleep 60
done
exit 0