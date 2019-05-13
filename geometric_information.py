import vtk


def information(poly):
    # get the maximum of z coordinate by the bounds
    bc = poly.GetBounds()
    num_points = poly.GetNumberOfPoints()

    p = [0, 0, 0]
    small_z = 1000
    xof_small_z = 1000
    yof_small_z = 1000
    for point_index in range(num_points):
        poly.GetPoint(point_index, p)
        tmp = p[2]
        if tmp < small_z:
            small_z = tmp
            xof_small_z = p[0]
            yof_small_z = p[1]

    # in order to put center of mass as
    # origin we want to deduct the first one from the rest of the points
    com = vtk.vtkCenterOfMass()
    com.SetInputData(poly)
    com.SetUseScalarsAsWeights(False)
    com.Update()
    center = com.GetCenter()

    return [bc, center, xof_small_z, yof_small_z, small_z]
