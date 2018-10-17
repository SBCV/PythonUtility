import pprint

from Utility.Classes.Frozen_Class import FrozenClass

class Task(FrozenClass):

    def __str__(self):
        return '\n' + self.__class__.__name__ + ': \n' + pprint.pformat(self.__dict__) + '\n'

    def __repr__(self):
        return self.__str__()



