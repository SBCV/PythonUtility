from Utility.Types.Task.Task import Task

class ImageOverlayTask(Task):
    def __init__(self,
                 path_to_rendered_views,
                 path_to_frame_images,
                 path_to_output_overlay_files,
                 iterated_file_extension='.jpg'):

        self.__dict__.update(locals())
        del self.self  # redundant (and a circular reference)