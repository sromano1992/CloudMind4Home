# -*- coding: utf-8 -*-
"""
Created on Sun Jan 12 19:42:28 2020

@author: SimoneRomano
"""

import numpy as np
import pandas as pd
from pandas import read_csv
from matplotlib import pyplot as plt

inputFileName = 'results-20200112-184658.csv'
data = pd.read_csv(inputFileName)
series = read_csv(inputFileName, header=0, parse_dates=True, squeeze=True)
series.plot()
#plt.plot(data['offChipTempValue'], data['rilevationTime'])
plt.plot(data['rilevationTime'][1:10], data['offChipTempValue'][1:10])

series.plot(kind='line',x='rilevationTime',y=['offChipTempValue','onboardBrightnessValue','onboardTemperatureValue','onboardHumidityValue','barometerTemperaturValue','barometerPressureValue','presenceValue'])

##brightnessClean
#☻series.replace(to_replace={'onboardBrightnessValue': > 60000.0}, value=0, inplace=True)
series['onboardBrightnessValue'] = series['onboardBrightnessValue'].apply(lambda x: x if int(x) <= 62000 else 0)

#plotting
series.rilevationTime = pd.to_datetime(series.rilevationTime)
series[1:200].plot(kind='line',x='rilevationTime',y=['offChipTempValue','onboardTemperatureValue','barometerTemperaturValue'])
series[1:200].plot(kind='line',x='rilevationTime',y=['onboardBrightnessValue'])
series[1:200].plot(kind='line',x='rilevationTime',y=['presenceValue'])
series[1:200].plot(kind='line',x='rilevationTime',y=['offChipTempValue','onboardBrightnessValue','onboardTemperatureValue','onboardHumidityValue','barometerTemperaturValue','barometerPressureValue','presenceValue'])


