# this code tries to align the coordinate system to one define by some principal analysis

# Kitware's visualization toolkit
import vtk

import numpy as np
from argparse import ArgumentParser

parser = ArgumentParser()
parser.add_argument("-i", "--input", default= "", help="input polydata file name")
parser.add_argument("-t", "--trans", default="", help="transformed polydata file name to write")
parser.add_argument("-r", "--rivet", default="", help="rivet file name to write")

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

# rotM.Invert()

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

b = pd.GetBounds()
z_min = b[4]
z_max = b[5]
z_length = z_max - z_min

# transform object stores the transformation information
trans2 = vtk.vtkTransform()
trans2.Translate(0, 0, -z_min)

# transform filter performs the actual operation
transF2 = vtk.vtkTransformPolyDataFilter()
transF2.SetInputData(pd)
transF2.SetTransform(trans2)
transF2.Update()

pd = transF2.GetOutput()

# we are going to set z as a scalar array for point data
numPoints = pd.GetNumberOfPoints()
zs = vtk.vtkDoubleArray()
zs.SetName("z_component")
zs.SetNumberOfValues(numPoints)

p = [0, 0, 0]

for i in range(numPoints):
    pd.GetPoint(i, p)
    zs.SetValue(i, p[2])

pd.GetPointData().SetScalars(zs)
b = pd.GetBounds()
z_min = b[4]
z_max = b[5]
con_r = [z_min, z_max]
con_num = 50

con = vtk.vtkContourFilter()
con.SetInputData(pd)
con.GenerateValues(con_num, con_r)
con.SetArrayComponent(0)
con.ComputeScalarsOn()
con.Update()

pd = con.GetOutput()

mask = vtk.vtkMaskPoints()
mask.SetInputData(pd)
mask.RandomModeOn()
mask.SetRandomModeType(2)  # spatially stratified based on Woodring et al
# mask.SingleVertexPerCellOn()
mask.SetMaximumNumberOfPoints(3000)
mask.Update()

pd = mask.GetOutput()

# print the rivet point data file
f = open(args.rivet, 'w+')
maxDist = 20

f.write('points\n')
f.write('3\n')
f.write('%d\n' %(maxDist))
f.write('height\n')

numPoints = pd.GetNumberOfPoints()

for i in range(numPoints):
    pd.GetPoints().GetPoint(i, p)
    g = np.array(pd.GetPointData().GetArray(0).GetTuple(i))
    g = np.array(g)
    g = g.item()
    f.write('%f %f %f %f\n' % (p[0], p[1], p[2], g))

f.close()

# writing the output
writer = vtk.vtkPolyDataWriter()
writer.SetFileName(args.trans)
writer.SetInputData(pd)
writer.Update()
writer.Write()

