class H5VisualizationTask():

    def __init__(self, path_to_input_image,
                 path_to_h5_file,
                 path_to_output_image,
                 masking_value,
                 background_color,
                 save_results,
                 lazy,
                 show_results):

        self.__dict__.update(locals())
        del self.self  # redundant (and a circular reference)


