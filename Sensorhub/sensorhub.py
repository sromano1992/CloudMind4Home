#!/usr/bin/python3
import json

BOARD_EMULATOR = False   

import sys
import time
import datetime
import logging
import logging.config
import gcloudmqtt
import ibmcloudmqtt
import os

if BOARD_EMULATOR == False:
    import smbus

def getserial():
  # Extract serial from cpuinfo file
  cpuserial = "0000000000000000"
  try:
    f = open('/proc/cpuinfo','r')
    for line in f:
      if line[0:6]=='Serial':
        cpuserial = line[10:26]
    f.close()
  except:
    cpuserial = "ERROR000000000"
 
  return cpuserial

def percent(a, b):
    if (a==0):
        return b
    if (b==0):
        return a
    result = int((abs(b - a) * 100) / a)   
    return result 
    
def checkImportantChange(currentDetection, lastDetection):
    if (percent(currentDetection.get('offChipTempValue'),lastDetection.get('offChipTempValue')))>10:
        logger.info("offChipTempValue important change...")
        return True
    if (percent(currentDetection.get('onboardBrightnessValue'),lastDetection.get('onboardBrightnessValue')))>15:
        logger.info("onboardBrightnessValue important change...")
        return True
    if (percent(currentDetection.get('onboardTemperatureValue'),lastDetection.get('onboardTemperatureValue')))>10:
        logger.info("onboardTemperatureValue important change...")
        return True
    if (percent(currentDetection.get('onboardHumidityValue'),lastDetection.get('onboardHumidityValue')))>10:
        logger.info("onboardHumidityValue important change...")
        return True
    if (percent(currentDetection.get('barometerTemperaturValue'),lastDetection.get('barometerTemperaturValue')))>10:
        logger.info("barometerTemperaturValue important change...")
        return True
    if (percent(currentDetection.get('barometerPressureValue'),lastDetection.get('barometerPressureValue')))>10:
        logger.info("barometerPressureValue important change...")
        return True
    if (percent(currentDetection.get('presenceValue'),lastDetection.get('presenceValue')))>0:
        logger.info("presenceValue important change...")
        return True


def myOnPublishCallback():
    logger.info("Confirmed event received by WIoTP")
    
#Sample commandline:
#python3 gcloudiotMqtt.py --algorithm RS256 --device_id RASP_000000001b982f0d --private_key_file ../../security/rsa_private.pem --registry_id cloudmind4home --ca_certs ../../security/roots.pem --project_id cloudmind4home --cloud_region europe-west1 gateway_send
def notifyStatus(jsonStatus_dict):
    logger.info('notifying...')
    jsonStatus = json.dumps(jsonStatus_dict)
    logger.info(jsonStatus)
    
    logger.info("Google IoT Core notification...")
    gcloudmqtt.send_data_from_bound_device(
            os.environ.get("GOOGLE_APPLICATION_CREDENTIALS"), "cloudmind4home",
            "europe-west1", "cloudmind4home", "RASP_000000001b982f0d",
            "", 100, "../../security/rsa_private.pem",
            "RS256", "../../security/roots.pem", "mqtt.googleapis.com",
            8883, 20, jsonStatus)
    
    logger.info("IBM Watson IoT notification...")
    ibmcloudmqtt.send("device.cfg", jsonStatus_dict, myOnPublishCallback)

DEVICE_BUS = 1
DEVICE_ADDR = 0x17

TEMP_REG = 0x01
LIGHT_REG_L = 0x02
LIGHT_REG_H = 0x03
STATUS_REG = 0x04
ON_BOARD_TEMP_REG = 0x05
ON_BOARD_HUMIDITY_REG = 0x06
ON_BOARD_SENSOR_ERROR = 0x07
BMP280_TEMP_REG = 0x08
BMP280_PRESSURE_REG_L = 0x09
BMP280_PRESSURE_REG_M = 0x0A
BMP280_PRESSURE_REG_H = 0x0B
BMP280_STATUS = 0x0C
HUMAN_DETECT = 0x0D

if BOARD_EMULATOR == False:
    bus = smbus.SMBus(DEVICE_BUS)



logging.config.fileConfig("logging.conf")
# create logger
logger = logging.getLogger("mylogger")
logger.info("Start sensing...")

lastSensorStatus = {}
lastNotificationTime = None
#getting pi imei
if BOARD_EMULATOR == False:
    imei = getserial()
else:
    imei = "EMULATOR"
if ("ERROR" in imei):
    logger.error("Cannot read imei...exiting...")
    sys.exit()
    
#start sensing
while True:
    try:
        aReceiveBuf = []
        
        aReceiveBuf.append(0x00) # 占位符
        
        if BOARD_EMULATOR == False:
            for i in range(TEMP_REG,HUMAN_DETECT + 1):
                aReceiveBuf.append(bus.read_byte_data(DEVICE_ADDR, i))
        else :
            aReceiveBuf.append(22)
            aReceiveBuf.append(0)
            aReceiveBuf.append(255)
            aReceiveBuf.append(8)
            aReceiveBuf.append(24)
            aReceiveBuf.append(49)
            aReceiveBuf.append(0)
            aReceiveBuf.append(25)
            aReceiveBuf.append(148)
            aReceiveBuf.append(138)
            aReceiveBuf.append(1)
            aReceiveBuf.append(0)
            aReceiveBuf.append(0)
        
        sensorStatus = {}
        
        if aReceiveBuf[STATUS_REG] & 0x01 :
            logger.debug("Off-chip temperature sensor overrange!")
            sensorStatus = {'offChipTempValue':0, 'offChipTempStatus': 'KO', 'offChipTempMessage': 'Off-chip temperature sensor overrange!'}
        elif aReceiveBuf[STATUS_REG] & 0x02 :
            logger.debug("No external temperature sensor!")
            sensorStatus = {'offChipTempValue':0, 'offChipTempStatus':'KO', 'offChipTempMessage': 'No external temperature sensor!'}
        else :
            logger.debug("Current off-chip sensor temperature = %d Celsius" % aReceiveBuf[TEMP_REG])
            sensorStatus = {'offChipTempValue':aReceiveBuf[TEMP_REG], 'offChipTempStatus':'OK'}
        
        if aReceiveBuf[STATUS_REG] & 0x04 :
            logger.debug("Onboard brightness sensor overrange!")
            sensorStatus['onboardBrightnessValue'] = 0
            sensorStatus['onboardBrightnessStatus'] = 'KO'
            sensorStatus['onboardBrightnessMessage'] = 'Onboard brightness sensor overrange!'
        elif aReceiveBuf[STATUS_REG] & 0x08 :
            logger.debug("Onboard brightness sensor failure!")
            sensorStatus['onboardBrightnessValue'] = 0
            sensorStatus['onboardBrightnessStatus'] = 'KO'
            sensorStatus['onboardBrightnessMessage'] = 'Onboard brightness sensor failure!'
        else :
            logger.debug("Current onboard sensor brightness = %d Lux" % (aReceiveBuf[LIGHT_REG_H] << 8 | aReceiveBuf[LIGHT_REG_L]))
            sensorStatus['onboardBrightnessValue'] = (aReceiveBuf[LIGHT_REG_H] << 8 | aReceiveBuf[LIGHT_REG_L])
            sensorStatus['onboardBrightnessStatus'] = 'OK'
        
        logger.debug("Current onboard sensor temperature = %d Celsius" % aReceiveBuf[ON_BOARD_TEMP_REG])
        sensorStatus['onboardTemperatureValue'] = aReceiveBuf[ON_BOARD_TEMP_REG]
        sensorStatus['onboardTemperatureStatus'] = 'OK'
        logger.debug("Current onboard sensor humidity = %d %%" % aReceiveBuf[ON_BOARD_HUMIDITY_REG])
        sensorStatus['onboardHumidityValue'] = aReceiveBuf[ON_BOARD_HUMIDITY_REG]
        sensorStatus['onboardHumidityStatus'] = 'OK'
        
        if aReceiveBuf[ON_BOARD_SENSOR_ERROR] != 0 :
            logger.debug("Onboard temperature and humidity sensor data may not be up to date!")
            sensorStatus['onboardTemperatureMessage'] = 'Onboard temperature and humidity sensor data may not be up to date!'
            sensorStatus['onboardHumidityMessage'] = 'Onboard temperature and humidity sensor data may not be up to date!'
            
        
        if aReceiveBuf[BMP280_STATUS] == 0 :
            logger.debug("Current barometer temperature = %d Celsius" % aReceiveBuf[BMP280_TEMP_REG])
            sensorStatus['barometerTemperaturValue'] = aReceiveBuf[BMP280_TEMP_REG]
            sensorStatus['barometerTemperaturStatus'] = 'OK'
            logger.debug("Current barometer pressure = %d pascal" % (aReceiveBuf[BMP280_PRESSURE_REG_L] | aReceiveBuf[BMP280_PRESSURE_REG_M] << 8 | aReceiveBuf[BMP280_PRESSURE_REG_H] << 16))
            sensorStatus['barometerPressureValue'] = aReceiveBuf[BMP280_PRESSURE_REG_L] | aReceiveBuf[BMP280_PRESSURE_REG_M] << 8 | aReceiveBuf[BMP280_PRESSURE_REG_H] << 16
            sensorStatus['barometerPressureStatus'] = 'OK'
        else :
            logger.debug("Onboard barometer works abnormally!")
            sensorStatus['barometerTemperaturValue'] = 0
            sensorStatus['barometerTemperaturStatus'] = 'KO'
            sensorStatus['barometerTemperatureMessage'] = 'Onboard barometer works abnormally!'
            sensorStatus['barometerPressureValue'] = 0
            sensorStatus['barometerPressureStatus'] = 'KO'
            sensorStatus['barometerPressureMessage'] = 'Onboard barometer works abnormally!'
        
        if aReceiveBuf[HUMAN_DETECT] == 1 :
            logger.debug("Live body detected within 5 seconds!")
            sensorStatus['presenceValue'] = 1
            sensorStatus['presenceStatus'] = 'OK'
            sensorStatus['presenceMessage'] = 'Live body detected within 5 seconds!'
        else:
            logger.debug("No humans detected!")
            sensorStatus['presenceValue'] = 0
            sensorStatus['presenceStatus'] = 'OK'
            sensorStatus['presenceMessage'] = 'No humans detected!'
        
        x = datetime.datetime.now()
        sensorStatus['rilevationTime'] = x.strftime("%d-%m-%Y %H:%M:%S.%f")
        
        sensorStatus['imei'] = imei
        sensorStatus['props'] = []    #for enrichment...
        
        if len(lastSensorStatus) == 0:  #first run --> NOTIFY!
            lastSensorStatus = sensorStatus
            notifyStatus(sensorStatus)
            lastNotificationTime = datetime.datetime.now()
        else:
            if (((datetime.datetime.now() - lastNotificationTime).seconds / 60) > 5 or checkImportantChange(sensorStatus, lastSensorStatus) == True):
                notifyStatus(sensorStatus)
                lastSensorStatus = sensorStatus
                lastNotificationTime = datetime.datetime.now()
            
        sensorStatus = json.dumps(sensorStatus)            
        logger.debug(sensorStatus)
        time.sleep(1)
    except Exception as e:
        logger.error("Error: " + str(e))

