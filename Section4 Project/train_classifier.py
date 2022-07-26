from keras.callbacks import CSVLogger, ModelCheckpoint, EarlyStopping
from keras.callbacks import ReduceLROnPlateau
from keras.preprocessing.image import ImageDataGenerator
from load_preprocess import prepare_data
from load_preprocess import augmentation
from models.cnn import cnn
from models.cnn import fine_tunning
from tensorflow.keras.utils import to_categorical

import pandas as pd


# parameters
batch_size = 64
num_epochs = 30
input_shape = (48, 48, 1)
validation_split = .2
verbose = 1
num_classes = 7
patience = 3
base_path = 'models/'



    # callbacks
early_stop = EarlyStopping('val_accuracy', patience=patience, verbose=verbose, restore_best_weights=True)
trained_models_path = base_path + '_cnn'
model_names = trained_models_path + '.{epoch:02d}-{val_accuracy:.2f}.hdf5'
model_checkpoint = ModelCheckpoint(model_names, monitor='val_accuracy', verbose=1,
                                                    save_best_only=True, mode='max')
callbacks = [model_checkpoint, early_stop]

# loading dataset
dataset_path = 'data/data/icml_face_data.csv'
data = pd.read_csv(dataset_path)

class_weight = dict(zip(range(0, 7), (((data[data[' Usage']=='Training']['emotion'].value_counts()).sort_index())/len(data[data[' Usage']=='Training']['emotion'])).tolist()))


xtrain, ytrain = prepare_data(data[data[' Usage']=='Training'])
print("이미지 증강 전 train 데어터 셋 형태")
print(xtrain.shape, ytrain.shape, '\n')
xtrain, ytrain = augmentation(data, xtrain, ytrain)
print("이미지 증강 후 train 데이터 셋 형태")
print(xtrain.shape, ytrain.shape)
xval, yval = prepare_data(data[data[' Usage']=='PublicTest'])
xtest, ytest = prepare_data(data[data[' Usage']=='PrivateTest'])

xtrain = xtrain.reshape((xtrain.shape[0], 48, 48, 1))
xtrain = xtrain.astype('float32')/255
xval = xval.reshape((xval.shape[0], 48, 48, 1))
xval = xval.astype('float32')/255
xtest = xtest.reshape((xtest.shape[0], 48, 48, 1))
xtest = xtest.astype('float32')/255

ytrain = to_categorical(ytrain)
yval = to_categorical(yval)
ytest = to_categorical(ytest)

model = cnn(input_shape, num_classes)
model.fit(
    xtrain, ytrain, 
    validation_data=(xval, yval),
    class_weight=class_weight,
    epochs=num_epochs,  
    callbacks=early_stop
    )


model = fine_tunning(model)
model.fit(
    xtrain, ytrain, 
    validation_data=(xval, yval),
    class_weight=class_weight,
    epochs=20,  
    callbacks=callbacks
    )

test_loss, test_acc = model.evaluate(xtest, ytest)
print('test acc: ', test_acc)