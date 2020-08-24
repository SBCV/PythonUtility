class TXTFileHandler(object):

    @staticmethod
    def read_lines(ifp):
        ifc = open(ifp, "r")
        #lines = list(map(lambda x: x.strip(), ifc.readlines()))
        lines = [line.strip() for line in ifc.readlines() if len(line.strip()) > 0]
        return lines

    @staticmethod
    def read_lines_as_type(ifp, as_type):
        ifc = open(ifp, "r")
        lines = []
        for line in ifc.readlines():
            res = as_type(line.strip())
            lines.append(as_type(res))
        return lines

    @staticmethod
    def read_lines_as_tuples(ifp, delimiter=' ', as_type=None):
        " Returns a list of tuples"
        lines = TXTFileHandler.read_lines(ifp)
        lines_as_tup = []
        for line in lines:
            elements = line.split(delimiter)
            if as_type is not None:
                elements = [as_type(element) for element in elements]
            lines_as_tup.append(elements)
        return lines_as_tup

    @staticmethod
    def write_list(ofp, list_content, add_line_breaks=False, write_mode='wb'):
        if add_line_breaks:
            suffix = b'\n'
        else:
            suffix = b''
        with open(ofp, write_mode) as output_file:
            output_file.writelines([item.encode() + suffix for item in list_content])

    @staticmethod
    def write_dict(ofp, dict_content, write_mode='wb'):
        with open(ofp, write_mode) as output_file:
            output_file.writelines([key.encode() + ': ' + item.encode() for key, item in dict_content.items()])

    @staticmethod
    def write_str(ofp, str_content, write_mode='wb'):
        with open(ofp, write_mode) as output_file:
            output_file.write(str_content.encode())
