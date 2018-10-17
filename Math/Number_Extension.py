import math


def approx_equal_vec(vec_1, vec_2, epsilon=0.000001):
    is_approx_equal = True
    for num_1, num_2 in zip(vec_1, vec_2):
        if is_approx_equal:
            is_approx_equal = approx_equal_scalar(num_1, num_2, epsilon)

    return is_approx_equal


def approx_equal_scalar(num_1, num_2, epsilon=0.000001):
    return math.fabs(num_1 - num_2) < epsilon


