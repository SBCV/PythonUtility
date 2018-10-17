from collections import OrderedDict

from Utility.Logging_Extension import logger
from Utility.Classes.Frozen_Class import FrozenClass
from Utility.Types.Camera import Camera
from Utility.Types.Stereo_Camera import StereoCamera

class CameraObjectTrajectory(FrozenClass):

    """
    This class stores / manages the information of a scene.
    For each frame
        the (stereo) camera intrinsics / extrinsics
        the object pose
    """

    def __init__(self):

        self._frame_name_to_camera = OrderedDict()
        self._frame_name_to_object_matrix_world = OrderedDict()

    def set_camera(self, frame_name, camera):
        assert isinstance(camera, Camera) or isinstance(camera, StereoCamera)
        self._frame_name_to_camera[frame_name] = camera

    def get_camera(self, frame_name):
        return self._frame_name_to_camera[frame_name]

    def has_camera(self, frame_name):
        return frame_name in self._frame_name_to_camera.keys()

    def set_object_matrix_world(self, frame_name, matrix_world):
        self._frame_name_to_object_matrix_world[frame_name] = matrix_world

    def get_object_matrix_world(self, frame_name):
        return self._frame_name_to_object_matrix_world[frame_name]

    def __str__(self):
        return str(self._frame_name_to_camera) + ' ' + str(self._frame_name_to_object_matrix_world)

    def get_frame_names_sorted(self):

        names_1 = self._frame_name_to_camera.keys()
        names_2 = self._frame_name_to_object_matrix_world.keys()

        # This is not necessarily always true
        # Camera could have been registered with background but not with object or vice versa
        #assert names_1 == names_2

        return sorted(list(set(names_1).union(set(names_2))))

    def get_incomplete_frame_names_sorted(self):

        # Incomplete frames are either missing in names_1 or names_2

        names_1 = self._frame_name_to_camera.keys()
        names_2 = self._frame_name_to_object_matrix_world.keys()

        return sorted(set(names_1).symmetric_difference(set(names_2)))

