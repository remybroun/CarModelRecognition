import os
import pandas as pd
from sklearn.model_selection import train_test_split
from keras.utils import to_categorical
from keras.models import Sequential
from keras.layers import *
from keras.optimizers import *
import matplotlib.pyplot as plt
import cv2
from tqdm import tqdm
import numpy as np

# def create_train_test():



def create_categories_csv():
    path = "./images/"
    brands = os.listdir(path)
    brands.remove(".DS_Store")
    DF = pd.DataFrame(columns=["Category", "Path"])
    for brand in brands:
        for model in os.listdir(str(path + brand)):
            if model != ".DS_Store":
                for image in os.listdir(str(path + brand + '/' + model)):
                    DF = DF.append({"Category": model, "Path": path + brand + '/' + model + '/' + image}, ignore_index=True)
    return DF

def one_hot_label(label):
    return to_categorical(label, num_classes=num_classes)



DF = create_categories_csv()
DF = DF.sample(frac=1).reset_index(drop=True)
xTrain, xTest, train_image_path, test_image_path = train_test_split(DF["Category"].values, DF["Path"].values, test_size=0.2)

print(type(xTrain), type(train_image_path))
cats = set(DF["Category"])
cat_to_index = dict((c, i) for i, c in enumerate(cats))
index_to_cat = dict((i, c) for i, c in enumerate(cats))

num_classes = len(cat_to_index)
print(cat_to_index)
train_images = []
test_images = []

for index, path in tqdm(np.ndenumerate(train_image_path)):
    img = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
    img = cv2.resize(img, (256, 256))
    train_images.append([np.array(img), one_hot_label(cat_to_index[DF["Category"][index[0]]])])

for index, path in tqdm(np.ndenumerate(test_image_path)):
    img = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
    img = cv2.resize(img, (256, 256))
    test_images.append([np.array(img), one_hot_label(cat_to_index[DF["Category"][index[0]]])])


tr_img_data = np.array([i[0] for i in train_images]).reshape(-1, 256, 256, 1)
tst_img_data = np.array([i[0] for i in test_images]).reshape(-1, 256, 256, 1)
tr_lbl_data = np.array([i[1] for i in train_images])
tst_lbl_data = np.array([i[1] for i in test_images])




model = Sequential()
model.add(InputLayer(input_shape=[256, 256, 1]))

model.add(Conv2D(filters=32, kernel_size=5, strides=1, padding='same', activation='relu'))
model.add(MaxPool2D(pool_size=5, padding='same'))

model.add(Conv2D(filters=50, kernel_size=5, strides=1, padding='same', activation='relu'))
model.add(MaxPool2D(pool_size=5, padding='same'))

model.add(Conv2D(filters=80, kernel_size=5, strides=1, padding='same', activation='relu'))
model.add(MaxPool2D(pool_size=5, padding='same'))

model.add(Dropout(0.25))
model.add(Flatten())
model.add(Dense(512, activation='relu'))
model.add(Dropout(0.5))
model.add(Dense(num_classes, activation='softmax'))
optimizer = Adam(lr=1e-3)
model.compile(loss='categorical_crossentropy', optimizer=optimizer, metrics=['accuracy'])
model.fit(tr_img_data, y=tr_lbl_data, epochs=10, batch_size=10)
model.summary()
model.save('cars_model.h5')
fig = plt.figure()

for cnt, data in enumerate(test_images[10:20]):
    y = fig.add_subplot(2, 5, cnt+1)
    img = data[0]
    data = img.reshape(1, 256, 256, 1)
    model_out = model.predict([data])
    label = index_to_cat[np.argmax(model_out)]
    y.imshow(img, cmap='gray')
    plt.title(label)
    y.axes.get_xaxis().set_visible(False)
    y.axes.get_yaxis().set_visible(False)

plt.show()


