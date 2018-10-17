import numpy as np

from Utility.Classes.Frozen_Class import FrozenClass

class Detection3D(FrozenClass):

    def __init__(self, frame, track_id, detection_type, truncation, occlusion, obs_angle, bbox, dimensions, location, rotation_y, score):
        self.frame = frame
        self.track_id = track_id
        # detection_type: 'Car', 'Van', 'Truck', 'Pedestrian', 'Person_sitting', 'Cyclist', 'Tram', 'Misc' or 'DontCare'
        self.detection_type = detection_type
        # truncated: Float from 0 (non-truncated) to 1 (truncated)
        self.truncation = truncation
        # occluded: integer (0,1,2,3) indicating occlusion state:
        # 0 = fully visible, 1 = partly occluded, 2 = largely occluded, 3 = unknown
        self.occlusion = occlusion
        # bservation angle of object, ranging [-pi..pi]
        self.obs_angle = obs_angle
        # 2D bounding box of object in the image (0-based index): contains left, top, right, bottom pixel coordinates
        self.bbox = bbox
        # 3D object dimensions: height, width, length (in meters)
        self.dimensions = dimensions
        # 3D object location x,y,z in camera coordinates (in meters)
        self.location = location
        # Rotation ry around Y-axis in camera coordinates [-pi..pi]
        self.rotation_y = rotation_y
        self.score = score

    @classmethod
    def from_string_list(cls, string_list):

        return cls(
            frame=int(float(string_list[0])),  # frame
            track_id=int(float(string_list[1])),  # id
            detection_type=string_list[2].lower(),  # object type [car, pedestrian, cyclist, ...]
            truncation=float(string_list[3]),  # truncation [0..1]
            occlusion=int(float(string_list[4])),  # occlusion  [0,1,2]
            obs_angle=float(string_list[5]),  # observation angle [rad]
            bbox=np.array([float(string_list[6]), float(string_list[7]), float(string_list[8]), float(string_list[9])], dtype=float),   # left [px], top [px], right [px], bottom [px]
            dimensions=np.array([float(string_list[10]), float(string_list[11]), float(string_list[12])], dtype=float), # height [m], width  [m], length [m]
            location=np.array([float(string_list[13]), float(string_list[14]), float(string_list[15])], dtype=float),  # X [m]
            rotation_y=float(string_list[16]),  # yaw angle [rad]
            score=float(string_list[17]) if len(string_list) >= 18 else None
        )
