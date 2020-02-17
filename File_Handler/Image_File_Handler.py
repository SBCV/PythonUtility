
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw
import numpy as np
import os
from Utility.Logging_Extension import logger
from pathos.multiprocessing import ProcessingPool
from pathos.helpers import cpu_count

class ImageFileHandler:

    @staticmethod
    def read_image_as_np_array(file_path_and_name):
        return np.asarray(Image.open(file_path_and_name).convert('L'))

    @staticmethod
    def overlay_images(path_image_1, path_image_2, blend_factor=0.5):

        image_1 = Image.open(path_image_1)
        image_1 = image_1.convert("RGBA")

        image_2 = Image.open(path_image_2)
        image_2 = image_2.convert("RGBA")

        overlay = Image.blend(image_1, image_2, blend_factor)

        return overlay

    @staticmethod
    def create_gif(idp, ofp, duration=100, loop=0):

        # Other tools like https://www.screentogif.com/ achieve better compression results

        img_list = []
        for fn in os.listdir(idp):
            ifp = os.path.join(idp, fn)
            img = Image.open(ifp)
            img_list.append(img)

        start_img = img_list[0]
        start_img.save(
            ofp,
            save_all=True,
            append_images=img_list[1:],
            duration=duration,
            loop=loop)

    @staticmethod
    def write_image_name_on_image(input_image_path,
                                  output_image_path,
                                  override=False,
                                  xy=(0, 0),
                                  text_color=(255, 255, 255),
                                  font_size=40,
                                  background_color=(0, 0, 0)):

        """
        :param input_image_path:
        :param output_image_path:
        :param override:
        :param xy:
        :param text_color:
        :param background_color: Can also be None to indicate a transparent background color
        :return:
        """


        img = Image.open(input_image_path)
        draw = ImageDraw.Draw(img)

        text = os.path.basename(input_image_path)

        # there are two types of fonts: bitmap and truetypes
        #   font = ImageFont.load("arial.pil")
        #       this returns the default font, which it is a bitmap, the size can't be changed
        #       the default font is a bitmap font (size can't be changed)
        #   font = ImageFont.truetype("arial.ttf", 15)

        #fnt = ImageFont.truetype("arial.ttf", size=font_size)

        #font_type = 'Pillow/Tests/fonts/FreeMono.ttf'
        #font_type = 'Pillow/Tests/fonts/FreeSerif.ttf'
        font_type = 'Pillow/Tests/fonts/FreeSans.ttf'       # probably the best for low resolutions

        fnt = ImageFont.truetype(font_type, font_size)

        text_size_in_pixel = draw.textsize(text, fnt)
        some_tup = [xy, (xy[0] + text_size_in_pixel[0], xy[1] + text_size_in_pixel[1])]
        if background_color is not None:
            draw.rectangle(some_tup, fill=background_color)
        draw.text(xy=xy, text=text, fill=text_color, font=fnt)

        if override and output_image_path is None:
            img.save(input_image_path)
        else:
            img.save(output_image_path)

    @staticmethod
    def write_image_name_on_images_in_dir(input_folder_path,
                                          output_folder_path,
                                          override=False,
                                          xy=(0, 0),
                                          text_color=(255, 255, 255),
                                          font_size=40,
                                          background_color=(0, 0, 0),
                                          parallel=True,
                                          number_gpus=6):

        """
        :param input_folder_path:
        :param output_folder_path:
        :param override:
        :param xy:
        :param text_color:
        :param background_color:  Can also be None to indicate a transparent background color
        :return:
        """

        img_files = os.listdir(input_folder_path)

        if parallel:
            ImageFileHandler.write_image_name_on_images_in_dir_parallel(
                img_files,
                input_folder_path,
                output_folder_path,
                override=override,
                xy=xy,
                text_color=text_color,
                font_size=font_size,
                background_color=background_color,
                number_gpus=number_gpus)
        else:
            ImageFileHandler.write_image_name_on_images_in_dir_sequential(
                img_files,
                input_folder_path,
                output_folder_path,
                override=override,
                xy=xy,
                text_color=text_color,
                font_size=font_size,
                background_color=background_color)



    @staticmethod
    def write_image_name_on_images_in_dir_sequential(img_files,
                                                     input_folder_path,
                                                     output_folder_path,
                                                     override=False,
                                                     xy=(0, 0),
                                                     text_color=(255, 255, 255),
                                                     font_size=40,
                                                     background_color=(0, 0, 0)):
        logger.info('write_image_name_on_images_in_dir_sequential: ...')
        num_files = len(img_files)

        for index, img_file in enumerate(img_files):

            if not index % 5:
                logger.info(str(index) + ' of ' + str(num_files))

            input_image_path = os.path.join(input_folder_path, img_file)

            if override and output_folder_path is None:
                output_image_path = None
            else:
                output_image_path = os.path.join(output_folder_path, img_file)

            ImageFileHandler.write_image_name_on_image(
                input_image_path,
                output_image_path,
                override=override,
                xy=xy,
                text_color=text_color,
                font_size=font_size,
                background_color=background_color)
        logger.info('write_image_name_on_images_in_dir_sequential: Done')

    @staticmethod
    def write_image_name_on_images_in_dir_parallel(img_files,
                                                   input_folder_path,
                                                   output_folder_path,
                                                   override=False,
                                                   xy=(0, 0),
                                                   text_color=(255, 255, 255),
                                                   font_size=40,
                                                   background_color=(0, 0, 0),
                                                   number_gpus=6):
        logger.info('write_image_name_on_images_in_dir_parallel: ...')
        logger.info('Using ' + str(number_gpus) + ' of ' + str(cpu_count()) + 'CPUs')

        from Utility.List_Extension import ListExtension
        chunks = ListExtension.split_list_in_n_parts(img_files, number_gpus)

        with ProcessingPool() as pool:

            results = []
            for gpu_id in range(number_gpus):
                result = pool.apipe(
                    ImageFileHandler.write_image_name_on_images_in_dir_sequential,
                    *[chunks[gpu_id], input_folder_path, output_folder_path, override, xy, text_color, font_size, background_color]
                )
                results.append(result)

            # Collect the asynchronous calls
            for result in results:
                result.get()
        logger.info('write_image_name_on_images_in_dir_parallel: Done')

