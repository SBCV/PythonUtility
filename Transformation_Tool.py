import os
import numpy as np
from pathos.multiprocessing import ProcessingPool
from Utility.CloudCompare.CloudCompare import CloudCompare
from Utility.Logging_Extension import logger


class TransformationTool(object):

    @staticmethod
    def create_object_to_world_transformation_files(rec_method_transf_dir,
                                                    camera_object_trajectory,
                                                    world_to_world_transf=np.identity(4)):
        logger.info('create_object_to_world_transformation_files: ...')
        logger.vinfo('path_to_reconstruction_method_transformation_file_folder',
                     rec_method_transf_dir)

        if not os.path.isdir(rec_method_transf_dir):
            os.mkdir(rec_method_transf_dir)

        for frame_name in sorted(camera_object_trajectory.get_frame_names_sorted()):
            transformation_file_path = os.path.join(
                rec_method_transf_dir, str(frame_name) + '.txt')
            logger.vinfo('frame_name', frame_name)

            #object_pose = camera_object_trajectory[frame_name]['object_pose']
            object_matrix_world = camera_object_trajectory.get_object_matrix_world(
                frame_name)

            np.savetxt(transformation_file_path,
                       world_to_world_transf.dot(object_matrix_world))

            # with open(transformation_file_path, 'w') as output_file:
            #     output_file.writelines([item for item in file_content])
        logger.info('create_object_to_world_transformation_files: Done')


    @staticmethod
    def apply_single_transformation_to_multiple_models(input_path_to_transformation_file,
                                                        input_path_to_model_folder,
                                                        output_path_to_transformed_model_file_folder,
                                                        save_clouds=False,
                                                        save_meshes=False,
                                                        lazy=True,
                                                        log_info_sub_methods=True
                                                        ):

        logger.info('apply_single_transformation_to_multiple_models: ...')
        if not (save_clouds ^ save_meshes):
            logger.debug('Either save_clouds or save_meshes must be True')
            assert False

        model_files = sorted(
            [model_file for model_file in os.listdir(input_path_to_model_folder)
             if (os.path.isfile(os.path.join(input_path_to_model_folder, model_file))
                 and os.path.splitext(model_file)[1] == '.ply')])

        for model_file in sorted(model_files):

            output_path_to_transformed_model_file = os.path.join(
                output_path_to_transformed_model_file_folder, model_file)

            input_path_to_model_file = os.path.join(input_path_to_model_folder, model_file)

            TransformationTool.apply_single_transformation_to_single_model(
                ifp_model=input_path_to_model_file,
                ifp_transformation=input_path_to_transformation_file,
                ofp_model=output_path_to_transformed_model_file,
                save_point_clouds=save_clouds,
                save_meshes=save_meshes,
                lazy=lazy,
                log_info=log_info_sub_methods
            )

        logger.info('apply_single_transformation_to_multiple_models: Done')

    @staticmethod
    def apply_multiple_transformations_to_single_model(transformation_files_idp,
                                                       model_ply_ifp,
                                                       transformed_model_odp,
                                                       suffix='',
                                                       save_point_clouds=False,
                                                       save_meshes=False,
                                                       lazy=True,
                                                       log_info_sub_methods=False):


        logger.info('apply_multiple_transformations_to_single_model: ...')

        if not (save_point_clouds ^ save_meshes):
            logger.debug('Either save_clouds or save_meshes must be True')
            assert False

        transformation_files = sorted([
            trans_file for trans_file in os.listdir(transformation_files_idp)
            if os.path.isfile(os.path.join(transformation_files_idp, trans_file))])

        logger.vinfo('transformation_files_idp', transformation_files_idp)
        logger.vinfo('model_ply_ifp', model_ply_ifp)
        logger.vinfo('transformed_model_odp', transformed_model_odp)

        # Transform the point cloud and the mesh into
        # ground truth world coordinates and store it to disc afterwards
        # ==== Apply Transformation ====
        # Make sure .obj file was converted correctly
        assert os.path.isfile(model_ply_ifp)

        results = []
        with ProcessingPool() as pool:
            for transformation_file in sorted(transformation_files):       # TODO FIXME
                logger.vinfo('transformation_file', transformation_file)

                transformed_model_ofp = os.path.join(
                    transformed_model_odp,
                    os.path.splitext(transformation_file)[0] + '_' +
                    suffix +
                    os.path.splitext(model_ply_ifp)[1])

                logger.vinfo('transformed_model_ofp', transformed_model_ofp)

                input_path_to_transformation_file = os.path.join(
                    transformation_files_idp, transformation_file)
                assert os.path.isfile(input_path_to_transformation_file)

                result = pool.apipe(
                    TransformationTool.apply_single_transformation_to_single_model,
                    *[model_ply_ifp,
                      input_path_to_transformation_file,
                      transformed_model_ofp,
                      save_point_clouds,
                      save_meshes,
                      lazy,
                      log_info_sub_methods])
                results.append(result)

            # Collect the asynchronous calls
            for result in results:
                result.get()

        logger.info('apply_multiple_transformations_to_single_model: Done')

    @staticmethod
    def apply_single_transformation_to_single_model(ifp_model,
                                                    ifp_transformation,
                                                    ofp_model,
                                                    save_point_clouds=False,
                                                    save_meshes=False,
                                                    lazy=True,
                                                    log_info=True):


        if log_info:
            logger.info('apply_single_transformation_to_model: ...')
            logger.vinfo('output_path_to_transformed_model_file', ofp_model)

        CloudCompare.apply_transformation_from_file(
            ifp_model,
            ifp_transformation,
            ofp_model,
            save_point_clouds,
            save_meshes,
            lazy)

        if log_info:
            logger.info('apply_single_transformation_to_model: Done')