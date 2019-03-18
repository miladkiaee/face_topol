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
yprime = np.array(pts.GetPoint(2)) - np.array(pts.GetPoint(0))
zprime = np.array(pts.GetPoint(4)) - np.array(pts.GetPoint(0))
oprime = np.array(pts.GetPoint(0))

# define the rotation matrix, here it is simply the local coordinate system
rotM = vtk.vtkMatrix4x4()
rotM.Identity()

for i in range(0, 3):
    rotM.SetElement(i, 0, xprime[i])

for i in range(0, 3):
    rotM.SetElement(i, 1, yprime[i])

for i in range(0, 3):
    rotM.SetElement(i, 2, zprime[i])

# transform object stores the transformation information
trans = vtk.vtkTransform()
trans.Translate(-1*oprime[0], -1*oprime[1], -1*oprime[2])
trans.SetMatrix(rotM)

# transform filter performs the actual operation
transF = vtk.vtkTransformPolyDataFilter()
transF.SetInputData(pd)
transF.SetTransform(trans)
transF.Update()

# writing the output
writer = vtk.vtkPolyWriter()
writer.SetFileName(args.input)
writer.SetInputData(transF.GetOutput())
writer.Update()
writer.Write()

