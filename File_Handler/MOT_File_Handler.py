import os
from Utility.Logging_Extension import logger

class MOTFileHandler(object):

    # e.g https://github.com/abewley/sort/blob/master/data/ADL-Rundle-6/det.txt

    @staticmethod
    def tracklets_to_string(frame_number, tracklets):
        output_lines = []
        for d in tracklets:
            output_string = '%d,%d,%.2f,%.2f,%.2f,%.2f,1,-1,-1,-1' % \
                            (frame_number, d[4], d[0], d[1], d[2] - d[0], d[3] - d[1])
            output_lines.append(output_string)
        return output_lines


    @staticmethod
    def write_tracklets_to_file(path_to_output_file, frame_name_to_tracklet_bbox_s, frame_number_offset=1):
        """
        In the MOT challenge frame numbers start with 1
        """
        logger.info('write_tracklets_to_file: ...' )
        logger.vinfo('path_to_output_file', path_to_output_file)

        #logger.vinfo('frame_name_to_tracklet_bbox', frame_name_to_tracklet_bbox)
        out_lines = []
        for frame_number, frame_name in enumerate(sorted(frame_name_to_tracklet_bbox_s.keys())):
            tracklets = frame_name_to_tracklet_bbox_s[frame_name]
            logger.vinfo('frame_name', frame_name)
            logger.vinfo('tracklets', tracklets)
            frame_number += frame_number_offset
            out_lines += MOTFileHandler.tracklets_to_string(
                frame_number, tracklets)

        output_file = open(path_to_output_file, 'wb')
        output_file.writelines([item + os.linesep for item in out_lines])
        logger.info('write_tracklets_to_file: Done')

