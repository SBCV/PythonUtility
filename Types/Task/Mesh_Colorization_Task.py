from Utility.Types.Task.Task import Task

class MeshColorizationTask(Task):
    def __init__(self,
                 mve_scene_path,
                 untextured_mesh_path_and_name,
                 output_dir
                 ):

        self.__dict__.update(locals())
        del self.self  # redundant (and a circular reference)

