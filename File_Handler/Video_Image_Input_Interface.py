import os
import cv2
from Utility.Logging_Extension import logger


class VideoImageInputInterface:
    # can read input videos or image folders
    def __init__(self, path_to_input):

        self.current_image_index = 0

        # check for video file
        if os.path.isfile(path_to_input):
            self.mode = 'VIDEO'
            self.cap = cv2.VideoCapture(path_to_input)

        elif os.path.isdir(path_to_input):
            self.mode = 'IMAGES'
            self.file_paths = [
                os.path.join(path_to_input, file_name)
                for file_name in os.listdir(path_to_input)
                if os.path.isfile(os.path.join(path_to_input, file_name))]
            print(self.file_paths)

        else:
            assert False

    def read_next_image_as_gray_scale(self):
        gray_image = None
        current_image_name = None
        if self.mode == 'VIDEO':
            # cap.read() returns None if there are no more frames left
            ret, bgr_image = self.cap.read()
            if bgr_image is not None:
                gray_image = cv2.cvtColor(bgr_image, cv2.COLOR_BGR2GRAY)
                current_image_name = str(self.current_image_index)
                self.current_image_index += 1
        elif self.mode == 'IMAGES':
            if self.file_paths: # check that the list is not empty
                current_image_path = self.file_paths.pop(0)
                bgr_image = cv2.imread(current_image_path, cv2.IMREAD_COLOR)
                if bgr_image is not None:
                    gray_image = cv2.cvtColor(bgr_image, cv2.COLOR_BGR2GRAY)
                current_image_name = os.path.basename(current_image_path)
        else:
            assert False

        return gray_image, current_image_name

    def release(self):
        if self.mode == 'VIDEO':
            self.cap.release()

    @staticmethod
    def read_image_from_path_as_gray_scale(path_to_image):
        gray_image = None
        bgr_image = cv2.imread(path_to_image, cv2.IMREAD_COLOR)
        if bgr_image is not None:
            gray_image = cv2.cvtColor(bgr_image, cv2.COLOR_BGR2GRAY)
        return gray_image


    @staticmethod
    def read_image_from_path_as_rgb(path_to_image):
        if not os.path.isfile(path_to_image):
            logger.vinfo('path_to_image', path_to_image)
            assert False
        grb_image = None
        bgr_image = cv2.imread(path_to_image, cv2.IMREAD_COLOR)
        if bgr_image is not None:
            grb_image = cv2.cvtColor(bgr_image, cv2.COLOR_BGR2RGB)
        return grb_image

