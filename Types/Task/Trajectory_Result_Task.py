from Utility.Types.Task.Task import Task


class TrajectoryResultTask(Task):
    def __init__(self,
                 trajectory_name,
                 vehicle_name,
                 frames_jpg_folder,
                 input_nvm_file_object,          # this can be None
                 scale_estimation_method,
                 scale_ratio_fp,
                 error_fp):

        self.__dict__.update(locals())
        del self.self  # redundant (and a circular reference)