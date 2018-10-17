class DenseMatchingMode:

    # Compute Offsets (i.e. Offsets of Matching Pixels in Corresponding Images)
    POLYNOMIAL_EXPANSION = 'POLYNOMIAL_EXPANSION'   # approach by Farneback et al, included in OpenCV
    FLOWNET2 = 'FLOWNET2'
    LITEFLOWNET = 'LITEFLOWNET'
    PWCNET = 'PWCNET'

    # Compute Matches (i.e. Matching Pixels in corresponding images)
    CPM = 'CPM'
    DEEP_MATCHES = 'DEEP_MATCHES'
    IDENTITY = 'IDENTITY'                           # dummy method, computes identity matches, for testing purposes



    @staticmethod
    def computes_dense_matches(method):
        return method in ['POLYNOMIAL_EXPANSION', 'FLOWNET2', 'IDENTITY']

    @staticmethod
    def computes_correspondences(method):
        return method in ['CPM', 'DEEP_MATCHES']