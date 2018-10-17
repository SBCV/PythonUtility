import struct


class BinaryFileHandler:

    # https://docs.python.org/3/library/struct.html#byte-order-size-and-alignment
    # https://docs.python.org/3/library/struct.html#format-characters
    # Q 	unsigned long long
    # d 	double 	float 	8

    @staticmethod
    def read_next_bytes_as_char(binary_file, num_bytes, format_char, endian_character='<'):
        """

        :param binary_file:
        :param num_bytes:
        :param format_char: {c}
        :param endian_character: {@, =, <, >, !}
        :return:
        """
        binary_data = binary_file.read(num_bytes)
        if binary_data == '':
            return None
        else:
            return struct.unpack(endian_character + format_char, binary_data)[0]

    @staticmethod
    def read_next_bytes_as_int(binary_file, num_bytes, format_char, endian_character='<'):

        """
        :param binary_file:
        :param num_bytes: {2,4,8}
        :param format_char: {h,H,i,I,l,L,q,Q}
        :param endian_character: {@, =, <, >, !}
        :return:
        """
        #assert format_char in ['h','H','i','I','l','L','q','Q']
        #assert endian_character in ['@', '=', '<', '>', '!']
        binary_data = binary_file.read(num_bytes)
        if binary_data == '':
            return None
        else:
            return struct.unpack(endian_character + format_char, binary_data)[0]

    @staticmethod
    def read_next_bytes_as_float(binary_file, num_bytes, format_char, endian_character='<'):

        """
        :param binary_file:
        :param num_bytes: {2,4,8}
        :param format_char: {e,f,d}
        :param endian_character: {@, =, <, >, !}
        :return:
        """

        #assert format_char in ['e','f','d']
        #assert endian_character in ['@', '=', '<', '>', '!']

        binary_data = binary_file.read(num_bytes)
        if binary_data == '':
            return None
        else:
            return struct.unpack(endian_character + format_char, binary_data)[0]

    @staticmethod
    def read_next_bytes(binary_file, num_bytes, format_char_sequence, endian_character ='<'):

        binary_data = binary_file.read(num_bytes)
        res = struct.unpack(endian_character + format_char_sequence, binary_data)
        return res
