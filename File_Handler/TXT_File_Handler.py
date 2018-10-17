class TXTFileHandler():

    @staticmethod
    def read_lines(ifp):
        ifc = open(ifp, "r")
        #lines = list(map(lambda x: x.strip(), ifc.readlines()))
        lines = [line.strip() for line in ifc.readlines() if len(line.strip()) > 0]
        return lines

    @staticmethod
    def write_list(ofp, list_content, add_line_breaks=False, write_mode='wb'):
        if add_line_breaks:
            suffix = '\n'
        else:
            suffix = ''
        with open(ofp, write_mode) as output_file:
            output_file.writelines([item.encode() + suffix for item in list_content])

    @staticmethod
    def write_dict(ofp, dict_content, write_mode='wb'):
        with open(ofp, write_mode) as output_file:
            output_file.writelines([key.encode() + ': ' + item.encode() for key, item in dict_content.items()])