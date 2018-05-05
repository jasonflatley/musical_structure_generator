# -*- coding: utf-8 -*-
"""
Created on Thu Mar 22 18:51:35 2018

@author: jason
"""

import pandas as pd
import numpy as np

url = 'https://raw.github.com/pandas-dev/pandas/master/pandas/tests/data/tips.csv'
tips = pd.read_csv(url)
tips.head()






tips_summed = tips.groupby(['sex', 'smoker'])['total_bill', 'tip'].sum()
tips_summed.head()





gb = tips.groupby('smoker')['total_bill']


tips['adj_total_bill'] = tips['total_bill'] - gb.transform('mean')
