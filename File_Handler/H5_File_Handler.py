__author__ = 'bullin'

import h5py
import matplotlib

class H5FileHandler(object):


    # ==========================
    # For H5 Visualization Tools see HDF5_Scripts / HDF5_Image_Tool.py
    # ==========================

    @staticmethod
    def read_h5(file_path_and_name, dataset_name=None):

        # if not os.path.isfile(file_path_and_name):
        #     logger.vinfo('file_path_and_name', file_path_and_name)
        #     assert False
        h5_file_object = h5py.File(file_path_and_name, "r")

        if dataset_name is None:  # Assume there is only one dataset
            dataset_names = list(h5_file_object.keys())
            assert len(dataset_names) == 1
            dataset_name = dataset_names[0]

        segmentation_as_h5_dataset = h5_file_object[dataset_name]
        segmentation_as_matrix = segmentation_as_h5_dataset[()]
        h5_file_object.close()
        return segmentation_as_matrix


    @staticmethod
    def write_h5(file_path_and_name, some_matrix, dtype, dataset_name='dataset'):

        """
        :param file_path_and_name:
        :param some_matrix:
        :param dtype:
                e.g.
                    dtype="i"  ==  dtype="int32"    or   dtype="int64"    (used for all segmentations)
                    dtype="f"  ==  dtype="float32"  or   dtype="float64"   (used for disparities)
                Creating an array without a dtype results in dtype="float64"
        :param dataset_name:
        :return:
        """

        shape = some_matrix.shape
        # print "shape (matrix): " + str(shape)
        h5_segmentation_file = h5py.File(file_path_and_name, "w")

        data_set = h5_segmentation_file.create_dataset(
            dataset_name, shape, dtype=dtype, compression="gzip")
        # print "shape (data_set): " + str(data_set.shape)
        # print "dtype (data_set): " + str(type(data_set))
        #write to dataset
        data_set[...] = some_matrix
        h5_segmentation_file.close()

    @staticmethod
    def save_h5_matrix_to_image(some_matrix, path_to_image, amount_categories=-1, cmap='jet'):

        if amount_categories == -1:
            matplotlib.image.imsave(path_to_image, some_matrix)
        else:
            matplotlib.image.imsave(path_to_image, some_matrix, vmin=0, vmax=amount_categories, cmap=cmap)

    @staticmethod
    def keep_single_class_in_h5_file(path_to_original_h5_file, class_index, path_to_extracted_h5_file):

        h5_file = H5FileHandler.read_h5(path_to_original_h5_file)
        h5_file[h5_file != class_index] = 0        # set all other values to 0

        H5FileHandler.write_h5(path_to_extracted_h5_file, h5_file)


if __name__ == '__main__':
    path_to_hdf5_file = '.h5'
    path_to_image_file = path_to_hdf5_file + '.jpg'
    segmentation_as_matrix = H5FileHandler.read_h5(path_to_hdf5_file)
    H5FileHandler.save_h5_matrix_to_image(segmentation_as_matrix, path_to_image_file)