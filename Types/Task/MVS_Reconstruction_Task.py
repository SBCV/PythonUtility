from Utility.Types.Task.Task import Task


class MVSReconstructionTask(Task):
    def __init__(self,
                 source_path,
                 image_path,
                 workspace_path,
                 workspace_format,
                 output_point_ply_file_path,
                 output_point_txt_file_path,
                 geometric_consistency,
                 max_image_size,
                 output_mesh_ply_file_path,
                 input_type,
                 pmvs_option_file_name):

        self.__dict__.update(locals())
        del self.self  # redundant (and a circular reference)