from keras.layers import Input, Dense
from keras.models import Model
from sklearn.cross_validation import train_test_split
from sklearn.preprocessing import MinMaxScaler
import pandas as pd
import numpy as np
import pickle

# load features for training
featureDim = ['hitCount', 'GETcount', 'POSTcount', 'HEADcount', '3xxCount', '4xxCount', 
              'hjRatio']

train = pd.DataFrame()
for i in range(1,4):
    for j in range(13,22):
        filename = './features/web'+str(i)+'_ex1610'+str(j)+'_f.csv'
        temp = pd.read_csv(filename)
        train = pd.concat([train, temp])

train = train[featureDim].as_matrix()
scaler = MinMaxScaler()
train = scaler.fit_transform(train)
x_train, x_test = train_test_split(train, test_size=0.05)

pickle.dump(scaler, open('scaler.sav', 'wb'))


# deep autoencoder network definition
input_img = Input(shape=(7,))
encoded  = Dense(6, activation='relu')(input_img)
encoded1 = Dense(5, activation='relu')(encoded)
encoded2 = Dense(4, activation='relu')(encoded1)

decoded  = Dense(5, activation='relu')(encoded2)
decoded1 = Dense(6, activation='relu')(decoded)
decoded2 = Dense(7, activation='sigmoid')(decoded1)

autoencoder = Model(input=input_img, output=decoded2)

# compile the model
autoencoder.compile(optimizer='sgd', loss='binary_crossentropy')

# training
autoencoder.fit(x_train, x_train,
                nb_epoch=500,
                batch_size=256,
                shuffle=True,
                validation_data=(x_test, x_test))

# extract the encode part
encoder = Model(input=input_img, output=encoded2)
encoded_imgs = encoder.predict(x_test)

# save encode model
encoder.save('encodeModel.h5')

temp = encoder.predict(x_train)


#from sklearn.manifold import TSNE
#import matplotlib.pyplot as plt
#model = TSNE(n_components=2, random_state=0)
#t = model.fit_transform(x_train[1:500]) 
#plt.scatter(t[:,0], t[:, 1])
#
#plt.scatter(encoded_imgs[:,0], encoded_imgs[:, 1])
#
#t2 = model.fit(x_train[250:500])



# Kmeans
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
kmeans = KMeans(n_clusters=2).fit(temp)
pickle.dump(kmeans, open('km.sav', 'wb'))
#plt.scatter(temp[:,0], temp[:, 1], c=['g','r'])