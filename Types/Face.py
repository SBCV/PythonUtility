import numpy as np

from Utility.Classes.Frozen_Class import FrozenClass

class Face(FrozenClass):

    """
    NOT TO CONFUSE WITH A REAL TRIANGLE (A FACE SAVES ONLY VERTEX INDICES, NO 3D INFORMATION)
    """

    def __init__(self, initial_indices=np.array([-1, -1, -1], dtype=int)):
        """
        We do NOT DEFINE COLOR PER FACE, since the color of the face is determined by the corresponding vertex colors
        :param initial_indices:
        """
        self.vertex_indices = np.array(initial_indices, dtype=int)


    # defines how the class will be printed
    def __str__(self):
        return str(self.vertex_indices)