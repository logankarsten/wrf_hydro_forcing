#!/bin/csh

rm State.AnalysisAssimLayering.txt
while 1
python AnalysisAssimLayeringDriver.py
sleep 60
end
exit 0
