class ListExtension(object):

    @staticmethod
    def split_list_in_n_parts(my_list, number_chunks):
        k, m = len(my_list) / number_chunks, len(my_list) % number_chunks
        return list(my_list[i * k + min(i, m):(i + 1) * k + min(i + 1, m)] for i in xrange(number_chunks))

    @staticmethod
    def convert_list_to_string(my_list, separator=' '):
        return separator.join(list(map(str, my_list)))

if __name__ == '__main__':


    my_list = [(1,2), (3,4), (5,6)]

    res = ListExtension.convert_list_to_string(my_list)
    print(res)