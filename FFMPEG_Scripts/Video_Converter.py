import subprocess
import os
from Utility.Logging_Extension import logger

class VideoConverter:

    @staticmethod
    def remove_meta_ata_from_video(path_to_input_file, path_to_output_file):
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

