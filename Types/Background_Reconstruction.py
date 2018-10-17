from Utility.Types.Reconstruction import Reconstruction

class Background_Reconstruction(Reconstruction):

    def __init__(self, cams, points, image_folder_path, sparse_reconstruction_type):
        super(Background_Reconstruction, self).__init__(
            cams,
            points,
            image_folder_path,
            sparse_reconstruction_type)

        self.ground_mesh = None

    def add_ground_mesh(self, mesh):
        self.ground_mesh = mesh

    def get_ground_mesh(self):
        return self.ground_mesh