# this code tries to align the coordinate system to one define by some principal analysis
# and to save some level curve points set files
# Kitware's visualization toolkit
import vtk
import sys

from argparse import ArgumentParser
from smoothFace import smooth
from cleanFace import cleaner

parser = ArgumentParser()
parser.add_argument("-i", "--input", default="", help="input polydata file name")
parser.add_argument("-a", "--along", default="", help="the axis of level curves")

args = parser.parse_args()

reader = vtk.vtkPLYReader()
reader.SetFileName(args.input)
reader.Update()
pd = reader.GetOutput()

# removing the non manifold cells
non_man = vtk.vtkFeatureEdges()
non_man.SetInputData(pd)
non_man.BoundaryEdgesOff()
non_man.FeatureEdgesOff()
non_man.NonManifoldEdgesOn()
non_man.Update()

# smooth
pd = smooth(pd, feature_angle=160,
            edge_angle=160, relax=0.25, num_iter=100,
            file_path=args.input)

pd = cleaner(pd, toler=0.01)

b = pd.GetBounds()
x_min = b[0]
x_max = b[1]
y_min = b[2]
y_max = b[3]
z_min = b[4]
z_max = b[5]

mid = 1000

if args.along == "x":
    mid = x_min + (x_max - x_min)/2
if args.along == "y":
    mid = y_min + (y_max - y_min)/2
if args.along == "z":
    mid = z_min + (z_max - z_min)/2

# ## ##
# print the curve points set data file
numPoints = pd.GetNumberOfPoints()

# we are going to set al as a scalar array for point data
al = args.along

als = vtk.vtkDoubleArray()
als.SetName("some_component")
als.SetNumberOfValues(numPoints)

p = [0, 0, 0]
# set the scalar array to be the z coordinate
if al == "x":
    for i in range(numPoints):
        pd.GetPoint(i, p)
        als.SetValue(i, p[0])
if al == "y":
    for i in range(numPoints):
        pd.GetPoint(i, p)
        als.SetValue(i, p[1])
if al == "z":
    for i in range(numPoints):
        pd.GetPoint(i, p)
        als.SetValue(i, p[2])

pd.GetPointData().SetScalars(als)

# ## ##
maxNumCurves = 0
elong = 0
delta = 0
increment = 0
value = 0
maxx = 0
minn = 0

if args.along == "x":
    maxNumCurves = 100
    elong = 200
    delta = abs(x_max - x_min)/1000
    increment = abs(x_max - x_min)/100
    value = x_min
    maxx = x_max
    minn = x_min

if args.along == "y":
    maxNumCurves = 250
    elong = 100
    delta = abs(y_max - y_min)/10000
    increment = abs(y_max - y_min)/100
    value = y_min
    maxx = y_max
    minn = y_min

if args.along == "z":
    maxNumCurves = 400
    elong = 400
    delta = abs(z_max - z_min)/10000
    increment = abs(z_max - z_min)/200
    value = z_min
    maxx = z_max
    minn = z_min

values = []
centersX = []
centersY = []
centersZ = []
MinXs = []
MaxXs = []
MinYs = []
MaxYs = []
MinZs = []
MaxZs = []

numCurves = 0
minNumCells = 40
extremelyLow = 20

while numCurves < maxNumCurves and value < (minn + elong) and value < (maxx - 2*increment):

    value = value + increment
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

    numPoints = pdc.GetNumberOfPoints()
    numCells = pdc.GetNumberOfCells()

    while numCells < extremelyLow or numRegions != 1 and value < maxx:
        value = value + delta
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
        numPoints = pdc.GetNumberOfPoints()
        numCells = pdc.GetNumberOfCells()
        # print("num regions: ", numRegions)

    # print ("value = ", value)
    if value > maxx:
        print("exceeded boundary!")
        break

    # we are going through all points but in order of neighboring
    cellIds = vtk.vtkIdList()
    orderedPointIds = vtk.vtkIdList()
    orderedCellIds = vtk.vtkIdList()

    closed = True

    if numCells < minNumCells and value > mid:
        print("region was too small, aborting!")
        break

    f = open(str(numCurves) + ".csv", 'w+')
    print("curve ", args.input, " level ", str(value))

    # adding to values array for saving all contours together in one file
    values.append(value)

    # first lets try to find the start and end of the curve in case it is open
    # we need to be consistent with the side of the curve we start with
    # here probably the one with lesser x would be a good choice
    # if curve is in zy plane we wanna choose one with lesser z
    prevId = -1
    for i in range(numCells):
        # for each cell get point id of the two sides
        pointId1 = pdc.GetCell(i).GetPointId(0)

        if pointId1 == prevId:
            pointId1 = pdc.GetCell(i).GetPointId(1)

        prevId = pointId1

        # cell ids for firs point of the cell
        big = 1000
        xx = big
        pdc.GetPointCells(pointId1, cellIds)
        nc = cellIds.GetNumberOfIds()
        if nc == 1:
            # print("curve is open at point", pointId1)
            orderedPointIds.InsertNextId(pointId1)
            closed = False
            p = [0, 0, 0]
            pdc.GetPoint(pointId1, p)
            if args.along == "z" or args.along == "y":
                xx = p[0]
            if args.along == "x":
                xx = p[2]
            if xx < big:
                big = xx
                pointId = pointId1
        if (nc == 0) or (nc > 2):
            print("number of cellIds:", nc)
            sys.exit("error with number of connected cells")

    if closed:
        # print("curve is closed")
        # for closed curve we want to start at point with smallest x??
        # if in zy plane we want smallest z
        pointId = 0
        p = [0, 0, 0]
        big = 1000
        np = pdc.GetNumberOfPoints()
        zz = big

        for i in range(np):
            pdc.GetPoint(i, p)

            if args.along == "z" or args.along == "y":
                zz = p[0]
            if args.along == "x":
                zz = p[2]

            if zz < big:
                big = zz
                pointId = i

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

    # get the maximum of z coordinate by the bounds
    bc = pdc.GetBounds()
    xc_min = bc[0]
    xc_max = bc[1]
    yc_min = bc[2]
    yc_max = bc[3]
    zc_min = bc[4]
    zc_max = bc[5]
    MinXs.append(xc_min)
    MaxXs.append(xc_max)
    MinYs.append(yc_min)
    MaxYs.append(yc_max)
    MinZs.append(zc_min)
    MaxZs.append(zc_max)

    # in order to put center of mass as origin we want to deduct the first one from the rest of the points
    com = vtk.vtkCenterOfMass()
    com.SetInputData(pdc)
    com.SetUseScalarsAsWeights(False)
    com.Update()
    center = com.GetCenter()

    centersX.append(center[0])
    centersY.append(center[1])
    centersZ.append(center[2])

    for i in range(0, orderedPointIds.GetNumberOfIds()):
        a = orderedPointIds.GetId(i)
        # print("id : ", a, " of point count : ", i)
        p = [0, 0, 0]
        pdc.GetPoint(a, p)

        # we are doing the x y z to y z x move for the geodesic software preferences
        # relative to the initial coordinates of the point in the curve
        if args.along == "x":
            f.write('%f, %f, %f\n' % (p[1], p[0], p[2]))
        if args.along == "y":
            f.write('%f, %f, %f\n' % (p[0], p[1], p[2]))
        if args.along == "z":
            f.write('%f, %f, %f\n' % (p[0], p[2], p[1]))
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

# writing levels
levelFile = open('levels.txt', 'w+')

for i in range(len(values)):
    if i == -1:
        rx = 0
        rxx = 0
        ry = 0
        ryy = 0
        rz = 0
        rzz = 0
    else:
        rx = MinXs[i]
        rxx = MaxXs[i]
        ry = MinYs[i]
        ryy = MaxYs[i]
        rz = MinZs[i]
        rzz = MaxZs[i]

    levelFile.write('%f, %f, %f, %f, %f, %f, %f, %f, %f, %f\n'
                    % (values[i], centersX[i], centersY[i], centersZ[i],
                       rx, rxx, ry, ryy, rz, rzz))

levelFile.close()
