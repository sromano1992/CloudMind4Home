#!/usr/bin/python3
import json
BOARD_EMULATOR = False

if BOARD_EMULATOR == False:
    import smbus

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

if aReceiveBuf[STATUS_REG] & 0x01 :
    print("Off-chip temperature sensor overrange!")
    sensorStatus = {'offChipTempValue':0, 'offChipTempStatus': 'KO', 'offChipTempMessage': 'Off-chip temperature sensor overrange!'}
elif aReceiveBuf[STATUS_REG] & 0x02 :
    print("No external temperature sensor!")
    sensorStatus = {'offChipTempValue':0, 'offChipTempStatus':'KO', 'offChipTempMessage': 'No external temperature sensor!'}
else :
    print("Current off-chip sensor temperature = %d Celsius" % aReceiveBuf[TEMP_REG])
    sensorStatus = {'offChipTempValue':aReceiveBuf[TEMP_REG], 'offChipTempStatus':'OK'}

if aReceiveBuf[STATUS_REG] & 0x04 :
    print("Onboard brightness sensor overrange!")
    sensorStatus['onboardBrightnessValue'] = 0
    sensorStatus['onboardBrightnessStatus'] = 'KO'
    sensorStatus['onboardBrightnessMessage'] = 'Onboard brightness sensor overrange!'
elif aReceiveBuf[STATUS_REG] & 0x08 :
    print("Onboard brightness sensor failure!")
    sensorStatus['onboardBrightnessValue'] = 0
    sensorStatus['onboardBrightnessStatus'] = 'KO'
    sensorStatus['onboardBrightnessMessage'] = 'Onboard brightness sensor failure!'
else :
    print("Current onboard sensor brightness = %d Lux" % (aReceiveBuf[LIGHT_REG_H] << 8 | aReceiveBuf[LIGHT_REG_L]))
    sensorStatus['onboardBrightnessValue'] = (aReceiveBuf[LIGHT_REG_H] << 8 | aReceiveBuf[LIGHT_REG_L])
    sensorStatus['onboardBrightnessStatus'] = 'OK'

print("Current onboard sensor temperature = %d Celsius" % aReceiveBuf[ON_BOARD_TEMP_REG])
sensorStatus['onboardTemperatureValue'] = aReceiveBuf[ON_BOARD_HUMIDITY_REG]
sensorStatus['onboardBrightnessStatus'] = 'OK'
print("Current onboard sensor humidity = %d %%" % aReceiveBuf[ON_BOARD_HUMIDITY_REG])
sensorStatus['onboardHumidityValue'] = aReceiveBuf[ON_BOARD_HUMIDITY_REG]
sensorStatus['onboardHumidityStatus'] = 'OK'

if aReceiveBuf[ON_BOARD_SENSOR_ERROR] != 0 :
    print("Onboard temperature and humidity sensor data may not be up to date!")
    sensorStatus['onboardBrightnessMessage'] = 'Onboard temperature and humidity sensor data may not be up to date!'
    sensorStatus['onboardHumidityMessage'] = 'Onboard temperature and humidity sensor data may not be up to date!'
    

if aReceiveBuf[BMP280_STATUS] == 0 :
    print("Current barometer temperature = %d Celsius" % aReceiveBuf[BMP280_TEMP_REG])
    sensorStatus['barometerTemperaturValue'] = aReceiveBuf[BMP280_TEMP_REG]
    sensorStatus['barometerTemperaturStatus'] = 'OK'
    print("Current barometer pressure = %d pascal" % (aReceiveBuf[BMP280_PRESSURE_REG_L] | aReceiveBuf[BMP280_PRESSURE_REG_M] << 8 | aReceiveBuf[BMP280_PRESSURE_REG_H] << 16))
    sensorStatus['barometerPressureValue'] = aReceiveBuf[BMP280_PRESSURE_REG_L] | aReceiveBuf[BMP280_PRESSURE_REG_M] << 8 | aReceiveBuf[BMP280_PRESSURE_REG_H] << 16
    sensorStatus['barometerPressureStatus'] = 'OK'
else :
    print("Onboard barometer works abnormally!")
    sensorStatus['barometerTemperaturValue'] = 0
    sensorStatus['barometerTemperaturStatus'] = 'KO'
    sensorStatus['barometerTemperatureMessage'] = 'Onboard barometer works abnormally!'
    sensorStatus['barometerPressureValue'] = 0
    sensorStatus['barometerPressureStatus'] = 'KO'
    sensorStatus['barometerPressureMessage'] = 'Onboard barometer works abnormally!'

if aReceiveBuf[HUMAN_DETECT] == 1 :
    print("Live body detected within 5 seconds!")
    sensorStatus['presenceValue'] = 1
    sensorStatus['presenceStatus'] = 'OK'
    sensorStatus['presenceMessage'] = 'Live body detected within 5 seconds!'
else:
    print("No humans detected!")
    sensorStatus['presenceValue'] = 0
    sensorStatus['presenceStatus'] = 'OK'
    sensorStatus['presenceMessage'] = 'No humans detected!'
    
sensorStatus = json.dumps(sensorStatus)
print(sensorStatus)

