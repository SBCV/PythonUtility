import os
import numpy as np
from collections import OrderedDict
import random
from Utility.File_Handler.NVM_File_Handler import NVMFileHandler
from Utility.File_Handler.PLY_File_Handler import PLYFileHandler
from Utility.Logging_Extension import logger
from Utility.Types.Point import Measurement
from Utility.Types.Enums.Sparse_Reconstruction_Type import SparseReconstructionType
from PIL import Image
from Utility.Classes.Frozen_Class import FrozenClass
from Utility.File_Handler.MVS_Colmap_FileHandler import MVSColmapFileHandler
from Utility.Types.Point import Point

class Reconstruction(FrozenClass):

    def __init__(self, cams, points, image_folder_path, sparse_reconstruction_type, h5_folder_path=None, reconstruction_file_path=None):
        """
        TODO
        :param cams:
        :param points:
        :param image_folder_path:
        :param sparse_reconstruction_type:
        """

        self.points = points
        self.camera_index_to_camera = OrderedDict([(cam.camera_index, cam) for cam in cams])
        Reconstruction.parse_camera_image_files(image_folder_path, cams)
        self.image_folder_path = image_folder_path
        self.h5_folder_path = h5_folder_path
        self.reconstruction_file_path = reconstruction_file_path

        if sparse_reconstruction_type == SparseReconstructionType.VSFM:
            Reconstruction.convert_measurement_to_image_coordinates(self.camera_index_to_camera, self.points)

        self.dense_points = None

    @classmethod
    def init_from_nvm(cls, nvm_file_path, image_folder_path, sparse_reconstruction_type, principal_point):

        cams, points = NVMFileHandler.parse_nvm_file(nvm_file_path)
        for cam in cams:
            cam.set_principal_point(principal_point)

        rec = cls(cams, points, image_folder_path, sparse_reconstruction_type)
        rec.reconstruction_file_path = nvm_file_path
        return rec

    def get_sparse_points_visible_in_camera(self, camera_index):
        return self.get_points_visible_in_camera(camera_index, self.points)

    def get_dense_points_visible_in_camera(self, camera_index):
        return self.get_points_visible_in_camera(camera_index, self.dense_points)

    def get_points_visible_in_camera(self, camera_index, points):
        visible_points = []
        for index, point in enumerate(points):
            for measurement in point.measurements:
                if measurement.camera_index == camera_index:
                    visible_points.append(point)
                    break
        return visible_points

    def get_rec_input_img_names_sorted(self):

        image_extensions = ['.JPG', '.jpg', '.PNG', '.png']

        input_image_names_sorted = []
        for current_file_name in sorted(os.listdir(self.image_folder_path)):
            ext = os.path.splitext(current_file_name)[1]
            if ext in image_extensions:
                input_image_names_sorted.append(current_file_name)
        return input_image_names_sorted

    def get_camera_with_camera_index(self, camera_index):
        return self.camera_index_to_camera[camera_index]

    def get_camera_index_to_camera(self):
        return self.camera_index_to_camera

    def get_camera_index_to_file_name(self):
        cam_idx_to_fn = {}
        for camera_index, camera in self.camera_index_to_camera.items():
            cam_idx_to_fn[camera_index] = camera.file_name
        return cam_idx_to_fn

    def get_file_name_to_camera_index(self):
        cam_idx_to_fn = self.get_camera_index_to_file_name()
        fn_to_cam_idx = {v: k for k, v in cam_idx_to_fn.items()}
        return fn_to_cam_idx

    def get_file_name_to_camera(self):
        fn_to_cam_idx = self.get_file_name_to_camera_index()
        fn_to_cam = {fn: self.camera_index_to_camera[cam_idx] for fn, cam_idx in fn_to_cam_idx.items()}
        return fn_to_cam

    def get_cameras_as_list(self):
        return self.camera_index_to_camera.values()

    def get_points(self):
        return self.points

    def set_dense_points(self, dense_points):
        assert self.dense_points is None
        self.dense_points = dense_points

    def has_dense_points(self):
        return self.dense_points is not None

    def get_dense_points(self):
        """
        Dense points contain in contrast to sparse points also a normal vector
        """
        return self.dense_points

    def remove_dense_points(self):
        self.dense_points = None

    def set_dense_points_from_colmap_mvs(self, input_path_to_mvs_colmap_file, n_th_point=2):

        logger.info('set_dense_points_from_colmap_mvs: ...')
        logger.info('The first time this may take a while')
        assert self.dense_points is None
        file_name_to_camera_id = self.get_file_name_to_camera_index()
        self.dense_points = MVSColmapFileHandler.parse_MVS_colmap_file(
            input_path_to_mvs_colmap_file,
            file_name_to_camera_id,
            n_th_point=n_th_point)
        logger.info('set_dense_points_from_colmap_mvs: Done')

    def set_dense_points_from_nvm(self, input_path_to_nvm_file):
        logger.info('set_dense_points_from_nvm: ...')
        assert self.dense_points is None
        _, self.dense_points = NVMFileHandler.parse_nvm_file(input_path_to_nvm_file)
        logger.info('set_dense_points_from_nvm: Done')

    def set_dense_points_from_ply(self, input_path_to_ply_file):
        logger.info('set_dense_points_from_ply: ...')
        assert self.dense_points is None
        dense_points, _ = PLYFileHandler.parse_ply_file(input_path_to_ply_file)
        if len(dense_points) > 0:
            self.dense_points = dense_points
        logger.info('set_dense_points_from_ply: Done')

    def update_dense_measurements_with_point_projections(self):
        """
        The measurement values (x and y image coordinates)
        provided by Colmap MVS are (currently) incorrect.
        :return:
        """
        logger.info('update_dense_measurements_with_point_projections: ...')
        self.dense_points = self.update_measurements_with_point_projections(self.dense_points)
        logger.info('update_dense_measurements_with_point_projections: Done')

    def update_sparse_measurements_with_point_projections(self):
        logger.info('update_sparse_measurements_with_point_projections: ...')
        self.points = self.update_measurements_with_point_projections(self.points)
        logger.info('update_sparse_measurements_with_point_projections: Done')

    def update_measurements_with_point_projections_debug(self,
                                                         points_background,
                                                         show_points_in_fov=False,
                                                         show_non_occluded_points=False,
                                                         debug_offset=0):

        logger.info('update_measurements_with_point_projections: ...')

        from Utility.Image.Image_Drawing_Interface import ImageDrawingInterface

        for camera_idx in sorted(self.camera_index_to_camera.keys()[debug_offset:]):
            logger.vinfo('camera_idx', camera_idx)
            camera = self.camera_index_to_camera[camera_idx]
            #camera.set_principal_point([1024, 512])
            logger.info('principal point: ' + str(camera.get_principal_point()))
            image_like_path = os.path.join(self.image_folder_path, camera.file_name)
            non_occluded_pixels = []
            for point in points_background:
                visible_camera_ids = [measurement.camera_index for measurement in point.measurements]

                if camera_idx in visible_camera_ids:
                    image_point, visible = camera.project_single_woorld_coord_into_camera_image_as_image_coord(
                        point.coord)
                    if visible:
                        non_occluded_pixels.append(image_point)

            if show_non_occluded_points:
                ImageDrawingInterface.show_pixel_positions_in_image(
                    non_occluded_pixels, image_like_path, title='non occluded points', single_color=(255, 0, 0))

            ImageDrawingInterface.show_pixel_positions_in_image(
                non_occluded_pixels, image_like_path)

    def update_measurements_with_point_projections_efficient(self, points_background_original):
        import copy
        points_background_mod = copy.deepcopy(points_background_original)
        num_invalid_projections = 0
        repr_errors = []
        for index, point in enumerate(points_background_mod):
            if not index % 10000:
                logger.vinfo('index', index)

            for measurement in point.measurements:

                camera = self.camera_index_to_camera[measurement.camera_index]
                image_point, visible = \
                    camera.project_single_woorld_coord_into_camera_image_as_image_coord(
                        point.coord)

                if visible:
                    #repr_error = camera.compute_reprojection_error_single_point(point)
                    #repr_errors.append(repr_error)

                    # Replace previous measurements and clip them if necessary
                    measurement.x = min(camera.width - 1, image_point[0])
                    measurement.y = min(camera.height - 1, image_point[1])

                else:
                    num_invalid_projections += 1

        if len(repr_errors) > 0:
            mean_repr_error = np.mean(repr_errors)
            logger.vinfo('mean_repr_error', mean_repr_error)
        logger.vinfo('num_invalid_projections', num_invalid_projections)
        return points_background_mod

    def update_measurements_with_point_projections(self, points_background_original, debug=False, debug_offset=0):

        logger.info('update_measurements_with_point_projections: ...')
        if debug:
            self.update_measurements_with_point_projections_debug(points_background_original, debug_offset=debug_offset)
            assert False
        else:
            points_background_mod = self.update_measurements_with_point_projections_efficient(
                points_background_original)

        logger.info('update_measurements_with_point_projections: Done')
        return points_background_mod


    def visualize_reconstruction(self,
                                 use_dense_points=False,
                                 use_h5_files=False,
                                 show_non_occluded_points=False,
                                 camera_index_offset=0):

        logger.info('visualize_reconstruction: ...')
        logger.vinfo('use_dense_points', use_dense_points)
        logger.vinfo('use_h5_files', use_h5_files)

        from Utility.Image.Image_Drawing_Interface import ImageDrawingInterface
        cam_index_list = self.camera_index_to_camera.keys()

        if use_dense_points:
            points = self.dense_points
        else:
            points = self.points

        if camera_index_offset >= len (cam_index_list):
            assert False    # offset too big

        for current_cam_index in cam_index_list[camera_index_offset:]:
            logger.info('current_cam_index: ' + str(current_cam_index))

            current_cam = self.camera_index_to_camera[current_cam_index]

            if use_h5_files:
                image_like_path = os.path.join(
                    self.h5_folder_path, current_cam.get_h5_file_name())
            else:
                image_like_path = os.path.join(
                    self.image_folder_path, current_cam.file_name)
                logger.vinfo('image_like_path: ', image_like_path)

            pixels_visible = []
            pixels_colors = []

            for point in points:
                for measurement in point.measurements:
                    if current_cam_index == measurement.camera_index:
                        image_point = measurement.x, measurement.y
                        pixels_visible.append(image_point)
                        pixels_colors.append(point.color)

            if show_non_occluded_points:
                ImageDrawingInterface.show_pixel_positions_in_image(
                    pixels_visible, image_like_path, title='non occluded points', colors=pixels_colors)

        logger.info('visualize_reconstruction: Done')

    def reduce_points(self, fraction=None, new_number=None):
        """ This method reduces the number of administered points
        fraction must be within (0.0, 1.0)
        """
        assert (fraction is not None) != (new_number is not None)

        if fraction is not None:
            assert 0.0 < fraction < 1.0
            new_number = int(fraction * len(self.points))

        assert 4 < new_number < len(self.points)
        random_indices = random.sample(range(len(self.points)), new_number)
        self.points = [self.points[i] for i in random_indices]

    @staticmethod
    def parse_camera_image_files(path_to_images, cameras):
        for camera in cameras:
            # this does NOT load the data into memory -> should be fast!
            image = Image.open(os.path.join(path_to_images, camera.file_name))
            camera.width, camera.height = image.size

    @staticmethod
    def convert_measurement_to_image_coordinates(camera_index_to_camera, points):
        logger.info('convert_measurement_to_image_coordinates: ...')
        if points is not None and len(points) > 0:
            if not points[0].measurements[0].x_y_are_image_coords:
                logger.info('Conversion of measurements are necessary!')

                for point in points:
                    for measurement in point.measurements:
                        if not measurement.x_y_are_image_coords:
                            measurement.x += camera_index_to_camera[measurement.camera_index].width / 2
                            measurement.y += camera_index_to_camera[measurement.camera_index].height / 2
                            measurement.x_y_are_image_coords = True
                        else:
                            assert False
            else:
                logger.info('No conversion of measurements necessary.')
        logger.info('convert_measurement_to_image_coordinates: Done')


    @staticmethod
    def compute_reprojection_errors(cams, points,
                                    image_path,
                                    max_allowed_mean_projection_error_in_pix,
                                    sparse_reconstruction_type):
        """
        All points with a measurement in a certain image must be visible in the corresponding image
        :param cams:
        :param points:
        :return:
        """
        logger.info('verify_cams_and_points: ...')
        rec = Reconstruction(cams, points, image_path, sparse_reconstruction_type)
        logger.vinfo('len(points)', len(points))
        repr_errors = []
        for iteration, point in enumerate(points):

            for measurement in point.measurements:

                cam = rec.get_camera_with_camera_index(measurement.camera_index)
                repro_error = cam.compute_reprojection_error_single_point(point)
                repr_errors.append(repro_error)

        logger.vinfo('max_repr_error', max(repr_errors))
        mean_repr_error = np.mean(repr_errors)
        logger.vinfo('mean_repr_error', mean_repr_error)
        assert mean_repr_error < max_allowed_mean_projection_error_in_pix
        logger.info('verify_cams_and_points: Done')


if __name__ == '__main__':
    colmap_image_path = '/home/sebastian/Desktop/temp/filtered/images_filtered'
    cams_colmap, points_colmap = NVMFileHandler.parse_nvm_file('/home/sebastian/Desktop/temp/filtered/test_without_radial.nvm')

    Reconstruction.compute_reprojection_errors(cams_colmap, points_colmap, colmap_image_path)