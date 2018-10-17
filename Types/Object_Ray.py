from Utility.Classes.Frozen_Class import FrozenClass

class RayObjectPosition(FrozenClass):
    UNSET = 0
    TOP = 1
    BOTTOM = 2
    LEFT = 3
    RIGHT = 4

class Ray:
    def __init__(self, pos_vector, dir_vector, horizontal_position=RayObjectPosition.UNSET, vertical_position=RayObjectPosition.UNSET):
        self.pos_vector = pos_vector
        self.dir_vector = dir_vector
        self.horizontal_position = horizontal_position
        self.vertical_position = vertical_position