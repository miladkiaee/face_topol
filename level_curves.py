# this code tries to align the coordinate system to one define by some principal analysis
# and to save some level curve points set files
# Kitware's visualization toolkit
import vtk
import numpy as np
from argparse import ArgumentParser

parser = ArgumentParser()
parser.add_argument("-i", "--input", default="", help="input polydata file name")

args = parser.parse_args()

reader = vtk.vtkPLYReader()
reader.SetFileName(args.input)
reader.Update()
# reader output to a polydata object
pd = reader.GetOutput()

# smooth
# sm = vtk.vtkSmoothPolyDataFilter()
# sm.SetInputData(pd)
# sm.SetNumberOfIterations(200)
# sm.FeatureEdgeSmoothingOn()
# sm.SetRelaxationFactor(0)
# sm.BoundarySmoothingOn()
# sm.SetEdgeAngle(0)
# sm.SetFeatureAngle(0)
# sm.Update()

# pd = sm.GetOutput()

b = pd.GetBounds()
x_min = b[0]
x_max = b[1]
y_min = b[2]
y_max = b[3]
z_min = b[4]
z_max = b[5]
mid = z_min + (z_max - z_min)/2
# con_r = [z_min, z_max]

# clipping data to get rid of first 1/10 x of data
# clipHeight = y_min + (y_max - y_min)/15
# plane = vtk.vtkPlane()
# p = [0, clipHeight, 0]
# plane.SetOrigin(p)
# n = [0, 1, 0]
# plane.SetNormal(n)

# clip = vtk.vtkClipPolyData()
# clip.SetInputData(pd)
# clip.SetClipFunction(plane)
# clip.SetValue(0)
# clip.Update()

# pd = clip.GetOutput()

# ## ##
# print the curve points set data file
numPoints = pd.GetNumberOfPoints()

# we are going to set z as a scalar array for point data
ys = vtk.vtkDoubleArray()
ys.SetName("some_component")
ys.SetNumberOfValues(numPoints)

p = [0, 0, 0]
# set the scalar array to be the z coordinate
for i in range(numPoints):
    pd.GetPoint(i, p)
    ys.SetValue(i, p[1])

pd.GetPointData().SetScalars(ys)

# ## ##

maxNumCurves = 30
delta = abs(y_max - y_min)/1000
decrement = abs(y_max - y_min)/(maxNumCurves)
value = y_max - 5*delta

values = []

numCurves = 0
minNumCells = 100

while numCurves < maxNumCurves and value > y_min:

    value = value - decrement
    con = vtk.vtkContourFilter()
    con.SetInputData(pd)
    con.SetValue(0, value)
    con.SetArrayComponent(0)
    con.ComputeScalarsOn()
    con.Update()

    pdc = con.GetOutput()

    conn = vtk.vtkConnectivityFilter()
    conn.SetInputData(pdc)
    conn.Update()
    numRegions = conn.GetNumberOfExtractedRegions()

    while numRegions != 1 and value > y_min:
        value = value - delta
        # print("trying value ", value)
        con = vtk.vtkContourFilter()
        con.SetInputData(pd)
        con.SetValue(0, value)
        con.SetArrayComponent(0)
        con.ComputeScalarsOn()
        con.Update()
        pdc = con.GetOutput()
        conn = vtk.vtkConnectivityFilter()
        conn.SetInputData(pdc)
        conn.Update()
        numRegions = conn.GetNumberOfExtractedRegions()
        # print("num regions: ", numRegions)

    # print ("value = ", value)
    if value < y_min:
        break

    # we are going through all points but in order of neighboring
    cellIds = vtk.vtkIdList()
    orderedPointIds = vtk.vtkIdList()
    orderedCellIds = vtk.vtkIdList()

    closed = True
    numPoints = pdc.GetNumberOfPoints()
    numCells = pdc.GetNumberOfCells()

    if numCells < minNumCells and value < mid:
        # print("region was too small, aborting!")
        break

    f = open("l" + str(value) + "_c" + str(numCurves) + ".csv", 'w+')
    print("curve ", args.input, " level ", str(value))

    # adding to values array for saving all contours together in one file
    values.append(value)

    # first lets try to find the start and end of the curve in case it is open
    for i in range(numCells):
        pointId1 = pdc.GetCell(i).GetPointId(0)
        pointId2 = pdc.GetCell(i).GetPointId(1)
        pdc.GetPointCells(pointId1, cellIds)
        if cellIds.GetNumberOfIds() == 1:
            # print("curve is open at point", pointId1)
            orderedPointIds.InsertNextId(pointId1)
            closed = False
            break
        pdc.GetPointCells(pointId2, cellIds)
        if cellIds.GetNumberOfIds() == 1:
            # print("curve is open at point", pointId2)
            orderedPointIds.InsertNextId(pointId2)
            closed = False
            break

    if closed:
        # print("curve is closed, starting at point 0")
        pointId = 0
        orderedPointIds.InsertNextId(pointId)

    for i in range(pdc.GetNumberOfPoints()-2):
        # print ("<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<")
        # print("point iteration ", i)

        # for j in range(orderedPointIds.GetNumberOfIds()):
        # print (" ", orderedPointIds.GetId(j)),

        nextPointId = orderedPointIds.GetId(i)
        # print("pointId: ", nextPointId)

        pdc.GetPointCells(nextPointId, cellIds)

        # print("this point shared with how many cells: ", cellIds.GetNumberOfIds())

        if cellIds.GetNumberOfIds() > 0:

            cellId = cellIds.GetId(0)
            # print("trying cellId: ", cellId)

            # check if this cell is the correct one by checking its points
            pointId1 = pdc.GetCell(cellId).GetPointId(0)
            pointId2 = pdc.GetCell(cellId).GetPointId(1)
            if orderedPointIds.IsId(pointId1) != -1 and orderedPointIds.IsId(pointId2) != -1:
                # print("both point of this cell exists. trying other possibility ")
                cellId = cellIds.GetId(1)
                pointId1 = pdc.GetCell(cellId).GetPointId(0)
                pointId2 = pdc.GetCell(cellId).GetPointId(1)
                # print("cellId: ", cellId)
                if orderedPointIds.IsId(pointId1) != -1 and orderedPointIds.IsId(pointId2) != -1:
                    # print("this is odd! second check not passed!")
                    break
                # else:
                    # print("second check passed!")
            else:
                # print("cell is not traversed. cellId: ", cellId)
                pointId1 = pdc.GetCell(cellId).GetPointId(0)
                pointId2 = pdc.GetCell(cellId).GetPointId(1)

            if orderedPointIds.IsId(pointId1) != -1:
                # print("point already exist in list. trying next one")
                pointId = pointId2
                if orderedPointIds.IsId(pointId2) != -1:
                    print("this is not right! second check not passed!")
                else:
                    # print("second check passed! adding this point.")
                    orderedPointIds.InsertNextId(pointId2)
            else:
                # print("adding a unique point to list. id: ", pointId1)
                orderedPointIds.InsertNextId(pointId1)

    for i in range(orderedPointIds.GetNumberOfIds()):
        a = orderedPointIds.GetId(i)
        # print("id : ", a, " of point count : ", i)
        p = [0, 0, 0]
        pdc.GetPoint(a, p)

        # we are doing the x y z to y z x move for the geodesic software preferences
        f.write('%f, %f, %f\n' % (p[0], p[1], p[2]))

    f.close()
    numCurves = numCurves + 1
    # print("curve number ", numCurves)

con = vtk.vtkContourFilter()
con.SetInputData(pd)
for i in range(len(values)):
    con.SetValue(i, values[i])
con.SetArrayComponent(0)
con.ComputeScalarsOn()
con.Update()

# writing the contours output
writer = vtk.vtkPolyDataWriter()
writer.SetFileName(args.input + "contours.ply")
writer.SetInputData(con.GetOutput())
writer.Update()
writer.Write()
