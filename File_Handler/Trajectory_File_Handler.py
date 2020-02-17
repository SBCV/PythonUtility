import numpy as np
import os
from collections import OrderedDict
from Utility.Logging_Extension import logger
from Utility.Types.Camera import Camera
from Utility.Types.Stereo_Camera import StereoCamera
from Utility.Types.Coordinate_Frame_System import CoordinateFrameSystem
from Utility.Types.Camera_Object_Trajectory import CameraObjectTrajectory


class TrajectoryFileHandler(object):

    # 11 is for the outdated folder structure (no intrinsics)
    # 14 monocular
    # 19 stereo

    gt_lines_per_frame_values = [11, 14, 19]
    CAMERA_POSE = 'camera_pose'
    OBJECT_POSE = 'object_pose'

    @staticmethod
    def _chunks(l, n):
        """Yield successive n-sized chunks from l."""
        for i in range(0, len(l), n):
            yield l[i:i + n]

    @staticmethod
    def compute_gt_lines_per_frame(content_list):

        logger.info('compute_gt_lines_per_frame: ...')
        # logger.vinfo('content_list', content_list)

        content_list = [x.strip() for x in content_list]

        frame_idx_list = []
        for idx, content_line in enumerate(content_list):
            if 'frame' in content_line:
                # DONT test for  'jpg' in content_line, since that is not true for the legacy data structure
                frame_idx_list.append(idx)
        # logger.vinfo('frame_idx_list', frame_idx_list)

        num_lines_per_frame = None
        for idx in range(len(frame_idx_list))[1:]:
            gt_lines_per_frame_tmp = frame_idx_list[idx] - frame_idx_list[idx - 1]
            if num_lines_per_frame is not None:
                assert num_lines_per_frame == gt_lines_per_frame_tmp
            num_lines_per_frame = gt_lines_per_frame_tmp

        # logger.vinfo('num_lines_per_frame', num_lines_per_frame)
        assert num_lines_per_frame is not None
        if not num_lines_per_frame in TrajectoryFileHandler.gt_lines_per_frame_values:
            logger.vinfo('num_lines_per_frame', num_lines_per_frame)
            assert False

        # split content per frame (index)
        lines_per_frame = list(TrajectoryFileHandler._chunks(
            content_list, num_lines_per_frame))

        logger.info('compute_gt_lines_per_frame: Done')
        return lines_per_frame, num_lines_per_frame

    @staticmethod
    def _matrix_to_string(some_matrix):

        matrix_str = ''
        for row in some_matrix:
            row_str = ''
            for entry in row:
                row_str += str(entry) + ' '
            # remove last space char
            row_str = row_str.rstrip()
            matrix_str += row_str + '\n'
        # remove last linesep char
        matrix_str = matrix_str.rstrip('\n')
        return matrix_str

    @staticmethod
    def write_camera_and_object_trajectory_file(path_to_trajectory_file,
                                                camera_object_trajectory,
                                                camera_to_world_transformation_name='Camera to World Transformation',
                                                object_to_world_transformation_name='Object to World transformation'):
        logger.info('write_camera_and_object_trajectory_file: ...')
        logger.info('path_to_trajectory_file: ' + path_to_trajectory_file)
        file_content = []

        # Usage
        # virtual_camera.set_4x4_cam_to_world_mat(camera_matrix_world)

        logger.vinfo(
            'get_incomplete_frame_names_sorted()',
            camera_object_trajectory.get_incomplete_frame_names_sorted())

        for frame_name in camera_object_trajectory.get_frame_names_sorted():

            logger.vinfo('frame_name', frame_name)

            cam = camera_object_trajectory.get_camera(frame_name)
            #logger.vinfo('cam.is_monocular_cam()', cam.is_monocular_cam())

            if cam.is_monocular_cam():
                left_cam = cam
            else:
                left_cam = cam.get_left_camera()
                right_cam = cam.get_right_camera()
                if left_cam is None or right_cam is None:
                    logger.info('Left or Right Camera is missing, skipping this frame.')
                    continue

            # REMARK: DO NOT use os.linesep as it generate an additional empty line using windows
            # The index of the frames in the ground truth file starts with 0
            file_content.append(frame_name + '\n')
            file_content.append(camera_to_world_transformation_name + '\n')

            file_content.append(TrajectoryFileHandler._matrix_to_string(
                left_cam.get_calibration_mat()) + '\n')

            file_content.append(TrajectoryFileHandler._matrix_to_string(
                left_cam.get_4x4_cam_to_world_mat()) + '\n')
            logger.vinfo('left_cam.get_4x4_cam_to_world_mat()', left_cam.get_4x4_cam_to_world_mat())

            if cam.is_monocular_cam():
                file_content.append('0' + '\n')
                # Fill in dummy values
                file_content.append(TrajectoryFileHandler._matrix_to_string(
                    np.zeros((4, 4), dtype=float)) + '\n')
            else:
                file_content.append(str(cam.get_baseline()) + '\n')
                file_content.append(TrajectoryFileHandler._matrix_to_string(
                    right_cam.get_4x4_cam_to_world_mat()) + '\n')

            file_content.append(object_to_world_transformation_name + '\n')
            file_content.append(TrajectoryFileHandler._matrix_to_string(
                camera_object_trajectory.get_object_matrix_world(frame_name)) + '\n')

        with open(path_to_trajectory_file, 'w') as output_file:
            output_file.writelines([item for item in file_content])
        logger.info('write_camera_and_object_trajectory_file: Done')

    @staticmethod
    def _parse_matrix_3x3(content, start_index):
        lines = content[start_index:start_index+3]
        return np.array([
            [float(i) for i in lines[0].split()],  # First Camera Matrix Row
            [float(i) for i in lines[1].split()],  # Second Camera Matrix Row
            [float(i) for i in lines[2].split()]],  # Third Camera Matrix Row
            dtype=float)

    @staticmethod
    def _parse_matrix_4x4(content, start_index):
        lines = content[start_index:start_index+4]
        return np.array([
            [float(i) for i in lines[0].split()],   # First Camera Matrix Row
            [float(i) for i in lines[1].split()],      # Second Camera Matrix Row
            [float(i) for i in lines[2].split()],      # Third Camera Matrix Row
            [float(i) for i in lines[3].split()]],       # 4th Camera Matrix Row
            dtype=float)

    @staticmethod
    def parse_camera_and_object_trajectory_file(cam_and_obj_trajectory_fp):

        """
        Access the returned data structure with
        # is a numpy 4x4 array (homogeneous transformation)
        image_name_to_cam_obj_transf[index]['camera_pose']
        # is a numpy 4x4 array (homogeneous transformation)
        image_name_to_cam_obj_transf[index]['object_matrix_world']
        """
        logger.info('parse_camera_and_object_trajectory_file: ...')
        logger.info('cam_and_obj_trajectory_fp: ' + cam_and_obj_trajectory_fp)

        with open(cam_and_obj_trajectory_fp) as gt_file:
            gt_content = gt_file.readlines()

        lines_per_frame, num_lines_per_frame = TrajectoryFileHandler.compute_gt_lines_per_frame(gt_content)

        camera_object_trajectory = CameraObjectTrajectory()

        image_name_to_cam_obj_transf = OrderedDict()
        # we can not use enumerate here, since we do not know
        # if the first camera is actually part of the trajectory
        for content in lines_per_frame:

            logger.info('content: ' + str(content))
            image_name = content[0]

            cam_left = Camera()

            current_line_idx = 2
            if num_lines_per_frame > 11:
                camera_calibration_matrix = TrajectoryFileHandler._parse_matrix_3x3(
                    content, start_index=current_line_idx)
                cam_left.set_calibration(camera_calibration_matrix, radial_distortion=0)
                current_line_idx += 3

            camera_matrix_left_world = TrajectoryFileHandler._parse_matrix_4x4(
                content, start_index=current_line_idx)
            cam_left.set_4x4_cam_to_world_mat(camera_matrix_left_world)
            current_line_idx += 4

            baseline_or_object_trans_str = content[current_line_idx]        # current_line_idx = 9
            current_line_idx += 1
            #logger.vinfo('baseline_or_object_trans_str', baseline_or_object_trans_str)

            # Check for the stereo case (legacy fiel structure handling)
            if baseline_or_object_trans_str != 'Object to World transformation':

                if baseline_or_object_trans_str == 'None':
                    baseline = None
                else:
                    baseline = float(baseline_or_object_trans_str)

                camera_matrix_right_world = TrajectoryFileHandler._parse_matrix_4x4(
                    content, start_index=current_line_idx)

                # Check if stereo camera is defined using the baseline
                if baseline is not None and baseline > 0:
                    stereo_cam = StereoCamera(cam_left, baseline=baseline)
                    camera_object_trajectory.set_camera(image_name, stereo_cam)

                # Check if the stereo camera is defined using the second transformation matrix
                elif not np.allclose(camera_matrix_right_world, np.zeros((4,4), dtype=float)):

                    cam_right = Camera()
                    cam_right.set_calibration(camera_calibration_matrix, radial_distortion=0)
                    cam_right.set_4x4_cam_to_world_mat(camera_matrix_left_world)

                    stereo_cam = StereoCamera(left_camera=cam_left, right_camera=cam_right)
                    camera_object_trajectory.set_camera(image_name, stereo_cam)

                current_line_idx += 5       # 1 line for the stereo baseline + 4 lines for the matrix

            else:
                # if baseline and second matrix is the 0 matrix, we consider the camera as monocular
                camera_object_trajectory.set_camera(image_name, cam_left)

            object_matrix_world = TrajectoryFileHandler._parse_matrix_4x4(
                content, start_index=current_line_idx)

            # logger.vinfo('object_matrix_world', object_matrix_world)

            # TODO THIS IS NOT READY FOR USAGE
            # TODO SCALE IS ATM NOT HANDLED BY THE COORDINATE_FRAME_SYSTEM class
            #obj_coord_sys = CoordinateFrameSystem()
            #obj_coord_sys.set_4x4_cam_to_world_mat(object_matrix_world)
            #camera_object_trajectory.add_object_single_coord_system(image_name, obj_coord_sys)

            # FIXME Temporary solution
            camera_object_trajectory.set_object_matrix_world(
                image_name, object_matrix_world)

        logger.info('parse_camera_and_object_trajectory_file: Done')

        return camera_object_trajectory


    @staticmethod
    def camera_and_object_trajectory_file_to_cams(cam_and_obj_trajectory_fp):
        image_name_to_cam_obj_transf = \
            TrajectoryFileHandler.parse_camera_and_object_trajectory_file(
                cam_and_obj_trajectory_fp)


if __name__ == "__main__":

    path_to_ground_truth_file = ''

    index_to_ground_truth_data = \
        TrajectoryFileHandler.parse_camera_and_object_trajectory_file(
            path_to_ground_truth_file)

    for index in index_to_ground_truth_data:
        print(index)
        print(index_to_ground_truth_data[index][TrajectoryFileHandler.CAMERA_POSE])
        print(index_to_ground_truth_data[index][TrajectoryFileHandler.OBJECT_POSE])

