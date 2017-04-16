
from pandas import read_csv
import pandas as pd
import numpy as np
from datetime import timedelta
from datetime import datetime
from keras.models import load_model
import os
import pickle
import warnings
warnings.filterwarnings('ignore')


logPath = './web1/u_ex161018.log'
logFPath = './features/web1_ex161018_f.csv'

def strHas(s, src):
    try:
        return (s in src)
    except TypeError:
        return 0

# known public bots
botList = ['Googlebot', 'bingbot', 'msnbot']


# analyze log file
suspicious = dict()     
temp = []
f = open(logPath, encoding='utf-8', errors='ignore')
logFeature = pd.read_csv(logFPath)
line = f.readline()
while line:
    if line.startswith('#'):
        line = f.readline()
        continue
    else:
        temp.append(line.split())
        line = f.readline()
logTable = pd.DataFrame(temp)
ips = logTable[9].unique()
for ip in ips:
        if ip.count('.')==3:      
            ipLogs = logTable[logTable[9]==ip]
            # known bot behabvior
            if ipLogs[5].str.contains('robots.txt').sum() > 0:
                suspicious[ip] = 66666
            # known bots
            elif ipLogs[11].str.contains('|'.join(botList)).sum() > 0:
                suspicious[ip] = 66666
            # slow but continuous crawl
            if logFeature[logFeature['IP']==ip].shape[0] > 100:
                suspicious[ip] = 66666


# read feature
featureDim = ['hitCount', 'GETcount', 'POSTcount', 'HEADcount', '3xxCount', '4xxCount', 
              'hjRatio']
testFeature = logFeature[featureDim].as_matrix()

# scaling feature
scaler = pickle.load(open('scaler.sav', 'rb'))
testFeature = scaler.transform(testFeature)

# load AE to encode feature
encodeModel = load_model('./encodeModel.h5')
enFeature = encodeModel.predict(testFeature)

# make classification with Kmeans
km = pickle.load(open('km.sav', 'rb'))
result = km.predict(enFeature)

for i in range(result.size):
    if result[i]==0:
        if logFeature['IP'][i] in suspicious:
            suspicious[logFeature['IP'][i]] += 1
        else:
            suspicious[logFeature['IP'][i]] = 0

print('\n\nSuspicious Crawler Bot IPs:')
for k in suspicious:
    if(suspicious[k]>0):
        print(k)

