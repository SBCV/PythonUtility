from Utility.Types.Task.Task import Task


class MeasurementBasedOutlierRemovalTask(Task):
    def __init__(self,
                 nvm_file_object='',
                 min_measurements=None,
                 output_file_name_stem=''):

        self.__dict__.update(locals())
        del self.self  # redundant (and a circular reference)
