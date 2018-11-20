# also pycharm highlights that OpenEXR is not found it is there
import OpenEXR, Imath

from Utility.Logging_Extension import logger
import matplotlib.pyplot as plt
import numpy as np

class EXRFileHandler(object):

    # http://excamera.com/articles/26/doc/intro.html
        # See: Interfacing with other packages

    @staticmethod
    def parse_optical_flow_exr_file(path_to_exr_file):

        logger.info('parse_optical_flow_exr_file: ...')
        logger.vinfo('path_to_exr_file', path_to_exr_file)

        pt = Imath.PixelType(Imath.PixelType.FLOAT)
        exr_file = OpenEXR.InputFile(path_to_exr_file)

        # To examine the content of the exr file use:
        logger.vinfo('exr_file.header()', exr_file.header())

        dw = exr_file.header()['dataWindow']

        size = (dw.max.x - dw.min.x + 1, dw.max.y - dw.min.y + 1)
        logger.vinfo('size', size)

        red_channel_str = exr_file.channel('R', pt)
        red_exr_data_as_np = np.fromstring(red_channel_str, dtype=np.float32)
        red_exr_data_as_np.shape = (size[1], size[0])  # Numpy arrays are (row, col)

        green_channel_str = exr_file.channel('G', pt)
        green_exr_data_as_np = np.fromstring(green_channel_str, dtype=np.float32)
        green_exr_data_as_np.shape = (size[1], size[0])  # Numpy arrays are (row, col)

        exr_data_as_np = np.dstack((red_exr_data_as_np, green_exr_data_as_np))

        logger.vinfo('shape', exr_data_as_np.shape)

        logger.info('parse_optical_flow_exr_file: Done')
        return exr_data_as_np

    @staticmethod
    def parse_depth_exr_file(path_to_exr_file):

        logger.info('parse_depth_exr_file: ...')
        logger.vinfo('path_to_exr_file', path_to_exr_file)

        pt = Imath.PixelType(Imath.PixelType.FLOAT)
        exr_file = OpenEXR.InputFile(path_to_exr_file)

        # To examine the content of the exr file use:
        # logger.vinfo('exr_file.header()', exr_file.header())

        dw = exr_file.header()['dataWindow']
        size = (dw.max.x - dw.min.x + 1, dw.max.y - dw.min.y + 1)
        red_channel_str = exr_file.channel('R', pt)
        exr_data_as_np = np.fromstring(red_channel_str, dtype=np.float32)
        exr_data_as_np.shape = (size[1], size[0])  # Numpy arrays are (row, col)
        logger.info('parse_depth_exr_file: Done')
        return exr_data_as_np

    @staticmethod
    def view_depth_exr_file(path_to_exr_file):
        exr_data_as_np = EXRFileHandler.parse_depth_exr_file(path_to_exr_file)
        plt.matshow(exr_data_as_np, cmap=plt.cm.binary)
        plt.show()

