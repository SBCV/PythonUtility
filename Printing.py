__author__ = 'sebastian'


def ils(indent_level=1):
    """
    ils = indent level space
    useful for structuring output messages
    :param indent_level:
    :return: an empty space corresponding to the provided indent_level
    """
    return "".ljust(indent_level*4)

def print_message(message, il=1):
    if type(message) == list:
        for element in message:
            print(ils(il) + str(element))
    else:
        print(ils(il) + str(message))

def print_section(message):
    print('###################################################################')
    print_message(message)
    print('###################################################################')

def print_salient_message(message, il=1):
    print('')
    print(ils(il) + '===================================================================')
    print_message(message, il)
    print(ils(il) + '===================================================================')
    print('')

def print_warning(message, il=1):
    print(ils(il) + '*******************************************************************')
    print_message(message, il)
    print(ils(il) + '*******************************************************************')

def print_executable_call(executable_arguments):
    exe_str = ''
    for arg in executable_arguments:
        exe_str += arg + ' '
    print('Executable call: ' + exe_str)