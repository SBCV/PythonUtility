import numpy as np
import math


def extract_scale(transformation_matrix):
    s_x, s_y, s_z = extract_axis_scales(
        transformation_matrix)
    assert np.isclose(s_x, s_y) and np.isclose(s_x, s_z) and np.isclose(s_y, s_z)
    return s_x


def extract_axis_scales(transformation_matrix):

    # https://www.gamedev.net/forums/topic/467665-decomposing-rotationtranslationscale-from-matrix/
    #   see last post

    # https://math.stackexchange.com/questions/237369/given-this-transformation-matrix-how-do-i-decompose-it-into-translation-rotati
    #   Rationale behind this approach:
    #       The rotation matrix contains the base vectors of the new coordinate system
    #       If they have a length different than one, scaling is applied

    # https://docs.blender.org/api/2.70/mathutils.html#mathutils.Matrix.to_scale
    #   Note: This method does not return negative a scale on any axis because
    #         it is not possible to obtain this data from the matrix alone.

    rot_scale_part = transformation_matrix[0:3, 0:3]
    rot_scale_part_trans = rot_scale_part.transpose()

    first_column_vec = rot_scale_part_trans[0]
    second_column_vec = rot_scale_part_trans[1]
    third_column_vec = rot_scale_part_trans[2]

    s_x = np.linalg.norm(first_column_vec)
    s_y = np.linalg.norm(second_column_vec)
    s_z = np.linalg.norm(third_column_vec)

    return s_x, s_y, s_z


def vector_to_spherical_coords(dir_vec):

    # represent the direction vector in spherical coordinates
    # using the ISO convention (radius r, inclination theta, azimuth phi)

    """
    Theta:
        * is in the interval of in [0, pi]
        * lies between the vector and the z axis

    Phi:
        * phi is in the interval (-pi, pi)
        * lies in the x-y-plane
    :param dir_vec:
    :return:
    """

    # There are special points, for which the angular coordinates are not unique.
    # The angle phi is not defined for points on the z axis.
    # For origin the angle theta is arbitrary.
    # To achieve uniqueness, one might define for
    # points on the z axis phi = 0 and for the origin theta = 0

    x = dir_vec[0]
    y = dir_vec[1]
    z = dir_vec[2]

    r = np.linalg.norm(dir_vec)

    # TODO check the coordinate system
    # Currently we asume that z points upwards

    theta = math.acos(float(z) / float(r))  # theta in [0, pi]
    assert(0 < theta < math.pi)
    phi = math.atan2(float(y), float(x))  # phi in (-pi, pi)
    assert (-math.pi < theta < math.pi)

    return r, theta, phi,


def spherical_coords_to_vector(r, theta, phi):
    """See the description of vector_to_spherical_coords
    for a definition of the angles theta and phi """

    x = r * math.sin(theta) * math.cos(phi)
    y = r * math.sin(theta) * math.sin(phi)
    z = r * math.cos(theta)
    return np.array([x, y, z], dtype=float)


def vsfm_coordinates_to_standard_coordinates(vsfm_coordinates):
    """
    For testing purposes:
    vsfm world coordinate system (at least for some examples):
        * x points backwards
        * y points top
        * z points right
    standard world coordinate system ()
        * x points in front
        * y points to the right
        * z points to the top

    :return:
    """

    x = -1 * vsfm_coordinates[0]
    y = vsfm_coordinates[2]
    z = vsfm_coordinates[1]
    return np.array([x,y,z])


def quaternion_to_rotation_matrix(q):

    """
    Original C++ Method defined in  pba/src/pba/DataInterface.h

    Comments of ChangCHang to visualfsm's coordinate system
    http://www.euclideanspace.com/maths/geometry/rotations/index.htm
    http://www.euclideanspace.com/maths/geometry/rotations/conversions/index.htm

    take a look at the  parallel bundle adjustment (pba) code (used by visualsfm)
    http://grail.cs.washington.edu/projects/mcba/
    in DataInterface.h the corresponding conversion function is 'SetQuaternionRotation'
    """

    qq = math.sqrt(q[0]*q[0]+q[1]*q[1]+q[2]*q[2]+q[3]*q[3])
    qw = qx = qy = qz = 0
    if qq > 0:  # NORMALIZE THE QUATERNION
        qw = q[0]/qq
        qx = q[1]/qq
        qy = q[2]/qq
        qz = q[3]/qq
    else:
        qw = 1
        qx = qy = qz = 0

    m = np.zeros((3, 3), dtype=float)
    m[0][0] = float(qw*qw + qx*qx- qz*qz- qy*qy )
    m[0][1] = float(2*qx*qy -2*qz*qw )
    m[0][2] = float(2*qy*qw + 2*qz*qx)
    m[1][0] = float(2*qx*qy+ 2*qw*qz)
    m[1][1] = float(qy*qy+ qw*qw - qz*qz- qx*qx)
    m[1][2] = float(2*qz*qy- 2*qx*qw)
    m[2][0] = float(2*qx*qz- 2*qy*qw)
    m[2][1] = float(2*qy*qz + 2*qw*qx )
    m[2][2] = float(qz*qz+ qw*qw- qy*qy- qx*qx)
    return m


def rotation_matrix_to_quaternion(m):

    """
    Original C++ Method defined in  pba/src/pba/DataInterface.h
    """

    q = np.array([0, 0, 0, 0], dtype=float)

    q[0] = 1 + m[0][0] + m[1][1] + m[2][2]
    if q[0] > 0.000000001:
        q[0] = math.sqrt(q[0]) / 2.0
        q[1] = (m[2][1] - m[1][2]) / ( 4.0 * q[0])
        q[2] = (m[0][2] - m[2][0]) / ( 4.0 * q[0])
        q[3] = (m[1][0] - m[0][1]) / ( 4.0 * q[0])
    else:
        if m[0][0] > m[1][1] and m[0][0] > m[2][2]:
            s = 2.0 * math.sqrt(1.0 + m[0][0] - m[1][1] - m[2][2])
            q[1] = 0.25 * s
            q[2] = (m[0][1] + m[1][0]) / s
            q[3] = (m[0][2] + m[2][0]) / s
            q[0] = (m[1][2] - m[2][1]) / s

        elif m[1][1] > m[2][2]:
            s = 2.0 * math.sqrt(1.0 + m[1][1] - m[0][0] - m[2][2])
            q[1] = (m[0][1] + m[1][0]) / s
            q[2] = 0.25 * s
            q[3] = (m[1][2] + m[2][1]) / s
            q[0] = (m[0][2] - m[2][0]) / s
        else:
            s = 2.0 * math.sqrt(1.0 + m[2][2] - m[0][0] - m[1][1])
            q[1] = (m[0][2] + m[2][0]) / s
            q[2] = (m[1][2] + m[2][1]) / s
            q[3] = 0.25 * s
            q[0] = (m[0][1] - m[1][0]) / s
    return q


def invert_y_and_z_axis(input_matrix_or_vector):
    """
    This Function inverts the y and the z coordinates in the corresponding matrix and vector entries
    (invert y and z axis <==> rotation by 180 degree around the x axis)

    For the matrix multiplication holds:
    |m11 m12 m13|    |x|       |m11 x + m12 y + m13 z|
    |m21 m22 m23|    |y|   =   |m21 x + m22 y + m23 z|
    |m31 m32 m33|    |z|       |m31 x + m32 y + m33 z|
    Therefore exactly the y and z rows must be inverted!

    For example VisualSFM and Bundler use coordinate systems, which differ in the y and z coordinate
    Both (VisualSfM and Bundler) are left hand coordinate systems
    """

    output_matrix_or_vector = input_matrix_or_vector.copy()
    output_matrix_or_vector[1] = -output_matrix_or_vector[1]
    output_matrix_or_vector[2] = -output_matrix_or_vector[2]

    return output_matrix_or_vector


def convert_camera_matrix_lhs_rhs(camera_matrix):

    """
    This converts a left hand coordinates system to
    a right hand coordinate system and vice versa

    # opengl_camera == blender_camera == vtk_camera

    :param camera_matrix:
    :return:
    """

    gt_camera_rotation_inverse = camera_matrix.copy()[0:3, 0:3]
    gt_camera_rotation = gt_camera_rotation_inverse.T

    # Important: Blender uses a blender_camera coordinate frame system,
    # which looks down the negative z-axis
    # This contradicts the camera coordinate systems used by most SfM camera coordinate systems
    # Thus rotate the camera rotation matrix by 180 degrees (i.e. invert the y and z axis)
    gt_camera_rotation = invert_y_and_z_axis(gt_camera_rotation)
    gt_camera_rotation_inverse = gt_camera_rotation.T

    rotated_camera_matrix_around_x_by_180 = camera_matrix.copy()
    rotated_camera_matrix_around_x_by_180[0:3, 0:3] = gt_camera_rotation_inverse
    return rotated_camera_matrix_around_x_by_180


def convert_opengl_to_computer_vision_camera(opengl_camera_matrix):
    return convert_camera_matrix_lhs_rhs(opengl_camera_matrix)


def convert_computer_vision_to_opengl_camera(computer_vision_camera_matrix):
    return convert_camera_matrix_lhs_rhs(computer_vision_camera_matrix)


def compute_camera_coordinate_system_translation_vector(center, rotation_mat):

    """
    x_cam = R (X - C) = RX - RC == RX + t
    <==> t = -RC
    """

    t = np.zeros(3, dtype=float)
    for j in range(0, 3):
        t[j] = -float(
            rotation_mat[j][0] * center[0] +
            rotation_mat[j][1] * center[1] +
            rotation_mat[j][2] * center[2])
    return t

