__author__ = 'sebastian'

import os
import subprocess
import platform
import shutil

from Utility.Logging_Extension import logger

class VideoFromImageCreator:

    def __init__(self, frame_rate=12.5):

        # By using a separate frame rate for the input and output you can control the duration at which each input is displayed
        # and tell ffmpeg the frame rate you want for the output file
        self.frame_rate = frame_rate

    def split_text_and_number_string(self, text_and_number_string):
        head = text_and_number_string.rstrip('0123456789')
        tail = text_and_number_string[len(head):]
        return head, tail

    def _count_missing_images(self, sorted_file_list):
        logger.debug('_count_missing_images: ...')
        number_missing_images = 0
        try:
            text_str, current_number_str = self.split_text_and_number_string(os.path.splitext(sorted_file_list[0])[0])
            last_number = int(current_number_str)

            for file_name in sorted_file_list[1:]:
                text_str, current_number_str = self.split_text_and_number_string(os.path.splitext(file_name)[0])
                current_number = int(current_number_str)
                if current_number != last_number + 1:
                    current_missing_images = current_number - last_number - 1
                    logger.info('There are ' + str(current_missing_images) + ' images missing between ' + str(
                        last_number) + ' and ' + str(current_number))
                    number_missing_images += current_missing_images
                last_number = current_number
            valid_count = True
        except ValueError:
            valid_count = False

        logger.debug('_count_missing_images: Done')
        return number_missing_images, valid_count

    def _get_starting_index(self, sorted_file_list):
        text_str, current_number_str = self.split_text_and_number_string(os.path.splitext(sorted_file_list[0])[0])
        try:
            starting_index = int(current_number_str)
        except:
            starting_index = -1
        return starting_index

    def _get_file_list_in_folder(self, path_to_images):
        return [os.path.join(path_to_images, element) for element in os.listdir(path_to_images) if
         os.path.isfile(os.path.join(path_to_images, element))]

    def _file_extension_from_file_list(self, file_list):

        file_list = sorted(file_list)

        extension_set = set()
        for file_name in file_list:
            extension_set.add(os.path.splitext(file_name)[1])
        extension_list = list(extension_set)
        assert (len(extension_list) == 1)
        ext = extension_list[0]
        return ext

    def _renaming_files_to_sequential_order_if_necessary(self, path_to_images, sequential_image_name_scheme):
        """
        FFMPEG REQUIRES (in sequential mode) a SEQUENTIAL naming of the input files.
        The sequence MUST start with 0
        """
        file_list = self._get_file_list_in_folder(path_to_images)
        logger.info('file_list: ' + str(file_list))
        ext = self._file_extension_from_file_list(file_list)
        logger.info('Found image extension: ' + str(ext))

        sorted_file_list = sorted(file_list)

        missing_images, valid_count = self._count_missing_images(sorted_file_list=sorted_file_list)
        logger.info('missing_images: ' + str(missing_images))
        logger.info('There are overall ' + str(missing_images) + ' missing images')
        starting_index = self._get_starting_index(sorted_file_list=sorted_file_list)
        logger.info('starting_index: ' + str(starting_index))
        if missing_images > 0 or starting_index > 0 or not valid_count:
            if not valid_count:
                logger.info('RENAMING FILES, BECAUSE NAMING SEQUENCE ARE NOT REPRESENTING NUMBERS')
            if missing_images > 0:
                logger.info('RENAMING FILES, BECAUSE NAMING SEQUENCE CONTAINS GAPS')
            if starting_index > 0:
                logger.info('RENAMING FILES, BECAUSE SEQUENCE DOES NOT START WITH 0')
            for index, file_name in enumerate(sorted_file_list):
                os.rename(os.path.join(path_to_images, file_name),
                          os.path.join(path_to_images, sequential_image_name_scheme % index + ext))


    def create_video_from_images(self,
                                 path_to_images,
                                 video_ofp,
                                 filter_str='',
                                 add_ignore_file=True,
                                 temp_dir_name='TMP',
                                 lazy=True):

        """
        Creates a video from images using one of two different modes
            pattern_type GLOB
            pattern_type SEQUENTIAL
        Recommended way is GLOB, since SEQUENTIAL requires a renaming of the files
        if they do not start with 0 or are not sequential

        :return:
        """

        logger.info('create_video_from_images:...')
        sequential_renaming_image_name_scheme = 'frame%05d'

        # Windows does not support GLOB in FFMPEG.
        # Make a copy of the files, rename them in a sequential way,
        # create the video and copied files afterwards.
        need_to_use_temp_files = platform.system() == 'Windows'
        use_ffmpeg_sequential = need_to_use_temp_files

        if need_to_use_temp_files:
            assert not os.path.isdir(os.path.join(path_to_images, temp_dir_name))
            shutil.copytree(path_to_images, os.path.join(path_to_images, temp_dir_name))
            path_to_images = os.path.join(path_to_images, temp_dir_name)

        if use_ffmpeg_sequential:
            # THIS IS REQUIRED FOR ffmpeg SEQUENCE to work
            self._renaming_files_to_sequential_order_if_necessary(
                path_to_images, sequential_renaming_image_name_scheme)

        file_list = self._get_file_list_in_folder(path_to_images)
        ext = self._file_extension_from_file_list(file_list)

        if use_ffmpeg_sequential:
            sequential_renaming_image_name_scheme_with_ext = sequential_renaming_image_name_scheme + ext
            sequential_renaming_image_name_scheme_with_ext_and_path = os.path.join(
                path_to_images, sequential_renaming_image_name_scheme_with_ext)

        logger.info("path_to_output_video_and_name: " + video_ofp)

        if not lazy and os.path.isfile(video_ofp):
            os.remove(video_ofp)

        if not os.path.isfile(video_ofp):

            # ffmpeg -framerate 1/5 -i img%03d.png -c:v libx264 -r 30 -pix_fmt yuv420p out.mp4
            #
            # ====== Remark to the Usage of Wild Cards ======
            # https://www.ffmpeg.org/ffmpeg-formats.html
            #   * see pattern_type
            #       * possible values: SEQUENCE, GLOB, GLOB_SEQUENCE (deprecated)
            #
            #       * Use GLOB to handle sequences, which contain GAPS or start with ANOTHER INDEX than 0
            #           * Advantage: No renaming of the files required
            #           * It is important that the pattern (i.e. ' "*.jpg" ') is in DOUBLE QUOTES!!!
            #             (see example below)
            #           * It is also possible to use the ** expression for arbitrary subdirectories
            #           * TO SUPPORT WILDCARDS + DOUBLE QUOTES
            #               * one must use a COMMAND string INSTEAD of a LIST
            #               * one must use subprocess.call with shell=True
            #
            # ====== Example Call ======
            # example_command = 'ffmpeg ' \
            #                   '-framerate 1 ' \
            #                   '-pattern_type glob ' \
            #                   '-i "/media/somePath/*.jpg"' \
            #                   ' -c:v libx264 ' \
            #                   '/media/somePath/out.mp4'
            # subprocess.call(example_command, shell=True)

            options = ''

            # https://ffmpeg.org/ffmpeg.html
            #   5.5 Video Options
            #       If in doubt use -framerate instead of the input option -r

            options += '-framerate ' + str(self.frame_rate)

            if use_ffmpeg_sequential:
                input_source = ' ' + sequential_renaming_image_name_scheme_with_ext_and_path
            else:
                options += ' ' + '-pattern_type glob'
                string_with_wild_card_and_double_quotes = '"' + os.path.join(path_to_images, '*' + filter_str + '*' + ext) + '"'
                input_source = ' ' + string_with_wild_card_and_double_quotes

            options += ' ' + '-i'
            options += ' ' + input_source

            options += ' ' + '-c:v libx264'

            # Round uneven image dimensions, otherwise a an error "width not divisible by 2" or
            # "height not divisible by 2" is thrown
            options += ' ' + '-vf'
            options += ' ' + '"scale=trunc(iw/2)*2:trunc(ih/2)*2"'

            # Call: ffmpeg -i path_to_video -r frame_rate -qscale:v jpg_quality path_to_output_frames_scheme_names
            call_str = 'ffmpeg' + ' ' + options + ' ' + video_ofp
            print(call_str)

            # it is crucial to call a command STRING (no list) + and shell=True
            subprocess.call(call_str, shell=True)

            if need_to_use_temp_files:
                shutil.rmtree(path_to_images)

            if add_ignore_file:
                # Create an ignore file, which avoids that this file is reread by the reconstruction pipeline
                ignore_file_name = os.path.splitext(video_ofp)[0] + '_ignore.txt'
                if not os.path.isfile(ignore_file_name):
                    os.mknod(ignore_file_name)

        else:
            logger.info('Do not create video, it already exists')

        logger.info('create_video_from_images:Done')

    def process_video_creation_tasks(self, video_creation_tasks):
        for video_creation_task in video_creation_tasks:
            self.create_video_from_images(
                path_to_images=video_creation_task.path_to_images,
                video_ofp=video_creation_task.output_video_path)


if __name__ == '__main__':

    path_to_images = ''

    path_to_output_video_and_name = os.path.join(
        os.path.dirname(path_to_images),
        os.path.basename(path_to_images) + '.mp4')

    frame_rate = 12.5
    add_ignore_file = False

    video_from_image_creator = VideoFromImageCreator(frame_rate)
    video_from_image_creator.create_video_from_images(
        path_to_images=path_to_images,
        video_ofp=path_to_output_video_and_name,
        add_ignore_file=add_ignore_file)
