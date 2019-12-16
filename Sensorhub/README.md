# C complie and run.
* gcc -o sensorhub sensorhub.c -lwiringPi 
* ./sensorhub

# run python code.
* python3 sensorhub.py 

# run in background
nohup python3 sensorhub.py > /dev/null 2>&1 &

#kill
ps -ef | grep -i sensorhub
kill _PID_