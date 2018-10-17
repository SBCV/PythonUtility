from Utility.Types.Task.Task import Task

from Thesis.Object_Reconstruction.Compute_Object_Contour_Pointcloud.SemanticSupport import SemanticSupportType

class SemanticOutlierRemovalTask(Task):
    def __init__(self,
                 nvm_file_object='',
                 ply_file_object='',
                 path_to_h5_object_files='',
                 output_file_name_stem='',
                 semantic_support_type=SemanticSupportType.Ratio,
                 point_support_threshold_ratio=0.98,
                 principal_point=None):

        self.__dict__.update(locals())
        del self.self  # redundant (and a circular reference)