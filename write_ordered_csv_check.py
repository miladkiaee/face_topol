import vtk
import os


def write_ordered_csv_check(poly, n_curves,
                      value, ids, path, option):

    name = str(n_curves) + "check" + ".csv"
    if os.path.exists(name):
        append_write = 'a'
    else:
        append_write = 'w'

    f = open(name, append_write)

    for i in range(0, ids.GetNumberOfIds()):
        a = ids.GetId(i)
        p = [0, 0, 0]
        poly.GetPoint(a, p)

        # we are doing the x y z to y z x move for
        # the geodesic software preferences
        # relative to the initial coordinates of
        # the point in the curve
        if option == "x":
            f.write('%f, %f, %f, %f\n' % (p[1], 0, p[2], i))
        if option == "y":
            f.write('%f, %f, %f, %f\n' % (p[0], p[1], p[2], i))
        if option == "z":
            f.write('%f, %f, %f, %f\n' % (p[0], p[2], p[1], i))
    f.close()


def write_ordered_check(poly, n_curves, path, value):

    num_p = poly.GetNumberOfPoints()

    name = str(n_curves) + "check.csv"
    if os.path.exists(name):
        append_write = 'a'
    else:
        append_write = 'w'

    f = open(name, append_write)
    # print("curve ", path, " level ", str(value))

    p = [0, 0, 0]
    p_0 = [0, 0, 0]
    p_last = [0, 0, 0]

    poly.GetPoint(0, p_0)
    poly.GetPoint(num_p-1, p_last)

    if p_0[2] < p_last[2]:
        first = 0
        last = num_p
        step = 1
    else:
        first = num_p
        last = 0
        step = -1

    for p_id in range(first, last, step):
        poly.GetPoint(p_id, p)
        f.write('%f, %f, %f, %f\n' % (p[1], 0, p[2], p_id))

    f.close()

