# -*- coding: utf-8 -*-
"""
Created on Tue Jan  7 17:17:52 2020

@author: SimoneRomano
"""

#https://github.com/ibm-watson-iot/iot-python/blob/master/samples/simpleDevice/simpleDevice.py

# *****************************************************************************
# Copyright (c) 2017, 2019 IBM Corporation and other Contributors.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Eclipse Public License v1.0
# which accompanies this distribution, and is available at
# http://www.eclipse.org/legal/epl-v10.html
# *****************************************************************************


import sys
import wiotp.sdk
import logging

def commandProcessor(cmd):
    print("Command received: %s" % cmd.data)



logging.config.fileConfig("logging.conf")
# create logger
logger = logging.getLogger("mylogger")
logger.info("Start IBM Watson IoT Platform adapter...")    

authMethod = None
authMethod = "token"
    
deviceCli = None

# Initialize the device client.
def initClient(configFilePath):
    try:
        logger.info('connecting to IBM Watson IoT Platform')
        deviceOptions = wiotp.sdk.device.parseConfigFile(configFilePath)
        global deviceCli
        deviceCli = wiotp.sdk.device.DeviceClient(deviceOptions)
        deviceCli.commandCallback = commandProcessor
    except Exception as e:
        logger.error("Caught exception connecting device: %s" % str(e))
        sys.exit()

def send(configFilePath, data, onpublishCallback):
    global deviceCli
    if deviceCli is None:
        initClient("device.cfg")
    deviceCli.connect()
    #data = {"simpledev": "ok", "x": 10}

    success = deviceCli.publishEvent("event", "json", data, qos=0, onPublish=onpublishCallback)
    if not success:
        logger.error("Not connected to WIoTP")

        

# Disconnect the device and application from the cloud
#deviceCli.disconnect()