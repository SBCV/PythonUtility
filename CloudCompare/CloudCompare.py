import platform
import subprocess
import os
import numpy as np
import uuid
from shutil import copyfile
from Utility.Logging_Extension import logger
from Utility.Config import Config

class SubSamplingMode:
    RANDOM = 'RANDOM'
    SPATIAL = 'SPATIAL'
    OCTREE = 'OCTREE'

class CloudCompare:

    """
    This is an interface to the cloudcompare command line mode

    For more information visit:
        http://www.cloudcompare.org/doc/wiki/index.php?title=Command_line_mode
            By default, this mode only opens a small console window, applies the requested actions,
            and eventually saves the result in a file in the same directory(ies) as the input file(s).

        http://www.cloudcompare.org/doc/qCC/CloudCompare%20v2.6.1%20-%20User%20manual.pdf
            CloudCompare Version 2.6.1
            Command line mode is documented on Page 171 (Appendix)

    There are two modes:
        1. Use static methods for a specific purpose
        2. Use non-static methods to build dynamically (long) point cloud commands.
           The final execution is called using "execute_previous_commands".
    """

    SUPPORTED_CLOUD_FILE_FORMATS = ['ASC', 'BIN', 'PLY', 'LAS', 'E57', 'VTK', 'PCD', 'SOI', 'PN', 'PV']
    SUPPORTED_MESH_FILE_FORMATS = ['BIN', 'OBJ', 'PLY', 'STL', 'VTK', 'MA', 'FBX']

    parent_dp = os.path.dirname(os.path.realpath(__file__))
    path_to_config = os.path.join(parent_dp, 'CloudCompare.cfg')
    path_to_config_example = os.path.join(parent_dp, 'CloudCompare_example.cfg')
    if not os.path.isfile(path_to_config):
        copyfile(path_to_config_example, path_to_config)
    cloud_compare_config = Config(path_to_config)

    if platform.system() == 'Windows':
        path_to_executable = cloud_compare_config.get_option_value('cloud_compare_path_windows', str)
    else:
        # this points to cloud compare 2.10 (with qt 5.7)
        path_to_executable = cloud_compare_config.get_option_value('cloud_compare_path_linux', str)


    def __init__(self):
        self.cmd_options = ['-SILENT']      # enables silent mode (no console will appear)
        self.cc_auto_save(save_flag='OFF')  # we do not want to enable auto save, this could produce multiple models

        # 'BIN' is the default output file format of cloudcompare
        self.cloud_output_file_format = '.BIN'    # this can be changed by using cc_set_cloud_export_format(format_str)
        self.mesh_output_file_format = '.BIN'     # this can be changed by using cc_set_mesh_export_format(format_str)

        # Output File Name Structure of CloudCompare:

        # Output point cloud files are stored in the folder
        #   of the first loaded point cloud
        #   of the first loaded mesh if no point cloud was loaded
        # Output mesh files are stored in the folder
        #   of the first loaded mesh
        #   of the first loaded point cloud if no mesh was loaded

        # Since there are "overlapping" file formats (like .bin, .ply. .vtk) we do not know in advance, if the loaded
        # object is a point cloud or a mesh. Thus, there are two possible folders, where the output will be created.

        self.loaded_file_path_list = []
        self.output_suffix = ''

    def cc_open(self, file_path):
        if not os.path.isfile(file_path):
            logger.vinfo('file_path', file_path)
            assert False    # Input File does not exist!
        self.cmd_options += ['-O', file_path]
        self.loaded_file_path_list.append(file_path)

    def cc_statistical_outlier_removal(self, number_of_neighbors=6, sigma_multiplier=1.0):
        self.cmd_options += ['-SOR', str(number_of_neighbors), str(sigma_multiplier)]

    def cc_subsampling(self, subsampling_mode='OCTREE', subsampling_parameter=9):
        """
        -SS {algorithm} {parameter}
        """
        self.cmd_options += ['-SS', subsampling_mode, str(subsampling_parameter)]

    def cc_apply_trans(self, matrix_transformation_file_path):
        """
        The matrix is read from a simple text file with the matrix rows on each line (4 values per lines, 4 lines).
        Each entity will be replaced in memory by its transformed version

        IMPORTANT: Apply_trans was added in 2.6.1 (Ubuntu is running 2.6.0)
            http://cloudcompare.org/forum/viewtopic.php?t=1153

        :param matrix_transformation_file_path:
        :return:
        """
        self.cmd_options += ['-APPLY_TRANS', matrix_transformation_file_path]

    def cc_compute_cloud_to_cloud_distance(self):
        """
        See documentation of compute_cloud_to_mesh_distance()
        :return:
        """
        self.cmd_options += ['-C2C_DIST']
        self.output_suffix += '_C2C_DIST'

    def cc_compute_cloud_to_mesh_distance(self):
        """
        CC will load cloud1.bin and mesh.obj, then compute the distance from cloud1 (compared) relatively to mesh
        (reference). On output a file cloud1_C2M_DIST_YYYY-MM-DD_HHhMM.bin will be generated (with the resulting
        distances as scalar field). Note: this cloud stays in memory and can be processed further
        (with -FILTER_SF for instance).

        Results are stored as scalar field (SF), which is a property of the point cloud. The scalar field is a property
        of the (automatically) saved point cloud (e.g. is a property in the .asc. or .ply file)

        In addition, the scalar field (SF) can be processed within cloudcompare using for example
            'STAT_TEST {distrib} {distrib parameters} {p-value} {neighbors count}'
            '-FILTER_SF {minVal} {maxVal}'
            '-SF_ARITHMETIC {SF index} {operation}'
            '-SF_OP {SF index} {operation} {value}'
            '-SET_ACTIVE_SF {index}'
            '-REMOVE_ALL_SFS'

        """
        self.cmd_options += ['-C2M_DIST']
        self.output_suffix += '_C2M_DIST'

    def cc_auto_save(self, save_flag='OFF'):
        """
        By default clouds/meshes are saved automatically in the input folder. The automatically saved files contain
        the names of the operation, which were applied to these objects.
        Calling the method again with a different parameter will overwrite the previous call.
        :param save_flag: ON or OFF
        :return:
        """
        self.cmd_options += ['-AUTO_SAVE', save_flag]

    def _cc_set_cloud_export_format(self, format_str='BIN', prepend=True):
        """
        Specifies the default output format for clouds.
        Format can be one of the following: ASC, BIN, PLY, LAS, E57, VTK, PCD, SOI, PN, PV.
        -C_EXPORT_FMT {format}
        :return:
        """

        self.cmd_options += ['-C_EXPORT_FMT', format_str]
        self.cloud_output_file_format = '.' + format_str

    def _cc_set_mesh_export_format(self, format_str='BIN'):
        """
        Specifies the default output format for clouds.
        Format can be one of the following: BIN, OBJ, PLY, STL, VTK, MA, FBX.
        :param format_str:
        :return:
        """
        self.cmd_options += ['-M_EXPORT_FMT', format_str]
        self.mesh_output_file_format = '.' + format_str

    def _cc_save_clouds(self, ofp):
        user_ext = (os.path.splitext(ofp)[1])[1:].upper()
        # necessary to define the output file format,
        # since cloud compare uses by default .bin
        self._cc_set_cloud_export_format(user_ext)
        # https://github.com/CloudCompare/CloudCompare/pull/667
        self.cmd_options += ['-SAVE_CLOUDS', 'FILE', ofp]

    def _cc_save_meshes(self, ofp):
        user_ext = (os.path.splitext(ofp)[1])[1:].upper()
        # necessary to define the output file format,
        # since cloud compare uses by default .bin
        self._cc_set_mesh_export_format(user_ext)
        # https://github.com/CloudCompare/CloudCompare/pull/667
        self.cmd_options += ['-SAVE_MESHES', 'FILE', ofp]

    def cc_save_clouds_and_meshes(self):
        self.cmd_options += ['-SAVE_CLOUDS']
        self.cmd_options += ['-SAVE_MESHES']


    def execute_and_save_result_to_disc(self,
                                        ofp,
                                        save_clouds=False,
                                        save_meshes=False,
                                        reset_options=True,
                                        lazy=False):

        """
        The output file format must support the output object type (i.e. mesh / cloud).

        Remark: Executing cloudcompare may throw the following error message:
            QInotifyFileSystemWatcherEngine::addPaths: inotify_add_watch failed: No space left on device
            QFileSystemWatcher: failed to add paths: /home/sebastian/.config/ibus/bus
            QInotifyFileSystemWatcherEngine::addPaths: inotify_add_watch failed: No space left on device
            QFileSystemWatcher: failed to add paths: /home/sebastian/.config/ibus/bus/d3d562ee6c50f192ecc2af5d55bb69ab-unix-0

            However, it works as expected (i.e. ignore this error message)

        :param reset_options:
        :return:
        """

        logger.info('execute_and_save_result_to_disc: ...')

        if not (save_clouds ^ save_meshes):
            logger.info('Either save_clouds or save_meshes must be True')
            assert False

        if save_clouds:
            self._cc_save_clouds(ofp)
        if save_meshes:
            self._cc_save_meshes(ofp)

        if not lazy or not os.path.isfile(ofp):
            cc_call = [CloudCompare.path_to_executable] + self.cmd_options
            logger.info('CloudCompare call: ' + str(cc_call))
            subprocess.call(cc_call)

        if reset_options:
            self.cmd_options = ['-SILENT']

        logger.info('execute_and_save_result_to_disc: Done')

    @staticmethod
    def statistical_outlier_removal(ifp, ofp, number_of_neighbors=6, lazy=False):

        # https://www.cloudcompare.org/doc/wiki/index.php?title=SOR_filter
        # The 'SOR filter' tool resembles a lot the S.O.R. (Statistical Outlier Removal) of the PCL library
        # http://pointclouds.org/documentation/tutorials/statistical_outlier.php

        cloud_compare = CloudCompare()
        # cc_open checks presence of file
        cloud_compare.cc_open(ifp)
        cloud_compare.cc_statistical_outlier_removal(
            number_of_neighbors=number_of_neighbors, sigma_multiplier=1.0)
        cloud_compare.execute_and_save_result_to_disc(
            ofp,
            save_clouds=True,
            lazy=lazy)

    @staticmethod
    def apply_transformation(ifp_model,
                             transformation_mat,
                             ofp_model,
                             save_point_clouds,
                             save_meshes,
                             lazy=False):

        if not isinstance(transformation_mat, np.ndarray):
            logger.vinfo('type(transformation_mat)', type(transformation_mat))
            assert False

        unique_filename = uuid.uuid4().hex
        transformation_fp = os.path.join(
            os.path.dirname(CloudCompare.path_to_executable),
            unique_filename)
        np.savetxt(transformation_fp, transformation_mat)
        CloudCompare.apply_transformation_from_file(
            ifp_model,
            transformation_fp,
            ofp_model,
            save_point_clouds,
            save_meshes,
            lazy)
        os.remove(transformation_fp)
        assert not os.path.isfile(transformation_fp)

    @staticmethod
    def apply_transformation_from_file(ifp_model,
                                       ifp_transformation,
                                       ofp_model,
                                       save_point_clouds,
                                       save_meshes,
                                       lazy=False):

        """
        :param ifp_model:
        :param ifp_transformation:
                The transformation is stored in a plain txt file.
                Spaces separate columns and new lines separate rows.
                For example, use np.savetxt(some_path, some_mat) to create the desired file.
        :param ofp_model:
        :param save_point_clouds:
        :param save_meshes:
        :param lazy:
        :return:
        """

        cloud_compare = CloudCompare()
        # cc_open checks presence of file
        cloud_compare.cc_open(ifp_model)
        cloud_compare.cc_apply_trans(ifp_transformation)
        cloud_compare.execute_and_save_result_to_disc(
            ofp_model,
            save_clouds=save_point_clouds,
            save_meshes=save_meshes,
            lazy=lazy)

    @staticmethod
    def cloud_to_mesh_distance(ifp_mesh, ifp_cloud, ofp_cloud, lazy=False):

        cloud_compare = CloudCompare()
        # cc_open checks presence of file
        cloud_compare.cc_open(ifp_mesh)
        cloud_compare.cc_open(ifp_cloud)
        cloud_compare.cc_compute_cloud_to_mesh_distance()
        cloud_compare.execute_and_save_result_to_disc(
            ofp_cloud,
            save_clouds=True,
            lazy=lazy)

