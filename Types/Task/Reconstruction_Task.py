from Utility.Types.Task.Task import Task

# https://stackoverflow.com/questions/16017397/injecting-function-call-after-init-with-decorator

class ReconstructionTask(Task):
    def __init__(self,
                 path_to_tool_reconstruction,
                 output_path_main_nvm_file,
                 output_model_file_name_stem,
                 calibration_params,
                 keypoint_matcher_type=None,
                 overlap=None,  # For sequential matching
                 vsfm_sift_gpu_params='-fo -1 -tc2 7680 -da',
                 colmap_refine_focal_length=True,
                 colmap_refine_extra_params=True,
                 colmap_quadratic_overlap=None  # Sequential specific
                 ):

        self.__dict__.update(locals())
        del self.self  # redundant (and a circular reference)


if __name__ == '__main__':

    reconstruction_task = ReconstructionTask(
        path_to_tool_reconstruction='path_to_tool_reconstruction',
        output_path_main_nvm_file='main_nvm_file_name',
        output_model_file_name_stem='output_model_file_name_stem',
        calibration_params='calibration_params')


    # Not allowed
    #reconstruction_task.does_not_exists = 3

    reconstruction_task.quadratic_overlap = 4


    print(reconstruction_task)
