from Utility.Types.Task.Task import Task

class MeshGenerationTask(Task):
    def __init__(self,
                 path_to_input_point_cloud_file,
                 path_to_output_mesh_file
                 ):

        self.__dict__.update(locals())
        del self.self  # redundant (and a circular reference)


