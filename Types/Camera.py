__author__ = 'sebastian'

import os
import copy
import numpy as np
import math
from Utility.Logging_Extension import logger
from Utility.Types.Coordinate_Frame_System import CoordinateFrameSystem
from Utility.Types.Ray import Ray


class Camera(CoordinateFrameSystem):
    def __init__(self, file_name=None, width=None, height=None):

        # Coordinate system defines self._quaternion and self.rotation_mat
        super(Camera, self).__init__()

        # Used for visualization
        self.normal = np.array([0, 0, 0], dtype=float)
        # single color to represent the camera (for example in a ply file)
        self.color = np.array([255, 255, 255], dtype=int)

        # contains focal length and pivot point, but NO distortion parameters
        self._calibration_mat1 = np.zeros((3, 3), dtype=float)
        # Only radial distortion with 1 distortion parameter is supported
        self._radial_distortion = None

        self.file_name = file_name

        self.width = width
        self.height = height

        # Differentiate between view/image index and reconstruction index
        self.view_index = None          # This is the index w.r.t. to the input images
        self.camera_index = None        # This is the index w.r.t the reconstructed cameras


    # defines how the class will be printed
    def __repr__(self):
        return self.__str__()

    def __str__(self):
        file_name = self.file_name
        if file_name is None:
            file_name = 'None'
        return str('Camera: ' + file_name + ' ' + str(self._center) + ' ' + str(self.normal))

    def is_monocular_cam(self):
        return True

    # def compare_file_name(self, other):
    #     return self.file_name < other.file_name

    def get_h5_file_name(self):
        return os.path.splitext(self.file_name)[0] + '.h5'

    def set_calibration(self, calibration_mat, radial_distortion):

        self._calibration_mat1 = np.asarray(calibration_mat, dtype=float)
        self._radial_distortion = float(radial_distortion)
        assert self._radial_distortion is not None

    def check_calibration_mat(self):
        assert self.is_principal_point_initialized()

    def get_calibration_mat(self):
        self.check_calibration_mat()
        return self._calibration_mat1

    def set_principal_point(self, principal_point):
        self._calibration_mat1[0][2] = principal_point[0]
        self._calibration_mat1[1][2] = principal_point[1]

    def get_principal_point(self):
        calibration_mat = self.get_calibration_mat()
        cx = calibration_mat[0][2]
        cy = calibration_mat[1][2]
        return np.asarray([cx,cy], dtype=float)

    def is_principal_point_initialized(self):
        cx_zero = np.isclose(self._calibration_mat1[0][2], 0.0)
        cy_zero = np.isclose(self._calibration_mat1[1][2], 0.0)
        initialized = (not cx_zero) and (not cy_zero)
        return initialized

    # def set_height(self, height):
    #     self.height = height
    #
    # def get_height(self):
    #     assert self.height > 0     # height not properly initialized
    #     return self.height
    #
    # def set_width(self, width):
    #     self.width = width
    #
    # def get_width(self):
    #     assert self.width > 0      # width not properly initialized
    #     return self.width

    @staticmethod
    def compute_calibration_mat(focal_length, cx, cy):
        return np.array([[focal_length, 0, cx],
                        [0, focal_length, cy],
                        [0, 0, 1]], dtype=float)

    def get_focal_length(self):
        assert self._calibration_mat1[0][0] == self._calibration_mat1[1][1]
        return self._calibration_mat1[0][0]

    def get_view_angle(self):
        assert self.width is not None and self.width > 0
        assert self.height is not None and self.height > 0
        min_extend = min(self.width, self.height)
        angle_of_view = 2 * math.degrees(math.atan((min_extend / float(2.0 * self._calibration_mat1[0][0]))))
        return angle_of_view

    def get_radial_distortion(self):
        assert self._radial_distortion is not None
        return self._radial_distortion

    def has_radial_distortion(self):
        return self._radial_distortion is not None and self._radial_distortion != 0.0

    def get_viewing_dir_world_coord(self):

        # Positive viewing dir
        viewing_dir_cam_coord = np.asarray([0, 0, 1], dtype=float)
        ray_dir_vec = np.dot(self.get_rotation_mat().T, viewing_dir_cam_coord)
        return ray_dir_vec

    def get_up_dir_world_coord(self):

        # Positive viewing dir
        up_dir_cam_coord = np.asarray([0, 1, 0], dtype=float)
        ray_dir_vec = np.dot(self.get_rotation_mat().T, up_dir_cam_coord)
        return ray_dir_vec

    # ============================= Projecting Single POINTS into Image ==========================================

    def project_single_point_woorld_coord_into_camera_image_as_image_coord(self, point_world_coord):
        """
        $ >>> point_world_coordinates.shape
        $ >>> (3,)
        :param point_world_coord:
        :return:
        """
        image_point, visible = self.project_single_woorld_coord_into_camera_image_as_image_coord(
            point_world_coord.coord)
        return image_point, visible

    # ============================= Projecting Single COORDS into Image ==========================================

    def project_single_woorld_coord_into_camera_image_as_image_coord(self,
                                                                     coord_in_world_coord):
        """
        $ >>> point_world_coordinates.shape
        $ >>> (3,)
        :param coord_in_world_coord:
        :return:
        """
        point_cam_coord = self.world_to_cam_coord_single_coord(
            world_coord=coord_in_world_coord)
        image_point, visible = \
            self.project_single_point_cam_coord_into_camera_image_as_image_coord(
            point_cam_coord)
        return image_point, visible

    def project_single_point_cam_coord_into_camera_image_as_image_coord(self,
                                                                        point_cam_coord):

        """
        THIS RETURNS IMAGE POINTS WITHIN [0, width] x [0, height]
        :param point_cam_coord:
        :param debug_output:
        :return:
        """

        visible = False
        image_point = None

        assert self.width > 0
        assert self.height > 0

        #logger.vinfo('calibration_mat', calibration_mat)

        # To the Visibility of 3D points (on the image plane)
        # Depth of a point with respect to a certain camera is described in Multiple View Geometry on page 162
        # Further Key Words: View Frustum
        # On the other hand: Each point is exactly visible if its projection into the camera coordinate frame
        # has a z component > 0. In addition, we must check that the projection of the point lies within the image
        # bounds (see below)
        if point_cam_coord[2] > 0:

            # Make sure the calibration matrix is valid

            #  project the 3d point onto the 2D camera image plane
            point_image_plane_hom = self.get_calibration_mat().dot(point_cam_coord)

            # See Multiple View Geometry page 155
            # point_image_plane_hom = [fX+Zp_x, fY+Zp_y, Z]
            # with camera point [X,Y,Z] and principal point [p_x, p_y]
            # Remember: two homogeneous coordinates hom_1 and hom_2 with hom_1 = a hom_2 for a scalar 'a' are
            # considered as equivalent
            # Dividing by the last component (i.e. z = 1) results in the image plane coordinates
            # [fX+Zp_x, fY+Zp_y, Z] -> [fX/Z+p_x, fY/Z+p_y, 1]
            point_image_plane_hom = (point_image_plane_hom / point_image_plane_hom[2])

            # x_image_coord and y_image_coord are within [0, width] x [0, height]
            x_image_coord = copy.deepcopy(point_image_plane_hom[0])
            y_image_coord = copy.deepcopy(point_image_plane_hom[1])

            if self.has_radial_distortion():

                # http://ccwu.me/vsfm/doc.html#nvm
                # https://groups.google.com/forum/#!msg/vsfm/IcbdIVv_Uek/Us32SBUNK9oJ

                # NOTE that the parameters saved in NVM file is slightly different with the internal representation.
                # Instead, NVM saves the following for each camera:
                # f, R (as quaternion), C = - R'T, rn = r * f * f.
                # The PBA code includes functions for loading the NVM file and convert the camera parameters.
                rn = self.get_radial_distortion()

                r = rn / float(self.get_focal_length() * self.get_focal_length())

                # mx and my are centered around the principal point
                principal_point = self.get_principal_point()
                mx = x_image_coord - principal_point[0]
                my = y_image_coord - principal_point[1]

                # The distortion factor is r2 = r * (mx * mx + my * my)
                r_2 = r * (mx * mx + my * my)
                logger.vinfo('r_2', r_2)

                # The undistorted measurement is (1 + r2) * (mx, my)
                undistorted_x = (1 + r_2) * mx
                undistorted_y = (1 + r_2) * my

                logger.vinfo('x_image_coord (without undistortion)', x_image_coord)
                logger.vinfo('y_image_coord (without undistortion)', y_image_coord)

                x_image_coord = undistorted_x + principal_point[0]
                y_image_coord = undistorted_y + principal_point[1]
                logger.vinfo('x_image_coord (with undistortion)', x_image_coord)
                logger.vinfo('y_image_coord (with undistortion)', y_image_coord)

                # THE UNDISTORTED VALUES ARE NOT REALLY BETTER THAN THE ORIGINAL ONES
                # TODO MAYBE BUG IS FIXED NOW
                # TODO INVESTIGATE
                # TODO TEST WITH FISHEYE
                assert False    # Radial Distortion support is disabled for now

            on_image_plane_x = abs(x_image_coord) < self.width
            on_image_plane_y = abs(y_image_coord) < self.height

            visible = on_image_plane_x and on_image_plane_y

            image_point = (x_image_coord, y_image_coord)

        return image_point, visible

    def compute_reprojection_error_single_point(self, point):
        projected_image_point, visible = \
            self.project_single_woorld_coord_into_camera_image_as_image_coord(
                point.coord)
        if not visible:
            return None
        for measurement in point.measurements:
            if measurement.camera_index == self.camera_index:
                error_x = measurement.x - projected_image_point[0]
                error_y = measurement.y - projected_image_point[1]
                error = math.sqrt(error_x * error_x + error_y * error_y)
                return error


    # ============================= Projecting Multiple POINTS into Image ==========================================

    def project_multiple_points_woorld_coord_into_camera_image_as_image_coord(self, points_world_coord):
        """
        $ >>> point_world_coordinates.shape
        $ >>> (3,)
        :param point_world_coord:
        :return:
        """

        image_points = []
        visibility_flags = []
        for point in points_world_coord:
            image_point, visible = \
                self.project_single_point_woorld_coord_into_camera_image_as_image_coord(point)
            image_points.append(image_point)
            visibility_flags.append(visible)
        return image_points, visibility_flags

    # ============================= Projecting Multiple COORDS into Image ==========================================

    def project_multiple_world_coords_into_camera_image_as_image_coord(self,
                                                                       coords_world_coord):
        """
        :param coords_world_coord: is a single array
        :return: points_image_plane: is not necessarily lying on the image plane (check visibility array)
        :return: visibility_array: contains True and False values (visibility_array.dtype is bool)
        """

        #logger.info('project_multiple_world_coords_into_camera_image_as_image_coord: ...')

        # shape = rows, columns
        #logger.info('points_world_coordinates.shape: ' + str(coords_world_coord.shape))
        assert coords_world_coord.shape[0] == 3 and coords_world_coord.shape[1] > 3
        assert self.width is not None
        assert self.height is not None

        if self.has_radial_distortion():
            assert False    # Radial distortion not supported atm

        # transformation of the object coordinate system to the camera coordinate system
        # point_cam_coord = (self.get_rotation_mat()).dot(point_world_coordinates - self.get_camera_center())

        # make coordinate homogeneous and apply transformation
        hom_row = np.ones(coords_world_coord.shape[1])
        # can't use hstack or vstack here, since dimensions do not match
        points_world_coordinates_hom = np.row_stack((coords_world_coord, hom_row))
        points_cam_coord_hom = self.get_4x4_world_to_cam_mat().dot(
            points_world_coordinates_hom)

        coord_cam_coord = points_cam_coord_hom[0:3]
        # Rows first, columns later => points_world_coordinates[row_index][column_index]
        # points_world_coordinates has 3 ROWS and N COLUMNS (N >> 3)
        # The first/second/third row contains the x/y/z values for ALL points
        # points_world_coordinates[row_index] is a np.array with N elements
        #logger.vinfo('points_world_coordinates.shape', points_world_coordinates.shape)
        #logger.vinfo('coord_cam_coord.shape', coord_cam_coord.shape)

        # logger.debug('============DEBUG============')
        # points_cam_coord_ref = np.empty([3, 0], dtype=float)
        # for ground_point in ground_points:
        #     point_world_coordinates = ground_point.get_coord_as_array()
        #     point_cam_coordinates = self.world_to_cam_coord_single_point(point_world_coordinates)
        #     points_cam_coord_ref = np.column_stack((points_cam_coord_ref, point_cam_coordinates))
        # # 'allclose' test due to numerical differences
        # comp_val = np.allclose(coord_cam_coord, points_cam_coord_ref)
        # assert comp_val
        # logger.debug('=============================')

        points_image_plane, visibility_array = \
            self.project_multiple_cam_coords_into_camera_image_as_image_coord(
                coord_cam_coord)

        #logger.info('project_multiple_world_coords_into_camera_image_as_image_coord: Done')

        return points_image_plane, visibility_array

    def project_multiple_cam_coords_into_camera_image_as_image_coord(self, coords_cam_coord):
        """

        :param coords_cam_coord:
        :return: points_image_plane: is not necessarily lying on the image plane (check visibility_array)
        :return: visibility_array: contains True and False values (visibility_array.dtype is bool)
        """

        #logger.vinfo('points_cam_coord.shape', coords_cam_coord.shape)
        assert coords_cam_coord.shape[0] == 3 and coords_cam_coord.shape[1] > 3

        points_image_plane_hom = self.get_calibration_mat().dot(coords_cam_coord)
        #points_image_plane_hom = (self.get_calibration_mat()).dot(coords_cam_coord)
        # logger.vinfo('points_image_plane_hom.shape', points_image_plane_hom.shape)

        # element wise ops: np.true_divide(), np.greater()
        in_front_of_array = np.greater(coords_cam_coord[2], np.zeros(len(coords_cam_coord[2]), dtype=float))

        # normalization of the homogeneous coordinates
        points_image_plane_hom[0] = np.true_divide(points_image_plane_hom[0], points_image_plane_hom[2])
        points_image_plane_hom[1] = np.true_divide(points_image_plane_hom[1], points_image_plane_hom[2])

        # use the absolute value to safe comparisons
        on_image_plane_x = np.logical_and(points_image_plane_hom[0] >= 0, points_image_plane_hom[0] < self.width)
        on_image_plane_y = np.logical_and(points_image_plane_hom[1] >= 0, points_image_plane_hom[1] < self.height)

        # np.logical_and does not support 3 arguments (3 parameter is the output array)
        visibility_array = np.logical_and(in_front_of_array, on_image_plane_x)
        visibility_array = np.logical_and(visibility_array, on_image_plane_y)

        points_image_plane_hom = copy.deepcopy(points_image_plane_hom)

        return points_image_plane_hom[0:2].T, visibility_array

    # ============================= Check Visibility ==========================================

    def check_visibilty_of_single_point_world_coords(self, point_world_coordinates):
        _, visible = self.project_single_point_woorld_coord_into_camera_image_as_image_coord(
            point_world_coordinates)
        return visible

    def check_visibilty_of_single_point_cam_coords(self, point_cam_coord):
        _, visible = self.project_single_point_cam_coord_into_camera_image_as_image_coord(
            point_cam_coord)
        return visible

    def check_visibility_of_points_world_coords(self, points_world_coordinates):
        """
        Checks the visibility of points in camera coordinates. Returns a binary array
        $ >>> points_world_coordinates.shape
        $ >>> (n,3)                 # where n is the number of points
        :param points_world_coordinates:
        :return:
        """
        logger.info('check_visibility_of_world_points: ...')
        _, visibility_array = \
            self.project_multiple_world_coords_into_camera_image_as_image_coord(
                points_world_coordinates)
        logger.info('check_visibility_of_world_points: Done')
        return visibility_array

    def check_visibility_of_points_cam_coords(self, points_cam_coord):
        """
        Checks the visibility of points in camera coordinates. Returns a binary array
        $ >>> points_world_coordinates.shape
        $ >>> (n,3)                 # where n is the number of points
        """
        logger.info('check_visibility_of_cam_points: ...' )
        _, visibility_array = \
            self.project_multiple_cam_coords_into_camera_image_as_image_coord(points_cam_coord)
        logger.info('check_visibility_of_cam_points: Done')
        return visibility_array

    # ============================== Measurements ===============================================================
    def compute_measurement_pos_of_points(self, points):

        measurement_pos = []
        for point in points:
            for measurement in point.measurements:
                if measurement.camera_index == self.camera_index:
                    measurement_pos.append(measurement.get_x_y())
        return measurement_pos

    # ============================== Camera Rays ===============================================================

    def generate_camera_rays(self, x_y_positions, convert_to_world_coords=True):
        """
        SUPPORTS ATM ONLY "SIMPLE_PINHOLE", i.e. f,cx,cy and a scale ratio of 0
        """

        assert self.width is not None
        assert self.height is not None

        focal_length = self._calibration_mat[0][0]
        rays = []
        for x_y in x_y_positions:
            #logger.info(x_y)
            assert x_y[0] >= 0 and x_y[1] >= 0

            # Compute the direction vector in CAMERA COORDINATES
            ray_dir_vec = np.array([x_y[0] - self.width/float(2),       # x
                                    x_y[1] - self.height/float(2),      # y
                                    focal_length],
                                   dtype=float)
            ray_pos_vec = np.zeros(3)

            if convert_to_world_coords:
                # Compute the direction vector in WORLD COORDINATES
                ray_dir_vec = np.dot(self.get_rotation_mat().T, ray_dir_vec)
                ray_pos_vec = self.get_camera_center()

            rays.append(Ray(pos_vec=ray_pos_vec, dir_vec=ray_dir_vec))
        return rays

    # ============================== Depth Buffer ===============================================================

    def convert_depth_buffer_to_cam_coords(self,
                                           depth_buffer_matrix,
                                           depth_scale_value=1.0,
                                           background_depth_value=1000,
                                           invert_y=False,
                                           n_th_result_point=100
                                           ):
        """
        Do not confuse z_buffer with depth_buffer!
        z_buffer contains values in [0,1]
        depth_buffer contains the actual distance values

        Computes only 1/n_th_result_point points for the point cloud
        :param depth_buffer_matrix:
        :param n_th_result_point:
        :return:
        """

        logger.info('convert_depth_matrix_to_camera_coords: ...')

        assert self.height is not None
        assert self.width is not None

        depth_buffer_matrix *= depth_scale_value

        focal_length_in_pixel = self.get_calibration_mat()[0][0]
        logger.vinfo('focal_length_in_pixel', focal_length_in_pixel)

        # use the local coordinate system of the camera
        # to analyze its viewing directions
        # blender camera coordinate system looks along the negative z axis (blue)
        # the up axis points along the y axis (green)

        coords_cam_coord = []
        result_point_idx = 0
        num_pixels = self.width * self.height
        for (y, x), depth_value in np.ndenumerate(depth_buffer_matrix):

            if depth_value < background_depth_value:

                x = self.width - x  # Invert x
                x = x - self.width / 2.0  # Shift x from image to camera coordinates
                if invert_y:
                    y = self.height - y
                y = y - self.height / 2.0  # Shift y from image to camera coordinates
                z = -focal_length_in_pixel  # Invert z
                pixel_vec = np.array([x, y, z], dtype=float)

                if result_point_idx % 10000 == 0:
                    logger.info('result_point_idx ' + str(result_point_idx) + ' ' + str(num_pixels))

                if result_point_idx % n_th_result_point == 0:
                    # convert to inhomogeneous coordinates
                    # divide using the focal length (in pixels)
                    # (i.e. the resulting vector is unit free)
                    pixel_vec /= pixel_vec[2]
                    # multiply by depth value in blender units / meters
                    # (i.e. the resulting vector is in blender units / meters)
                    pixel_vec *= depth_value
                    coords_cam_coord.append(pixel_vec)
                result_point_idx += 1

        logger.info('convert_depth_matrix_to_camera_coords: Done')
        return coords_cam_coord

    def convert_depth_buffer_to_world_coords(self,
                                             depth_buffer_matrix,
                                             depth_scale_value=1.0,
                                             background_depth_value=1000,
                                             invert_y=False,
                                             n_th_result_point=100
                                           ):

        coords_cam_coord = self.convert_depth_buffer_to_cam_coords(
            depth_buffer_matrix=depth_buffer_matrix,
            depth_scale_value=depth_scale_value,
            background_depth_value=background_depth_value,
            invert_y=invert_y,
            n_th_result_point=n_th_result_point
        )

        coords_world_coord = self.cam_to_world_coord_multiple_coords(
            coords_cam_coord)
        return coords_world_coord

    @staticmethod
    def parse_camera_image_files(cameras, path_to_images):
        from PIL import Image
        for camera in cameras:
            # this does NOT load the data; into memory -> should be fast!
            image = Image.open(os.path.join(path_to_images, camera.file_name))
            camera.width, camera.height = image.size
        return cameras

    @staticmethod
    def parse_camera_h5_files(cameras, path_to_h5_files):
        from Utility.File_Handler.H5_File_Handler import H5FileHandler
        for camera in cameras:
            seg = H5FileHandler.read_h5(os.path.join(path_to_h5_files, camera.get_h5_file_name()))
            camera.height, camera.width = seg.shape
        return cameras








