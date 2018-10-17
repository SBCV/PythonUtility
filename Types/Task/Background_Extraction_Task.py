from Utility.Types.Task.Task import Task


class BackgroundExtractionTask(Task):

    def __init__(self, path_to_image_folder,
                 path_to_input_object_category_h5_files,
                 path_to_output_background_images,
                 lazy_extraction=True):

        self.__dict__.update(locals())
        del self.self  # redundant (and a circular reference)