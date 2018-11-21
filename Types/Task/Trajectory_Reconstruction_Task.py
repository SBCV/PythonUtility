from Utility.Types.Task.Task import Task


class TrajectoryReconstructionTask(Task):
    def __init__(self,
                 input_nvm_file_object,
                 input_nvm_file_background,
                 frames_jpg_idp,
                 object_h5_idp,
                 ground_h5_idp,
                 stereo_triangulations_idp,
                 trajectory_reconstruction_odp,
                 trajectory_reconstruction_transf_ofp,
                 trajectory_camera_positions_ply_ofp,
                 trajectory_points_ply_ofp,
                 trajectory_points_ply_odp,
                 trajectory_points_no_scale_ply_ofp,
                 trajectory_reconstruction_estimated_scale_ratio_ofp,
                 trajectory_reconstruction_unfiltered_scale_ratios_ofp,
                 trajectory_reconstruction_filtered_scale_ratios_ofp,
                 scale_estimation_method,
                 plane_estimation_mode,
                 # Optional
                 dense_object_ply_ifp,
                 background_mvs_colmap_ifp,
                 background_mvs_colmap_config_ifp,
                 object_mvs_colmap_ifp,
                 ground_points_ply_ofp=None,
                 ground_plane_inlier_ply_ofp=None,
                 ground_representation_ply_odp=None):

        self.__dict__.update(locals())
        del self.self  # redundant (and a circular reference)