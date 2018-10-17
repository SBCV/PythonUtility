import numpy as np
import copy
from Utility.Types.Camera import Camera

class StereoCamera(object):
    def __init__(self,
                 left_camera=None,
                 baseline=None,
                 right_camera=None):

        self.left_camera = left_camera
        self.baseline = baseline
        self.right_camera = right_camera

        # there are two ways of providing stereo information
        # the user has to choose between these
        set_right_cam = right_camera is not None
        set_baseline = baseline is not None
        assert not set_right_cam or not set_baseline

        if set_right_cam:
            self.right_camera = right_camera

        if set_baseline:
            self.compute_right_camera(baseline)

    def is_monocular_cam(self):
        return False

    def get_baseline(self):
        return self.baseline

    def set_baseline(self, baseline):
        assert self.right_camera is None
        self.baseline = baseline

    def set_left_camera(self, left_cam):
        self.left_camera = left_cam

    def set_right_camera(self, right_cam):
        assert self.baseline is None
        self.right_camera = right_cam

    def compute_right_camera(self, baseline):
        assert self.left_camera is not None
        assert self.baseline is not None

        # Cameras should be identical, except for the camera center
        self.right_camera = copy.deepcopy(self.left_camera)

        # the second camera shows a shift along the x axis in camera coordinates
        right_center_left_cam_coords = np.asarray([baseline, 0, 0])
        right_center_world_coords = self.left_camera.cam_to_world_coord_single_coord(
            right_center_left_cam_coords)

        self.right_camera.set_camera_center_after_rotation(
            right_center_world_coords
        )

    def get_left_camera(self):
        return self.left_camera

    def get_right_camera(self):
        return self.right_camera

    def set_calibration(self, calibration_mat, radial_distortion):
        self.left_camera.set_calibration(
            calibration_mat, radial_distortion)
        self.right_camera.set_calibration(
            calibration_mat, radial_distortion)
