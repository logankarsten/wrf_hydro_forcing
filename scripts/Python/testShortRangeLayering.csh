#!/bin/csh

rm State.ShortRangeLayering.txt
while 1
python ShortRangeLayeringDriver.py
sleep 60
end
exit 0
