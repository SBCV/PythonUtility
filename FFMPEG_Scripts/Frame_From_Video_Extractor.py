__author__ = 'sebastian'

import os
import re
import subprocess

from Utility.Printing import ils
from Utility.Printing import print_salient_message
from Utility.Logging_Extension import logger


class VideoTime():
    START_TIME = 'start'
    END_TIME = 'end'
    NONE = 'none'


class FrameFromVideoExtractor:

    @staticmethod
    def is_time_in_number_format(time):
        result = False
        if time is not None:
            time_scheme = '[0-9][0-9]:[0-5][0-9]:[0-5][0-9]'
            pattern = re.compile(time_scheme)
            match_result = pattern.match(time)
            if match_result:
                result = True
        return result

    @staticmethod
    def split_string_in_text_and_number(some_string):
        head = some_string.rstrip('0123456789')
        tail = some_string[len(head):]
        return head, tail

    @staticmethod
    def decrease_image_index_by_one(folder, output_frame_name_scheme):
        image_files = [element for element in os.listdir(folder) if os.path.isfile(os.path.join(folder, element))]
        image_files = sorted(image_files)
        for image_file_old_name_with_ext in image_files:
            image_file_old_name, ext = os.path.splitext(image_file_old_name_with_ext)
            text_str, number_str = FrameFromVideoExtractor.split_string_in_text_and_number(image_file_old_name)
            image_file_new_name_with_ext = output_frame_name_scheme % (int(number_str) - 1)
            os.rename(os.path.join(folder, image_file_old_name_with_ext),
                      os.path.join(folder, image_file_new_name_with_ext))

    @staticmethod
    def convert_video_to_images(path_to_input_video,
                                path_to_output_frames,
                                output_frame_name_scheme,
                                frame_rate,
                                jpg_quality=2,
                                start_time=None,
                                end_time=None,
                                indent_level_space=1):

        """

        :param path_to_input_video:
        :param path_to_output_frames:
        :param output_frame_name_scheme: e.g. 'frame%05d.jpg'
        :param frame_rate: e.g. 12.5
        :param jpg_quality: a value from 2 (best) to 31 (worst)
        :param start_time:
        :param end_time:
        :param indent_level_space:
        :return:
        """

        print(ils(indent_level_space) + 'Converting video to images: ...')
        print(ils(indent_level_space + 1) + 'Output path: ' + path_to_output_frames)
        print(ils(indent_level_space + 1) + 'Output scheme: ' + output_frame_name_scheme)
        print(ils(indent_level_space + 1) + 'Start time: ' + str(start_time))
        print(ils(indent_level_space + 1) + 'End time: ' + str(end_time))

        options = []
        options += ['-nostdin']
        #options += ['-loglevel quiet']
        options += ["-i", path_to_input_video]
        # treat the input video as a video with a frame rate of 12.5 (no matter what the real frame rate is)
        options += ["-r", str(frame_rate)]
        # use the highest available quality for jpeg output (2 (best) - 31 (worst))
        options += ['-qscale:v', str(jpg_quality)]
        if FrameFromVideoExtractor.is_time_in_number_format(start_time):
            options += ["-ss", start_time]
        if FrameFromVideoExtractor.is_time_in_number_format(end_time):
            options += ["-to", end_time]
        output_path_and_frame_name_schmeme = os.path.join(
            path_to_output_frames, output_frame_name_scheme)
        options += [output_path_and_frame_name_schmeme]

        # Call: ffmpeg -i path_to_video -r frame_rate -qscale:v jpg_quality path_to_output_frames_scheme_names
        subprocess.call(["ffmpeg"] + options)

        #rename the images, so the index is starting with 0
        FrameFromVideoExtractor.decrease_image_index_by_one(
            path_to_output_frames, output_frame_name_scheme)

        print(ils(indent_level_space) + 'Converting video to images: Done')

    @staticmethod
    def extract_subpart_video(path_to_input_video,
                              path_to_output_video,
                              start_time,
                              end_time,
                              indent_level_space=1):

        # ffmpeg -i movie.mp4 -ss 00:00:03 -to 00:00:08 -async 1 cut.mp4

        print(ils(indent_level_space) + 'Converting video to subvideo: ...')
        print(ils(indent_level_space + 1) + 'Start time: ' + start_time)
        print(ils(indent_level_space + 1) + 'End time: ' + end_time)

        options = []
        options += ['-nostdin']
        #options += ['-loglevel quiet']
        options += ['-i', path_to_input_video]

        if FrameFromVideoExtractor.is_time_in_number_format(start_time):
            options += ['-ss', start_time]
        if FrameFromVideoExtractor.is_time_in_number_format(end_time):
            options += ['-to', end_time]
        options += [path_to_output_video]

        options += ['-an']  # remove sound from video


        # Call: ffmpeg -i path_to_video -r frame_rate -qscale:v jpg_quality path_to_output_frames_scheme_names
        subprocess.call(["ffmpeg"] + options)
        print(ils(indent_level_space) + 'Converting video to subvideo: Done')


    @staticmethod
    def extract_subpart_video_if_necessary(path_to_input_video,
                                           path_to_output,
                                           output_name_scheme,
                                           start_time,
                                           end_time,
                                           indent_level_space=1):

        path_to_output_video = os.path.join(path_to_output, output_name_scheme) \
                               + os.path.splitext(path_to_input_video)[1]

        if os.path.isfile(path_to_output_video):
            print(ils(indent_level_space) + 'THE OUTPUT VIDEO ALREADY EXISTS ... skipping video extraction')
        else:
            print(ils(indent_level_space) + 'Extracting Subpart Video: ...')
            print(ils(indent_level_space + 1) + 'Subpart Video name ' + str(path_to_output))
            FrameFromVideoExtractor.extract_subpart_video(
                path_to_input_video, path_to_output_video, start_time, end_time,
                indent_level_space=indent_level_space+1)
            print(ils(indent_level_space) + 'Extracting Subpart Video: Done')


    @staticmethod
    def extract_images_if_necessary(path_to_input_video,
                                    path_to_output,
                                    output_name_scheme,
                                    frames_img_folder_suffix,
                                    output_frame_name_scheme,
                                    frame_rate,
                                    jpg_quality,
                                    start_time,
                                    end_time,
                                    indent_level_space=1):

        path_to_output_frames = os.path.join(path_to_output, output_name_scheme + frames_img_folder_suffix)
        print_salient_message('Outputfolder is: ' + path_to_output_frames)

        if os.path.isdir(path_to_output_frames):
            print(ils(indent_level_space) +
                  'THE OUTPUT DIRECTORY ALREADY EXISTS ... skipping image extraction')
        else:
            print(ils(indent_level_space) + 'Extracting Subpart Images ...')
            os.makedirs(path_to_output_frames)

            FrameFromVideoExtractor.convert_video_to_images(
                path_to_input_video,
                path_to_output_frames,
                output_frame_name_scheme,
                frame_rate,
                jpg_quality,
                start_time,
                end_time,
                indent_level_space=indent_level_space+1)

    @staticmethod
    def process_video_extraction_tasks(tasks):
        for task in tasks:
            FrameFromVideoExtractor.extract_subpart_video_if_necessary(
                task.path_to_input_video,
                task.path_to_output,
                task.output_name_scheme,
                task.start_time,
                task.end_time,
                indent_level_space=task.indent_level_space)

    @staticmethod
    def process_image_extraction_tasks(tasks):
        for task in tasks:

            logger.info(str(task))

            FrameFromVideoExtractor.extract_images_if_necessary(
                task.path_to_input_video,
                task.path_to_output,
                task.output_name_scheme,
                task.frames_img_folder_suffix,
                task.output_frame_name_scheme,
                task.frame_rate,
                task.jpg_quality,
                task.start_time,
                task.end_time,
                indent_level_space=task.indent_level_space)

