from Utility.Types.Task.Task import Task

class VideoCreationTask(Task):
    def __init__(self,
                 path_to_images,
                 sequential_image_name_scheme,
                 output_video_path):

        self.__dict__.update(locals())
        del self.self  # redundant (and a circular reference)