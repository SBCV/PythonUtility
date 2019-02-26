import os
import platform
from shutil import copyfile
from Utility.Config import Config


class FFmpeg:

    parent_dp = os.path.dirname(os.path.realpath(__file__))
    path_to_config = os.path.join(parent_dp, 'FFmpeg.cfg')
    path_to_config_example = os.path.join(parent_dp, 'FFmpeg_example.cfg')
    if not os.path.isfile(path_to_config):
        copyfile(path_to_config_example, path_to_config)
    cloud_compare_config = Config(path_to_config)

    if platform.system() == 'Windows':
        path_to_executable = cloud_compare_config.get_option_value(
            'ffmpeg_path_windows', str)
    else:
        # this points to cloud compare 2.10 (with qt 5.7)
        path_to_executable = cloud_compare_config.get_option_value(
            'ffmpeg_path_linux', str)

    if not os.path.isfile(path_to_executable):
        path_to_executable = 'ffmpeg'

    @staticmethod
    def get_exec_path():
        return FFmpeg.path_to_executable