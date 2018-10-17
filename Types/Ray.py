import numpy as np
from Utility.Math.Number_Extension import approx_equal_scalar
from Utility.Classes.Frozen_Class import FrozenClass

class Ray(FrozenClass):
    def __init__(self, pos_vec, dir_vec):
        assert isinstance(pos_vec, np.ndarray) and isinstance(dir_vec, np.ndarray)
        self.pos_vec = pos_vec
        self.dir_vec = dir_vec

    def is_normalized(self):
        return approx_equal_scalar(np.linalg.norm(self.dir_vec), 1)

    def normalize(self):
        self.dir_vec /= float(np.linalg.norm(self.dir_vec))