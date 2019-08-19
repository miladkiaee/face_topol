import vtk
import math

import numpy as np
import sys

from argparse import ArgumentParser

parser = ArgumentParser()
parser.add_argument("-i", "--input", default="", help="input polydata file name")
parser.add_argument("-o", "--output", default="", help="output path for writing")

args = parser.parse_args()

reader = vtk.vtkPLYReader()
reader.SetFileName(args.input)
reader.Update()
pd = reader.GetOutput()

numPoints = pd.GetNumberOfPoints()

als = vtk.vtkDoubleArray()
als.SetName("some_component")
als.SetNumberOfValues(numPoints)
p = [0, 0, 0]
for i in range(numPoints):
    pd.GetPoint(i, p)
    als.SetValue(i, p[0])
pd.GetPointData().SetScalars(als)

contourAt = -65.81
con = vtk.vtkContourFilter()
con.SetInputData(pd)
con.SetValue(0, contourAt)
con.SetArrayComponent(0)
con.ComputeScalarsOn()
con.Update()

# writing original contour output
writer = vtk.vtkPolyDataWriter()
writer.SetFileName(args.output + "contour_org.ply")
writer.SetInputData(con.GetOutput())
writer.Update()
writer.Write()

vs = vtk.vtkStripper()
vs.SetInputData(con.GetOutput())
vs.JoinContiguousSegmentsOn()
vs.Update()

cpd2 = vtk.vtkCleanPolyData()
cpd2.SetInputData(vs.GetOutput())
cpd2.Update()

spline = vtk.vtkCardinalSpline()
spline.SetLeftConstraint(2)
spline.SetLeftValue(0)
spline.SetRightConstraint(2)
spline.SetRightValue(0)

spFilter = vtk.vtkSplineFilter()
spFilter.SetInputData(cpd2.GetOutput())
conNumPoint = cpd2.GetOutput().GetNumberOfPoints()
spFilter.SetNumberOfSubdivisions(conNumPoint*10)
spFilter.SetSpline(spline)
spFilter.Update()

bc = cpd2.GetOutput().GetBounds()
yl = bc[3] - bc[2]
zl = bc[5] - bc[4]
yzl = math.sqrt(yl**2 + zl**2)
def_tol = yzl/(100**2)

print 'bound diag = ', yzl
print 'max p dist = ', def_tol

cpd = vtk.vtkCleanPolyData()
cpd.SetInputData(spFilter.GetOutput())
cpd.ToleranceIsAbsoluteOn()
cpd.PointMergingOn()
cpd.ConvertStripsToPolysOn()
cpd.GetConvertLinesToPoints()
cpd.ConvertPolysToLinesOn()
cpd.ToleranceIsAbsoluteOn()
cpd.SetAbsoluteTolerance(def_tol)
cpd.Update()

# writing converted spline output
writer = vtk.vtkPolyDataWriter()
writer.SetFileName(args.output + "contour_spline.ply")
writer.SetInputData(cpd.GetOutput())
writer.Update()
writer.Write()


