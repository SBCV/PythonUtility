import os

from Utility.Logging_Extension import logger

class ColmapFileHandler:

    @staticmethod
    def write_cameras_txt(camera_path):
        with open(camera_path, 'wb') as output_file:
            output_file.writelines(
                ["# Camera list with one line of data per camera:\n",
                 "#   CAMERA_ID, MODEL, WIDTH, HEIGHT, PARAMS[]\n",
                 "# Number of cameras: 1\n",
                 "1 SIMPLE_RADIAL 2832 2128 2971.75 1416 1064 -0.163881\n"])

    @staticmethod
    def write_images_txt(image_path, cams, points, number_camera_models):
        with open(image_path, 'wb') as output_file:
            output_file.writelines(
                ["# Image list with two lines of data per image:\n",
                 "#   IMAGE_ID, QW, QX, QY, QZ, TX, TY, TZ, CAMERA_ID, NAME\n",
                 "#   POINTS2D[] as (X, Y, POINT3D_ID)\n",
                 "# Number of images: 11, mean observations per image: 3376.91\n"])

            for index, cam in enumerate(cams):

                index += 1

                # https://colmap.github.io/format.html
                # The reconstructed pose of an image is specified as the projection from world to
                # image coordinate system using a quaternion (QW, QX, QY, QZ)
                # and a translation vector (TX, TY, TZ).
                # The quaternion is defined using the Hamilton convention, which is, for example,
                # also used by the Eigen library.
                # The coordinates of the projection center are given by -R^t * T,
                # where R^t is the inverse/transpose of the 3x3 rotation matrix
                # composed from the quaternion and T is the translation vector.

                line = ''
                line += str(index) + ' '

                quaternion_str = ' '.join(map(str, cam.get_quaternion()))
                line += quaternion_str + ' '
                camera_translation_str = ' '.join(map(str, cam.get_translation_vec()))
                line += camera_translation_str + ' '

                line += str(1) + ' '
                line += str(index) + '.JPG'
                output_file.write(line + '\n')

                # second data entry
                line = ''
                line += "1.0 2.0 -1"    # TODO
                output_file.write(line + '\n')


    @staticmethod
    def write_points3D_txt(point_path, points):
        with open(point_path, 'wb') as output_file:
            output_file.writelines(
                ["# 3D point list with one line of data per point:\n",
                 "#   POINT3D_ID, X, Y, Z, R, G, B, ERROR, TRACK[] as (IMAGE_ID, POINT2D_IDX)\n",
                 "# Number of points: 7867, mean track length: 4.72175\n"])

            for index, point in enumerate(points):
                line = ''
                if point.id is not None:
                    line += str(point.id) + ' '
                else:
                    line += str(index) + ' '

                line += ' '.join(map(str, point.coord)) + ' '
                line += ' '.join(map(str, point.color)) + ' '
                line += '1.0'   # error
                if point.measurements is not None:
                    for meas in point.measurements:
                        line += ' ' + str(meas.camera_index) + ' ' + str(meas.feature_index)
                output_file.write(line + '\n')


    @staticmethod
    def create_colmap_model_files(model_path, cams, points, number_camera_models):

        os.mkdir(model_path)

        logger.info('create_colmap_model_files: ...')
        camera_path = os.path.join(model_path, 'cameras.txt')
        ColmapFileHandler.write_cameras_txt(camera_path)

        image_path = os.path.join(model_path, 'images.txt')
        ColmapFileHandler.write_images_txt(image_path, cams, points, number_camera_models)

        point_path = os.path.join(model_path, 'points3D.txt')
        ColmapFileHandler.write_points3D_txt(point_path, points)
        logger.info('create_colmap_model_files: Done')

