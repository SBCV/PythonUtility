from Utility.Types.Task.Task import Task

class MeshRenderTask(Task):
    def __init__(self,
                 path_to_bundler_file,
                 path_to_list_file,
                 path_to_object_images,
                 path_to_OBJ_file,
                 path_to_output,
                 image_output_index_offset=0
                 ):

        self.__dict__.update(locals())
        del self.self  # redundant (and a circular reference)


