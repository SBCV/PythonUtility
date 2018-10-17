import numpy as np
from Utility.Classes.Frozen_Class import FrozenClass

class Triangle(FrozenClass):

    """
    NOT TO CONFUSE WITH A FACE (A TRIANGLE SAVES REAL 3D INFORMATION)
    """

    def __init__(self, vertex_0, vertex_1, vertex_2):
        self.vertex_0 = vertex_0
        self.vertex_1 = vertex_1
        self.vertex_2 = vertex_2

    def return_normal(self):
        normal = np.cross(self.vertex_0 - self.vertex_1, self.vertex_0 - self.vertex_2)
        return np.divide(normal, np.linalg.norm(normal))

    # __repr__ goal is to be unambiguous
    def __repr__(self):
        return str([self.vertex_0, self.vertex_1, self.vertex_2])

    #__str__ goal is to be readable
    def __str__(self):
        return str([self.vertex_0, self.vertex_1, self.vertex_2])

