from Utility.Types.Task.Task import Task


class TrajectoryEvaluationTask(Task):

    def __init__(self,
                 input_path_to_frames_jpg_folder,

                 scale_estimation_method,

                 ground_truth_transformations_ifp,
                 trajectory_reconstruction_transformations_ifp,
                 reconstruction_to_ground_truth_trans_ofp,
                 ground_truth_environment_mesh_ifp,

                 reconstruction_background_ply_ifp,

                 trajectory_reconstruction_method_specific_name,
                 trajectory_reconstruction_transformation_odp,

                 # Paths for comparing the reconstruction with the corresponding mesh
                 # and to compute the ground truth scale ratio
                 gt_camera_trajectory_nvm_ifp,
                 transformed_object_mesh_idp,
                 object_reconstruction_nvm_ifp,
                 background_reconstruction_nvm_ifp,

                 reconstruction_object_ply_ifp,

                 # Paths to compute reconstruction error
                 trajectory_points_ply_gtc_odp,
                 trajectory_points_ply_rec_odp,
                 trajectory_points_ply_with_mesh_distance_odp,
                 reconstruction_to_gt_transformation_estimation_method,
                 reconstruction_error_ofp,

                 # Paths to REFERENCE TRAJECTORY
                 reference_scale_ratio_ofp,
                 trajectory_reference_gt_coord_odp,
                 trajectory_reference_transformation_ofp,
                 trajectory_reference_transformation_odp,
                 trajectory_points_ply_reference_odp,
                 trajectory_points_ply_with_mesh_distance_reference_odp,
                 reference_error_ofp,

                 # Paths for camera trajectory files
                 camera_trajectory_ply_ifp,
                 camera_trajectory_gtc_ply_ofp,

                 # Paths for ground files
                 ground_ply_ifp,
                 ground_gtc_ply_ofp,

                 # Path for ground representation files
                 ground_representation_ply_idp,
                 ground_representation_gtc_ply_odp,

                 # Paths for scale ratio visualization
                 trajectory_reconstruction_estimated_scale_ratio_ofp,
                 trajectory_reconstruction_unfiltered_scale_ratios_ofp,
                 trajectory_reconstruction_filtered_scale_ratios_ofp
                 ):

        self.__dict__.update(locals())
        del self.self  # redundant (and a circular reference)