# this code tries to align the coordinate system to one define by some principal analysis

# Kitware's visualization toolkit
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

# save the reader output to a polydata object
pd = reader.GetOutput()

# oriented tree data structure uses the eigenvelues and eigenvectors to find the fittest box for the geometry
obbTree = vtk.vtkOBBTree()
obbTree.SetDataSet(pd)
obbTree.Update()

# a polydata object to store the oriented structure
polydata = vtk.vtkPolyData()
obbTree.GenerateRepresentation(0, polydata)
obbTree.Update()

# these are the corners of the oriented box
pts = polydata.GetPoints()

# and vectors of local coordinate system in terms of the original one

xprime = np.array(pts.GetPoint(1)) - np.array(pts.GetPoint(0))
xprime = xprime/np.linalg.norm(xprime)
print("xprime: ", xprime)

yprime = np.array(pts.GetPoint(2)) - np.array(pts.GetPoint(0))
yprime = yprime/np.linalg.norm(yprime)
print("yprime: ", yprime)

zprime = np.array(pts.GetPoint(4)) - np.array(pts.GetPoint(0))
zprime = zprime/np.linalg.norm(zprime)
print("zprime: ", zprime)

# corner coordinates
oprime = np.array(pts.GetPoint(0))
print("oprime: ", oprime)

# we need to find some origin for the geometry
com = vtk.vtkCenterOfMass()
com.SetInputData(pd)
com.SetUseScalarsAsWeights(False)
com.Update()
center = [0, 0, 0]
center = com.GetCenter()


# define the rotation matrix, here it is simply the local coordinate system
rotM = vtk.vtkMatrix4x4()
rotM.Identity()

for i in range(0, 3):
    rotM.SetElement(0, i, xprime[i])
    rotM.SetElement(1, i, yprime[i])
    rotM.SetElement(2, i, zprime[i])

#rotM.Invert()

# transform object stores the transformation information
trans = vtk.vtkTransform()
trans.Translate(-center[0], -center[1], -center[2])
trans.PostMultiply()
trans.Concatenate(rotM)

# transform filter performs the actual operation
transF = vtk.vtkTransformPolyDataFilter()
transF.SetInputData(pd)
transF.SetTransform(trans)
transF.Update()

pd = transF.GetOutput()


pd = transF.GetOutput()
b = pd.GetBounds()
z_min = b[4]

# transform object stores the transformation information
trans2 = vtk.vtkTransform()
trans2.Translate(0, 0, -z_min)

# transform filter performs the actual operation
transF2 = vtk.vtkTransformPolyDataFilter()
transF2.SetInputData(pd)
transF2.SetTransform(trans2)
transF2.Update()

pd = transF2.GetOutput()

# writing the output
writer = vtk.vtkPolyDataWriter()
writer.SetFileName(args.output)
writer.SetInputData(pd)
writer.Update()
writer.Write()

