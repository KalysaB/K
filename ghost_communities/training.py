import pandas as pd
import os
import random
from PIL import Image
from sklearn.model_selection import train_test_split

# Define file paths
data_dir = 'data/training_data'
filename_data = data_dir + '/data.csv'
filename_train = data_dir + '/data_train.csv'
filename_test = data_dir + '/data_test.csv'

# Open data.csv
with open(filename_data, 'w') as file:
            file.write("r,g,b,class\n")

# Read through folders 1 to 7 and read through all pixels
for dir in os.listdir(data_dir):
    image_dir = os.path.join(data_dir, dir)
    if os.path.isdir(image_dir):
        print("Reading training data from", image_dir)
        # Write image pixel data to a CSV file
        with open(filename_data, 'a') as file:
            for image_name in os.listdir(image_dir):
                # Load image
                if not image_name.startswith('.'):
                    image_path = os.path.join(image_dir, image_name)
                    image = Image.open(image_path)
                    image_rgb = image.convert("RGB")

                    # Extracting width and height of the image
                    width, height = image.width, image.height

                    for x in range(1, width):
                        for y in range(1, height):
                            r, g, b = image_rgb.getpixel((x, y))
                            c = str(r) + "," + str(g) + "," + str(b) + "," + str(dir) + "\n"
                            file.write(c)
        print("Complete!")

# Remove duplicates from the data
data = pd.read_csv(filename_data)
data = data.drop_duplicates()
data = data.sort_values(by=['class'])
data.to_csv(filename_data, index=False)
print("Training data size by class")
print(data['class'].value_counts())

# Split the data into train and test datasets
train, test = train_test_split(data, test_size=0.1)
train.to_csv(filename_train, index=False)
test.to_csv(filename_test, index=False)