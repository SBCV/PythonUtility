import os
from Utility.File_Handler.PLY_File_Handler import PLYFileHandler
from Utility.File_Handler.NVM_File_Handler import NVMFileHandler
from Utility.File_Handler.Colmap_File_Handler import ColmapFileHandler
from Utility.Logging_Extension import logger

class ReconstructionFileConverter:

    @staticmethod
    def parse_reconstruction_file(ifp):

        if os.path.splitext(ifp)[1] == '.nvm':
            cameras, points = NVMFileHandler.parse_nvm_file(ifp)
        elif os.path.splitext(ifp)[1] == '.ply':
            points, faces = PLYFileHandler.parse_ply_file(ifp)
            cameras = []
        else:
            logger.vinfo('ext', os.path.splitext(ifp)[1])
            logger.info('Input file type Not implemented yet')
            assert False

        return cameras, points

    @staticmethod
    def write_reconstruction_file(cameras, points, ofp_or_odp):

        if os.path.splitext(ofp_or_odp)[1] == '.ply':
            PLYFileHandler.write_ply_file(
                ofp=ofp_or_odp,
                vertices=points)

        # TODO ADD Other file formats

        else:   # If no file format matches, convert to colmap
            # NOTE: IN COLMAP ONLY POINTS WITH MORE THAN 3 MEASUREMENTS ARE SHOWN BY DEFAULT
            # (CAN BE CHANGED IN THE VIEWER SETTINGS)
            ColmapFileHandler.create_colmap_model_files(
                ofp_or_odp,
                cameras,
                points,
                number_camera_models=1)

        # else:
        #     logger.vinfo('ext', os.path.splitext(ofp_or_odp)[1])
        #     logger.info('Output file type Not implemented yet')
        #     assert False

    @staticmethod
    def convert(main_input_file, main_output_file):

        cameras, points = ReconstructionFileConverter.parse_reconstruction_file(
            main_input_file)

        ReconstructionFileConverter.write_reconstruction_file(
            cameras, points, main_output_file)

    @staticmethod
    def merge_files(list_w_cam_ifp, list_w_cam_colors, list_wo_cam_ifp, list_wo_cam_colors, ofp_or_odp, overwrite=False):

        """

        :param list_w_cam_ifp: use camera information contained in these files
        :param list_w_cam_colors:
        :param list_wo_cam_ifp: ignore camera information contained in these files
        :param list_wo_cam_colors:
        :param ofp_or_odp: output file extension
        :return:
        """

        if overwrite is False:
            if os.path.isfile(ofp_or_odp):
                assert False
            if os.path.isdir(ofp_or_odp) and os.listdir(ofp_or_odp) != []:
                assert False

        assert len(list_w_cam_ifp) == len(list_w_cam_colors)
        assert len(list_wo_cam_ifp) == len(list_wo_cam_colors)

        cams = []
        points = []

        for ifp, color in zip(list_w_cam_ifp, list_w_cam_colors):
            c_cams, c_points = ReconstructionFileConverter.parse_reconstruction_file(ifp)
            cams += c_cams

            if color is not None:
                for point in c_points:
                    point.color = color
            points += c_points

        for ifp, color in zip(list_wo_cam_ifp, list_wo_cam_colors):
            _, c_points = ReconstructionFileConverter.parse_reconstruction_file(ifp)

            if color is not None:
                for point in c_points:
                    point.set_color(color)
            points += c_points

        # adjust the point ids (after parsing duplicates exists)
        for index, point in enumerate(points):
            point.id = index

        logger.vinfo('len(points)', len(points))

        ReconstructionFileConverter.write_reconstruction_file(
            cams, points, ofp_or_odp)














