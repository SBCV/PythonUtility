import subprocess
import os
import re
import sys
from Utility.Printing import ils
from Utility.Logging_Extension import logger
import platform
from Utility.FFMPEG_Scripts.FFmpeg import FFmpeg


class Unbuffered(object):
   def __init__(self, stream):
       self.stream = stream
   def write(self, data):
       self.stream.write(data)
       self.stream.flush()
   def writelines(self, datas):
       self.stream.writelines(datas)
       self.stream.flush()
   def __getattr__(self, attr):
       return getattr(self.stream, attr)

import sys
sys.stdout = Unbuffered(sys.stdout)
sys.stderr = Unbuffered(sys.stderr)

class VideoConverter(object):

    # https://ffmpeg.org/ffmpeg.html#Generic-options
    #   shows the different log levels
    log_level_info = 'info'
    log_level_verbose = 'verbose'
    log_level_debug = 'debug'               # this prints information for each frame

    # https://ffmpeg.org/ffmpeg.html#toc-Main-options
    #
    # -stats (global)
    #   Print encoding progress/statistics.
    #   It is on by default, to explicitly disable it you need to specify -nostats
    #
    # -progress url (global)
    #   Send program-friendly progress information to url.
    #   Progress information is written approximately every second and at the end of the encoding process.
    #   It is made of "key=value" lines. key consists of only alphanumeric characters.
    #   The last key of a sequence of progress information is always "progress".

    # Although "ffmpeg -h" does not list the "-program" option its there

    # https://stackoverflow.com/questions/54385690/how-to-redirect-progress-option-output-of-ffmpeg-to-stderr
    #   example for the "-progress" option
    progress_stdout = "pipe:1"
    progress_stderr = "pipe:2"


    # https://github.com/althonos/ffpb/blob/master/ffpb.py
    # https://github.com/sidneys/ffmpeg-progressbar-cli
    #   Javascript

    # https://stackoverflow.com/questions/7632589/getting-realtime-output-from-ffmpeg-to-be-used-in-progress-bar-pyqt4-stdout

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
    def _general_options():

        # https://trac.ffmpeg.org/wiki/Encode/H.264
        options = ['-preset', 'ultrafast']
        return options

    @staticmethod
    def stack_videos_vertically(ifp1, ifp2, ofp, show_progress=False):

        # https://stackoverflow.com/questions/11552565/vertically-or-horizontally-stack-several-videos-using-ffmpeg/33764934#33764934
        # Input videos must have the same spatial extent
        options = []
        options += ['-i', ifp1]
        options += ['-i', ifp2]
        options += ['-filter_complex', 'vstack=inputs=2']
        options += [ofp]

        cmd = [FFmpeg.path_to_executable] + options

        if show_progress:
            VideoConverter._run_and_show_progress_in_stderr(cmd)
        else:
            subprocess.call(cmd)



    @staticmethod
    def stack_videos_horizontally(ifp1, ifp2, ofp):

        # https://unix.stackexchange.com/questions/233832/merge-two-video-clips-into-one-placing-them-next-to-each-other
        # The spatial extent of the second video must be smaller than the first one
        options = []
        options += ['-i', ifp1]
        options += ['-i', ifp2]
        options += ['-filter_complex', '[0:v]pad=iw*2:ih[int];[int][1:v]overlay=W/2:0[vid]']
        options += ['-map', '[vid]']
        options += ['-c:v', 'libx264']
        options += ['-crf', '23']
        options += ['-preset', 'veryfast']
        options += [ofp]

        subprocess.call(['ffmpeg'] + options)


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

        # The order of -i and -ss matters, see:
        #   https://blog.superuser.com/2012/02/24/ffmpeg-the-ultimate-video-and-audio-manipulation-tool/

        options = []
        options += ['-nostdin']
        #options += ['-loglevel quiet']
        options += ['-i', path_to_input_video]

        if VideoConverter.is_time_in_number_format(start_time):
            options += ['-ss', start_time]
        else:
            assert False
        if VideoConverter.is_time_in_number_format(end_time):
            options += ['-to', end_time]
        else:
            assert False

        # TODO Consider specific copy options
        # options += ['-c', 'copy']
        # options += ['-c:v', 'copy']
        # options += ['-c:a', 'copy']

        options += [path_to_output_video]

        options += ['-an']  # remove sound from video


        # Call: ffmpeg -i path_to_video -r frame_rate -qscale:v jpg_quality path_to_output_frames_scheme_names
        subprocess.call(["ffmpeg"] + options)
        print(ils(indent_level_space) + 'Converting video to subvideo: Done')

    @staticmethod
    def remove_meta_data_from_video(path_to_input_file, path_to_output_file):
        # ffmpeg -i in.mov -map_metadata -1 -c:v copy -c:a copy out.mov

        options = []
        options += ['-i', path_to_input_file]
        options += ['-map_metadata', '-1']
        options += ['-c:v', 'copy']
        options += ['-c:a', 'copy']
        options += [path_to_output_file]

        subprocess.call(['ffmpeg'] + options)

    @staticmethod
    def remove_audio_from_video_file(path_to_input_file, path_to_output_file):

        # FFMPEG cant overwrite input file
        assert path_to_input_file != path_to_output_file

        # ffmpeg -i example.mkv -c copy -an example-nosound.mkv

        # http://ffmpeg.org/ffmpeg.html#SEC8
        #       -c[:stream_specifier] codec (input/output,per-stream)
        #       -codec[:stream_specifier] codec (input/output,per-stream)
        #           Select an encoder (when used before an output file) or a decoder (when used before an input file)
        #           for one or more streams.
        #           codec is the name of a decoder/encoder or a special value copy (output only) to indicate that the
        #           stream is not to be re-encoded.
        #      -an (output): Disable audio recording.

        options = []
        options += ['-i', path_to_input_file]
        # treat the input video as a video with a frame rate of 12.5 (no matter what the real frame rate is)
        options += ['-c', 'copy']
        # use the highest available quality for jpeg output (2 (best) - 31 (worst))
        options += ['-an']

        options += [path_to_output_file]

        # Call: ffmpeg -i path_to_video -r frame_rate -qscale:v jpg_quality path_to_output_frames_scheme_names
        subprocess.call(['ffmpeg'] + options)

    @staticmethod
    def remove_audio_from_all_video_files_in_folder(path_to_folder, video_file_exts=['.MOV']):

        for root, dirs, files in os.walk(path_to_folder):

            print('Current Folder: ' + root)

            for file in files:
                file_stem, file_ext = os.path.splitext(file)
                path_to_file = os.path.join(root, file)

                if file_ext in video_file_exts:
                    print('Found Video File: ' + path_to_file)
                    path_to_temp_file = os.path.join(root, file_stem + '_temp' + file_ext)
                    VideoConverter.remove_audio_from_video_file(path_to_file, path_to_temp_file)
                    assert os.path.isfile(path_to_temp_file)
                    os.remove(path_to_file)
                    os.rename(path_to_temp_file, path_to_file)

    @staticmethod
    def subsample_framerate(ifp, ofp, factor=1.0):

        options = ''
        options += ' ' + '-i'
        options += ' ' + ifp
        options += ' ' + '-filter:v'
        options += ' ' + '"setpts=' + str(factor) + '*PTS"'

        call_str = 'ffmpeg' + ' ' + options + ' ' + ofp
        subprocess.call(call_str, shell=True)

    @staticmethod
    def resize_video(ifp, ofp, new_width=None, new_height=None):

        """ Either new_width or new_height has to be provided """

        options = ''
        options += ' ' + '-i'
        options += ' ' + ifp
        if new_width is not None and new_height is not None:
            # Use the basic scale option -s
            options += ' ' + '-s'
            options += ' ' + str(new_width) + 'x' + str(new_height)

        elif new_width is not None or new_height is not None:
            # Use the scale filter
            options += ' ' + '-vf'
            if new_height is not None:
                options += ' ' + 'scale="trunc(oh*a/2)*2:' + str(new_height) + '"'
            elif new_width is not None:
                options += ' ' + 'scale="' + str(new_width) +':trunc(ow/a/2)*2"'
        else:
            assert False

        call_str = 'ffmpeg' + ' ' + options + ' ' + ofp
        logger.vinfo('call_str', call_str)
        subprocess.call(call_str, shell=True)

    @staticmethod
    def add_frame_numbers_to_video(ifp, ofp):
        # https://stackoverflow.com/questions/15364861/frame-number-overlay-with-ffmpeg
        # https://stackoverflow.com/questions/8103808/ffmpeg-drawtext-could-not-load-fontface-from-file

        if platform.system() == 'windows':
            font_ifp = 'C:\\Windows\\Fonts\\Arial.ttf'
        else:
            font_ifp = '/usr/share/fonts/truetype/freefont/FreeMono.ttf'

        # x_pos = 'x=(w-tw)/2'    # center horizontally
        x_pos = 'x=(w-tw)'        # right border
        y_pos = 'y=h-(2*lh)'

        options = ''
        options += ' ' + '-i'
        options += ' ' + ifp
        options += ' ' + '-vf'
        options += ' ' + '"drawtext=fontfile=' + font_ifp + ': text=\'%{frame_num}\': start_number=0: ' + \
                   x_pos + ': ' + y_pos + ': fontcolor=black: fontsize=20: box=1: boxcolor=white: boxborderw=5"'
        options += ' ' + '-c:a'
        options += ' ' + 'copy'

        call_str = 'ffmpeg' + ' ' + options + ' ' + ofp
        logger.vinfo('call_str', call_str)
        subprocess.call(call_str, shell=True)

    @staticmethod
    def _run_and_show_progress_in_stderr(cmd_list):

        # The argument "universal_newlines" is necessary that FFmpeg writes out the progress immediately
        # https://docs.python.org/3/glossary.html#term-universal-newlines
        sub_process = subprocess.Popen(cmd_list, stderr=subprocess.PIPE, universal_newlines=True)
        output_str = ''
        printed_user_question = False
        condition = True
        while condition:  # asynchronous reading of the information

            if not printed_user_question:
                symbol = sub_process.stderr.read(1)
                sys.stderr.write(symbol)

                output_str += symbol
                if 'frame=' in output_str or 'Overwrite ? [y/N]' in output_str:
                    printed_user_question = True

            else:
                line = sub_process.stderr.readline()
                sys.stderr.write(line)

                if line.rstrip() == '':
                    condition = False

    @staticmethod
    def _run_and_show_progress_in_stdout(cmd):

        # Note: Better use "_run_and_show_progress_in_stderr"

        # The default information of ffmpeg is written to stderr,
        # therefore we write the progress information to stdout
        # This way the progress out put can be easily parsed
        cmd += ['-progress', 'pipe:1']

        # - Provide the "stdout=subprocess.PIPE" argument to read ANY output
        #   of the subprocess with sub_process.stdout.readline()
        # - Provide the "stderr=subprocess.PIPE" argument to read ANY output
        #   of the subprocess with sub_process.stdout.readline()
        # - Since we want to see the standard output of FFMPEG (which is written to stderr),
        #   the following must not contain "stderr=subprocess.PIPE"
        sub_process = subprocess.Popen(cmd, stdout=subprocess.PIPE, universal_newlines=True)

        # parse the output written by progress to pipe:1 and show only the relevant information
        condition = True
        while condition:    # asynchronous reading of the information

            # Read the output of the subprocess from stdout
            line = sub_process.stdout.readline()
            line = line.rstrip()

            print(line)

            if line == 'progress=end':
                 condition = False

