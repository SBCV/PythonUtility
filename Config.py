
# from configparser import ConfigParser           # Python 2 and 3 (after ``pip install configparser``):

try:
    import configparser                     # Python 3 import
except ImportError:
    import ConfigParser as configparser     # Python 2 import

import os
import json
from Utility.Logging_Extension import logger


class Config(object):

    default_section = 'DEFAULT'
    comment_symbol = '#'

    # https://docs.python.org/2/library/configparser.html
    #   Can also save "references"
    # config.set('Section1', 'baz', 'fun')
    # config.set('Section1', 'bar', 'Python')
    # config.set('Section1', 'foo', '%(bar)s is %(baz)s!')

    def __init__(self, path_to_config_file, working_file_suffix=None):

        self.path_to_config_file = path_to_config_file
        self.config = configparser.RawConfigParser()

        if not os.path.isfile(self.path_to_config_file):
            abs_path = os.path.abspath(os.path.dirname(self.path_to_config_file))
            if not os.path.isdir(abs_path):
                logger.vinfo('abs_path', abs_path)
                assert False    # config folder missing
            open(self.path_to_config_file, 'a').close()
        else:
            self.config.read(self.path_to_config_file)

        if working_file_suffix is not None:
            self.path_to_working_copy = self.path_to_config_file + working_file_suffix
        else:
            self.path_to_working_copy = self.path_to_config_file


    def add_option_value_pairs(self, pair_list, section=None):
        """

        :param tuple_list: ('option', 'Value')
        :return:
        """
        if section is None:
            section = Config.default_section
        elif not self.config.has_section(section):
            self.config.add_section(section)

        for pair in pair_list:
            option, value = pair
            self.config.set(section, option, value)

    def detect_missing_commas(self, list_str):

        repaired_string = list_str.replace('"\n"', '",\n"')
        return repaired_string

    def remove_appended_commas(self, list_str):
        repaired_string = list_str.replace('",\n]', '"\n]')
        return repaired_string


    def get_option_value(self, option, target_type, section=None):
        """
        :param section:
        :param option:
        :param target_type:
        :return:
        """
        if section is None:
            section = Config.default_section

        try:
            if target_type == list:
                option_str = self.config.get(section, option)
                option_str = self.detect_missing_commas(option_str)
                option_str = self.remove_appended_commas(option_str)
                result = json.loads(option_str)
            else:
                option_str = self.config.get(section, option)
                option_str = option_str.split('#')[0].rstrip()
                if target_type == bool:  # Allow True/False bool values in addition to 1/0
                    result = option_str == 'True' or option_str == 'T' or option_str == '1'
                else:
                    result = target_type(option_str)

        except configparser.NoOptionError as NoOptErr:
            logger.info('ERROR: ' + str(NoOptErr))
            logger.info('CONFIG FILE: ' + self.path_to_config_file)
            assert False    # Option Missing
        except:
            logger.info('option_str: ' + str(option_str))
            raise

        return result

    def get_option_value_or_default_value(self, option, target_type, default_value, section=None):
        #logger.debug('option: ' + str(option))
        #logger.debug('target_type: ' + str(target_type))
        if section is None:
            section = Config.default_section

        if self.config.has_option(section, option):
            result = self.get_option_value(option, target_type, section=section)
        else:
            result = default_value
            #logger.info('result: ' + str(result))
            assert type(result) == target_type

        return result

    def get_option_value_or_None(self, option, target_type, section=None):
        if section is None:
            section = Config.default_section
        result = None
        if self.config.has_option(section, option):
            result = self.get_option_value(option, target_type, section=section)
        return result

    def log_option_value_pairs(self):
        for val in self.config.values():
            logger.info(val)

    def write_state_to_disc(self):
        with open(self.path_to_working_copy, 'w') as configfile:
            self.config.write(configfile)

if __name__ == '__main__':

    logger.info('Main called')

    config = Config(path_to_config_file='example.cfg')
    section_option_value_pairs = [('option1', '125'),
                                  ('option2', 'aaa'),
                                  ('option1', '222'),
                                  ('option3', '213')]
    config.add_option_value_pairs(section_option_value_pairs, section='Section1')

    option_value_pairs = [('option5', '333'),
                          ('option6', '555')]
    config.add_option_value_pairs(option_value_pairs)

    config.log_option_value_pairs()
    config.write_state_to_disc()

    some_number = config.get_option_value('option1', int, section='Section1')
    logger.info(some_number)
    logger.info(some_number + 3)

    some_number = config.get_option_value('option5', int)
    logger.info(some_number)
    logger.info(some_number + 3)
