import re
from Utility.Logging_Extension import logger

class RegexExtension(object):

    # https://docs.python.org/2/library/re.html
    # https://docs.python.org/2/howto/regex.html#match-versus-search

    def __init__(self):
        self.regex_pattern_str = ""
        self.present_strs = []
        self.absent_strs = []
        #self.last_present_str_consuming = True

    def add_present_str(self, present_str, consuming=False):
        """
        ONLY IF THE LAST ADDED present_str was added WITH consuming=True will return a string!
        In the present case there is the option to use consuming regex or not
        In the absent case we have to use non-consuming regex strings

        """
        present_pattern_str = ".*" + present_str
        if consuming:
            self.regex_pattern_str = self.regex_pattern_str + present_pattern_str
        else:
            # (?=...) Matches if ... matches next, but doesn't consume any of the string.
            # This is called a lookahead assertion.
            self.regex_pattern_str = self.regex_pattern_str + "(?=" + present_pattern_str + ")"
        self.present_strs.append(present_str)
        #self.last_present_str_consuming = consuming

    def add_wildcard(self):
        self.regex_pattern_str += ".*"

    def add_absent_str(self, absent_str):
        # (?!...)
        # Matches if ... doesn't match next.
        # DOES NOT consume the string
        # This is a negative lookahead assertion.
        absent_pattern_str = "(?!.*" + absent_str + ")"
        self.regex_pattern_str = self.regex_pattern_str + absent_pattern_str
        self.absent_strs.append(absent_str)

    def compile(self):
        return re.compile(self.regex_pattern_str)

    def compile_and_match_str(self, input_str):
        """
            print('input_str', input_str)
            print('present_strs', self.present_strs)
            print('absent_strs', self.absent_strs)
            print('pattern', self.regex_pattern_str)
        :param input_str:
        :return:
        """

        # if not self.last_present_str_consuming:
        #     assert False

        pattern = re.compile(self.regex_pattern_str)
        result = pattern.match(input_str)
        return result

    def compile_and_match_lst(self, input_list):
        result = []
        for ele in input_list:
            res = self.compile_and_match_str(ele)
            result.append(res)
        return result

    def to_string(self):
        return self.regex_pattern_str

if __name__ == '__main__':

    # https://stackoverflow.com/questions/1240275/how-to-negate-specific-word-in-regex

    # Example 1: True for consuming and non-consuming
    input_str = "asd luleu wawa laala wuwu asd"

    # Example 2: True only for non-consuming
    # "wuwu" is consumed by "wawa" strinig
    input_str = "asd luleu wuwu laala wawa asd"

    # Example 3: True only for consuming
    # "lala" is consumed by "wuwu"
    input_str = "asd luleu wawa lala wuwu asd"

    present_str_1 = "wuwu"
    present_str_2 = "wawa"

    absent_str_1 = "lala"
    absent_str_2 = "luleu"

    regex_extension = RegexExtension()
    # ==================================================================
    # === Order of add_present_str and add_absent_str matters! ===
    # ==================================================================
    # Subsequent expressions may work only on remaining strings!
    regex_extension.add_present_str(present_str_1, consuming=False)
    # the last present string MUST BE CONSUMING, OTHERWISE THE RESULT WILL BE EMPTY
    regex_extension.add_present_str(present_str_2, consuming=False)
    #regex_extension.add_absent_str(absent_str_1)
    #regex_extension.add_absent_str(absent_str_2)
    regex_extension.add_wildcard()
    result = regex_extension.compile_and_match_str(input_str)

    if result is None:
        print ('AND specification: False')
    else:
        print ('AND specification: True')
        print (input_str[result.start():result.end()])
        print(result.start())
        print(result.end())