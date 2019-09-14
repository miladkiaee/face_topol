import vtk


from argparse import ArgumentParser

from reduceTriangles import reduce_it

print('----------')
parser = ArgumentParser()
parser.add_argument("-i", "--input", default="", help="input polydata file name")
parser.add_argument("-o", "--output", default="", help="output path for writing")

args = parser.parse_args()

reader = vtk.vtkPLYReader()
reader.SetFileName(args.input)
reader.Update()
pd = reader.GetOutput()

# triangulate in case
trif = vtk.vtkTriangleFilter()
trif.SetInputData(pd)
trif.Update()

pd = trif.GetOutput()

# removing the non manifold cells
# pd = separate(pd, args.input)

# reduce the poly data
pd = reduce_it(pd, args.input)

feature_angle = 60
edge_angle = 60
relax = 0.4
num_iter = 200
file_path = args.output

print("smoothing test ..")
smoother = vtk.vtkSmoothPolyDataFilter()
smoother.SetInputData(pd)
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
