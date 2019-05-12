import vtk


def information(pdc):
    # get the maximum of z coordinate by the bounds
    bc = pdc.GetBounds()

    # in order to put center of mass as origin we want to deduct the first one from the rest of the points
    com = vtk.vtkCenterOfMass()
    com.SetInputData(pdc)
    com.SetUseScalarsAsWeights(False)
    com.Update()
    center = com.GetCenter()

    return [bc, center]