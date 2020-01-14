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

#doc
##Watson IoT Platform
https://www.ibm.com/support/knowledgecenter/SSQP8H/iot/platform/GA_information_management/ga_im_definitions.html#definitions_resources
https://www.ibm.com/support/knowledgecenter/SSQP8H/iot/platform/GA_information_management/ga_im_index_scenario.html#scenario
##Google Cloud Platform
https://cloud.google.com/docs/authentication/production