from Utility.Types.Task.Task import Task

class Multiscale_Reconstruction_Task(Task):

    # TODO add params: density_threshold=0.1, filter_radius=2, lambda1=40, lambda2=40

    def __init__(self,
                 path_to_point_cloud,
                 path_to_output_dir):

        self.__dict__.update(locals())
        del self.self  # redundant (and a circular reference)