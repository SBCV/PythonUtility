import numpy as np

from Utility.Types.Pixel import Pixel
from Utility.Classes.Frozen_Class import FrozenClass
from Utility.Logging_Extension import logger

class SegmentationInstance(FrozenClass):

    def __init__(self, occupied_pixel_mat=None, id=-1, file_name='', image_height=-1, image_width=-1,
                 dense_flag=True, predicted_flag=None):

        # private
        # TODO Replace with (sub)matrix??? + offset (nice trade of between memory and speed)
        self._occupied_pixel_mat = occupied_pixel_mat

        # public
        self.id = id
        self.file_name = file_name

        self.image_height = image_height
        self.image_width = image_width

        self.dense_flag = dense_flag
        self.predicted_flag = predicted_flag

        assert self.predicted_flag is not None

    def is_dense(self):
        return self.dense_flag

    def get_id(self):
        return self.id

    def is_occupied_pixel_mat_initialized(self):
        return self._occupied_pixel_mat is not None

    def initialize_pixel_mat(self, occupied_pixel_mask):
        assert self._occupied_pixel_mat is None
        occupied_values = occupied_pixel_mask > 0
        assert len(set(occupied_values.flatten().tolist())) > 0
        self._occupied_pixel_mat = occupied_pixel_mask

    def get_image_height(self):
        return self.image_height

    def get_image_width(self):
        return self.image_width

    def get_occupied_pixel_mat(self):
        return self._occupied_pixel_mat

    def check_pixel_mat(self, occupied_pixel_mask):
        occupied_pixel_flags = occupied_pixel_mask > 0
        unique_values = set(occupied_pixel_flags.flatten().tolist())
        if not True in unique_values:
            logger.vinfo('self.file_name', self.file_name)
            logger.vinfo('self.id', self.id)
            logger.vinfo('occupied_pixel_mask.shape', str(occupied_pixel_mask.shape))
            assert False

    def add_pixel_mat(self, occupied_pixel_mask):
        # This is a bool numpy array with the same dimenions as occupied_pixel_mask
        self.check_pixel_mat(occupied_pixel_mask)
        occupied_pixel_flags = occupied_pixel_mask > 0
        self._occupied_pixel_mat[occupied_pixel_flags] = 255

    def replace_pixel_mat(self, occupied_pixel_mat):
        assert self._occupied_pixel_mat.shape == occupied_pixel_mat.shape
        self.check_pixel_mat(occupied_pixel_mat)
        self._occupied_pixel_mat = occupied_pixel_mat

    def compute_bounding_box_using_mat(self):
        score = 1  # we do not provide score information

        xy_values = (np.argwhere(self._occupied_pixel_mat > 0)).T
        y_values = xy_values[0]
        x_values = xy_values[1]
        return min(x_values), min(y_values), max(x_values), max(y_values), score


    def compute_xy_centroid_from_mat(self):

        # FIXME
        # from scipy import ndimage
        # ndimage.measurements.center_of_mass(self._occupied_pixel_mat)

        self.check_pixel_mat(self._occupied_pixel_mat)

        centroid = np.array([0, 0], dtype=float)
        y_indices, x_indices = np.where(self._occupied_pixel_mat > 0)
        pixels = np.dstack((x_indices, y_indices))[0]
        num_pixels = pixels.shape[0]
        num_pixels_float = float(num_pixels)

        for pixel in pixels:
            centroid += pixel
        centroid *= float(1.0 / num_pixels_float)
        return centroid

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return 'Instance Segmentation: Centroid ' + str(self.compute_xy_centroid_from_mat())


    # def visualize_segmentation_instances(self, segmentation_list, figure_id=1928):
    #       TODO
    #     # assert all segmentations are defined on the same image size
    #     mat_to_visualize = np.zeros((segmentation_list[0].image_height, segmentation_list[0].image_width), dtype=int)
    #     for segmentation_index, segmentation in enumerate(segmentation_list):
    #         mat_to_visualize[segmentation.pixels_as_mask() > 0] = (segmentation.id + 1) % 255    # value 0 is background
    #         # mat_to_visualize[segmentation.pixels_as_mask() > 0] = segmentation_index + 1    # value 0 is background
    #
    #
    #     fig = plt.figure(22)    # figure_id = 22
    #     ax = fig.add_subplot(111)
    #     ax.matshow(mat_to_visualize)