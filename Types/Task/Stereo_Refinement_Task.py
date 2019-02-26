from Utility.Types.Task.Task import Task

class StereoRefinementTask(Task):
    def __init__(self,
                 sfm_ifp,
                 sfm_ofp,
                 ply_ofp,
                 calib_u=None,
                 calib_v=None,
                 baseline=None
                 ):

        self.__dict__.update(locals())
        del self.self  # redundant (and a circular reference)