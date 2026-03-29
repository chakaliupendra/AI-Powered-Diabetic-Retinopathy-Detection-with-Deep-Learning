from django.shortcuts import render
from tensorflow.keras.preprocessing import image
from tensorflow.keras.preprocessing.image import ImageDataGenerator
import joblib
from keras.models import Sequential
from keras.layers import Convolution2D
from keras.layers import MaxPooling2D
from keras.layers import Flatten
from keras.layers import Dense
from keras.layers import Dropout
from tensorflow.keras.optimizers import Adam
import os

# Create your views here.
def adminlogin(request):
    return render(request, "AdminApp/Login.html")


def logaction(request):
    name = request.POST.get('username')
    apass = request.POST.get('password')
    if name == 'Admin' and apass == 'Admin':
        return render(request, "AdminApp/AdminHome.html")
    else:
        context = {'data': "Admin Login Failed..!!"}
        return render(request, "AdminApp/Login.html", context)


def AdminHome(request):
    return render(request, "AdminApp/AdminHome.html")


global dataset


def UploadDataset(request):
    global dataset

    dataset = "dataset\\"
    context = {'data':"Dataset Uploaded Successfully...!!"}
    return render(request, "AdminApp/AdminHome.html", context)


global train_generator, validation_generator


def Preprocess(request):

    global train_generator, validation_generator
    train_datagen = ImageDataGenerator(shear_range=0.1, zoom_range=0.1, horizontal_flip=True)
    test_datagen = ImageDataGenerator()
    train_generator = train_datagen.flow_from_directory("dataset",
                                                    target_size=(48, 48),
                                                    batch_size=32,
                                                    class_mode='categorical',
                                                    )
    validation_generator = test_datagen.flow_from_directory("dataset",
                                                        target_size=(48, 48),
                                                        batch_size=32,
                                                        class_mode='categorical',
                                                         )
    # Get the number of images in the training set
    num_train_samples = len(train_generator.filenames)

    # Get the number of images in the validation set
    num_validation_samples = len(validation_generator.filenames)
    total=num_train_samples

    context = {'data': total, 'train':num_train_samples, 'validation':num_validation_samples}
    return render(request, 'AdminApp/Preprocess.html', context)




global annacc, model


def runCNN(request):
    global classifier
    if os.path.exists("model\\retinopathy_model.h5"):
        classifier = Sequential()
        classifier.add(Convolution2D(32, kernel_size=(3, 3), activation='relu', input_shape=(48, 48, 3)))
        classifier.add(MaxPooling2D((2, 2)))
        classifier.add(Convolution2D(32, kernel_size=(3, 3), activation='relu'))
        classifier.add(MaxPooling2D((2, 2)))
        classifier.add(Flatten())
        classifier.add(Dense(activation="relu", units=128))
        classifier.add(Dense(activation="softmax", units=4))
        classifier.load_weights('model\\retinopathy_model.h5')
        context = {"data": "CNN Model Loaded Successfully.."}
        return render(request, 'AdminApp/AdminHome.html', context)
    else:
        classifier = Sequential()
        classifier.add(Convolution2D(32, kernel_size=(3, 3), activation='relu', input_shape=(48, 48, 3)))
        classifier.add(MaxPooling2D((2, 2)))
        classifier.add(Convolution2D(32, kernel_size=(3, 3), activation='relu'))
        classifier.add(MaxPooling2D((2, 2)))
        classifier.add(Flatten())
        classifier.add(Dense(activation="relu", units=128))
        classifier.add(Dense(activation="softmax", units=4))
        classifier.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
        history = classifier.fit_generator(train_generator,
                              steps_per_epoch=125,
                              epochs=60,
                              validation_data=validation_generator,
                              validation_steps=125)
        classifier.save_weights('model/retinopathy_model.h5')
        final_val_accuracy = history.history['accuracy'][-1]
        msg=f'Final Accuracy: {final_val_accuracy:.4f}'
        context = {"data": "CNN Model Generated Successfully..","acc":msg}
        return render(request, 'AdminApp/Algorithms.html', context)


