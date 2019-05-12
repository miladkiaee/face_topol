import vtk


def smooth(poly, feature_angle, edge_angle,
           relax, num_iter, file_path):

    print("smoothing ..")
    smoother = vtk.vtkSmoothPolyDataFilter()
    smoother.SetInputData(poly)
    smoother.SetFeatureEdgeSmoothing(True)
    smoother.SetFeatureAngle(feature_angle)
    smoother.SetRelaxationFactor(relax)
    smoother.SetEdgeAngle(edge_angle)
    smoother.SetBoundarySmoothing(True)
    smoother.SetNumberOfIterations(num_iter)
    smoother.Update()

    print("writing down smooth surface ..")
    writer = vtk.vtkPLYWriter()
    writer.SetInputData(smoother.GetOutput())
    writer.SetFileName(file_path + "smooth.ply")
    writer.Write()

    return smoother.GetOutput()

