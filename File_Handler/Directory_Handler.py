# https://docs.python.org/2/library/re.html
import re
import glob
import os
from Utility.Logging_Extension import logger
import shutil

# ============================================================================================================
# If you are looking for functions, to iterate over all images in a folder go to Utility/OS_Extension!
# ============================================================================================================

class DirectoryHandler:

    # https://docs.python.org/2/library/re.html#re.compile
    # Compile a regular expression pattern into a regular expression object, which can
    # be used for matching using its match() and search() methods, described below.

    @staticmethod
    def get_matching_files_in_folder(folder_path_name, regex_pattern, file_ext):

        """
        regex_pattern = ".*[0-9]{4}-[0-9]{2}-[0-9]{2}_[0-9]{2}h[0-9]{2}_[0-9]{2}"
        [0-9]{4} : repeats 4 times the numbers 0-9

        :param folder_path_name:
        :param file_ext:
        :return:
        """
        logger.info('get_matching_files_in_folder:...')

        possible_files = sorted(glob.glob(os.path.join(folder_path_name, '*' + file_ext)))
        # prepend the folder name to the regex, so it matches the output of glob.glob()
        regex_pattern = os.path.join(folder_path_name, regex_pattern)
        pattern = re.compile(regex_pattern)
        matching_files = [model_file for model_file in possible_files if pattern.match(model_file)]

        logger.info('get_matching_files_in_folder:Done')
        return matching_files

    @staticmethod
    def append_suffix_to_files_in_folder(idp, odp, suffix):
        logger.info('append_suffix_to_files_in_folder:...')

        ifn_s = [ele for ele in os.listdir(idp) if os.path.isfile(os.path.join(idp, ele))]

        for ifn in ifn_s:
            name, ext = os.path.splitext(ifn)
            shutil.copyfile(os.path.join(idp, ifn), os.path.join(odp, name + suffix + ext))
        logger.info('append_suffix_to_files_in_folder:Done')


if __name__ == '__main__':

    # ==========================

    # possible_file_names = ['with_rd_with_sc_with_calib.nvm',
    #                        'with_rd_with_sc_with_calib_model_0.nvm',
    #                        'with_rd_with_sc_with_calib_model_0_min_measurement_3.nvm']
    #
    # regex_pattern = 'with_rd_with_sc_with_calib_model_[0-9]+.nvm'
    # pattern = re.compile(regex_pattern)
    #
    # matching_files = [model_file for model_file in possible_file_names if pattern.match(model_file)]
    # logger.info(matching_files)

    # ==========================

    idp = ''
    odp = ''
    suffix = '_right'
    DirectoryHandler.append_suffix_to_files_in_folder(
        idp, odp, suffix)