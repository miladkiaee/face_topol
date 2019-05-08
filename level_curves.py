# this code tries to align the coordinate system to one define by some principal analysis
# and to save some level curve points set files
# Kitware's visualization toolkit
import vtk
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
smoother = vtk.vtkSmoothPolyDataFilter()
smoother.SetInputData(reader.GetOutput())
smoother.SetFeatureEdgeSmoothing(True)
smoother.SetFeatureAngle(180)
smoother.SetRelaxationFactor(0.1)
smoother.SetEdgeAngle(180)
smoother.SetBoundarySmoothing(True)
smoother.SetNumberOfIterations(400)
smoother.Update()

pd = smoother.GetOutput()

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
zs = vtk.vtkDoubleArray()
zs.SetName("some_component")
zs.SetNumberOfValues(numPoints)

p = [0, 0, 0]
# set the scalar array to be the z coordinate
for i in range(numPoints):
    pd.GetPoint(i, p)
    zs.SetValue(i, p[2])

pd.GetPointData().SetScalars(zs)

# ## ##
maxNumCurves = 400
# elongY = 80
elongZ = 200
delta = abs(z_max - z_min)/10000
increment = 0.5
value = z_min  # + 5*delta

values = []
centersX = []
centersY = []
centersZ = []
MaxZs = []
MinXs = []

numCurves = 0
minNumCells = 200
extremelyLow = 100

while numCurves < maxNumCurves and value < (z_min + elongZ):

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

    while numRegions != 1 and value < z_max:
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
        # print("num regions: ", numRegions)

    # print ("value = ", value)
    if value > z_max:
        break

    # we are going through all points but in order of neighboring
    cellIds = vtk.vtkIdList()
    orderedPointIds = vtk.vtkIdList()
    orderedCellIds = vtk.vtkIdList()

    closed = True
    numPoints = pdc.GetNumberOfPoints()
    numCells = pdc.GetNumberOfCells()

    if numCells < minNumCells and value > mid:
        print("region was too small, aborting!")
        break
    if numCells < extremelyLow:
        print("starting region was too small, aborting!")
        break

    f = open(str(numCurves) + ".csv", 'w+')
    print("curve ", args.input, " level ", str(value))

    # adding to values array for saving all contours together in one file
    values.append(value)

    # first lets try to find the start and end of the curve in case it is open
    # we need to be consistent with the side of the curve we start with
    # here probably the one with lesser x would be a good choice
    prevId = -1
    for i in range(numCells):
        # for each cell get point id of the two sides
        pointId1 = pdc.GetCell(i).GetPointId(0)

        if pointId1 == prevId:
            pointId1 = pdc.GetCell(i).GetPointId(1)

        prevId = pointId1

        # cell ids for firs point of the cell
        big = 1000
        pdc.GetPointCells(pointId1, cellIds)
        nc = cellIds.GetNumberOfIds()
        if nc == 1:
            # print("curve is open at point", pointId1)
            orderedPointIds.InsertNextId(pointId1)
            closed = False
            p = [0, 0, 0]
            pdc.GetPoint(pointId1, p)
            x = p[0]
            if x < big:
                big = x
                pointId = pointId1
        if (nc == 0) or (nc > 2):
            print("problem with point cell!")

    if closed:
        # print("curve is closed")
        # for closed curve we want to start at point with smallest x
        pointId = 0
        p = [0, 0, 0]
        big = 1000
        np = pdc.GetNumberOfPoints()

        for i in range(np):

            pdc.GetPoint(i, p)
            z = p[2]

            if z < big:
                big = z
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
    zc_max = bc[5]
    MinXs.append(xc_min)
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
        f.write('%f, %f, %f\n' % (p[0] - center[0], p[1] - center[1], p[2] - center[2]))

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
    if i == 0:
        rx = 0
        rz = 0
    else:
        rx = MinXs[i] - MinXs[0]
        rz = MaxZs[i] - MaxZs[0]

    levelFile.write('%f, %f, %f, %f, %f, %f\n' % (values[i], centersX[i], centersY[i], centersZ[i], rx, rz))

levelFile.close()
