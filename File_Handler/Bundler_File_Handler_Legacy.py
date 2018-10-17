
import os
import os.path
from PIL import Image
import numpy as np

from Utility.Types.Point import Point
from Utility.Types.Camera import Camera

class BundleFileHandlerLegacy:

    # uses a state
    def parse_bundler_file(self, path_to_bundler_file):
        f = open(path_to_bundler_file, "r")
        self.lines = list(map(lambda x: x.strip(), f.readlines()))
        self.row = 0

        # Read file content:
        cameraCount, pointCount = map(int, self._readItems())
        cameras = self._readCameras(cameraCount)
        points = self._readPoints(pointCount)
        print("Found %d valid cameras and %d points." % (len(cameras), len(points)))
        return cameras, points

    def _readLine(self):
        while self.row < len(self.lines):
            self.line = self.lines[self.row]
            self.row += 1
            # Skip empty lines and comments:
            if len(self.line) > 0 and not self.line.startswith("#"):
                return self.line
        return None # Reached end

    def _readItems(self):
        return self._readLine().split(" ")

    def _readIntItems(self):
        return tuple(map(int, self._readLine().split(" ")))

    def _readFloatItems(self):
        return tuple(map(float, self._readLine().split(" ")))

    def _readCameras(self, cameraCount):
        cameras = []
        for index in range(cameraCount):

            focal_length, k1, k2 = self._readFloatItems()
            rotation = np.array([self._readFloatItems(),
                        self._readFloatItems(),
                        self._readFloatItems()])
            translation = np.array(self._readFloatItems())

            if focal_length > 0.0:
                camera = Camera()
                camera.set_rotation_mat(rotation)
                camera._translation_vec = translation
                camera.calibration_mat = np.array([[focal_length, 0, 0],
                                                   [0, focal_length, 0],
                                                   [0, 0, 1]])

                cameras.append(camera) # Only add valid cameras
        return cameras

    def _readPoints(self, pointCount):
        points = []
        for index in range(pointCount):
            # Add points:
            position = np.array(self._readFloatItems())
            color = np.array(self._readIntItems())
            points.append(Point(coord=position, color=color))
            self._readLine()  # Skip mapped image features
        return points

    # def parse_image_list_file(self, filepath, cameras):
    #     # Load image paths:
    #     f = open(filepath, "r")
    #     paths = list(map(
    #         lambda x: os.path.basename(x.split()[0]), f.readlines()))
    #     f.close()
    #
    #     # Map to cameras:
    #     for index in range(len(cameras)):
    #         cameras[index].file_name = paths[index]
    #     return cameras


    def parse_camera_image_files(self, cameras, camera_file_name, path_to_images):
        input_file = open(camera_file_name, 'r')
        for image_file_name, camera in zip(input_file, cameras):
            camera.file_name = image_file_name.rstrip()
            # this does NOT load the data into memory -> should be fast!
            image = Image.open(os.path.join(path_to_images, camera.file_name))
            camera.width, camera.height = image.size
        return cameras