
import logging as standard_logging
from logging import Logger

# https://docs.python.org/3/library/logging.html
# https://docs.python.org/3/library/logging.html#logging.LogRecord
# https://docs.python.org/3/library/logging.html#logrecord-attributes
# Shows the same process and thread name when using pathos :(
# logging.basicConfig(level=logging.DEBUG, format="%(processName)s:%(threadName)s:%(message)s")

standard_logging.basicConfig(level=standard_logging.INFO)
standard_logger = standard_logging.getLogger()


# # ================================
#
# # http://code.activestate.com/recipes/412603-stack-based-indentation-of-formatted-logging/
# import logging, inspect
# class IndentFormatter(logging.Formatter):
#     def __init__( self, fmt=None, datefmt=None ):
#         logging.Formatter.__init__(self, fmt, datefmt)
#         self.baseline = len(inspect.stack())
#     def format( self, rec ):
#         stack = inspect.stack()
#         rec.indent = ' '*(len(stack)-self.baseline)
#         rec.function = stack[8][3]
#         out = logging.Formatter.format(self, rec)
#         del rec.indent; del rec.function
#         return out
#
# # USAGE:
# #formatter = IndentFormatter("[%(levelname)s]%(indent)s%(function)s:%(message)s")
# formatter = IndentFormatter("%(levelname)s%(indent)s%(function)s:%(message)s")
#
# #logger = logging.getLogger('logger')
# handler = logging.StreamHandler()
# handler.setFormatter(formatter)
# standard_logger.addHandler(handler)
#
# # ================================

class CustomLogger(object):

    def info(self, param):
        standard_logger.info(param)

    def debug(self, param):
        standard_logger.debug(param)

    def warning(self, param):
        standard_logger.warning(param)

    # Add a method to the logger object (not to the class definition) during runtime x
    def vinfo(self, some_str, some_var):
        assert type(some_str) is str

        """
        Prints a variable info
        :return:
        """
        if some_var is None:
            some_var = 'None'
        standard_logger.info(some_str + ': ' + str(some_var))

    def pinfo(self, current, total):
        # Progress info
        standard_logger.info(str(current) + ' of ' + str(total))

    def log_error(self, message):
        standard_logger.info('###################################################################')
        standard_logger.info(message)
        standard_logger.info('###################################################################')

    def log_warning(self, message):
        standard_logger.info('*******************************************************************')
        standard_logger.info(message)
        standard_logger.info('*******************************************************************')

    def log_salient_message(self, message):
        standard_logger.info('')
        standard_logger.info('===================================================================')
        standard_logger.info(message, )
        standard_logger.info('===================================================================')
        standard_logger.info('')

    def ils(self, indent_level=1):
        """
        ils = indent level space
        useful for structuring output messages
        :param indent_level:
        :return: an empty space corresponding to the provided indent_level
        """
        return "".ljust(indent_level * 4)

logger = CustomLogger()

# logger.vinfo = vinfo
# logger.log_error_message = log_error
# logger.log_warning_message = log_warning
# logger.log_salient_message = log_salient_message
