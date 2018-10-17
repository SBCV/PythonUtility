import numpy as np
from Utility.Classes.Frozen_Class import FrozenClass
from Utility.Math.Conversion import Conversion_Collection

class CoordinateFrameSystem(FrozenClass):

    def __init__(self):

        # center is the coordinate of the camera center with respect to the world coordinate frame
        self._center = np.array([0, 0, 0], dtype=float)              # t = -R C
        # the translation vector is the vector used to transform points in world coordinates to camera coordinates
        self._translation_vec = np.array([0, 0, 0], dtype=float)     # C = -R^T t

        # use for these attributes the getter and setter methods
        self._quaternion = np.array([0, 0, 0, 0], dtype=float)
        # for rotations the inverse is equal to the transpose
        # self._rotation_inv_mat = np.linalg.transpose(self._rotation_mat)
        self._rotation_mat = np.zeros((3, 3), dtype=float)

        self._scale = 1.0

    def set_scale(self, scale):
        self._scale = scale

    def get_scale(self,):
        return self._scale

    def is_rotation_mat_valid(self, some_mat):
        # TEST if rotation_mat is really a rotation matrix (i.e. det = -1 or det = 1)
        det = np.linalg.det(some_mat)
        is_close = np.isclose(det, 1) or np.isclose(det, -1)
        # if not is_close:
        #     logger.vinfo('some_mat', some_mat)
        #     logger.vinfo('determinante', det)
        return is_close

    def set_quaternion(self, quaternion):
        self._quaternion = quaternion
        # we must change the rotation matrixes as well
        self._rotation_mat = Conversion_Collection.quaternion_to_rotation_matrix(quaternion)

    def set_rotation_mat(self, rotation_mat):
        assert self.is_rotation_mat_valid(rotation_mat)
        self._rotation_mat = rotation_mat
        # we must change the quaternion as well
        self._quaternion = Conversion_Collection.rotation_matrix_to_quaternion(rotation_mat)

    def set_camera_center_after_rotation(self, center):
        assert self.is_rotation_mat_valid(self._rotation_mat)
        self._center = center
        self._translation_vec = - np.dot(self._rotation_mat, center)

    def set_camera_translation_vector_after_rotation(self, translation_vector):
        """
        :param translation_vector: trans_vec = -Rc
        :return:
        """
        assert self.is_rotation_mat_valid(self._rotation_mat)
        self._translation_vec = translation_vector
        self._center = - np.dot(self._rotation_mat.transpose(), translation_vector)

    def get_quaternion(self):
        return self._quaternion

    def get_rotation_mat(self):
        # Note:
        # self._rotation_mat.T or self._rotation_mat.transpose()
        # DO NOT CHANGE THE MATRIX
        return self._rotation_mat

    def get_translation_vec(self):
        return self._translation_vec

    def get_camera_center(self):
        return self._center

    # def set_4x4_world_to_cam_mat(self, world_to_cam_mat):
    #     # TODO Verify
    #     """
    #     https://en.wikipedia.org/wiki/Transformation_matrix#/media/File:2D_affine_transformation_matrix.svg
    #     This matrix can be used to convert points given in world coordinates into points given in camera coordinates
    #     M = [R      -Rc]
    #         [0      1]
    #
    #     https://en.wikipedia.org/wiki/Transformation_matrix#/media/File:2D_affine_transformation_matrix.svg
    #     """
    #     # TODO Verify
    #     rotation_mat = world_to_cam_mat[0:3, 0:3]
    #     self.set_rotation_mat(rotation_mat)
    #     # A = -Rc <=> -A R^T = c
    #     self.set_camera_center_after_rotation(-rotation_mat.transpose() * world_to_cam_mat[0:3, 3])

    def get_4x4_world_to_cam_mat(self):
        """
        This matrix can be used to convert points given in world coordinates into points given in camera coordinates
        M = [R      -Rc]
            [0      1],

        https://en.wikipedia.org/wiki/Transformation_matrix#/media/File:2D_affine_transformation_matrix.svg
        """
        homogeneous_mat = np.identity(4, dtype=float)
        homogeneous_mat[0:3, 0:3] = self.get_rotation_mat()
        homogeneous_mat[0:3, 3] = -self.get_rotation_mat().dot(self.get_camera_center())
        return homogeneous_mat

    def set_4x4_cam_to_world_mat(self, cam_to_world_mat):
        """
        This matrix can be used to convert points given in camera coordinates into points given in world coordinates
        M = [R^T    c]
            [0      1]

        https://en.wikipedia.org/wiki/Transformation_matrix#/media/File:2D_affine_transformation_matrix.svg
        Blender stores this matrix in "obj.matrix_world"
        """

        rotation_part = cam_to_world_mat[0:3, 0:3]
        translation_part = cam_to_world_mat[0:3, 3]

        # TODO Proper HAndling of scale
        # TODO APPLY SCALE ALSO TO TRANSLATION?
        #scale = TransformationCollection.transformation_matrix_to_scale(cam_to_world_mat)
        #rotation_part /= scale


        self.set_rotation_mat(rotation_part.transpose())
        self.set_camera_center_after_rotation(translation_part)

    def get_4x4_cam_to_world_mat(self):
        """
        This matrix can be used to convert points given in camera coordinates into points given in world coordinates
        M = [R^T    c]
            [0      1]
        :return:

        https://en.wikipedia.org/wiki/Transformation_matrix#/media/File:2D_affine_transformation_matrix.svg
        """
        homogeneous_mat = np.identity(4, dtype=float)
        homogeneous_mat[0:3, 0:3] = self.get_rotation_mat().transpose()
        homogeneous_mat[0:3, 3] = self.get_camera_center()
        return homogeneous_mat

    # ============================= HOMOGENEOUS Transformation Between Coordinate Frames ==============================

    def hom_world_to_cam_coord_single_coord(self, world_coord):
        point_cam_coord = self.get_4x4_world_to_cam_mat().dot(np.append(world_coord, [1]))[0:3]
        return point_cam_coord

    def hom_cam_to_world_coord_single_coord(self, cam_coords):
        point_world_coord = self.get_4x4_cam_to_world_mat().dot(np.append(cam_coords, [1]))[0:3]
        return point_world_coord

    # ============================= INHOMOGENEOUS Transformation Between Coordinate Frames ==============================

    def world_to_cam_coord_multiple_coords(self, world_coords, none_values_allowed=True):
        cam_coords = []
        for world_coord in world_coords:
            if world_coord is None:
                if none_values_allowed:
                    cam_coord = None
                else:
                    assert False
            else:
                cam_coord = self.world_to_cam_coord_single_coord(world_coord)
            cam_coords.append(cam_coord)
        return cam_coords

    def world_to_cam_coord_single_coord(self, world_coord):
        cam_coord = self.get_rotation_mat().dot(world_coord - self.get_camera_center())
        return cam_coord

    def cam_to_world_coord_multiple_coords(self, cam_coords):
        world_coords = []
        for cam_coord in cam_coords:
            world_coord = self.cam_to_world_coord_single_coord(cam_coord)
            world_coords.append(world_coord)
        return world_coords

    def cam_to_world_coord_single_coord(self, cam_coord):

        # my_array.T returns the transpose and does not change my_array

        rotation_transposed = np.transpose(self.get_rotation_mat())
        # transform the vector (without translation) and adding translation
        world_coord = rotation_transposed.dot(cam_coord.T) + self.get_camera_center()
        return world_coord

    def cam_direction_to_world_direction(self, cam_dir):
        rotation_transposed = np.transpose(self.get_rotation_mat())
        world_dir = rotation_transposed.dot(cam_dir.T)
        return world_dir