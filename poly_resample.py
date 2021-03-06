import vtk

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

contourAt = 25
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

ps = vtk.vtkPolyDataPointSampler()
ps.AddInputData(con.GetOutput())
ps.SetDistance(0.5)
# ps.GenerateEdgePointsOff()
# ps.GenerateInteriorPointsOff()
# ps.GenerateVertexPointsOff()
ps.GenerateVerticesOn()
ps.Update()

vs = vtk.vtkStripper()
vs.SetInputData(ps.GetOutput())
vs.JoinContiguousSegmentsOn()
vs.PassThroughCellIdsOff()
vs.PassThroughPointIdsOff()
vs.Update()

cpd = vtk.vtkCleanPolyData()
cpd.SetInputData(vs.GetOutput())
cpd.ToleranceIsAbsoluteOn()
cpd.SetTolerance(0.02)
cpd.Update()

# writing converted spline output
writer = vtk.vtkPolyDataWriter()
writer.SetFileName(args.output + "contour_polysample.ply")
writer.SetInputData(cpd.GetOutput())
writer.Update()
writer.Write()


