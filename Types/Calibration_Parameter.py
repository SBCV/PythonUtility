from Utility.Types.Enums.Camera_Model_Types import CameraModelTypes
from Utility.Classes.Frozen_Class import FrozenClass

class CalibrationParameter(object):

    def assert_float_or_int(self, value):
        assert type(value) == float or type(value) == int

    def __init__(self, sc, camera_model_type, f, fx, fy, cx, cy, k):

        # sift_gpu_params = '-fo -1 -tc2 7680 -da -maxd 4096'

        # the given images are captured by the same camera
        self.sc = sc    # sc = shared calibration

        self.camera_model_type = camera_model_type

        if camera_model_type is None:
            'Nothing to do here'
        elif camera_model_type == CameraModelTypes.SIMPLE_RADIAL:
            self.assert_float_or_int(f)
            self.f = f
        elif camera_model_type == CameraModelTypes.PINHOLE:
            self.assert_float_or_int(fx)
            self.fx = fx
            self.assert_float_or_int(fy)
            self.fy = fy
        else:
            assert False

        # each camera model uses cx and cy
        self.assert_float_or_int(cx)
        self.cx = cx
        self.assert_float_or_int(cy)
        self.cy = cy
        self.assert_float_or_int(k)
        self.k = k

    @classmethod
    def init_single_f(cls, sc, camera_model_type, f, cx, cy, k):
        assert camera_model_type == CameraModelTypes.SIMPLE_RADIAL \
               or camera_model_type == CameraModelTypes.SIMPLE_PINHOLE

        if camera_model_type == CameraModelTypes.SIMPLE_PINHOLE:
            assert k == None
        return cls(sc=sc,
                   camera_model_type=camera_model_type,
                   f=f,
                   fx=None,
                   fy=None,
                   cx=cx,
                   cy=cy,
                   k=k)

    @classmethod
    def init_fx_fy(cls, sc, camera_model_type, fx, fy, cx, cy, k):
        assert camera_model_type == CameraModelTypes.PINHOLE
        return cls(sc=sc,
                   camera_model_type=camera_model_type,
                   f=None,
                   fx=fx,
                   fy=fy,
                   cx=cx,
                   cy=cy,
                   k=k)

    def is_calibration_valid(self):

        if self.camera_model_type is None:
            camera_parameters_validity = False
        elif self.camera_model_type == CameraModelTypes.SIMPLE_RADIAL:
            camera_parameters_validity = self.f is not None \
                                         and self.cx is not None and self.cy is not None \
                                         and self.k is not None
        elif self.camera_model_type == CameraModelTypes.PINHOLE:
            camera_parameters_validity = self.fx is not None and self.fy is not None \
                                         and self.cx is not None and self.cy is not None
        else:
            assert False
        return camera_parameters_validity

    def colmap_parameter_string(self, comma_seperated=True):

        if comma_seperated:
            separator = ', '
        else:
            separator = ' '

        if self.camera_model_type is None:
            assert False
        elif self.camera_model_type == CameraModelTypes.SIMPLE_RADIAL:
            param_string = str(self.f) + separator + str(self.cx) + separator + str(self.cy) + separator + str(self.k)
        elif self.camera_model_type == CameraModelTypes.PINHOLE:
            param_string = str(self.fx) + separator + str(self.fy) + separator + str(self.cx) + separator + str(self.cy)
        else:
            assert False
        return param_string

    def vsfm_parameter_string(self):

        assert self.camera_model_type == CameraModelTypes.PINHOLE
        # fx,cx,fy,cy
        # e.g '1165.70706768 951.915279791 1163.69355243 544.73711819'
        return str(self.fx) + ' ' + str(self.cx) + ' ' + str(self.fy) + ' ' + str(self.cy)


    def to_string(self):
        result = 'sc: ' + str(self.sc)
        result += ' fx: ' + str(self.fx) + ' fy: ' + str(self.fy) + ' cx: ' + str(self.cx) + ' cy: ' + str(self.cy)

    def __str__(self):
        return self.__class__.__name__ + ': ' + str(self.__dict__)