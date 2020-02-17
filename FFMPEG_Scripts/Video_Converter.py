import subprocess
import os
import re
import sys
import shlex
import json
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

sys.stdout = Unbuffered(sys.stdout)
sys.stderr = Unbuffered(sys.stderr)


# def escape_spaces(some_str):
#     return some_str.replace(" ", "\\ ")
#
# def ensure_quotes(some_str):
#     starts_with_quote = some_str.startswith("'") or some_str.startswith('"')
#     ends_with_quote = some_str.endswith("'") or some_str.endswith('"')
#     if not starts_with_quote and ends_with_quote:
#         some_str = '"' + some_str
#         some_str = some_str + '"'
#     return some_str

def check_path(ifp):
    assert not " " in ifp

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
    # function to find the resolution of the input video file
    def get_video_resolution(ifp):
        cmd = "ffprobe -v quiet -print_format json -show_streams"
        args = shlex.split(cmd)
        args.append(ifp)
        # run the ffprobe process, decode stdout into utf-8 & convert to JSON
        ffprobeOutput = subprocess.check_output(args).decode('utf-8')
        ffprobeOutput = json.loads(ffprobeOutput)

        # find height and width
        height = ffprobeOutput['streams'][0]['height']
        width = ffprobeOutput['streams'][0]['width']

        return height, width

    @staticmethod
    def get_video_height(ifp):
        return VideoConverter.get_video_resolution(ifp)[0]

    @staticmethod
    def get_video_width(ifp):
        return VideoConverter.get_video_resolution(ifp)[1]

    @staticmethod
    def stack_videos_vertically(ifp_list, ofp, show_progress=False):

        assert isinstance(ifp_list, list)
        # https://stackoverflow.com/questions/11552565/vertically-or-horizontally-stack-several-videos-using-ffmpeg/33764934#33764934
        # Input videos must have the same spatial extent
        options = []
        for ifp in ifp_list:
            options += ['-i', ifp]
        options += ['-filter_complex', 'vstack=inputs=' + str(len(ifp_list))]
        options += [ofp]

        cmd = [FFmpeg.path_to_executable] + options

        if show_progress:
            VideoConverter._run_and_show_progress_in_stderr(cmd)
        else:
            subprocess.call(cmd)

    @staticmethod
    def stack_videos_horizontally(ifp_list, ofp, lazy=False):

        assert isinstance(ifp_list, list)

        # https://ffmpeg.org/ffmpeg-all.html
        #   -filter[:stream_specifier] filtergraph (output,per-stream)
        #       - Create the filtergraph specified by filtergraph and use it to filter the stream.
        #       - filtergraph is a description of the filtergraph to apply to the stream, and must have a single input
        #       and a single output of the same type of the stream. In the filtergraph, the input is associated to the
        #       label in, and the output to the label out. See the ffmpeg-filters manual for more information about the
        #       filtergraph syntax.
        #       - See the -filter_complex option if you want to create filtergraphs with multiple inputs and/or outputs.
        #
        #   -filter_complex filtergraph (global)
        #       ... Here [0:v] refers to the first video stream in the first input file
        #
        #   Example: unlabeled filtergraph outputs
        #       The overlay filter requires exactly two video inputs, but none are specified,
        #       so the first two available video streams are used

        # https://ffmpeg.org/ffmpeg-filters.html

        options = []

        # Find the maximal height of all provided videos
        max_height_str = str(max([VideoConverter.get_video_height(ifp) for ifp in ifp_list]))

        def get_padded_str(i):
            return '[padded' + str(i) + ']'

        def get_overlay_str(i):
            return '[overlay' + str(i) + ']'

        def get_video_stream_str(i):
            return '[' + str(i) + ':v]'

        filter_complex_str = ''

        for i, ifp in enumerate(ifp_list):
            options += ['-i', ifp]

        previous_total_width = VideoConverter.get_video_width(ifp_list[0])
        for i, ifp in enumerate(ifp_list[1:], start=1):

            current_total_width = previous_total_width + VideoConverter.get_video_width(ifp_list[i])

            # padding filter
            if i == 1:
                prev_video_input_stream = get_video_stream_str(i-1)
            else:
                prev_video_input_stream = get_overlay_str(i-1)
            prev_padded_stream = get_padded_str(i-1)
            filter_complex_str += prev_video_input_stream                           # Input stream
            filter_complex_str += 'pad=' + str(current_total_width) + ':' + max_height_str
            filter_complex_str += prev_padded_stream                                # Output Stream
            filter_complex_str += ';'

            # overlay filter
            current_video_stream = get_video_stream_str(i)
            current_overlay_stream = get_overlay_str(i)
            filter_complex_str += prev_padded_stream                                # First input stream
            filter_complex_str += current_video_stream                              # Second input stream
            filter_complex_str += 'overlay=' + str(previous_total_width) + ':0'     # Takes two streams as input
            filter_complex_str += current_overlay_stream                            # Output Stream

            # Append a semi colon except for the last iteration
            if i != len(ifp_list)-1:
                filter_complex_str += ';'

            previous_total_width = current_total_width

        options += ['-filter_complex', filter_complex_str]
        options += ['-map', current_overlay_stream]
        options += ['-c:v', 'libx264']
        options += ['-crf', '23']
        options += ['-preset', 'veryfast']
        if not lazy:
            options += ['-y']
        options += [ofp]
        stack_call = ['ffmpeg'] + options
        print(stack_call)
        subprocess.call(stack_call)

    @staticmethod
    def extract_subpart_video(video_ifp,
                              video_ofp,
                              start_time=None,
                              end_time=None,
                              start_frame=None,
                              end_frame=None,
                              indent_level_space=1,
                              show_progress=False):

        print('extract_subpart_video: ...')
        time_provided = start_time is not None and end_time is not None
        print(time_provided)
        frames_provided = start_frame is not None and end_frame is not None

        assert time_provided != frames_provided

        # The order of -i and -ss matters, see:
        #   https://blog.superuser.com/2012/02/24/ffmpeg-the-ultimate-video-and-audio-manipulation-tool/

        options = []
        options += ['-nostdin']
        #options += ['-loglevel quiet']
        options += ['-i', video_ifp]

        if time_provided:

            # With time in seconds
            # ffmpeg -i movie.mp4 -ss 00:00:03 -to 00:00:08 -async 1 cut.mp4
            assert VideoConverter.is_time_in_number_format(start_time)
            assert VideoConverter.is_time_in_number_format(end_time)
            print('Start time: ' + start_time)
            print('End time: ' + end_time)
            options += ['-ss', start_time]
            options += ['-to', end_time]

        elif frames_provided:

            # https://superuser.com/questions/866144/cutting-videos-at-exact-frames-with-ffmpeg-select-filter
            #   ffmpeg -i in.mp4 -vf "select=between(n\,start_frame\,end_frame),setpts=PTS-STARTPTS" out.mp4

            options += ['-vf',
                        '"select=between(n\,' + str(start_frame) + '\,' + str(end_frame) + '),' +
                        'setpts=PTS-STARTPTS"']
        else:
            assert False

        # TODO Consider specific copy options
        # options += ['-c', 'copy']
        # options += ['-c:v', 'copy']
        # options += ['-c:a', 'copy']

        options += [video_ofp]
        options += ['-an']  # remove sound from video

        # Call: ffmpeg -i path_to_video -r frame_rate -qscale:v jpg_quality path_to_output_frames_scheme_names
        call_list = ["ffmpeg"] + options

        call_str = ' '.join(call_list)
        print('call_str', call_str)

        if show_progress:
            VideoConverter._run_and_show_progress_in_stderr(call_str, shell=True)
        else:
            subprocess.call(call_str, shell=True)

        print('extract_subpart_video: Done')

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
        print('call_str', call_str)
        subprocess.call(call_str, shell=True)


    @staticmethod
    def _run_and_show_progress_in_stderr(cmd_list_or_string, shell=False):

        # The argument "universal_newlines" is necessary that FFmpeg writes out the progress immediately
        # https://docs.python.org/3/glossary.html#term-universal-newlines
        sub_process = subprocess.Popen(cmd_list_or_string, shell=shell, stderr=subprocess.PIPE, universal_newlines=True)
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

