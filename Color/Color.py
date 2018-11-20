import colorsys


class Color(object):

    RED = 'RED'
    GREEN = 'GREEN'
    BLUE = 'BLUE'

    @staticmethod
    def rgb_to_pseudocolor(rgb_vec):
        return rgb_vec/255.0

    @staticmethod
    def pseudocolor_from_value(val, min_val, max_val):
        # source: http://stackoverflow.com/questions/10901085/range-values-to-pseudocolor

        # convert val in range minval..maxval to the range 0..120 degrees which
        # correspond to the colors red..green in the HSV colorspace

        h = (float(val - min_val) / (max_val - min_val)) * 120
        # convert hsv color (h,1,1) to its rgb equivalent
        # note: the hsv_to_rgb() function expects h to be in the range 0..1 not 0..360
        r, g, b = colorsys.hsv_to_rgb(h / 360, 1., 1.)
        return r, g, b

    @staticmethod
    def color_from_value(val, min_val, max_val):
        """
        Small values are red, big values are green
        """
        r, g, b = Color.pseudocolor_from_value(val, min_val, max_val)
        return int(255*r), int(255*g), int(255*b)

if __name__ == '__main__':

    # Test 1
    # steps = 10
    # print 'val       R      G      B'
    # for val in xrange(0, 100 + steps, steps):
    #     #print '%3d -> (%.3f, %.3f, %.3f)' % ((val,) + Color.pseudocolor(val, 0, 100))
    #     print '%3d -> (%.3f, %.3f, %.3f)' % ((val,) + Color.color(val, 0, 100))

    # Test 2
    color = Color.color_from_value(0.0001, min_val=0, max_val=0.1)
    print(color)

    color = Color.color_from_value(0.09, min_val=0, max_val=0.1)
    print(color)