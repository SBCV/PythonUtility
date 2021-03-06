import numpy as np
import math
import scipy

from Utility.Math.ext.transforms3d.transforms3d.affines import decompose

def decompose_affine_transformation(trans_mat):

    # See Multiple View Geometry p. 39 and p.42

    # https://github.com/matthew-brett/transforms3d
    trans, rot, scales, shear = decompose(trans_mat)
    return trans, rot, scales, shear

def decompose_similarity_transformation(trans_mat):

    # See Multiple View Geometry p. 39 and p.42

    trans = np.transpose(trans_mat)[-1][:-1]
    scales = extract_axis_scales(trans_mat)
    # the normalization is important to remove the scaling
    rot_scale_part = trans_mat[0:-1, 0:-1]
    rot_scale_part_norm = np.linalg.norm(rot_scale_part)
    rot_scale_part_normalized = rot_scale_part / rot_scale_part_norm
    rot = rot_scale_part_normalized
    return trans, rot, scales


def extract_scale(transformation_matrix):
    scales = extract_axis_scales(
        transformation_matrix)

    for scale_1, scale_2 in zip(scales, scales[1:]):
        assert np.isclose(scale_1, scale_2)

    return scales[0]


def extract_axis_scales(transformation_matrix):

    # https://math.stackexchange.com/questions/237369/given-this-transformation-matrix-how-do-i-decompose-it-into-translation-rotati
    #   Rationale behind this approach:
    #       The rotation matrix contains the base vectors of the new coordinate system
    #       If they have a length different than one, scaling is applied

    # https://docs.blender.org/api/2.70/mathutils.html#mathutils.Matrix.to_scale
    #   Note: This method does not return negative a scale on any axis because
    #         it is not possible to obtain this data from the matrix alone.

    # https://www.researchgate.net/publication/238189035_General_Formula_for_Extracting_the_Euler_Angles
    #

    rot_scale_part = transformation_matrix[0:-1, 0:-1]
    rot_scale_part_trans = rot_scale_part.transpose()

    scales = []
    for column_vec in rot_scale_part_trans:
        scales.append(np.linalg.norm(column_vec))

    return scales


def rotation_matrix_2d_to_angle(rotation_mat, degrees):

    # Use the scipy implementation to deal with ill posed input data

    # Note: A 2D image rotation is equivalent to a ration around the axis orthogonal to the image plane
    # Thus: The image rotation corresponds to the rotation around the z euler angle

    angles = rotation_matrix_to_euler_angles(rotation_mat, degrees)
    return angles[2]


def rotation_matrix_to_euler_angles(rotation_mat, degrees):

    # Scipy uses the following algorithm to compute euler angles
    #   https://www.researchgate.net/publication/238189035_General_Formula_for_Extracting_the_Euler_Angles

    assert scipy.__version__ >= '1.2.1'
    from scipy.spatial.transform import Rotation as R  # requires at least scipy 1.2.1

    if rotation_mat.shape == (3, 3):
        scipy_rot = R.from_dcm(rotation_mat)
    elif rotation_mat.shape == (2, 2):
        rotation_mat_3d = np.identity(3)
        rotation_mat_3d[:2,:2] = rotation_mat
        scipy_rot = R.from_dcm(rotation_mat_3d)
    else:
        assert False

    return scipy_rot.as_euler('xyz', degrees=degrees)


def angle_to_rotation_matrix_2d(theta, in_degree=False):
    # https://docs.scipy.org/doc/scipy/reference/generated/scipy.spatial.transform.Rotation.from_euler.html#scipy.spatial.transform.Rotation.from_euler
    if in_degree:
        theta = np.radians(theta)
    cos_theta, sin_theta = np.cos(theta), np.sin(theta)
    return np.array(((cos_theta, -sin_theta),
                     (sin_theta, cos_theta)))


def angles_to_rotation_matrix_3d(theta, phi, psi, in_degree):
    # https://docs.scipy.org/doc/scipy/reference/generated/scipy.spatial.transform.Rotation.from_euler.html#scipy.spatial.transform.Rotation.from_euler
    if in_degree:
        theta = np.radians(theta)
        phi = np.radians(phi)
        psi = np.radians(psi)
    cos_theta, sin_theta = np.cos(theta), np.sin(theta)
    cos_phi, sin_phi = np.cos(phi), np.sin(phi)
    cos_psi, sin_psi = np.cos(psi), np.sin(psi)
    return np.array((
        (cos_phi * cos_psi, cos_psi * sin_theta * sin_phi - cos_theta * sin_psi, cos_theta * cos_psi * sin_phi + sin_theta * sin_psi),
        (cos_phi * sin_psi, cos_theta * cos_psi + sin_theta * sin_phi * sin_psi, cos_theta * sin_phi * sin_psi - cos_psi * sin_theta),
        (-sin_phi,          cos_phi * sin_theta,                                 cos_theta * cos_phi)))



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

