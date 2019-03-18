import vtk
import numpy as np
from argparse import ArgumentParser

parser = ArgumentParser()

parser.add_argument("-i", "--input", default= "CF001.ply", help="input file name")
parser.add_argument("-o", "--output", default="tmpOutput.ply", help="output file name")
parser.add_argument("-c", "--curveFile", default="curv.ply", help="curvature file name")
parser.add_argument("-f", "--curveFileFull", default="curvfull.ply", help="curvature full scale file name")

args = parser.parse_args()

reader = vtk.vtkPLYReader()
reader.SetFileName(args.input)
reader.Update()

pd = reader.GetOutput()

####
pointsMapper = vtk.vtkPolyDataMapper()
pointsMapper.SetInputConnection(reader.GetOutputPort());

pointsActor = vtk.vtkActor()
pointsActor.SetMapper(pointsMapper);
pointsActor.GetProperty().SetInterpolationToFlat();
####

obbTree = vtk.vtkOBBTree()
obbTree.SetDataSet(pd)
obbTree.Update()

polydata = vtk.vtkPolyData()

obbTree.GenerateRepresentation(0, polydata);
obbTree.Update()

################################################################################
pts = polydata.GetPoints()



xprime = np.array(pts.GetPoint(1)) - np.array(pts.GetPoint(0))
yprime = np.array(pts.GetPoint(2)) - np.array(pts.GetPoint(0))
zprime = np.array(pts.GetPoint(4)) - np.array(pts.GetPoint(0))
oprime = np.array(pts.GetPoint(0))

x = np.array([1, 0, 0])
thetaX = np.arccos(np.dot(x, xprime) / (np.linalg.norm(x) * np.linalg.norm(xprime)))

y = np.array([0, 1, 0])
thetaY = np.arccos(np.dot(y, yprime) / (np.linalg.norm(y) * np.linalg.norm(yprime)))

z = np.array([0, 0, 1])
thetaZ = np.arccos(np.dot(z, zprime) / (np.linalg.norm(z) * np.linalg.norm(zprime)))


################################################################################
trans = vtk.vtkTransform()

trans.Translate(-1*oprime[0], -1*oprime[1], -1*oprime[2])

trans.RotateX(thetaX)
trans.RotateY(thetaY)

transF = vtk.vtkTransformPolyDataFilter()
transF.SetInputData(pd)
transF.SetTransform(trans)
transF.Update()
################################################################################

writer = vtk.vtkPolyWriter()
writer.SetFileName(args.input)
writer.SetInputData(transF.GetOutput())
writer.Update()
writer.Write()

