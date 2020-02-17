import sys
import platform
import subprocess
import os

horizontal_center = 'x=(w-tw)/2'
horizontal_right_margin = 'x=(w-tw)'
vertical_bottom_margin = 'y=h-(2*lh)'


class VideoDrawer(object):

    @staticmethod
    def _get_font_ifp():
        if platform.system() == 'windows':
            font_ifp = 'C:\\Windows\\Fonts\\Arial.ttf'
        else:
            font_ifp = '/usr/share/fonts/truetype/freefont/FreeMono.ttf'
        return font_ifp

    @staticmethod
    def _get_font_ifp_option():
        return 'fontfile=' + VideoDrawer._get_font_ifp()


    @staticmethod
    def _get_font_size_option(size):
        return 'fontsize=' + str(size)

    @staticmethod
    def _get_color_option(color):
        return 'fontcolor=' + color

    @staticmethod
    def _get_activate_box_option():
        return 'box=1'

    @staticmethod
    def _get_box_color_option(color):
        return 'boxcolor=' + color

    @staticmethod
    def _get_box_with_option(width):
        return 'boxborderw=' + str(width)

    @staticmethod
    def _get_text_option(text):
        return 'text=\'' + str(text) + '\''

    @staticmethod
    def _get_frame_number_text_option():
        return 'text=\'%{frame_num}\''

    @staticmethod
    def _get_start_number_option(start_number):
        return 'start_number=' + str(start_number)

    @staticmethod
    def _get_enable_between_option(start, end, values_in_frames=True):
        # This option is used to show some string only in a specific subpart of the video

        # http://ffmpeg.org/ffmpeg-all.html#Expression-Evaluation
        # n: the number of current processed frame, starting from 0
        # t: the number of current processed frame, starting from 0

        if values_in_frames:
            test_variable = 'n'
        else:
            test_variable = 't'

        return 'enable=\'between(' + test_variable + ',' + str(start) + ',' + str(end) + ')\''

    @staticmethod
    def _create_colon_separated_draw_options(option_list):
        option_str = ''
        option_str += '"'   # prepend quote
        option_str += 'drawtext='

        for ele in option_list[:-1]:
            option_str += ele + ': '
        option_str += option_list[-1]

        option_str += '"'   # append quote
        return option_str

    @staticmethod
    def add_text_to_video(ifp,
                          ofp,
                          text_time_interval_triples_list=None,
                          add_frame_numbers=True):

        options = ''
        options += ' ' + '-i'
        options += ' ' + ifp
        options += ' ' + '-vf'

        font_ifp_option = VideoDrawer._get_font_ifp_option()
        x_pos_option = horizontal_center
        y_pos_option = vertical_bottom_margin
        font_color_option = VideoDrawer._get_color_option('black')
        font_size_option = VideoDrawer._get_font_size_option(20)

        active_box_option = VideoDrawer._get_activate_box_option()
        box_color_option = VideoDrawer._get_box_color_option('green')
        box_width_option = VideoDrawer._get_box_with_option(5)

        if text_time_interval_triples_list is not None:
            draw_text_options = ''
            for index, text_with_time_stamp in enumerate(text_time_interval_triples_list):

                text_option = VideoDrawer._get_text_option(text_with_time_stamp[0])
                start = text_with_time_stamp[1]
                end = text_with_time_stamp[2]
                enable_between_option = VideoDrawer._get_enable_between_option(start, end)

                single_draw_options = VideoDrawer._create_colon_separated_draw_options(
                    [font_ifp_option,
                     text_option,
                     enable_between_option,
                     x_pos_option,
                     y_pos_option,
                     font_color_option,
                     font_size_option,
                     active_box_option,
                     box_color_option,
                     box_width_option
                     ])

                if index > 0:
                    draw_text_options += ','     # draw commands must be comma separated
                draw_text_options += single_draw_options

            options += ' ' + draw_text_options

        if add_frame_numbers:

            frame_number_text_option = VideoDrawer._get_frame_number_text_option()
            start_number_option = VideoDrawer._get_start_number_option(0)
            x_pos_option = horizontal_right_margin

            draw_options = VideoDrawer._create_colon_separated_draw_options(
                [font_ifp_option,
                 frame_number_text_option,
                 start_number_option,
                 x_pos_option,
                 y_pos_option,
                 font_color_option,
                 font_size_option,
                 active_box_option,
                 box_color_option,
                 box_width_option
                 ])

            if text_time_interval_triples_list is not None:
                options += ',' + draw_options # draw commands must be comma separated
            else:
                options += ' ' + draw_options

        options += ' ' + '-c:a'
        options += ' ' + 'copy'

        call_str = 'ffmpeg' + ' ' + options + ' ' + ofp
        print('call_str', call_str)
        subprocess.call(call_str, shell=True)

        # Make sure the file has been created
        assert os.path.isfile(ofp)
