from Utility.Classes.Frozen_Class import FrozenClass

class Pixel(FrozenClass):
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def as_xy_tuple(self):
        return self.x, self.y

    def as_yx_tuple(self):
        return self.y, self.x

    def __add__(self, other):
        return Pixel(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return Pixel(self.x - other.x, self.y - other.y)

    def __mul__(self, scalar):
        return Pixel(self.x * float(scalar), self.y * float(scalar))

    def __div__(self, scalar):
        return Pixel(self.x / float(scalar), self.y / float(scalar))

    def __str__(self):
        return '(' + str(self.x) + ',' + str(self.y) + ')'