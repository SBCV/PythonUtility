from Utility.Types.Task.Task import Task


class ImageConversionTask(Task):
    def __init__(self,
                 path_to_png_folder='',
                 path_to_jpg_folder=''):

        self.__dict__.update(locals())
        del self.self  # redundant (and a circular reference)





