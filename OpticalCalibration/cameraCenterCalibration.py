import numpy

def calculateCenterOfArc(a, b, c):
    """For a triplet of points on an arc, find the midpoint of the circle
    See also https://math.stackexchange.com/a/1114321

    >>> calculateCenterOfArc((1,1), (2,2), (3,1))
    array([[ 2.],
           [ 1.]])
    >>> calculateCenterOfArc((-1,0), (0,1), (1,0))
    array([[ 0.],
           [ 0.]])
    >>> calculateCenterOfArc((-3,-3), (-2,-4), (-3,-5))
    array([[-3.],
           [-4.]])
    >>> calculateCenterOfArc((-3.5,-3), (-2.5,-4), (-3.5,-5))
    array([[-3.5],
           [-4. ]])
    """
    l = numpy.array([[a[0] - b[0], a[1] - b[1]],
                     [b[0] - c[0], b[1] - c[1]]])
    r = numpy.array(
        [[pow(a[0], 2) - pow(b[0], 2) + pow(a[1], 2) - pow(b[1], 2)],
         [pow(b[0], 2) - pow(c[0], 2) + pow(b[1], 2) - pow(c[1], 2)]])
    r = numpy.multiply(r, 0.5)
    l = numpy.linalg.inv(l)
    out = numpy.dot(l, r)
    return out

if __name__ == "__main__":
    import doctest
    doctest.testmod()
