from Utility.Types.Task.Task import Task


class TrajectoryEvaluationTask(Task):

    def __init__(self,
                 input_path_to_frames_jpg_folder,

                 ground_truth_transformations_file_path,
                 trajectory_reconstruction_transformations_file_path,
                 transformation_reconstruction_to_ground_truth_file_path,
                 input_ground_truth_environment_mesh_file_path,

                 input_reconstruction_background_cloud_file_path,

                 trajectory_reconstruction_method_specific_name,
                 output_path_to_object_reconstruction_transformation_files_folder,

                 # Paths for comparing the reconstruction with the corresponding mesh
                 # and to compute the ground truth scale ratio
                 input_path_to_gt_camera_trajectory_nvm_file,
                 input_path_to_transformed_object_mesh_files,
                 input_path_to_object_reconstruction_nvm_file,
                 input_path_to_background_reconstruction_nvm_file,

                 input_reconstruction_object_cloud_file_path,

                 # Paths to compute reconstruction error
                 output_path_to_transformed_object_ply_files,
                 output_path_to_transformed_object_ply_files_with_mesh_distance,
                 reconstruction_to_gt_transformation_estimation_method,
                 output_path_reconstruction_error_file,

                 # Paths to REFERENCE TRAJECTORY
                 output_path_to_reference_scale_ratio_file,
                 output_trajectory_reference_gt_coord_path_folder,
                 output_trajectory_reference_transformation_file_path,
                 output_path_to_object_reference_transformation_files_folder,
                 output_path_to_transformed_object_ply_files_reference,
                 output_path_to_transformed_object_ply_files_with_mesh_distance_reference,
                 output_path_reference_error_file,

                 # Paths for camera trajectory files
                 input_path_to_camera_trajectory_ply_file,
                 output_path_to_camera_trajectory_gtc_ply_file,

                 # Paths for ground files
                 input_path_to_ground_ply_file,
                 output_path_to_ground_gtc_ply_file,

                 # Path for ground representation files
                 input_path_to_ground_representation_ply_folder,
                 output_path_to_ground_representation_gtc_ply_folder,

                 # Paths for scale ratio visualization
                 output_fp_trajectory_reconstruction_estimated_scale_ratio,
                 output_fp_trajectory_reconstruction_unfiltered_scale_ratios,
                 output_fp_trajectory_reconstruction_filtered_scale_ratios
                 ):

        self.__dict__.update(locals())
        del self.self  # redundant (and a circular reference)