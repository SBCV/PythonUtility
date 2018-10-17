from Utility.Types.Task.Task import Task


class TrajectoryReconstructionTask(Task):
    def __init__(self,
                 input_nvm_file_object,
                 input_nvm_file_background,
                 input_path_to_frames_jpg_folder,
                 input_path_to_ground_h5_folder,
                 trajectory_reconstruction_odp,
                 output_trajectory_reconstruction_file_path,
                 output_ply_file_path_trajectory_camera_positions,
                 output_ply_file_path_trajectory_points,
                 output_ply_file_path_trajectory_points_no_scale,
                 output_fp_trajectory_reconstruction_estimated_scale_ratio,
                 output_fp_trajectory_reconstruction_unfiltered_scale_ratios,
                 output_fp_trajectory_reconstruction_filtered_scale_ratios,
                 scale_estimation_method,
                 plane_estimation_mode,
                 # Optional
                 dense_object_ply_ifp,
                 input_path_to_background_mvs_colmap_file,
                 input_path_to_background_mvs_colmap_config_file,
                 input_path_to_object_mvs_colmap_file,
                 output_ply_file_path_ground_points=None,
                 output_ply_file_path_ground_plane_inlier=None,
                 output_ply_folder_path_ground_representation=None):

        self.__dict__.update(locals())
        del self.self  # redundant (and a circular reference)