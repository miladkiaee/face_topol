import vtk


def reduce_it(poly, loc):
    deci = vtk.vtkDecimatePro()

    deci.SetInputData(poly)
    deci.PreserveTopologyOff()
    deci.BoundaryVertexDeletionOn()

    deci.PreSplitMeshOn()
    deci.SplittingOn()
    deci.SetMaximumError(vtk.VTK_DOUBLE_MAX)

    deci.SetSplitAngle(30)
    deci.SetFeatureAngle(30)

    # deci.SetDegree(6)
    deci.SetTargetReduction(0.01)
    deci.Update()

    # writing the contours output
    writer = vtk.vtkPolyDataWriter()
    writer.SetFileName(loc + "decimated.ply")
    writer.SetInputData(deci.GetOutput())
    writer.Update()
    writer.Write()

    return deci.GetOutput()
