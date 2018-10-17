import os

class ORB_SLAM2_File_Handler:

    @staticmethod
    def create_rgb_text_file(path_to_rgb_folder, path_to_rgb_txt, fps=12.5):

        time_between_frames = 1 / float(12.5)
        current_time = 0

        img_paths = [img_path for img_path in sorted(os.listdir(path_to_rgb_folder))]
        print(img_paths)

        with open(path_to_rgb_txt, 'w') as f:
            f.write("# color images\n")
            f.write("# file: 'rgbd_dataset_freiburg1_xyz.bag\n")
            f.write("# color images\n")
            for img_path in img_paths:
                f.write(str("{:0.6f}".format(current_time)).zfill(16) + ' ' + os.path.join('rgb', img_path) + '\n')
                current_time += time_between_frames
