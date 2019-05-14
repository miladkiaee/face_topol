# this code tries to align the coordinate system to one define by some principal analysis
# and to save some level curve points set files
# Kitware's visualization toolkit
import vtk
import numpy as np
import sys

from argparse import ArgumentParser
from smoothFace import smooth
from cleanFace import cleaner
from seperateNonManifold import separate
from reduceTriangles import reduce_it
from reorderPoints import initial_reorder
from reorderPoints import reorder
from geometric_information import information
from write_ordered_csv import write_ordered_csv
from write_ordered_csv_check import write_ordered_csv_check

parser = ArgumentParser()
parser.add_argument("-i", "--input", default="", help="input polydata file name")
parser.add_argument("-a", "--along", default="", help="the axis of level curves")
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

# smooth
pd = smooth(pd, feature_angle=160,
            edge_angle=160, relax=0.4, num_iter=20,
            file_path=args.input)

# pd = cleaner(pd, toler=0.01)

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
XofMinZs = []
YofMinZs = []
MaxZs = []

numCurves = 0
minNumCells = 40
extremelyLow = 20

# starting the find contour curves
while numCurves < maxNumCurves and \
        value < (minn + elong) and \
        value < (maxx - 2*increment):

    value = value + increment

    # extract contour
    con = vtk.vtkContourFilter()
    con.SetInputData(pd)
    con.SetValue(0, value)
    con.SetArrayComponent(0)
    con.ComputeScalarsOn()
    con.Update()

    pdc = con.GetOutput()
    [bc, center, xof_small_z,
     yof_small_z, small_z] = information(pdc)

    MinXs.append(bc[0])
    MaxXs.append(bc[1])
    MinYs.append(bc[2])
    MaxYs.append(bc[3])
    MinZs.append(small_z)
    XofMinZs.append(xof_small_z)
    YofMinZs.append(yof_small_z)
    MaxZs.append(bc[5])
    centersX.append(center[0])
    centersY.append(center[1])
    centersZ.append(center[2])

    numPoints = pdc.GetNumberOfPoints()
    numCells = pdc.GetNumberOfCells()

    # some checks
    if value > maxx or \
            numCells < minNumCells and value > mid:
        break

    # contour can contain multiple non-connected curves
    conn = vtk.vtkConnectivityFilter()
    conn.SetInputData(pdc)
    conn.Update()
    numRegions = conn.GetNumberOfExtractedRegions()

    ordered_points_ids = vtk.vtkIdList()
    ordered_cells_ids = vtk.vtkIdList()

    # array of sub polydata included in an individual contour
    if numRegions == 0:
        print("no region found")

    if numRegions == 1:
        initial_point_id = initial_reorder(pdc, args.along)
        ordered_points_ids = reorder(pdc, initial_point_id)
        write_ordered_csv(pdc, numCurves, value,
                          ordered_points_ids, args.output, args.along)
        write_ordered_csv_check(pdc, numCurves, value,
                          ordered_points_ids, args.output, args.along)


    if numRegions > 1:
        sub_pds = []
        max_index = np.zeros(numRegions)
        max_region_z = np.zeros(numRegions)
        for region_index in range(numRegions):
            # finding max z of each region
            tmp_conn = vtk.vtkConnectivityFilter()
            tmp_conn.SetInputData(pdc)
            tmp_conn.SetExtractionModeToSpecifiedRegions()
            tmp_conn.AddSpecifiedRegion(region_index)
            tmp_conn.Update()
            tmp_pd = tmp_conn.GetPolyDataOutput()
            c = vtk.vtkCleanPolyData()
            c.SetInputData(tmp_pd)
            c.Update()
            tmp_pd = c.GetOutput()
            sub_pds.append(tmp_pd)
            tmp_num_points = tmp_pd.GetNumberOfPoints()
            if tmp_num_points > 1:
                p = [0, 0, 0]
                small = -1000
                for point_index in range(tmp_num_points):
                    tmp_pd.GetPoint(point_index, p)
                    tmp = p[2]
                    if tmp > small:
                        small = tmp
                        max_region_z[region_index] = tmp
                        max_index[region_index] = point_index

        # sort regions based on maximum z in them
        regions_index_sorted = np.argsort(max_region_z)

        for index in regions_index_sorted:
            sorted_pd = sub_pds[index]
            if sorted_pd.GetNumberOfPoints() > 1:
                initial_point_id = initial_reorder(sorted_pd, args.along)
                ordered_points_ids = reorder(sorted_pd, initial_point_id)
                write_ordered_csv(sorted_pd, numCurves, value,
                                  ordered_points_ids, args.output, args.along)
                write_ordered_csv_check(sorted_pd, numCurves, value,
                                  ordered_points_ids, args.output, args.along)

    numCurves += 1

    # adding to values array for saving all contours together in one file
    values.append(value)

con = vtk.vtkContourFilter()
con.SetInputData(pd)
for i in range(len(values)):
    con.SetValue(i, values[i])
con.SetArrayComponent(0)
con.ComputeScalarsOn()
con.Update()

# writing the contours output
writer = vtk.vtkPolyDataWriter()
writer.SetFileName(args.output + "contours.ply")
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
        rx = MinXs[i]  # - MinXs[0]
        rxx = MaxXs[i]  # - MaxXs[0]
        ry = MinYs[i]  # - MinYs[0]
        ryy = MaxYs[i]  # - MaxYs[0]
        rz = MinZs[i]  # - MinZs[0]
        rzz = MaxZs[i]  # - MaxZs[0]

    levelFile.write('%f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f\n'
                    % (values[i], centersX[i], centersY[i], centersZ[i],
                       rx, rxx, ry, ryy, rz, rzz, XofMinZs[i], YofMinZs[i]))

levelFile.close()
