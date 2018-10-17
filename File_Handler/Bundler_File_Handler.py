__author__ = 'bullin'

# The bundler v0.3 file format is described here
# http://www.cs.cornell.edu/~snavely/bundler/bundler-v0.3-manual.html

import os

import numpy as np
from PIL import Image

from Utility.Types.Camera import Camera
from Utility.Types.Point import Point
from Utility.Math.Transformation.Transformation_Collection import TransformationCollection


class BundlerFileHandler:

    @staticmethod
    def parse_camera_image_files(cameras, camera_file_name, path_to_images):
        input_file = open(camera_file_name, 'r')
        for image_file_name, camera in zip(input_file, cameras):
            camera.file_name = image_file_name.rstrip()
            # this does NOT load the data into memory -> should be fast!
            image = Image.open(os.path.join(path_to_images, camera.file_name))
            camera.width, camera.height = image.size
        return cameras


    @staticmethod
    def parse_bundler_file(input_visual_fsm_bundle_out_file_name):

        # =======
        # REMARK: The camera coordinate frame is transformed to
        #         the same camera coordinate frame used by VisualSfM
        #         i.e. a rotation around the x axis by 180 degree
        # =======

        input_file = open(input_visual_fsm_bundle_out_file_name, 'r')
        # first line is just a comment, throw it away
        (input_file.readline()).rstrip()

        # read amount cameras and points
        current_line = (input_file.readline()).rstrip()
        amount_cams = 0
        amount_points = 0
        amount_cams, amount_points = map(int, current_line.split(' '))
        print(amount_cams)
        print(amount_points)

        cameras = []

        # for camera_index in range(0, int(amount_cams)):
        for camera_index in range(0, amount_cams):

            # Each camera entry <cameraI> contains the estimated camera intrinsics and extrinsics, and has the form:
            # <f> <k1> <k2>   [the focal length, followed by two radial distortion coeffs]
            # <R>             [a 3x3 matrix representing the camera rotation]
            # <t>             [a 3-vector describing the camera translation]

            current_line = (input_file.readline()).rstrip()     # read internal camera parameters
            # TODO Handle Radial Distortion
            focal_length = float(current_line.split(' ')[0])
            camera_calibration_matrix = np.asarray(
                [[focal_length, 0, 0], [0, focal_length, 0], [0, 0, 1]],
                dtype=float)

            # use map to convert all string numbers to floats
            # python 3 requires a explicit cast from 'map object' to list
            current_line = (input_file.readline()).rstrip()
            first_row = list(map(float, current_line.split(' ')))
            current_line = (input_file.readline()).rstrip()
            second_row = list(map(float, current_line.split(' ')))
            current_line = (input_file.readline()).rstrip()
            third_row = list(map(float, current_line.split(' ')))

            cam_rotation_matrix = np.asarray(
                [first_row, second_row, third_row],
                dtype=float)

            # this line contains the translation vector and not the camera center
            current_line = (input_file.readline()).rstrip()     # read translation vector
            translation_vector = np.asarray(
                list(map(float, current_line.split(' '))),
                dtype=float)

            # Transform the camera coordinate system from the computer vision camera coordinate frame to the computer
            # vision camera coordinate frame (i.e. rotate the camera matrix around the x axis by 180 degree)
            # inverting the y and the z axis transform the points in the camera coordinate frame used by visualsfm
            cam_rotation_matrix = TransformationCollection.invert_y_and_z_axis(cam_rotation_matrix)
            translation_vector = TransformationCollection.invert_y_and_z_axis(translation_vector)


            current_camera = Camera()
            current_camera.set_rotation_mat(cam_rotation_matrix)
            # set camera center AFTER rotation (since setting the center sets also the translation vector)
            #current_camera.set_camera_center_after_rotation(center_vec)
            current_camera.set_camera_translation_vector_after_rotation(translation_vector)

            # from cam coordinates to world coordinates
            cam_rotation_matrix_inv = np.linalg.inv(cam_rotation_matrix)
            current_camera.rotation_inv_mat = cam_rotation_matrix_inv
            current_camera.calibration_mat = camera_calibration_matrix
            current_camera.id = camera_index

            cameras.append(current_camera)

        points = []
        for point_index in range(0, amount_points):

            current_point = Point()

            # Each point entry has the form:
            # <position>      [a 3-vector describing the 3D position of the point]
            # <color>         [a 3-vector describing the RGB color of the point]
            # <view list>     [a list of views the point is visible in]

            current_line = (input_file.readline()).rstrip()         # read the 3d position
            point_center = np.array(list(map(float, current_line.split(' '))))
            current_point._coord = point_center

            current_line = (input_file.readline()).rstrip()         # read the color
            point_color = np.array(list(map(int, current_line.split(' '))))
            current_point._color = point_color

            current_line = (input_file.readline()).rstrip()         # read the view list
            measurement_values = current_line.split(' ')
            measurements = [measurement_values[1+i*4:1+i*4+4] for i in range(int(measurement_values[0]))]
            # Remark: The last measurement is inverted, so the y axis points downwards (like in visualsfm)
            current_point.measurements = [
                (int(measurement[0]), int(measurement[1]), float(measurement[2]), -float(measurement[3]))
                for measurement in measurements]
            current_point.id = point_index

            points.append(current_point)

        return cameras, points

    @staticmethod
    def write_bundler_file(output_bundler_out_file_name, output_bundler_txt_file_name, cameras, points):

        print('Write Bundle Out file: ...')

        bundle_content = []

        bundle_content.append('# Bundle file v0.3' + os.linesep)
        # <num_cameras> <num_points>
        bundle_content.append(str(len(cameras)) + ' ' + str(len(points)) + os.linesep)

        # for camera_index in range(0, int(amount_cams)):
        for camera in cameras:

            # Each camera entry <cameraI> contains the estimated camera intrinsics and extrinsics, and has the form:
            # <f> <k1> <k2>   [the focal length, followed by two radial distortion coeffs]
            # <R>             [a 3x3 matrix representing the camera rotation]
            # <t>             [a 3-vector describing the camera translation]

            # TODO HANDLE RADIAL DISTORTION
            bundle_content.append(str(camera.calibration_mat[0][0]) + ' ' + '0 0' + os.linesep)

            # SEE "DataInterface.h" in "PBA" Code (GetInvertedR9T method)
            # FROM THE DOCUMENTATION:
            # ci.GetInvertedR9T(q, c);
            cam_rotation_matrix, center_vec = TransformationCollection.invert_y_and_z_axis(
                camera.get_rotation_mat(), camera.translation_vec)

            for row_index in range(0,3):
                line = map(str, list(cam_rotation_matrix[row_index]))
                line = " ".join(line)
                bundle_content.append(line + os.linesep)

            line = map(str, list(center_vec))
            line = " ".join(line)
            bundle_content.append(line + os.linesep)

        for point in points:

            # Each point entry has the form:
            # <position>      [a 3-vector describing the 3D position of the point]
            # <color>         [a 3-vector describing the RGB color of the point]
            # <view list>     [a list of views the point is visible in]

            line = map(str, list(point.coord))
            line = " ".join(line)
            bundle_content.append(line + os.linesep)

            line = map(str, list(point.color))
            line = " ".join(line)
            bundle_content.append(line + os.linesep)

            # The view list begins with the length of the list (i.e., the number of cameras the point is visible in ).
            # The list is then given as a list of quadruplets < camera > < key > < x > < y >, where < camera > is a
            # camera index, < key > the index of the SIFT keypoint where the point was detected in that camera,
            # and < x > and < y > are the detected positions of that keypoint.

            line = str(len(point.measurements))
            for measurement in point.measurements:
                # Invert the second argument, to adjust the direction of the y axis
                #line += ' ' + " ".join(map(str, list(measurement[0:3]) + list([-measurement[3]])))
                line += ' ' + str(measurement.image_index) + \
                        ' ' + str(measurement.feature_index) + ' ' + \
                        str(measurement.x) + ' ' + str(-measurement.y)

            bundle_content.append(line + os.linesep)


        print('Write Bundler file: ' + output_bundler_out_file_name)
        output_file = open(output_bundler_out_file_name, 'wb')
        output_file.writelines([item for item in bundle_content])

        print('Write Bundler Out File: Done')

        print('Write Bundle Txt File: ...')
        txt_content = []
        for camera in cameras:
            txt_content.append(camera.file_name + os.linesep)
        print('Write Bundler Txt File: ' + output_bundler_out_file_name)
        output_file = open(output_bundler_txt_file_name, 'wb')
        output_file.writelines([item for item in txt_content])
        print('Write Bundler TxT File: Done')




















