import numpy as np
import pandas as pd
from sklearn import svm
import os
import rasterio
from matplotlib import pyplot
from PIL import Image
import cv2
from sklearn.metrics import classification_report, confusion_matrix, ConfusionMatrixDisplay

# Specifying the file path for the training data and testing data
data_dir = 'data/training_data'
filename_train = data_dir + '/data_train.csv'
filename_test = data_dir + '/data_test.csv'

# Reading the training data into a DataFrame
train = pd.read_csv(filename_train)

# Extracting RGB values for training features
X_train = train[['r', 'g', 'b']]

# Extracting the target variable for training
y_train = train[['class']]

# Creating and training an SVM classifier
clf = svm.SVC()
clf.fit(X_train, y_train.values.ravel());

test = pd.read_csv(filename_test)

X_test = test[['r','g','b']]
y_test = test[['class']]

y_pred = clf.predict(X_test)

cm = confusion_matrix(y_test, y_pred)
disp = ConfusionMatrixDisplay(confusion_matrix=cm,
                              display_labels=clf.classes_)
disp.plot()

print(classification_report(y_test, y_pred))
# Defining a list of colors corresponding to different classes
colors = [(255, 255, 255), (255, 0, 0), (255, 255, 0), (128, 128, 0), (192, 192, 192), (0, 255, 255), (0, 0, 0)]

# Setting the directory containing image files
image_dir = "data/maps/chicago"

# Iterating through image files in the specified directory
for image_name in os.listdir(image_dir):
    # Checking if the file has a .tif extension
    if image_name.endswith(".tif"):

        print("Reading in ", image_name)
        
        # Constructing the full path to the image file
        image_path = os.path.join(image_dir, image_name)
        
        # Opening the raster image using rasterio
        image = rasterio.open(image_path)
        image_meta = image.profile
        image_crs = image.crs
        # Modifying image metadata
        image_meta['nodata'] = 1
        image_meta['count'] = 3

        # Extracting width and height of the image
        width, height = image.width, image.height
        print("Image size:", width, "*", height)

        # Reading the image array
        image_array = image.read()

        # Creating a DataFrame for prediction input
        X_pred = pd.DataFrame({'r': image_array[0,:,:].reshape(-1), 'g': image_array[1,:,:].reshape(-1), 'b': image_array[2,:,:].reshape(-1)})
        
        # Making predictions using the pre-trained classifier (clf)
        class_pred = clf.predict(X_pred)
        class_pred = np.reshape(class_pred, (height, width))

        # Writing the predicted classes to a new raster image
        with rasterio.open(os.path.join('data/1_predicted', image_name.split('.')[0] + '_predicted.tif'), 'w', **image_meta) as new_image:
            new_image.write(class_pred.astype(np.uint8), 1)

        # Displaying the predicted classes using pyplot
        pyplot.imshow(class_pred, cmap='pink')
        pyplot.show() 

        # Creating a new RGB image based on predicted classes and saving it as a JPEG
        new_image_rgb = Image.new('RGB', (width, height))
        for x in range(width):
            for y in range(height):
                label = class_pred[y, x]
                new_image_rgb.putpixel((x, y), colors[label - 1])
        new_image_rgb.save(os.path.join('data/1_predicted', image_name.split('.')[0] + '_predicted.jpg'))