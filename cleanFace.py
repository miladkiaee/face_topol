import vtk


def cleaner(poly, toler):

    print("cleaning ..")
    num_points = poly.GetNumberOfPoints()
    print("number of points was: ", num_points)
    clean = vtk.vtkCleanPolyData()
    clean.SetInputData(poly)
    clean.ToleranceIsAbsoluteOn()
    clean.SetAbsoluteTolerance(toler)
    clean.ConvertLinesToPointsOn()
    clean.ConvertPolysToLinesOn()
    clean.ConvertStripsToPolysOn()
    # clean.PointMergingOn()
    clean.PieceInvariantOn()
    clean.Update()
    num_points = clean.GetOutput().GetNumberOfPoints()
    print("number of points is: ", num_points)

    return clean.GetOutput()

