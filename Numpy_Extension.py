import numpy as np
from sortedcontainers import SortedList
from scipy.ndimage.filters import gaussian_filter, uniform_filter, uniform_filter1d, maximum_filter, percentile_filter

# https://stackoverflow.com/questions/22669252/how-exactly-does-the-reflect-mode-for-scipys-ndimage-filters-work
#    mode       |   Ext   |         Input          |   Ext
#    -----------+---------+------------------------+---------
#    'mirror'   | 4  3  2 | 1  2  3  4  5  6  7  8 | 7  6  5
#    'reflect'  | 3  2  1 | 1  2  3  4  5  6  7  8 | 8  7  6
#    'nearest'  | 1  1  1 | 1  2  3  4  5  6  7  8 | 8  8  8
#    'constant' | 0  0  0 | 1  2  3  4  5  6  7  8 | 0  0  0
#    'wrap'     | 6  7  8 | 1  2  3  4  5  6  7  8 | 1  2  3


def compute_local_average(inpur_arr, window_size, mode="reflect"):

    # https://github.com/scipy/scipy/blob/v1.2.1/scipy/ndimage/filters.py#L1196-L1231
    #   uniform_filter      # local_average
    #       >>> uniform_filter1d([2., 8., 0., 4., 1., 9., 9., 0.], size=2)
    #       array([2. , 5. , 4. , 2. , 2.5, 5. , 9. , 4.5])

    assert window_size % 2 == 1    # window size must be an uneven number
    cval = 0  # centered around the current index
    return uniform_filter1d(inpur_arr, size=window_size, cval=cval, mode=mode)


def compute_local_quantile(inpur_arr, q_or_list, window_size):

    # https://github.com/scipy/scipy/blob/v1.2.1/scipy/ndimage/filters.py#L1196-L1231
    #   percentile_filter

    assert window_size % 2 == 1

    if not isinstance(q_or_list, list):
        q_or_list = [q_or_list]

    res_list = []
    for q in q_or_list:
        assert 0.0 <= q <= 1.0
        percentile = q * 100.0
        res = percentile_filter(inpur_arr, percentile=percentile, size=window_size)
        assert len(res) == len(inpur_arr)
        res_list.append(res)

    return res_list




