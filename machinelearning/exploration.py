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
#plt.plot(data['offChipTempValue'], data['rilevationTime'])
#plt.plot(data['rilevationTime'][1:10], data['offChipTempValue'][1:10])