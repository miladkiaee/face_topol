import vtk
import os

# deprecated
def write_ordered_csv(poly, n_curves,
                      value, ids, path, option):

    name = str(n_curves) + ".csv"
    if os.path.exists(name):
        append_write = 'a'
    else:
        append_write = 'w'

    f = open(name, append_write)
    print("curve ", path, " level ", str(value))

    for i in range(0, ids.GetNumberOfIds()):
        a = ids.GetId(i)
        p = [0, 0, 0]
        poly.GetPoint(a, p)

        # we are doing the x y z to y z x move for
        # the geodesic software preferences
        # relative to the initial coordinates of
        # the point in the curve
        # if option == "x":
        #    f.write('%f, %f, %f\n' % (p[1], 0, p[2]))
        #if option == "y":
        #    f.write('%f, %f, %f\n' % (p[0], p[1], p[2]))
        #if option == "z":
        #    f.write('%f, %f, %f\n' % (p[0], p[2], p[1]))
        f.write('%f, %f, %f\n' % (p[0], p[1], p[2]))
    f.close()


def write_ordered(poly, n_curves, path, value):

    print("writing contour curve ..")

    # connect = vtk.vtkPolyDataConnectivityFilter()
    # connect.SetInputData(poly)
    # connect.InitializeSpecifiedRegionList()
    # connect.SetExtractionModeToSpecifiedRegions()
    # connect.SetExtractionModeToLargestRegion()
    # connect.Modified()
    # connect.Update()

    # num_regions = connect.GetNumberOfExtractedRegions()

    # print("curve has num regions: ", num_regions)

    name = str(n_curves) + ".csv"

    # for r in range(num_regions):

    num_p = poly.GetNumberOfPoints()

    if os.path.exists(name):
        append_write = 'a'
    else:
        append_write = 'w'

    f = open(name, append_write)
    print("curve ", path)

    p = [0, 0, 0]
    p_0 = [0, 0, 0]
    p_last = [0, 0, 0]

    poly.GetPoint(0, p_0)
    poly.GetPoint(num_p-1, p_last)

    # this might have a bit of trick to find out
    if p_0[2] < p_last[2]:
        first = 0
        last = num_p
        step = 1
    else:
        first = num_p - 1
        last = -1
        step = -1

    for p_id in range(first, last, step):
        poly.GetPoint(p_id, p)
        f.write('%f, %f, %f\n' % (p[0], p[1], p[2]))

    f.close()

