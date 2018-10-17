from Utility.Types.Ray import Ray
from Utility.Types.Point import Point
from Utility.Logging_Extension import logger
import numpy as np
import math

class GeometryCollection:

    epsilon = 0.000001

    @staticmethod
    def compute_centroid_coord(points):
        centroid = np.array([0,0,0], dtype=float)
        if all([isinstance(point, Point) for point in points]):
            for point in points:
                centroid += point.coord
        else:
            for point in points:
                centroid += point
        centroid /= float(len(points))
        return centroid

    @staticmethod
    def unit_vector(vector):
        """ Returns the unit vector of the vector.  """
        return vector / np.linalg.norm(vector)

    @staticmethod
    def angle_between_rad(v1, v2):

        # VARIANTE 1

        """ Returns the angle in radians between vectors 'v1' and 'v2'::

                angle_between((1, 0, 0), (0, 1, 0))
                1.5707963267948966
                angle_between((1, 0, 0), (1, 0, 0))
                0.0
                angle_between((1, 0, 0), (-1, 0, 0))
                3.141592653589793
        """
        v1_u = GeometryCollection.unit_vector(v1)
        v2_u = GeometryCollection.unit_vector(v2)
        return np.arccos(np.clip(np.dot(v1_u, v2_u), -1.0, 1.0))


        # # VARIANTE 2
        # https://de.mathworks.com/matlabcentral/answers/16243-angle-between-two-vectors-in-3d
        # return np.arctan2(np.linalg.norm(np.cross(v1, v2)), np.dot(v1, v2))

    @staticmethod
    def rotation_matrix(rotation_axis, angle):
        """
        Return the rotation matrix associated with counterclockwise rotation about
        the given axis by theta radians.
        """
        rotation_axis = np.asarray(rotation_axis)
        rotation_axis = rotation_axis / math.sqrt(np.dot(rotation_axis, rotation_axis))
        a = math.cos(angle / 2.0)
        b, c, d = -rotation_axis * math.sin(angle / 2.0)
        aa, bb, cc, dd = a * a, b * b, c * c, d * d
        bc, ad, ac, ab, bd, cd = b * c, a * d, a * c, a * b, b * d, c * d
        return np.array([[aa + bb - cc - dd, 2 * (bc + ad), 2 * (bd - ac)],
                         [2 * (bc - ad), aa + cc - bb - dd, 2 * (cd + ab)],
                         [2 * (bd + ac), 2 * (cd - ab), aa + dd - bb - cc]])

    @staticmethod
    def is_rotation_matrix(R):
        # Checks if a matrix is a valid rotation matrix.
        # https://www.learnopencv.com/rotation-matrix-to-euler-angles/
        Rt = np.transpose(R)
        shouldBeIdentity = np.dot(Rt, R)
        I = np.identity(3, dtype = R.dtype)
        n = np.linalg.norm(I - shouldBeIdentity)
        return n < 1e-6

    @staticmethod
    def rotation_matrix_to_euler_angles(R):
        # Calculates rotation matrix to euler angles
        # The result is the same as MATLAB except the order
        # of the euler angles ( x and z are swapped ).

        # https://www.learnopencv.com/rotation-matrix-to-euler-angles/

        assert(GeometryCollection.is_rotation_matrix(R))

        sy = math.sqrt(R[0,0] * R[0,0] + R[1,0] * R[1,0])

        singular = sy < 1e-6

        if not singular:
            x = math.atan2(R[2,1] , R[2,2])
            y = math.atan2(-R[2,0], sy)
            z = math.atan2(R[1,0], R[0,0])
        else :
            x = math.atan2(-R[1,2], R[1,1])
            y = math.atan2(-R[2,0], sy)
            z = 0

        return np.array([x, y, z])

    @staticmethod
    def compute_ray_plane_intersection(ray, plane, color_intersection_point=[0, 255, 0]):
        """
        Note: A plane has no spatial margin.
        If a spatial margin is required use "compute_rays_triangles_closest_intersection_points()"
        :param ray:
        :param plane:
        :param color_intersection_point:
        :return: Point, t
        """

        # https://en.wikipedia.org/wiki/Line%E2%80%93plane_intersection
        assert ray is not None

        # the closest intersection is the intersection with the smallest t value
        t = None

        ray_dir_dot_plane_normal = (ray.dir_vec).dot(plane.normal_vec)
        if ray_dir_dot_plane_normal != 0:   # check parallel case
            t = (plane.pos_vec - ray.pos_vec).dot(plane.normal_vec) / float(ray_dir_dot_plane_normal)

        if t is not None:
            return Point(coord=ray.pos_vec + t * ray.dir_vec, color=color_intersection_point), t
        else:
            return None, None

    @staticmethod
    def compute_rays_triangles_closest_intersection_points(rays,
                                                           triangles,
                                                           color_intersection_points=[0, 255, 0]):
        intersection_points = []
        for ray in rays:
            intersection_point, _ = GeometryCollection.compute_ray_triangles_closest_intersection_point(
                ray, triangles, color_intersection_point=color_intersection_points)
            intersection_points.append(intersection_point)
        return intersection_points

    @staticmethod
    def compute_ray_triangles_closest_intersection_point(ray,
                                                         triangles,
                                                         color_intersection_point=[0, 255, 0]):
        """
        Returns the parameter of the closest intersection of ray with any triangle in triangles and the corresponding
        intersection point.
        :param ray:
        :param triangles:
        :param color_intersection_point:
        :return:
        """

        assert ray is not None

        # the closest intersection is the intersection with the smallest t value
        t = None
        # print('len(triangles)')
        # print(len(triangles))
        for triangle in triangles:
            #print(triangle)
            t_temp, u_temp, v_temp = GeometryCollection.compute_ray_triangle_intersection_intersecting_parameter(
                ray, triangle)
            # check if we found a valid intersection
            if t_temp is not None:
                if t is None:
                    t = t_temp
                elif t is not None and t_temp < t:
                    t = t_temp

        if t is not None:
            return Point(coord=ray.pos_vec + t * ray.dir_vec, color=color_intersection_point), t
        else:
            return None, None


    @staticmethod
    def compute_ray_triangle_intersection_intersecting_parameter(ray, triangle):
        """
        Mueller-Trumbore-Algorithm:
            http://cg-dev.ltas.ulg.ac.be/inf/Fast%20MinimumStorage%20RayTriangle%20Intersection.pdf

        The following implementation basaes on the c++ implementation provided in the paper

        returns: t is the distance to the plane in which the triangle lies and |(u, v)|
        represents the coordinates inside the triangle
        """

        # find vectors for two edges sharing vert0
        edge1 = triangle.vertex_1 - triangle.vertex_0
        edge2 = triangle.vertex_2 - triangle.vertex_0

        # begin calculating determinant, also used to calculate U parameter
        pvec = np.cross(ray.dir_vec, edge2)

        # if determinant is near zero, ray lies in plane of triangle
        det = np.dot(edge1, pvec)

        # TODO implement culling branch

        # the non-culling branch
        if -GeometryCollection.epsilon < det < GeometryCollection.epsilon:
            return None, None, None

        inv_det = 1.0/det

        # calculate distance from vert0 to ray origin
        tvec = ray.pos_vec - triangle.vertex_0

        # calculate U paramter and test bounds
        u = np.dot(tvec, pvec) * inv_det
        if u < 0.0 or u > 1.0:
            return None, None, None

        # prepare to test V parameter
        qvec = np.cross(tvec, edge1)

        # calculate V parameter and test bounds
        v = np.dot(ray.dir_vec, qvec) * inv_det
        if v < 0.0 or u + v > 1.0:
            return None, None, None

        # calculate t, ray intersect triangle
        t = np.dot(edge2, qvec) * inv_det

        # u and v are barycentric coordinates
        # (u,v) can be used for texture mapping, normal interpolation, color interpolation, etc

        return t, u, v

    @staticmethod
    def compute_line_line_distance(cam_1_center,
                                   cam_1_dir_vec,
                                   cam_2_center,
                                   cam_2_dir_vec,
                                   comp_eps=0.00001):

        mu_1, mu_2 = GeometryCollection.compute_line_line_distance_parameters(
            cam_1_center, cam_1_dir_vec,
            cam_2_center, cam_2_dir_vec,
            comp_eps=comp_eps)
        if mu_1 is None or mu_2 is None:
            return None

        p1 = cam_1_center + mu_1 * cam_1_dir_vec
        p2 = cam_2_center + mu_2 * cam_2_dir_vec

        return np.linalg.norm(p1 - p2)


    @staticmethod
    def compute_line_line_distance_parameters(cam_1_center,
                                              cam_1_dir_vec,
                                              cam_2_center,
                                              cam_2_dir_vec,
                                              comp_eps=0.00001):
        """
        The distance between two lines is the closest distance between any point pair lying on the lines.

        Idea taken from: http://paulbourke.net/geometry/pointlineplane/
            - The shortest line segment between the two lines will be perpendicular to the two lines.

        :return:
        """

        cam_2_to_cam_1 = [0, 0, 0]
        cam_2_to_cam_1[0] = cam_1_center[0] - cam_2_center[0]
        cam_2_to_cam_1[1] = cam_1_center[1] - cam_2_center[1]
        cam_2_to_cam_1[2] = cam_1_center[2] - cam_2_center[2]

        if abs(cam_1_dir_vec[0]) < comp_eps and \
                        abs(cam_1_dir_vec[1]) < comp_eps and \
                        abs (cam_1_dir_vec[2]) < comp_eps \
                or abs(cam_2_dir_vec[0]) < comp_eps and \
                                abs(cam_2_dir_vec[1]) < comp_eps and \
                                abs(cam_2_dir_vec[2]) < comp_eps:
            #logger.info('Could not compute LineLineIntersect!')
            return None, None
        else:
            d1343 = cam_2_to_cam_1[0] * cam_2_dir_vec[0] + \
                    cam_2_to_cam_1[1] * cam_2_dir_vec[1] + \
                    cam_2_to_cam_1[2] * cam_2_dir_vec[2]
            d4321 = cam_2_dir_vec[0] * cam_1_dir_vec[0] + \
                    cam_2_dir_vec[1] * cam_1_dir_vec[1] + \
                    cam_2_dir_vec[2] * cam_1_dir_vec[2]
            d1321 = cam_2_to_cam_1[0] * cam_1_dir_vec[0] + \
                    cam_2_to_cam_1[1] * cam_1_dir_vec[1] + \
                    cam_2_to_cam_1[2] * cam_1_dir_vec[2]
            d4343 = cam_2_dir_vec[0] * cam_2_dir_vec[0] + \
                    cam_2_dir_vec[1] * cam_2_dir_vec[1] + \
                    cam_2_dir_vec[2] * cam_2_dir_vec[2]
            d2121 = cam_1_dir_vec[0] * cam_1_dir_vec[0] + \
                    cam_1_dir_vec[1] * cam_1_dir_vec[1] + \
                    cam_1_dir_vec[2] * cam_1_dir_vec[2]

            denom = d2121 * d4343 - d4321 * d4321
            if abs(denom) < comp_eps:
                #logger.info('Could not compute LineLineIntersect!')
                return None, None
            else:
                numer = d1343 * d4321 - d1321 * d4343

                # the scalar parameters, which define the point on each line, which is shortest to the other line
                mu_1 = numer / float(denom)
                mu_2 = (d1343 + d4321 * mu_1) / float(d4343)

                return mu_1, mu_2

    @staticmethod
    def compute_line_point_distance(ray_pos, ray_dir, point_pos):

        #logger.info('compute_line_point_distance: ...')
        # http://mathworld.wolfram.com/Point-LineDistance3-Dimensional.html
        distance = np.linalg.norm(np.cross(ray_dir, ray_pos - point_pos)) / float(np.linalg.norm(ray_dir))
        #logger.info('compute_line_point_distance: Done')
        return distance


    @staticmethod
    def compute_line_point_distance_parameter(ray_pos, ray_dir, point_pos):
        # TODO TEST THIS METHOD
        assert False
        # http://mathworld.wolfram.com/Point-LineDistance3-Dimensional.html
        diff_pos = ray_pos - point_pos
        ray_norm = float(np.linalg.norm(ray_dir))
        t_parameter = - diff_pos * ray_dir / (ray_norm * ray_norm)
        return t_parameter

    @staticmethod
    def compute_plane_point_distance(plane, point):
        # Utility/Types/Plane.py
        return plane.normal_vec.dot(point - plane.pos_vec)

    @staticmethod
    def generate_points_along_rays(ray_list, color=np.array([255, 0 , 0]), amount_steps=100, scale=None):

        if scale is None:
            # use the distance of the rays to determine a scale value

            min_distance = float('inf')
            for index, ray_1 in enumerate(ray_list):
                min_ray_ray_distance = float('inf')
                for ray_2 in ray_list[index:]:      # Consider only the remaining
                    line_line_distance = GeometryCollection.compute_line_line_distance(
                        ray_1.pos_vec, ray_1.dir_vec, ray_2.pos_vec, ray_2.dir_vec)
                    if line_line_distance:
                        min_ray_ray_distance = min(min_ray_ray_distance, line_line_distance)
                min_distance = min(min_distance, min_ray_ray_distance)
            logger.info('min_distance: ' + str(min_distance))

            scale = min_distance

        points_along_rays = []
        for ray in ray_list:
            points_along_rays += GeometryCollection.generate_points_along_ray(ray, color, amount_steps, scale)
        return points_along_rays


    @staticmethod
    def generate_points_along_ray(ray, color=np.array([255, 0 , 0]), amount_steps=100, scale=1.0):
        points_along_ray = []

        # the length of the direction vector is the distance in which we need too draw points
        length = np.linalg.norm(ray.dir_vec)
        step_width = length / float(amount_steps)

        ray_direction_vector_normalized = ray.dir_vec / np.linalg.norm(ray.dir_vec)

        # we need amount_steps+1 to cover also the start and the end point
        for step in range(amount_steps+1):
            coords = ray.pos_vec + float(step_width) * float(step) * ray_direction_vector_normalized * float(scale)
            point = Point(coord=coords, color=color)
            points_along_ray.append(point)
        return points_along_ray

