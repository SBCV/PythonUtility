import os
import dill
from Utility.Types.Point import Point, Measurement
from Utility.Logging_Extension import logger

from collections import defaultdict

class MVSColmapFileHandler:

    @staticmethod
    def parse_config_file(config_ifp):
        dense_img_index_to_name = {}
        with open(config_ifp, 'r') as input_file:
            lines = input_file.readlines()
            for dense_index, line in enumerate(lines):
                line = line.rstrip()
                if line != '':
                    dense_img_index_to_name[dense_index] = line
        return dense_img_index_to_name

    @staticmethod
    def parse_MVS_colmap_file(mvs_colmap_ifp, file_name_to_camera_id, with_nxnynz=True, n_th_point=1):

        """
        :param mvs_colmap_ifp:
        :return:
        """
        logger.info('parse_MVS_colmap_file: ...')
        logger.vinfo('mvs_colmap_ifp', mvs_colmap_ifp)
        logger.vinfo('n_th_point', n_th_point)

        camera_index_to_current_feature_index = defaultdict(int)
        points = []

        with open(mvs_colmap_ifp, 'r') as input_file:

            remaining_content = input_file.readlines()
            remaining_content = [x.strip() for x in remaining_content]

            # first line is a comment
            remaining_content = remaining_content[1:]                   # skipp 1 line

            dense_index_to_image_name = dict()

            num_dense_images = int(remaining_content[0])
            remaining_content = remaining_content[1:]                   # skipp 1 line
            for index in range(num_dense_images):
                dense_index_and_image_name = remaining_content[index].split()
                assert len(dense_index_and_image_name) == 2
                dense_index_to_image_name[int(dense_index_and_image_name[0])] = \
                    dense_index_and_image_name[1]

            remaining_content = remaining_content[num_dense_images:]    # skipp lines

            #logger.info(dense_index_to_image_name)

            # next 3 lines are comments
            #logger.info(remaining_content[0])
            #logger.info(remaining_content[1])
            #logger.info(remaining_content[2])
            remaining_content = remaining_content[3:]

            dense_index_to_camera_index = {}
            if file_name_to_camera_id is not None:
                for dense_index, image_name in dense_index_to_image_name.items():
                    camera_id = file_name_to_camera_id[image_name]
                    dense_index_to_camera_index[dense_index] = camera_id

            #logger.info(dense_index_to_camera_index)

            # DENSE_IMAGE_ID != CAMERA_ID and DENSE_IMAGE_ID != IMAGE_ID
            # POINT3D_ID, X, Y, Z, NX, NY, NZ, R, G, B, TRACK[] as (DENSE_IMAGE_ID, DENSE_COL, DENSE_ROW)
            remaining_content = remaining_content[::n_th_point]
            num_points = len(remaining_content)
            for index, point_line in enumerate(remaining_content):

                if index % 100000 == 0:
                    logger.pinfo(index, num_points)

                point_line_elements = (point_line.rstrip()).split()
                current_point = Point()

                # Adjust the point_3d id w.r.t n_th_point
                point_3d_id = index     # int(point_line_elements[0])
                current_point.id = point_3d_id

                xyz_vec = list(map(float, point_line_elements[1:4]))
                current_point.set_coord(xyz_vec)

                if with_nxnynz:
                    nxnynz_vec = list(map(float, point_line_elements[4:7]))
                    current_point.set_normal(nxnynz_vec)

                    rgb_vec = list(map(int, point_line_elements[7:10]))
                    current_point.set_color(rgb_vec)

                    img_id_col_row_triples_as_str = point_line_elements[10:]

                else:
                    rgb_vec = list(map(int, point_line_elements[4:7]))
                    current_point.set_color(rgb_vec)

                    img_id_col_row_triples_as_str = point_line_elements[7:]

                assert len(img_id_col_row_triples_as_str) % 3 == 0

                dense_image_ids = list(map(int, img_id_col_row_triples_as_str[0::3]))
                cols = list(map(float, img_id_col_row_triples_as_str[1::3]))
                rows = list(map(float, img_id_col_row_triples_as_str[2::3]))

                measurements = []
                #
                for dense_image_id, col, row in zip(dense_image_ids, cols, rows):

                    if file_name_to_camera_id is not None:
                        camera_id = dense_index_to_camera_index[dense_image_id]
                    else:
                        camera_id = dense_image_id

                    measurement = Measurement(
                        camera_index=camera_id,
                        # Adding None here would create parsing problems
                        feature_index=camera_index_to_current_feature_index[camera_id],
                        x=col,
                        y=row,
                        x_y_are_image_coords=True)
                    measurements.append(measurement)

                    camera_index_to_current_feature_index[camera_id] += 1

                current_point.measurements = measurements
                points.append(current_point)

            # Detect bad point ids
            point_ids = [point.id for point in points]
            assert len(list(set(point_ids))) == len(point_ids)

        # Compute REAL 2D image coordinates (the one of colmap are probably not correct)
        #cameras_background
        logger.info('parse_MVS_colmap_file: Done')

        return points

    @staticmethod
    def write_MVS_colmap_file(points, dense_id_to_file_name, mvs_colmap_ofp):
        logger.info('write_MVS_colmap_file: ...')
        logger.vinfo('mvs_colmap_ofp', mvs_colmap_ofp)

        mvs_content = []
        mvs_content.append('# DENSE_IMAGE_ID to image_name')
        mvs_content.append(dense_id_to_file_name.size())
        for dense_id, file_name in dense_id_to_file_name.items():
            mvs_content.append(str(dense_id) + ' ' + file_name)


        mvs_content.append('# 3D point list with one line of data per point:\n')
        mvs_content.append('#   POINT3D_ID, X, Y, Z, NX, NY, NZ, R, G, B, TRACK[] as (DENSE_ID, DENSE_COL, DENSE_ROW)\n')
        mvs_content.append('# Number of points: x, mean track length: 0\n')
        for point in points:
            # From the docs:
            # <Point>  = <XYZ> <RGB> <number of measurements> <List of Measurements>
            current_line = ' '.join(list(map(str, point.coord)))
            current_line += ' ' + ' '.join(list(map(str, point.normal)))
            current_line += ' ' + ' '.join(list(map(str, point.color)))
            if point.measurements is not None:
                for measurement in point.measurements:
                    current_line += ' ' + str(measurement.camera_index)
                    current_line += ' ' + str(measurement.x)                    # x = col
                    current_line += ' ' + str(measurement.y)                    # y = row

            mvs_content.append(current_line + ' ' + '\n')

        with open(mvs_colmap_ofp, 'wb') as output_file:
            output_file.writelines([item.encode() for item in mvs_content])


        logger.info('write_MVS_colmap_file: Done')
