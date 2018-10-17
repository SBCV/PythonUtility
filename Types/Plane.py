import numpy as np
from Utility.Classes.Frozen_Class import FrozenClass

class Plane(FrozenClass):
    def __init__(self, pos_vec, dir_vec_1=None, dir_vec_2=None, normal_vec=None):
        # either the dir_vecs or n_vec must be provided
        assert (dir_vec_1 is not None and dir_vec_2 is not None) or normal_vec is not None
        # assure that not both vector types are provided
        assert not (dir_vec_1 is not None and dir_vec_2 is not None and normal_vec is not None)
        self.pos_vec = pos_vec
        if dir_vec_1 is not None and dir_vec_2 is not None:
            self.set_dir_vecs_and_normal_vec_using_dir_vecs(dir_vec_1, dir_vec_2)
        else:
            self.set_dir_vecs_and_normal_vec_using_normal_vec(normal_vec)

    def set_dir_vecs_and_normal_vec_using_dir_vecs(self, dir_vec_1, dir_vec_2):
        self.dir_vec_1 = dir_vec_1
        self.dir_vec_2 = dir_vec_2
        self.normal_vec = np.cross(dir_vec_1, dir_vec_2)

    def set_dir_vecs_and_normal_vec_using_normal_vec(self, normal_vec):
        self.normal_vec = normal_vec
        self.dir_vec_1, self.dir_vec_2 = Plane.create_dir_vecs_from_normal_vec(normal_vec)

    @staticmethod
    def create_dir_vecs_from_normal_vec(n_vec):
        """
        The result is ambigous, since there are infinite solutions
        """

        # define an arbitray non-parallel vector
        non_parallel_vec = Plane.create_non_parallel_vector(n_vec)
        # create an orthogonal vector (this vector lies in the plane!)
        dir_vec_1 = np.cross(n_vec, non_parallel_vec)
        dir_vec_2 = np.cross(n_vec, dir_vec_1)
        return dir_vec_1, dir_vec_2

    @staticmethod
    def create_non_parallel_vector(n_vec):
        # non_parallel_vec should differ from n_vec at the first non-zero dimension
        non_parallel_vec = np.copy(n_vec)
        not_changed = True

        for index, value in np.ndenumerate(n_vec):
            print('index, value: ' + str(index)  + ' ' +str(value))
            if not_changed and value != 0:
                #print 'Changed Value'
                non_parallel_vec[index] = -value
                not_changed = False

        print(non_parallel_vec)
        return non_parallel_vec