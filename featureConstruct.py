
from pandas import read_csv
import pandas as pd
import numpy as np
from datetime import timedelta
from datetime import datetime
import os

featureDim = ['hitCount', 'GETcount', 'POSTcount', 'HEADcount', '3xxCount', '4xxCount', 
              'hjRatio']
              
              
def num(s):
    try:
        return int(s)
    except ValueError:
        return 0

def generateFeature(logTable):
    bNum = 0
    features = pd.DataFrame(columns=featureDim)
    relatedIP = []
    trackRange = timedelta(0, 300)
    ips = logTable[9].unique()
    for ip in ips:
        if ip.count('.')==3:      
            ipLogs = logTable[logTable[9]==ip]
            # processing time
            temp = ipLogs[1].as_matrix()
            ipLogs[1] = np.array([datetime.strptime(d, '%H:%M:%S') for d in temp])
            # start behavior tracking
            startTime = ipLogs.iloc[0][1]
            behavior = np.zeros((1, 7))
            hCount = 0
            jCount = 0
            for i in range(0, ipLogs.shape[0]):
                curTime = ipLogs.iloc[i][1]
                if i%500 == 0:
                    print('ip:%s iter:%d\n' %(ip, i))
                
                if curTime - startTime < trackRange:
                    behavior[0][0] += 1
                    behavior[0][1] += (ipLogs.iloc[i][4] == 'GET')
                    behavior[0][2] += (ipLogs.iloc[i][4] == 'POST')
                    behavior[0][3] += (ipLogs.iloc[i][4] == 'HEAD')            
                    behavior[0][4] += (num(ipLogs.iloc[i][14]) in range(300, 400))
                    behavior[0][5] += (num(ipLogs.iloc[i][14]) in range(400, 500))
                    if ipLogs.iloc[i][5][ipLogs.iloc[i][5].rfind('.')+1:] in ['jpg', 'jpeg', 'png', 'gif', 'bmp']:
                        jCount += 1
                    else:
                        hCount += 1
                else:
                    behavior[0][6] = hCount - jCount
                    features.loc[bNum] = behavior[0]
                    relatedIP.append(ip)
                    bNum += 1
                    startTime = curTime
                    hCount = 0
                    jCount = 0
                    behavior = np.zeros((1, 7))
                    behavior[0][0] += 1
                    behavior[0][1] += (ipLogs.iloc[i][4] == 'GET')
                    behavior[0][2] += (ipLogs.iloc[i][4] == 'POST')
                    behavior[0][3] += (ipLogs.iloc[i][4] == 'HEAD')            
                    behavior[0][4] += (num(ipLogs.iloc[i][14]) in range(300, 400))
                    behavior[0][5] += (num(ipLogs.iloc[i][14]) in range(400, 500))
                    if ipLogs.iloc[i][5][ipLogs.iloc[i][5].rfind('.')+1:] in ['jpg', 'jpeg', 'png', 'gif', 'bmp']:
                        jCount += 1
                    else:
                        hCount += 1
    features['IP'] = relatedIP
    return features
    

                        
                            
curDir = os.getcwd()
logDir = 'web'
if not os.path.isdir(curDir+'/features'):
    os.makedirs(curDir+'/features')
    
for i in range(1,4):
    for filename in os.listdir(curDir+'/'+logDir+str(i)):
        filePath = './web'+str(i)+'/'+filename
        temp = []
        f = open(filePath, encoding='utf-8', errors='ignore')
        line = f.readline()
        while line:
            if line.startswith('#'):
                line = f.readline()
                continue
            else:
                temp.append(line.split())
                line = f.readline()
        logTable = pd.DataFrame(temp)
        features = generateFeature(logTable)
        
        writePath = curDir+'/features/'+\
                    logDir+str(i)+\
                    filename[filename.rfind('ex')-1:filename.rfind('.')]+'_f.csv'
        features.to_csv(writePath, index=False)
        
        
        
        
