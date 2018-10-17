import numpy as np
from Utility.Classes.Frozen_Class import FrozenClass
from Thesis.VTK.Data_Interface import DataInterface

class Mesh(FrozenClass):

    # This class currently builds heavyily on vtk

    def __init__(self, poly_data):
        # polydata is vtkPolyData
        self.vtk_poly_data = poly_data

    @classmethod
    def init_from_ply(cls, path_to_ply_file):
        poly_data = DataInterface.create_poly_data_from_PLY(
            path_to_ply_file)
        return cls(poly_data)

    def get_vtk_poly_data(self):
        return self.vtk_poly_data

