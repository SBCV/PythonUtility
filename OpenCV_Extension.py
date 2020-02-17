from __future__ import print_function

import cv2
print('cv2.__version__: ' + cv2.__version__)
assert cv2.__version__ >= '3.4.1'       # cv2.VideoCapture produced incorrect meta with opencv version 3.2.0


def get_video_meta_data(video_ifp):

    # This returns a rough estimation of frames
    video_capture = cv2.VideoCapture(video_ifp)
    total_frames_video = int(video_capture.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = int(video_capture.get(cv2.CAP_PROP_FPS))
    video_capture.release()

    return total_frames_video, fps


def count_video_frames(video_ifp):
    total_frames_video_estimated, fps= get_video_meta_data(video_ifp)

    cap = cv2.VideoCapture(video_ifp)
    total_frames = 0
    while (cap.isOpened()):
        read_flag, frame = cap.read()
        if read_flag:
            total_frames += 1
            if total_frames % 1000 == 0:
                my_str = str(total_frames) + ' of roughly ' + str(total_frames_video_estimated)
                print('\r' + my_str, end='')
        else:
            print('')  # to handle the end='above'
            break
    cap.release()
    return total_frames


