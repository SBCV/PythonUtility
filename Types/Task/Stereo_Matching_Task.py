from Utility.Types.Task.Task import Task

class StereoMatchingTask(Task):
    def __init__(self,
                 image_idp,
                 object_h5_sub_dp,
                 disparity_odp,
                 triangulation_sub_odp
                 ):

        self.__dict__.update(locals())
        del self.self  # redundant (and a circular reference)
