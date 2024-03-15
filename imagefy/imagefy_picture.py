"""
imagefy_picture.py : class for the processing of the picture.
"""
from datetime import datetime
from multiprocessing import Lock
import os
import threading
from typing import List
import cv2
from cv2 import dnn_superres
import requests
from imagefy.imagefy import IMagefy
import tensorflow as tf
import numpy as np
import transformers
import tensorflow as tf
from tensorflow import image
from glob import glob
from tensorflow import keras
import keras
from keras import layers
from keras.models import load_model
from PIL import Image
import numpy as np
from huggingface_hub import from_pretrained_keras


class PictureData:
    """ PictureData is the storage class of data of the picture """

    def __init__(self, path: str, height: int, width: int) -> None:
        """ class constructor """
        self.path = path
        self.height = height
        self.width = width


class IMagefyPicture(IMagefy):
    """ IMagefyPicture is the processing class of the picture  """

    DOWNLOAD_FOLDER = "static/img/downloads/"
    GENERATED_FOLDER = "static/img/generated/"

    def __init__(self) -> None:
        """ class constructor """
        self.current_index = 0
        self.original_picture = None
        self.pictures: List[PictureData] = list()
        # Initialize the list of 5 pictures(original + 3 zoomed + 1 low-light-enhanced)
        for _ in range(5):
            self.pictures.append(PictureData("", 0, 0))

    def __download_url_content(self, response: requests.Response, file_extension: str):
        """ download the content of the URL"""
        current_datetime = datetime.now()
        # As original file name can be unreliable, file name is built with the current datetime
        file_path = self.DOWNLOAD_FOLDER + \
            current_datetime.strftime("%Y_%m_%d_%H_%M_%S") + file_extension
        open(file_path, 'xb').write(response.content)
        return file_path

    def __generate_pictures(self):
        """ generate the pictures of the 3 models """
        mutex = threading.Lock()
        x2_picture_thread = threading.Thread(target=self.__process_picture, args=(
            self.EDSR_MODEL_X2_PATH, mutex, 1))
        x3_picture_thread = threading.Thread(target=self.__process_picture, args=(
            self.EDSR_MODEL_X3_PATH, mutex, 2))
        x4_picture_thread = threading.Thread(target=self.__process_picture, args=(
            self.EDSR_MODEL_X4_PATH, mutex, 3))
        low_light_picture_thread = threading.Thread(target=self.__process_low_light_picture, args=(
            mutex, 4))
        x2_picture_thread.start()
        x3_picture_thread.start()
        x4_picture_thread.start()
        low_light_picture_thread.start()
        x2_picture_thread.join()
        x3_picture_thread.join()
        x4_picture_thread.join()
        low_light_picture_thread.join()
        
    # def post_process(self, image, output):
    #     # from zero_dce post process
    #     r1 = output[:, :, :, :3]
    #     r2 = output[:, :, :, 3:6]
    #     r3 = output[:, :, :, 6:9]
    #     r4 = output[:, :, :, 9:12]
    #     r5 = output[:, :, :, 12:15]
    #     r6 = output[:, :, :, 15:18]
    #     r7 = output[:, :, :, 18:21]
    #     r8 = output[:, :, :, 21:24]
    #     x = image + r1 * (tf.square(image) - image)
    #     x = x + r2 * (tf.square(x) - x)
    #     enhanced_img = x + r4 * (tf.square(x) - x)
    #     x = enhanced_img + r5 * (tf.square(enhanced_img) - enhanced_img)
    #     x = x + r6 * (tf.square(x) - x)
    #     x = x + r7 * (tf.square(x) - x)
    #     enhanced_img = x + r8 * (tf.square(x) - x)
    #     return enhanced_img


    def __process_low_light_picture(self, mutex: Lock,  index: int):
        """ thread which generates a picture by calling the model """        
        
        # model = from_pretrained_keras("keras-io/low-light-image-enhancement", compile=False)
        path = "C:\\Users\\Uday Prasad\\.cache\\huggingface\\hub\\models--keras-io--low-light-image-enhancement\\snapshots\\b15aa894233ca043793c2e110490fef138f02497"
        model = keras.layers.TFSMLayer(path, call_endpoint='serving_default')
        
        mutex.acquire()
        file_path = self.pictures[0].path
        mutex.release()
        file_name = os.path.basename(file_path)
        file_name, _ = os.path.splitext(file_name)
        orig = Image.open(file_path)
        
        image = keras.preprocessing.image.img_to_array(orig)
        print(image)
        image = image.astype("float32") / 255.0 
        print(image)
        image = np.expand_dims(image, axis=0) # create batch of 1 image
        temp = image
        print(image)
        output_image = model(image) # run the image through model
        print(output_image['conv2d_20'].numpy())
        output_image = output_image['conv2d_20'].numpy()
        
        # from zero_dce post process
        r1 = output_image[:, :, :, 0:3]
        r2 = output_image[:, :, :, 3:6]
        r3 = output_image[:, :, :, 6:9]
        r4 = output_image[:, :, :, 9:12]
        r5 = output_image[:, :, :, 12:15]
        r6 = output_image[:, :, :, 15:18]
        r7 = output_image[:, :, :, 18:21]
        r8 = output_image[:, :, :, 21:24]
        x = temp + r1 * (tf.square(temp) - temp)
        x = x + r2 * (tf.square(x) - x)
        enhanced_img = x + r4 * (tf.square(x) - x)
        x = enhanced_img + r5 * (tf.square(enhanced_img) - enhanced_img)
        x = x + r6 * (tf.square(x) - x)
        x = x + r7 * (tf.square(x) - x)
        enhanced_img = x + r8 * (tf.square(x) - x)
        
        output_image = enhanced_img # will implement this later
        output_image = tf.cast((output_image[0, :, :, :] * 255), dtype=np.uint8) # processing for PIL.Image
        output_image = output_image.numpy()
        print("output image")
        print(output_image)
        # output_image = Image.fromarray(output_image.numpy())
        
        height, width, _= output_image.shape
        print(height, width)
        new_file_path = self.GENERATED_FOLDER + \
            file_name+"_low_light_enhanced"+".png"
        cv2.imwrite(new_file_path, output_image)
        mutex.acquire()
        self.pictures[index] = PictureData(new_file_path, height, width)
        print(new_file_path + "saved!")
        mutex.release()

    def __get_shape(self, index: int):
        """ return a string with shape data """
        picture_data = self.pictures[index]
        return "Height : " + str(picture_data.height) + " px X Width : " + str(picture_data.width) + " px"

    def __get_url(self, url: str):
        """ do a GET request on the URL """
        response = requests.get(url, allow_redirects=True)
        _, file_extension = os.path.splitext(url)
        return response, file_extension

    def __process_picture(self, model_path: str, mutex: Lock, index: int):
        """ thread which generates a picture by calling the model """
        # Create an SR object
        super_res = dnn_superres.DnnSuperResImpl_create()
        # Get the model name
        model_type = model_path.split("/")[2].lower()
        base_name = os.path.basename(model_path)
        model_name, _ = os.path.splitext(base_name)
        # Get the model scale
        model_scale = int(model_name.split("x")[1])
        # The mutex permits to access with safe our list of pictures
        mutex.acquire()
        file_path = self.pictures[0].path
        mutex.release()
        file_name = os.path.basename(file_path)
        file_name, _ = os.path.splitext(file_name)
        # Read the desired model
        super_res.readModel(model_path)
        # Set CUDA backend and target to enable GPU inference, one day !
        # super_res.setPreferableBackend(cv2.dnn.DNN_BACKEND_CUDA)
        # super_res.setPreferableTarget(cv2.dnn.DNN_BACKEND_CUDA)
        # Configure the model
        super_res.setModel(model_type, model_scale)
        # Process the picture
        generated_picture = super_res.upsample(self.original_picture)
        height, width, _ = generated_picture.shape
        # Save the picture
        new_file_path = self.GENERATED_FOLDER + \
            file_name+"_x"+str(model_scale)+".png"
        cv2.imwrite(new_file_path, generated_picture)
        mutex.acquire()
        self.pictures[index] = PictureData(new_file_path, height, width)        
        print(new_file_path + "saved!")
        mutex.release()

    def __validate_file(self, path: str):
        """ validate if the file in input is a picture """
        file_extension_list = [".png", ".jpg", ".jpeg"]
        _, file_extension = os.path.splitext(path)
        try:
            file_extension_list.index(file_extension)
        except ValueError:
            # ValueError means that the file extension found isn't in our list
            return False
        mat = cv2.imread(path)
        height, width, colors = mat.shape
        if height > 0 and width > 0 and colors == 3:
            # picture is valid if we have an height and width greater than 0 and 3 color channels
            self.original_picture = mat
            # store the picture in the list
            self.pictures[0] = PictureData(path, height, width)
            return True
        else:
            return False

    def get_picture_data(self, index: int):
        """ return a tuple with path and shape data """
        # update the current index with new index from slider
        self.current_index = index
        picture_data = self.pictures[index]
        low_light_picture_data = self.pictures[4]
        return picture_data.path, low_light_picture_data.path,self.__get_shape(index)

    def process_url(self, url: str):
        self.pictures = []
        for _ in range(5):
            self.pictures.append(PictureData("", 0, 0))
        """ process the URL """
        response, file_extension = self.__get_url(url)
        if response.status_code == 200:
            # status code 200 is OK
            file_path = self.__download_url_content(response, file_extension)
            res = self.__validate_file(file_path)
            if res:
                self.__generate_pictures()
                return self.get_picture_data(self.current_index)
            else:
                # if picture is invalid, remove file from disk
                os.remove(file_path)
                return "", "error picture is invalid !"
        else:
            return "", "error "+str(response.status_code)
        
    def process_saved_image(self, saved_file_path):
        self.pictures = []
        for _ in range(5):
            self.pictures.append(PictureData("", 0, 0))
        res = self.__validate_file(saved_file_path)
        if res:
            self.__generate_pictures()
        return self.get_picture_data(self.current_index)