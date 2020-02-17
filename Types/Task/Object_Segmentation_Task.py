from Utility.Types.Task.Task import Task

from Utility.Types.Enums.Dense_Matching_Mode import DenseMatchingMode
from Utility.Types.Enums.Tracking_Mode import TrackingMode


class ObjectSegmentationTask(Task):
    def __init__(self,
                 path_to_image_folder='',
                 path_to_segmentation_folder='',
                 segmentation_category_type_list=[],
                 frames_object_subfolder='',
                 categorie_suffix='',
                 instance_suffix='',
                 segmentation_mode=None,
                 path_to_dense_matches_folder=None):# dense matches may be used for instance segmentation

        self.__dict__.update(locals())
        del self.self  # redundant (and a circular reference)