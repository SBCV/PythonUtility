import os
from collections import OrderedDict
from Utility.Classes.Frozen_Class import FrozenClass
from Utility.Logging_Extension import logger
from Utility.Types.Reconstruction import Reconstruction
from Utility.Types.Background_Reconstruction import Background_Reconstruction

class ObjectBackgroundReconstruction(FrozenClass):

    def __init__(self, obj_rec, back_rec, path_to_frames=None, max_amount_cams=None):
        self.obj_rec = obj_rec
        self.back_rec = back_rec

        self.path_to_frames = path_to_frames

        obj_cam_index_to_camera = obj_rec.get_camera_index_to_camera()
        assert isinstance(back_rec, Background_Reconstruction)
        back_cam_index_to_camera = back_rec.get_camera_index_to_camera()

        self.valid_cam_names_sorted = ObjectBackgroundReconstruction.compute_valid_cam_names(
            obj_cam_index_to_camera, back_cam_index_to_camera)

        # Object Cameras
        self.valid_obj_cam_index_to_cam = \
            ObjectBackgroundReconstruction.compute_valid_cam_index_to_camera(
                self.valid_cam_names_sorted, obj_cam_index_to_camera)

        self.valid_cam_name_to_obj_cam_index = \
            self.compute_cam_name_to_cam_index(self.valid_obj_cam_index_to_cam)

        self.valid_cam_name_to_obj_cam = self.compute_cam_name_to_obj_cam()

        self.valid_obj_cam_index_to_img_index = \
            self.compute_valid_obj_cam_index_to_img_index()

        # Background Cameras
        self.valid_back_cam_index_to_cam = \
            ObjectBackgroundReconstruction.compute_valid_cam_index_to_camera(
                self.valid_cam_names_sorted, back_cam_index_to_camera)

        self.valid_cam_name_to_back_cam_index = \
            self.compute_cam_name_to_cam_index(self.valid_back_cam_index_to_cam)

        self.valid_cam_name_to_back_cam = self.compute_cam_name_to_back_cam()

        self.valid_back_cam_index_to_img_index = \
            self.compute_valid_back_cam_index_to_img_index()

        if len(obj_cam_index_to_camera) > len(self.valid_obj_cam_index_to_cam):
            logger.info(
                'Removing ' +
                str(len(obj_cam_index_to_camera) -
                    len(self.valid_obj_cam_index_to_cam)) +
                ' object cameras')

        if len(back_cam_index_to_camera) > len(self.valid_back_cam_index_to_cam):
            logger.info(
                'Removing ' +
                str(len(back_cam_index_to_camera) -
                    len(self.valid_back_cam_index_to_cam)) +
                ' background cameras')

        self.check_validity_of_valid_cams()

    @classmethod
    def init_from_nvm(cls,
                      input_path_to_frames_jpg_folder,
                      input_nvm_file_object,
                      object_sparse_reconstruction_type,
                      input_nvm_file_background,
                      background_sparse_reconstruction_type,
                      principal_point):

        obj_rec = Reconstruction.init_from_nvm(
            input_nvm_file_object,
            input_path_to_frames_jpg_folder,
            object_sparse_reconstruction_type,
            principal_point)

        # background reconstruction adds support for ground mesh and ground point cloud
        # dont mix up background and ground!
        back_rec = Background_Reconstruction.init_from_nvm(
            input_nvm_file_background,
            input_path_to_frames_jpg_folder,
            background_sparse_reconstruction_type,
            principal_point)
        return cls(obj_rec, back_rec, path_to_frames=input_path_to_frames_jpg_folder)


    # ============= IMAGES ==============

    def compute_valid_cam_file_name_to_img_index(self):
        """
        :return: valid_cam_name -> img_index
        """
        obj_img_names = self.obj_rec.get_rec_input_img_names_sorted()
        back_img_names = self.back_rec.get_rec_input_img_names_sorted()
        assert obj_img_names == back_img_names
        all_img_names = obj_img_names

        valid_cam_names = self.get_valid_cam_names_sorted()

        valid_cam_file_name_to_image_index = OrderedDict()
        cam_index = 0
        for img_index, img_name in enumerate(all_img_names):
            if cam_index < len(valid_cam_names):
                cam_file_name = valid_cam_names[cam_index]
                if img_name == cam_file_name:
                    valid_cam_file_name_to_image_index[cam_file_name] = img_index
                    cam_index += 1
            else:
                break

        assert cam_index == len(valid_cam_names) # - 1
        return valid_cam_file_name_to_image_index

    def compute_valid_obj_cam_index_to_img_index(self):
        """
        :return: valid_obj_cam_index -> img_index
        """
        valid_obj_cam_file_name_to_img_index = \
            self.compute_valid_cam_file_name_to_img_index()
        valid_obj_cam_index_to_image_index = OrderedDict()
        for cam_index, cam in self.valid_obj_cam_index_to_cam.items():
            img_index = valid_obj_cam_file_name_to_img_index[cam.file_name]
            valid_obj_cam_index_to_image_index[cam_index] = img_index
        return valid_obj_cam_index_to_image_index

    def compute_valid_back_cam_index_to_img_index(self):
        """
        :return: valid_back_cam_index -> img_index
        """
        valid_back_cam_file_name_to_img_index = \
            self.compute_valid_cam_file_name_to_img_index()
        valid_back_cam_index_to_image_index = OrderedDict()
        for cam_index, cam in self.valid_back_cam_index_to_cam.items():
            img_index = valid_back_cam_file_name_to_img_index[cam.file_name]
            valid_back_cam_index_to_image_index[cam_index] = img_index
        return valid_back_cam_index_to_image_index

    # ============= CAMERAS ==============

    def is_index_matching(self, obj_cam_index, back_cam_index):
        """
        :return: obj_image_index == back_image_index
        """
        # logger.info('is_index_matching: ...')
        # logger.info(self.valid_obj_cam_index_to_img_index)
        # logger.info(self.valid_back_cam_index_to_img_index)
        obj_image_index = self.valid_obj_cam_index_to_img_index[obj_cam_index]
        back_image_index = self.valid_back_cam_index_to_img_index[back_cam_index]
        return obj_image_index == back_image_index

    def is_stereo_reconstruction(self):
        contains_left = 'left' in self.valid_cam_names_sorted
        contains_right = 'right' in self.valid_cam_names_sorted
        return contains_left and contains_right

    def get_valid_cam_names_sorted(self):
        """
        :return: valid_cam_names_sorted
        """
        return sorted(self.valid_cam_names_sorted)

    def get_valid_obj_cams_sorted(self):
        """
        :return: valid_obj_cams_sorted
        """
        assert self.valid_cam_name_to_obj_cam is not None
        obj_cams_sorted = []
        for cam_name in sorted(self.valid_cam_names_sorted):
            obj_cams_sorted.append(self.valid_cam_name_to_obj_cam[cam_name])
        return obj_cams_sorted

    def get_valid_back_cams_sorted(self):
        """
        :return: valid_back_cams_sorted
        """
        assert self.valid_cam_name_to_back_cam is not None
        back_cams_sorted = []
        for cam_name in sorted(self.valid_cam_names_sorted):
            back_cams_sorted.append(self.valid_cam_name_to_back_cam[cam_name])
        return back_cams_sorted

    def is_obj_back_cam_pair_valid(self, cam_name):
        obj_valid = cam_name in self.valid_cam_name_to_obj_cam_index.keys()
        back_valid = cam_name in self.valid_cam_name_to_back_cam_index.keys()
        return obj_valid and back_valid

    def get_obj_back_cam_pair(self, valid_cam_name):
        """
        :return: (obj_cam, back_cam)
        """
        obj_cam_index = self.valid_cam_name_to_obj_cam_index[valid_cam_name]
        back_cam_index = self.valid_cam_name_to_back_cam_index[valid_cam_name]
        obj_cam = self.valid_obj_cam_index_to_cam[obj_cam_index]
        back_cam = self.valid_back_cam_index_to_cam[back_cam_index]
        obj_back_cam_pair = (obj_cam, back_cam)
        return obj_back_cam_pair

    def get_valid_obj_back_cam_pairs_sorted_as_sorted_list(self):
        """
        Returns pairs of Utility.Types.Camera
        :return:
        """
        valid_cam_obj_back_pairs = []
        for valid_cam_name in sorted(self.valid_cam_names_sorted):
            valid_obj_back_cam_pair = self.get_obj_back_cam_pair(valid_cam_name)
            valid_cam_obj_back_pairs.append(valid_obj_back_cam_pair)
        return valid_cam_obj_back_pairs

    def get_valid_name_obj_back_cam_triples_as_sorted_list(self):
        """
        :return: valid_name -> (obj_cam, back_cam)
        """
        name_cam_obj_back_triples = []
        for valid_cam_name in sorted(self.valid_cam_names_sorted):
            obj_back_cam_pair = self.get_obj_back_cam_pair(valid_cam_name)
            name_cam_obj_back_triples.append(
                (valid_cam_name, obj_back_cam_pair[0], obj_back_cam_pair[1]))
        return name_cam_obj_back_triples

    def compute_cam_name_to_cam_index(self, cam_index_to_camera):
        """
        :return: cam_name_to_index
        """
        cam_name_to_index = OrderedDict((camera.file_name, cam_index) for cam_index, camera
                               in cam_index_to_camera.items())
        return cam_name_to_index

    def compute_cam_name_to_obj_cam(self):
        """
        :return: cam_name -> obj_cam
        """
        assert self.valid_cam_name_to_obj_cam_index is not None
        assert self.valid_obj_cam_index_to_cam is not None
        cam_name_to_obj_cam = OrderedDict()
        for cam_name in self.valid_cam_names_sorted:
            obj_cam_index = self.valid_cam_name_to_obj_cam_index[cam_name]
            obj_cam = self.valid_obj_cam_index_to_cam[obj_cam_index]
            cam_name_to_obj_cam[cam_name] = obj_cam
        return cam_name_to_obj_cam

    def compute_cam_name_to_back_cam(self):
        """
        :return: cam_name -> back_cam
        """
        assert self.valid_cam_name_to_back_cam_index is not None
        assert self.valid_back_cam_index_to_cam is not None
        cam_name_to_back_cam = OrderedDict()
        for cam_name in self.valid_cam_names_sorted:
            back_cam_index = self.valid_cam_name_to_back_cam_index[cam_name]
            back_cam = self.valid_back_cam_index_to_cam[back_cam_index]
            cam_name_to_back_cam[cam_name] = back_cam
        return cam_name_to_back_cam

    def get_valid_obj_cam_index_to_cam(self):
        """
        :return: valid_obj_cam_index -> cam
        """
        return self.valid_obj_cam_index_to_cam

    def get_valid_back_cam_index_to_cam(self):
        """
        :return: valid_back_cam_index -> cam
        """
        return self.valid_back_cam_index_to_cam

    def check_validity_of_valid_cams(self):
        assert len(self.valid_obj_cam_index_to_cam) == len(self.valid_back_cam_index_to_cam)
        obj_file_names = sorted([cam.file_name for cam in self.valid_obj_cam_index_to_cam.values()])
        back_file_names = sorted([cam.file_name for cam in self.valid_back_cam_index_to_cam.values()])
        assert obj_file_names == back_file_names

    def get_obj_cam_index_to_cam(self, obj_cam_index):
        return self.obj_rec.get_camera_index_to_camera(obj_cam_index)

    def get_back_cam_index_to_cam(self, back_cam_index):
        return self.back_rec.get_camera_index_to_camera(back_cam_index)

    # ============= Points ==============

    def get_obj_points(self):
        return self.obj_rec.get_points()

    def has_dense_obj_points(self):
        return self.obj_rec.has_dense_points()

    def get_dense_obj_points(self):
        return self.obj_rec.get_dense_points()

    def get_back_points(self):
        return self.back_rec.get_points()


    @staticmethod
    def compute_valid_cam_names(obj_cam_index_to_camera, back_cam_index_to_camera):
        # find a mapping between object and background cameras
        # (a virtual camera may be only present in one of the reconstructions)
        camera_names_object = set(
            [camera.file_name for cam_index, camera in obj_cam_index_to_camera.items()])
        camera_names_background = set(
            [camera.file_name for cam_index, camera in back_cam_index_to_camera.items()])
        valid_camera_names = sorted(list(camera_names_object.intersection(
            camera_names_background)))
        return valid_camera_names

    @staticmethod
    def compute_valid_cam_index_to_camera(valid_camera_names, unfiltered_cam_index_to_camera):
        valid_obj_cam_index_to_camera = OrderedDict()
        for cam_index, camera in unfiltered_cam_index_to_camera.items():
            if camera.file_name in valid_camera_names:
                valid_obj_cam_index_to_camera[cam_index] = camera
        return valid_obj_cam_index_to_camera



