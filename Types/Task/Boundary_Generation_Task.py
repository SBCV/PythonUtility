from Utility.Types.Task.Task import Task

class BoundaryGenerationTask(Task):
    def __init__(self,
                 nvm_file_object,
                 ply_file_object,
                 path_to_h5_object_files,
                 output_path,
                 semantic_support_type,
                 point_support_threshold_ratio,
                 amount_iterations,
                 max_amount_steps_initial_point_cloud,
                 amount_buffer_steps
                 ):

        self.__dict__.update(locals())
        del self.self  # redundant (and a circular reference)

