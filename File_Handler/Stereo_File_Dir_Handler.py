from Utility.OS_Extension import get_image_file_paths_in_dir

class StereoMonoFileDirHandler(object):

    @staticmethod
    def is_left_cam(file_name):
        is_left_cam = 'left' in file_name
        if is_left_cam:
            assert not 'right' in file_name
        return is_left_cam

    @staticmethod
    def get_stem(file_name):
        is_left_cam = StereoMonoFileDirHandler.is_left_cam(file_name)
        if is_left_cam:
            stem = file_name.split('_left')[0]
        else:
            stem = file_name.split('_right')[0]
        return stem

    @staticmethod
    def get_common_name(stem):
        return stem + '.jpg'

    @staticmethod
    def get_left_name(stem):
        return stem + '_left.jpg'

    @staticmethod
    def get_right_name(stem):
        return stem + '_right.jpg'

    @staticmethod
    def get_corresponding_stereo_image_name(image_name):
        assert 'left' in image_name or 'right' in image_name
        assert not ('left' in image_name and 'right' in image_name)
        if 'left' in image_name:
            return image_name.replace('left', 'right')
        if 'right' in image_name:
            return image_name.replace('right', 'left')

    # =============== Return Stereo Or Mono Results =======================

    @staticmethod
    def contains_folder_stereo_images(path_to_image_folder):
        left_image_names, right_image_names, stereo_image_flag = \
            StereoMonoFileDirHandler.get_mono_or_stereo_ifp_s_from_folder(
                path_to_image_folder)
        return stereo_image_flag

    @staticmethod
    def get_mono_or_stereo_ifp_s_from_folder(path_to_image_folder, base_name_only=False):
        image_ifp_s = get_image_file_paths_in_dir(
            path_to_image_folder,
            base_name_only=base_name_only)

        left_image_ifp_s, right_image_ifp_s, stereo_image_flag = \
            StereoMonoFileDirHandler.get_mono_or_stereo_ifp_s_from_paths(image_ifp_s)
        # else:
        #     left_image_ifp_s = image_ifp_s
        #     right_image_ifp_s = []
        #     stereo_image_flag = False

        return left_image_ifp_s, right_image_ifp_s, stereo_image_flag

    @staticmethod
    def get_mono_or_stereo_ifp_s_from_paths(image_ifp_s, assert_stereo_pairs=True):

        """
        Returns image file names
        :param image_ifp_s:
        :return:
        """

        left_image_ifp_s = sorted([image_ifp for image_ifp in image_ifp_s if 'left' in image_ifp])
        right_image_ifp_s = sorted([image_ifp for image_ifp in image_ifp_s if 'right' in image_ifp])

        # Intersection must be empty
        assert set(left_image_ifp_s).intersection(set(right_image_ifp_s)) == set()

        stereo_image_flag = len(left_image_ifp_s) > 0 and len(right_image_ifp_s) > 0
        if stereo_image_flag:
            assert len(left_image_ifp_s) > 0 and len(right_image_ifp_s) > 0
            if assert_stereo_pairs:
                assert len(left_image_ifp_s) == len(right_image_ifp_s)

        else:
            left_image_ifp_s = image_ifp_s
            right_image_ifp_s = []

        return left_image_ifp_s, right_image_ifp_s, stereo_image_flag


if __name__ == '__main__':

    path_to_folder = ''
    left_image_ifp_s, right_image_ifp_s, stereo_image_flag = \
        StereoMonoFileDirHandler.get_mono_or_stereo_ifp_s_from_folder(
            path_to_folder)

    print(left_image_ifp_s)