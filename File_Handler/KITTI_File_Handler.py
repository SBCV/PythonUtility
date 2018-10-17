from Utility.Types.Detection_3D import Detection3D

class KITTIFileHandler(object):
    """
        Data Format Description
        =======================

        The label files contain the following information, which can be read and written using the matlab tools
        (readLabels.m) provided within this devkit. All values (numerical or strings) are separated via spaces,
        each row  corresponds to one object. The 17 columns represent:

        #Values    Name      Description
        ----------------------------------------------------------------------------
        1    frame        Frame within the sequence where the object appearers
        1    track id     Unique tracking id of this object within this sequence
        1    type         Describes the type of object: 'Car', 'Van', 'Truck',
                         'Pedestrian', 'Person_sitting', 'Cyclist', 'Tram',
                         'Misc' or 'DontCare'
        1    truncated    Float from 0 (non-truncated) to 1 (truncated), where
                         truncated refers to the object leaving image boundaries.
                 Truncation 2 indicates an ignored object (in particular
                 in the beginning or end of a track) introduced by manual
                 labeling.
        1    occluded     Integer (0,1,2,3) indicating occlusion state:
                         0 = fully visible, 1 = partly occluded
                         2 = largely occluded, 3 = unknown
        1    alpha        Observation angle of object, ranging [-pi..pi]
        4    bbox         2D bounding box of object in the image (0-based index):
                         contains left, top, right, bottom pixel coordinates
        3    dimensions   3D object dimensions: height, width, length (in meters)
        3    location     3D object location x,y,z in camera coordinates (in meters)
        1    rotation_y   Rotation ry around Y-axis in camera coordinates [-pi..pi]
        1    score        Only for results: Float, indicating confidence in
                         detection, needed for p/r curves, higher is better.
    """


    @staticmethod
    def read_KITTI_tracking_file(file_path_and_name):
        detections_3d = []

        with open(file_path_and_name, "r") as fh:
            for i,line in enumerate(fh):
                string_list = line.split(" ")
                detection_3d = Detection3D.from_string_list(string_list)
                detections_3d.append(detection_3d)

        return detections_3d

if __name__ == '__main__':

    path_to_tracking_file = 'PATH/TO/kitti/kitti/tracking/data_tracking_label_2/label_02/0000.txt'

    list_of_detections_3d = KITTIFileHandler.read_KITTI_tracking_file(path_to_tracking_file)