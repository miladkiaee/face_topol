import vtk

filepath = "/home/milad/face_topol/polys/aligned/CC002Aligned.ply"

reader = vtk.vtkPLYReader()
reader.SetFileName(filepath)
reader.Update()

smoother = vtk.vtkSmoothPolyDataFilter()
smoother.SetInputData(reader.GetOutput())
smoother.SetFeatureEdgeSmoothing(True)
smoother.SetFeatureAngle(180)
smoother.SetRelaxationFactor(0.1)
smoother.SetEdgeAngle(180)
smoother.SetBoundarySmoothing(True)
smoother.SetNumberOfIterations(400)
smoother.Update()

writer = vtk.vtkPLYWriter()
writer.SetInputData(smoother.GetOutput())
writer.SetFileName(filepath + "smooth.ply")
writer.Write()

