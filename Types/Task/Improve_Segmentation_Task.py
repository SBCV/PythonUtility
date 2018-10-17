from Utility.Types.Task.Task import Task

class ImproveSegmentationTask(Task):
    def __init__(self,
                 parameters=''
                 ):

        self.__dict__.update(locals())
        del self.self  # redundant (and a circular reference)
