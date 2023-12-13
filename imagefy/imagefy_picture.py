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
        # Initialize the list of 4 pictures(original + 3 zoomed)
        for _ in range(4):
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
        x2_picture_thread.start()
        x3_picture_thread.start()
        x4_picture_thread.start()
        x2_picture_thread.join()
        x3_picture_thread.join()
        x4_picture_thread.join()

    def __get_shape(self, index: int):
        """ return a string with shape data """
        picture_data = self.pictures[index]
        return "height : " + str(picture_data.height) + " px X width : " + str(picture_data.width) + " px"

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
            file_name+"_x"+str(model_scale)+".jpg"
        cv2.imwrite(new_file_path, generated_picture)
        mutex.acquire()
        self.pictures[index] = PictureData(new_file_path, height, width)
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
        return picture_data.path, self.__get_shape(index)

    def process_url(self, url: str):
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
