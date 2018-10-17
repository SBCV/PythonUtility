__author__ = 'bullin'

import os
from collections import defaultdict
import numpy as np
from Utility.Logging_Extension import logger
from Utility.Types.Camera import Camera
from Utility.Types.Point import Measurement
from Utility.Types.Point import Point
from Utility.Math.Conversion.Conversion_Collection import compute_camera_coordinate_system_translation_vector



class NVMFileHandler(object):

    # Check the LoadNVM function in util.h of Multicore bundle adjustment code for more details.
    # http://grail.cs.washington.edu/projects/mcba/
    # pba/src/pba/util.h

    #**************************** PARSE NVM FILE ****************************#
    @staticmethod
    def _parse_cameras(input_file, num_cameras, camera_calibration_matrix):

        # VisualSFM CAMERA coordinate system is the standard
        # CAMERA coordinate system in computer vision
        # (not the same as in computer graphics like in bundler, blender, etc.)
        # That means
        #       the y axis in the image is pointing downwards (not upwards)
        #       the camera is looking along the positive z axis
        #       (points in front of the camera show a positive z value)


        # The camera coordinate system in computer vision VISUALSFM
        # uses camera matrices which are rotated around the x axis by 180 degree
        # i.e. the y and z axis of the CAMERA MATRICES are inverted
        # therefore, the y and z axis of the TRANSLATION VECTOR are also inverted

        cameras = []

        for camera_index in range(num_cameras):
            line = input_file.readline()

            # <Camera> = <File name> <focal length> <quaternion WXYZ> <camera center> <radial distortion> 0
            line_values = line.split()

            file_name = os.path.basename(line_values[0])

            focal_length = float(line_values[1])

            if camera_calibration_matrix is None:
                camera_calibration_matrix = np.array(
                    [[focal_length, 0, 0],
                     [0, focal_length, 0],
                     [0, 0, 1]])

            quaternion_w = float(line_values[2])
            quaternion_x = float(line_values[3])
            quaternion_y = float(line_values[4])
            quaternion_z = float(line_values[5])
            quaternion = np.array(
                [quaternion_w, quaternion_x, quaternion_y, quaternion_z],
                dtype=float)

            camera_center_x = float(line_values[6])
            camera_center_y = float(line_values[7])
            camera_center_z = float(line_values[8])
            center_vec = np.array([camera_center_x, camera_center_y, camera_center_z])

            radial_distortion = float(line_values[9])
            zero_value = float(line_values[10])
            assert(zero_value == 0)

            current_camera = Camera()
            # Setting the quaternion also sets the rotation matrix
            current_camera.set_quaternion(quaternion)

            # Set the camera center after rotation
            # COMMENT FROM PBA CODE:
            #   older format for compability
            #   camera_data[i].SetQuaternionRotation(q); // quaternion from the file
            #   camera_data[i].SetCameraCenterAfterRotation(c); // camera center from the file
            current_camera._center = center_vec

            # set the camera view direction as normal w.r.t world coordinates
            cam_view_vec_cam_coord = np.array([0, 0, 1]).T
            cam_rotation_matrix_inv = np.linalg.inv(current_camera.get_rotation_mat())
            cam_view_vec_world_coord = cam_rotation_matrix_inv.dot(cam_view_vec_cam_coord)
            current_camera.normal = cam_view_vec_world_coord

            translation_vec = compute_camera_coordinate_system_translation_vector(
                center_vec,
                current_camera.get_rotation_mat())
            current_camera._translation_vec = translation_vec

            current_camera.set_calibration(
                camera_calibration_matrix,
                radial_distortion)
            current_camera.file_name = file_name
            current_camera.camera_index = camera_index

            cameras.append(current_camera)

        return cameras

    @staticmethod
    def _parse_nvm_points(input_file, num_3D_points):

        points = []

        for point_index in range(num_3D_points):

            # From the docs:
            # <Point>  = <XYZ> <RGB> <number of measurements> <List of Measurements>
            point_line = input_file.readline()

            point_line_elements = (point_line.rstrip()).split()
            xyz_vec = list(map(float, point_line_elements[0:3]))
            rgb_vec = list(map(int, point_line_elements[3:6]))

            number_measurements = int(point_line_elements[6])
            measurements = point_line_elements[7:]
            class_ids = defaultdict(lambda: 0)

            current_point_measurement = []

            for measurement_index in range(0, number_measurements):

                # From the docs:
                # <Measurement> = <Image index> <Feature Index> <xy>
                current_measurement = measurements[measurement_index*4:(measurement_index+1)*4]
                # print current_measurement
                image_index = int(current_measurement[0])
                feature_index = int(current_measurement[1])

                # REMARK: The order of ndarray.shape (first height, then width) is complimentary to
                # pils image.size (first width, then height).
                # That means
                # height, width = segmentation_as_matrix.shape
                # width, height = image.size

                # Therefore
                #   x_in_nvm_file == x_image == y_ndarray and
                #   y_in_nvm_file == y_image == x_ndarray
                x_in_nvm_file = float(current_measurement[2])
                y_in_nvm_file = float(current_measurement[3])

                current_point_measurement.append(
                    Measurement(image_index, feature_index, x_in_nvm_file, y_in_nvm_file))

                # REMARK: x_in_nvm_file and y_in_nvm_file are relative to the image center

            current_point = Point(coord=xyz_vec, color=rgb_vec)
            current_point.measurements = current_point_measurement
            current_point.id = point_index

            points.append(current_point)

        return points

    @staticmethod
    def _set_point_measurement_interval_flag(points):

        negative_value_found = False
        for point in points:
            for measurement in point.measurements:
                if not negative_value_found:
                    negative_value_found = measurement.x < 0 or measurement.y < 0
        for point in points:
            for measurement in point.measurements:
                measurement.x_y_are_image_coords = not negative_value_found

    @staticmethod
    def parse_fixed_calibration(line):

        line_elements = line.split()
        if len(line_elements) == 1:
            assert line.startswith('NVM_V3')
            calib_mat = None
        elif len(line_elements) == 7:
            _,_, fx, cx, fy, cy, r = line_elements
            calib_mat = np.array(
                [[float(fx), 0, float(cx)],
                 [0, float(fy), float(cy)],
                 [0, 0, 1]])
        else:
            assert False
        return calib_mat

    @staticmethod
    def parse_nvm_file(input_visual_fsm_file_name, parse_only_cams=False):

        """
        Remark:
            VisualSFM stores measurements coordinates within [-width/2, width/2] x [-height/2, height/2]
            Colmap stores measurements coordinates within [0, width] x [0, height]
        """

        logger.info('Parse NVM file: ' + str(input_visual_fsm_file_name))
        input_file = open(input_visual_fsm_file_name, 'r')
        # Documentation of *.NVM data format
        # http://ccwu.me/vsfm/doc.html#nvm

        # In a simple case there is only one model

        #Each reconstructed <model> contains the following
        #<Number of cameras>   <List of cameras>
        #<Number of 3D points> <List of points>


        # Read the first two lines (fixed)
        current_line = (input_file.readline()).rstrip()
        # Fixed Calibration Note might be appended, e..g. FixedK 2100 960 2100 540 0
        calibration_matrix = NVMFileHandler.parse_fixed_calibration(current_line)

        current_line = (input_file.readline()).rstrip()
        assert current_line == ''

        # Read the camera section
        # From the docs:
        # <Camera> = <File name> <focal length> <quaternion WXYZ> <camera center> <radial distortion> 0

        num_cameras = int((input_file.readline()).rstrip())
        logger.info(logger.ils() + 'Amount Cameras (Images in NVM file): ' + str(num_cameras))

        cameras = NVMFileHandler._parse_cameras(input_file, num_cameras, calibration_matrix)
        current_line = (input_file.readline()).rstrip()
        assert current_line == ''
        current_line = (input_file.readline()).rstrip()
        if current_line.isdigit() and not parse_only_cams:
            amount_points = int(current_line)
            logger.info(logger.ils() + 'Amount Sparse Points (Points in NVM file): ' + str(amount_points))
            points = NVMFileHandler._parse_nvm_points(input_file, amount_points)
            NVMFileHandler._set_point_measurement_interval_flag(points)

        else:
            points = []

        logger.info('Parse NVM file: Done')
        return cameras, points

    @staticmethod
    def nvm_line(content):
        return content + ' ' + os.linesep

    @staticmethod
    def create_nvm_first_line(cameras):

        # The first line can be either
        #   'NVM_V3'
        # or
        #   'NVM_V3 FixedK fx cx fy cy r'

        calib_mat = cameras[0].get_calibration_mat()
        # radial_dist = None
        # if cameras[0].has_radial_distortion():
        #     radial_dist = cameras[0].has_radial_distortion()

        fixed_calibration = True
        for cam in cameras:
            if not np.allclose(cam.get_calibration_mat(), calib_mat):
                fixed_calibration = False
                break
        if fixed_calibration:
            fl = 'NVM_V3 FixedK'
            fl += ' ' + str(calib_mat[0][0])
            fl += ' ' + str(calib_mat[0][2])
            fl += ' ' + str(calib_mat[1][1])
            fl += ' ' + str(calib_mat[1][2])
            fl += ' ' + str(0)      # TODO Radial distortion
            return fl
        else:
            return 'NVM_V3'

    @staticmethod
    def write_nvm_file(output_nvm_file_name, cameras, points):

        logger.info('Write NVM file: ' + output_nvm_file_name)

        nvm_content = []
        nvm_content.append(NVMFileHandler.nvm_line(
            NVMFileHandler.create_nvm_first_line(cameras)))
        nvm_content.append(NVMFileHandler.nvm_line(''))
        amount_cameras = len(cameras)
        nvm_content.append(NVMFileHandler.nvm_line(str(amount_cameras)))
        logger.info(logger.ils() + 'Amount Cameras (Images in NVM file): ' + str(amount_cameras))

        # Write the camera section
        # From the docs:
        # <Camera> = <File name> <focal length> <quaternion WXYZ> <camera center> <radial distortion> 0

        for camera in cameras:

            #quaternion = TransformationFunctions.rotation_matrix_to_quaternion(camera.rotation_mat)
            quaternion = camera.get_quaternion()

            assert camera.file_name is not None

            current_line = camera.file_name
            current_line += '\t' + str(camera.get_focal_length())
            current_line += ' ' + ' '.join(list(map(str, quaternion)))
            current_line += ' ' + ' '.join(list(map(str, camera.get_camera_center())))
            current_line += ' ' + str(camera.get_radial_distortion())
            current_line += ' ' + '0'
            nvm_content.append(current_line + ' ' + os.linesep)

        nvm_content.append(' ' + os.linesep)
        number_points = len(points)
        nvm_content.append(str(number_points) + ' ' + os.linesep)
        logger.info(logger.ils() + 'Found ' + str(number_points) + ' object points')

        for point in points:
            # From the docs:
            # <Point>  = <XYZ> <RGB> <number of measurements> <List of Measurements>
            current_line = ' '.join(list(map(str, point.coord)))
            current_line += ' ' + ' '.join(list(map(str, point.color)))
            if point.measurements is not None:
                current_line += ' ' + str(len(point.measurements))
                for measurement in point.measurements:
                    current_line += ' ' + str(measurement)
            else:
                current_line += ' ' + str(0)

            # print current_line
            nvm_content.append(current_line + ' ' + os.linesep)

        nvm_content.append('' + os.linesep)
        nvm_content.append('' + os.linesep)
        nvm_content.append('' + os.linesep)
        nvm_content.append('0' + os.linesep)
        nvm_content.append('' + os.linesep)
        nvm_content.append('#the last part of NVM file points to the PLY files' + os.linesep)
        nvm_content.append('#the first number is the number of associated PLY files' + os.linesep)
        nvm_content.append('#each following number gives a model-index that has PLY' + os.linesep)
        nvm_content.append('0' + os.linesep)

        with open(output_nvm_file_name, 'wb') as output_file:
            output_file.writelines([item.encode() for item in nvm_content])

        logger.info('Write NVM file: Done')


if __name__ == '__main__':

    input_nvm_file = '/home/sebastian/Desktop/a/example.nvm'

    cameras, points = NVMFileHandler.parse_nvm_file(input_nvm_file)

    for camera in cameras:
        camera.set_principal_point([1400, 1100])

    output_nvm_file_name = '/home/sebastian/Desktop/a/example_mod.nvm'
    NVMFileHandler.write_nvm_file(output_nvm_file_name, cameras, points)

    cameras, points = NVMFileHandler.parse_nvm_file(output_nvm_file_name)
    for camera in cameras:
        logger.vinfo('a', camera.get_principal_point())