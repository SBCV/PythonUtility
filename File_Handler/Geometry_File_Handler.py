import numpy as np

from Utility.File_Handler.PLY_File_Handler import PLYFileHandler
from Utility.Types.Face import Face
from Utility.Types.Point import Point
from Utility.Logging_Extension import logger


# https://github.com/dranjan/python-plyfile

class GeometryFileHandler:

    @staticmethod
    def save_triangles_in_ply_file(output_path_to_file, triangles):
        logger.info('save_triangles_in_ply_file: ...')
        points = []
        faces = []
        for triangle_index, triangle in enumerate(triangles):
            assert isinstance(triangle.vertex_0, np.ndarray) \
                   and isinstance(triangle.vertex_1, np.ndarray) \
                   and isinstance(triangle.vertex_2,np.ndarray)

            # FIXME this will result in duplicated points (in the ply file)
            points += [Point(triangle.vertex_0), Point(triangle.vertex_1), Point(triangle.vertex_2)]
            # FIXME these face indices refer to duplicated points
            faces.append(Face(
                initial_indices=[3*triangle_index, 3*triangle_index+1, 3*triangle_index+2]))

        PLYFileHandler.write_ply_file(
            ofp=output_path_to_file,
            vertices=points,
            faces=faces)

        logger.info('save_triangles_in_ply_file: Done')

    @staticmethod
    def save_single_triangle_in_ply_file(output_path_to_file, corner_0, corner_1, corner_2):
        assert isinstance(corner_0, np.ndarray) and \
               isinstance(corner_1, np.ndarray) and \
               isinstance(corner_2, np.ndarray)
        points = [Point(corner_0), Point(corner_1), Point(corner_2)]

        # the first 3 points are building the triangle
        faces = [Face(initial_indices=[0, 1, 2])]

        PLYFileHandler.write_ply_file(ofp=output_path_to_file,
                                      vertices=points,
                                      faces=faces)

    @staticmethod
    def save_rectangle_in_ply_file(output_path_to_file, corner_0, corner_1, corner_2, corner_3):
        assert isinstance(corner_0, np.ndarray) and \
               isinstance(corner_1, np.ndarray) and \
               isinstance(corner_2, np.ndarray) is isinstance(corner_3, np.ndarray)
        points = [Point(corner_0), Point(corner_1), Point(corner_2), Point(corner_3)]

        # represent the rectangle by 2 triangles
        face_1 = Face(initial_indices=[0, 1, 2])
        face_2 = Face(initial_indices=[3, 2, 1])
        faces = [face_1, face_2]

        PLYFileHandler.write_ply_file(ofp=output_path_to_file,
                                      vertices=points,
                                      faces=faces)


    @staticmethod
    def approximate_plane_by_corners(pos_vec, dir_vec_1, dir_vec_2, size_ratio=1):

        # returns numpy arrays

        assert isinstance(pos_vec, np.ndarray) and isinstance(dir_vec_1, np.ndarray) and isinstance(dir_vec_2, np.ndarray)

        # build a rectangle around the position vector
        corner_0 = pos_vec + size_ratio * dir_vec_1 - size_ratio * dir_vec_2
        corner_1 = pos_vec + size_ratio * dir_vec_1 + size_ratio * dir_vec_2
        corner_2 = pos_vec - size_ratio * dir_vec_1 - size_ratio * dir_vec_2
        corner_3 = pos_vec - size_ratio * dir_vec_1 + size_ratio * dir_vec_2
        return corner_0, corner_1, corner_2, corner_3

    @staticmethod
    def save_plane_in_ply_file(output_path_to_file, pos_vec, dir_vec_1, dir_vec_2, size_ratio=1):

        corner_0, corner_1, corner_2, corner_3 = GeometryFileHandler.approximate_plane_by_corners(
            pos_vec, dir_vec_1, dir_vec_2, size_ratio)
        GeometryFileHandler.save_rectangle_in_ply_file(
            output_path_to_file, corner_0, corner_1, corner_2, corner_3)


if __name__ == '__main__':
    output_path_to_file = ''

    pos_vec = Point(coord=np.array([0, 0, 0]), color=[255, 0, 0])
    dir_vec_1 = Point(coord=[0, 1, 0], color=[0, 255, 0])
    dir_vec_2 = Point(coord=[0, 0, 1], color=[0, 0, 255])

    GeometryFileHandler.save_plane_in_ply_file(output_path_to_file, pos_vec, dir_vec_1, dir_vec_2)

