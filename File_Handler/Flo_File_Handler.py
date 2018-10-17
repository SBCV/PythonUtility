import cv2
import numpy as np
from Utility.Logging_Extension import logger
from Thesis.Matches_And_Optical_Flow.Optical_Flow_Vizualizer import OpticalFlowVisualizer

class FloFileHandler:

    @staticmethod
    def parse_flo_file(path_to_flo_file):

        # https://stackoverflow.com/questions/28013200/reading-middlebury-flow-files-with-python-bytes-array-numpy

        data_2d = None
        # WARNING: this will work on little-endian architectures (e.g. Intel x86) only!
        with open(path_to_flo_file, 'rb') as f:
            magic = np.fromfile(f, np.float32, count=1)
            if 202021.25 != magic:
                logger.error('Magic number incorrect. Invalid .flo file')
            else:
                w = np.fromfile(f, np.int32, count=1)[0]
                h = np.fromfile(f, np.int32, count=1)[0]
                # print('Reading %d x %d flo file' % (w, h))
                data = np.fromfile(f, np.float32, count=2 * w * h)
                # Reshape data into 3D array (columns, rows, bands)
                data_2d = np.resize(data, (h, w, 2))
        return data_2d

    @staticmethod
    def write_flo_visualization_file(flo_ifp, viz_ofp):
        flow_data = FloFileHandler.parse_flo_file(flo_ifp)
        bgr_flow_image_1 = OpticalFlowVisualizer.convert_flow_mat_to_opencv_image(flow_data, color_coding='BGR')
        cv2.imwrite(viz_ofp, bgr_flow_image_1)


if __name__ == '__main__':

    flo_ifp = '.flo'
    viz_ofp = '.png'

    FloFileHandler.write_flo_visualization_file(
        flo_ifp, viz_ofp)