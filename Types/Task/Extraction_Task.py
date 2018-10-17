from Utility.Types.Task.Task import Task


class ExtractionTask(Task):
    def __init__(self,
                 path_to_input_video='',
                 path_to_output='',
                 output_name_scheme='',
                 frames_img_folder_suffix='',
                 output_frame_name_scheme='',
                 frame_rate=12.5,
                 jpg_quality=2,
                 start_time=None,
                 end_time=None,
                 indent_level_space=1):

        self.__dict__.update(locals())
        del self.self  # redundant (and a circular reference)





