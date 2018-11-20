class StereoMatchingParameter(object):

    def __init__(self,
                 cx,
                 cy,
                 f_pix,
                 baseline):

        self.__dict__.update(locals())
        del self.self  # redundant (and a circular reference)