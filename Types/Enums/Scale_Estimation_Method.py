from Utility.Classes.Frozen_Class import FrozenClass
from Utility.Types.Enums.Outlier_Filter_Type import OutlierFilterType
from Utility.Types.Enums.Stereo_SfM_Type import StereoSfMType

class ScaleEstimationMethodBase(FrozenClass):

    # Options to demonstrate usefulness of semantic and statistical outlier filtering
    any_filter = OutlierFilterType.any_filter           # takes an arbitrary sfm file
    all_filters = OutlierFilterType.all_filters         # applies only to reconstruction files with all filters applied
    no_filters = OutlierFilterType.no_filters
    semantic_filtering_only = OutlierFilterType.semantic_filtering_only
    statistical_filterinig_only = OutlierFilterType.statistical_filterinig_only

    filter_method = any_filter

    stereo_sfm_type = StereoSfMType.initial_stereo_sfm

    uses_environment = False

    def get_filter_method(self):
        return self.filter_method

    def get_stereo_sfm_type(self):
        return self.stereo_sfm_type

class ScaleEstimationReferenceMethod(ScaleEstimationMethodBase):
    def __str__(self):
        return 'REFERENCE'

class ScaleEstimationStereoMatchingMethod(ScaleEstimationMethodBase):
    """
    Does not require the estimation of a scale (dummy method)
    """
    def __str__(self):
        return 'STEREO_MATCHING'

class ScaleEstimationStereoSfMMethod(ScaleEstimationMethodBase):

    camera_distance_simple_contraint = 'CAMERA_DISTANCE_SIMPLE'
    camera_distance_ranking_constraint = 'CAMERA_DISTANCE_RANKING'
    point_cloud_distance_constraint = 'POINT_CLOUD_DISTANCE'

    def __init__(self):
        self.stereo_sfm_type = StereoSfMType.refined_stereo_sfm

    def use_initial_sfm_rec(self):
        self.stereo_sfm_type = StereoSfMType.initial_stereo_sfm
        #assert False    # TODO

    def use_refined_sfm_rec(self):
        self.stereo_sfm_type = StereoSfMType.refined_stereo_sfm
        # assert False  # TODO

    def __str__(self):
        # TODO REPLACE RETURN STRING
        # return 'STEREO_SfM_' + self.stereo_sfm_type + '_' + self.filter_method
        return 'STEREO_SfM'

class ScaleEstimationConstantVelocityMethod(ScaleEstimationMethodBase):
    def __str__(self):
        return 'CONSTANT_VELOCITY'

class ScaleEstimationPlaneIntersectionMethod(ScaleEstimationMethodBase):

    semi_dense = False
    uses_environment = True

    def __str__(self):
        return 'PLANE_INTERSECTION_' + 'SEMI_DENSE_' + str(self.semi_dense)

    def set_semi_dense(self, semi_dense=False):
        self.semi_dense = semi_dense

class ScaleEstimationMeshIntersectionMethod(ScaleEstimationMethodBase):

    semi_dense = False
    uses_environment = True

    def __str__(self):
        # Legacy
        #return 'MESH_INTERSECTION' + '_SEMI_DENSE_' + str(self.semi_dense)
        # Current
        return 'MESH_INTERSECTION' + '_SEMI_DENSE_' + str(self.semi_dense) + '_FILTER_METHOD_' + str(self.filter_method)


    def set_semi_dense(self, semi_dense=False):
        self.semi_dense = semi_dense

    def set_all_filters(self):
        self.filter_method = ScaleEstimationMeshIntersectionMethod.all_filters

    def set_no_filters(self):
        self.filter_method = ScaleEstimationMeshIntersectionMethod.no_filters

    def set_semantic_filtering_only(self):
        self.filter_method = ScaleEstimationMeshIntersectionMethod.semantic_filtering_only

    def set_statistical_filterinig_only(self):
        self.filter_method = ScaleEstimationMeshIntersectionMethod.statistical_filterinig_only

class ScaleEstimationConstantDistanceMethod(ScaleEstimationMethodBase):

    uses_environment = True

    # Which Image Pairs are considered
    stride = 'STRIDE'
    brute_force = 'BRUTE_FORCE'

    # How are ratios filtered
    no_filtering = 'NO_FILTERING'
    numerator_denominator_filtering = 'NUMERATOR_DENOMINATOR_FILTERING'
    camera_center_distance_filtering = 'CAMERA_CENTER_DISTANCE_FILTERING'

    # How is the final scale estimated
    least_sequares = 'LEAST_SQUARES'
    suitable_pairs = 'SUITABLE_PAIRS'

    def __str__(self):
        return 'CONSTANT_DISTANCE_' + self.get_current_config_as_string()

    def __init__(self):
        self.image_pair_method = ScaleEstimationConstantDistanceMethod.stride
        self.filtering_method = ScaleEstimationConstantDistanceMethod.no_filtering
        self.estimation_method = ScaleEstimationConstantDistanceMethod.least_sequares
        self.stride = 1
        self.dist_to_suit_rank_weight = 0.5
        self.max_num_index_pairs = 1000

    def get_current_config_as_string(self):
        return self.image_pair_method + "_" + self.filtering_method + "_" + self.estimation_method

    def get_image_pair_method(self):
        return self.image_pair_method

    def get_filtering_method(self):
        return self.filtering_method

    def get_estimation_method(self):
        return self.estimation_method

    def get_stride(self):
        return self.stride

    def get_dist_to_suit_rank_weight(self):
        return self.dist_to_suit_rank_weight

    def get_max_num_index_pairs(self):
        return self.max_num_index_pairs

    # Brute Force + No Filtering + Least Squares
    def set_brute_force_no_filtering_least_squares_config(self, max_num_index_pairs=1000):
        self.image_pair_method = ScaleEstimationConstantDistanceMethod.brute_force
        self.filtering_method = ScaleEstimationConstantDistanceMethod.no_filtering
        self.estimation_method = ScaleEstimationConstantDistanceMethod.least_sequares
        self.max_num_index_pairs = max_num_index_pairs

    # Brute Force + Numerator Denominator Filtering + Least Squares
    def set_brute_force_numerator_denominator_filtering_least_squares_config(self):
        self.image_pair_metho\
            = ScaleEstimationConstantDistanceMethod.brute_force
        self.filtering_method = ScaleEstimationConstantDistanceMethod.numerator_denominator_filtering
        self.estimation_method = ScaleEstimationConstantDistanceMethod.least_sequares

    # Brute Force + Distance Filtering
    def set_brute_force_camera_distance_filtering_least_squares_config(self,
                                                                       dist_to_suit_rank_weight=0.5,
                                                                       max_num_index_pairs=1000):
        """
        dist_to_suit_rank_weight = 0.5 means that distance rank and suitability rank are equally weighted
        dist_to_suit_rank_weight = 0 means that only distance rank is used
        dist_to_suit_rank_weight = 1 means that only suitability rank is used
        :param dist_to_suit_rank_weight:
        :param index_range
        :return:
        """
        assert 0.0 <= dist_to_suit_rank_weight <= 1.0
        self.image_pair_method = ScaleEstimationConstantDistanceMethod.brute_force
        self.filtering_method = ScaleEstimationConstantDistanceMethod.camera_center_distance_filtering
        self.estimation_method = ScaleEstimationConstantDistanceMethod.least_sequares
        self.dist_to_suit_rank_weight = dist_to_suit_rank_weight
        self.max_num_index_pairs = max_num_index_pairs

    # Stride + No Filtering + Least Squares
    def set_stride_no_filtering_least_squares_config(self, stride):
        self.image_pair_method = ScaleEstimationConstantDistanceMethod.stride
        self.filtering_method = ScaleEstimationConstantDistanceMethod.no_filtering
        self.estimation_method = ScaleEstimationConstantDistanceMethod.least_sequares
        self.stride = stride

    # Stride + Numerator Denominator Filtering + Least Squares
    def set_stride_numerator_denominator_filtering_least_squares_config(self, stride):
        self.image_pair_method = ScaleEstimationConstantDistanceMethod.stride
        self.filtering_method = ScaleEstimationConstantDistanceMethod.numerator_denominator_filtering
        self.estimation_method = ScaleEstimationConstantDistanceMethod.least_sequares
        self.stride = stride

    # Stride + Distance Filtering
    def set_stride_camera_distance_filtering_least_squares_config(self, stride, dist_to_suit_rank_weight=0.5):
        """
        dist_to_suit_rank_weight = 0.5 means that distance rank and suitability rank are equally weighted
        dist_to_suit_rank_weight = 0 means that only distance rank is used
        dist_to_suit_rank_weight = 1 means that only suitability rank is used
        :param dist_to_suit_rank_weight:
        :return:
        """
        assert 0.0 <= dist_to_suit_rank_weight <= 1.0
        self.image_pair_method = ScaleEstimationConstantDistanceMethod.stride
        self.filtering_method = ScaleEstimationConstantDistanceMethod.camera_center_distance_filtering
        self.estimation_method = ScaleEstimationConstantDistanceMethod.least_sequares
        self.dist_to_suit_rank_weight = dist_to_suit_rank_weight
        self.stride = stride

class ScaleEstimationHeadingMethod(ScaleEstimationMethodBase):

    def __str__(self):
        return 'HEADING'

class ScaleEstimationMethod(FrozenClass):
    REFERENCE = ScaleEstimationReferenceMethod()
    MESH_INTERSECTION = ScaleEstimationMeshIntersectionMethod()
    PLANE_INTERSECTION = ScaleEstimationPlaneIntersectionMethod()
    CONSTANT_DISTANCE = ScaleEstimationConstantDistanceMethod()
    HEADING = ScaleEstimationHeadingMethod()
    CONSTANT_VELOCITY = ScaleEstimationConstantVelocityMethod()
    STEREO_SFM = ScaleEstimationStereoSfMMethod()
    STEREO_MATCHING = ScaleEstimationStereoMatchingMethod()