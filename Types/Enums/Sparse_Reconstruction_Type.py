class SparseReconstructionType:

    COLMAP = 'colmap'
    OPENMVG = 'openmvg'
    VSFM = 'visualsfm'
    THEIA = 'theia'

    UNSUPPORTED = 'UNSUPPORTED'

    @staticmethod
    def get_reconstruction_types():
        return [SparseReconstructionType.COLMAP,
                SparseReconstructionType.OPENMVG,
                SparseReconstructionType.VSFM,
                SparseReconstructionType.THEIA]

