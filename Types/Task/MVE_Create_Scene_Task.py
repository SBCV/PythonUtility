from Utility.Types.Task.Task import Task

class MVE_Create_Scene_Task(Task):
    def __init__(self,
                 mve_model_dir,
                 model_file_path,
                 mve_point_cloud_name
                 ):

        self.__dict__.update(locals())
        del self.self  # redundant (and a circular reference)
