import vtk


def separate(poly, loc):
    bo = vtk.vtkBooleanOperationPolyDataFilter()
    # operation = "union"
    # operation = "intersection"
    # operation = difference
    non_man = vtk.vtkFeatureEdges()
    non_man.SetInputData(poly)
    non_man.BoundaryEdgesOff()
    non_man.FeatureEdgesOff()
    non_man.NonManifoldEdgesOn()
    non_man.Update()

    num_points = non_man.GetOutput().GetNumberOfPoints()
    print("non-manifold has num points: ", num_points)

    bo.SetOperationToDifference()
    bo.SetInputData(0, poly)
    bo.SetInputData(1, non_man.GetOutput())

    bo.Update()

    # writing the contours output
    # writer = vtk.vtkPolyDataWriter()
    # writer.SetFileName(loc + "separated.ply")
    # writer.SetInputData(poly)
    # writer.Update()
    # writer.Write()

    return poly

