# getting two surfaces
# probably from two condiles
# based on cross sections calculate the bending potential between them

import vtk

from argparse import ArgumentParser

from smoothFace import smooth
from reduceTriangles import reduce_it
from geometric_information import information
# from write_ordered_csv import write_ordered
# from write_ordered_csv_check import write_ordered_check
from resample_points import resample_points

print('----------')

parser = ArgumentParser()
parser.add_argument("-i1", "--input1", default="", help="input polydata 1 file name")
parser.add_argument("-i2", "--input2", default="", help="input polydata 2 file name")
parser.add_argument("-a", "--along", default="", help="the axis of level curves")
parser.add_argument("-o", "--output", default="", help="output path for writing")

args = parser.parse_args()

reader1 = vtk.vtkPLYReader()
reader1.SetFileName(args.input1)
reader1.Update()
pd1 = reader1.GetOutput()

reader2 = vtk.vtkPLYReader()
reader2.SetFileName(args.input2)
reader2.Update()
pd2 = reader1.GetOutput()

# triangulate in case
trif1 = vtk.vtkTriangleFilter()
trif1.SetInputData(pd1)
trif1.Update()

pd1 = trif1.GetOutput()

trif2 = vtk.vtkTriangleFilter()
trif2.SetInputData(pd2)
trif2.Update()

pd2 = trif2.GetOutput()

# reduce the poly data & smooth
pd1 = reduce_it(pd1, args.input)
pd1 = smooth(pd1, feature_angle=180,
            edge_angle=180, relax=0.4, num_iter=20,
            file_path=args.input1)

b1 = pd1.GetBounds()
x_min1 = b1[0]
x_max1 = b1[1]
y_min1 = b1[2]
y_max1 = b1[3]
z_min1 = b1[4]
z_max1 = b1[5]

pd2 = reduce_it(pd2, args.input2)
pd2 = smooth(pd2, feature_angle=180,
            edge_angle=180, relax=0.4, num_iter=20,
            file_path=args.input2)

b2 = pd2.GetBounds()
x_min2 = b2[0]
x_max2 = b2[1]
y_min2 = b2[2]
y_max2 = b2[3]
z_min2 = b2[4]
z_max2 = b2[5]


mid1 = 1000
mid2 = 1000

al = args.along

if al == "x":
    mid1 = x_min1 + (x_max1 - x_min1) / 2
    mid2 = x_min2 + (x_max2 - x_min2) / 2
if al == "y":
    mid1 = y_min1 + (y_max1 - y_min1) / 2
    mid2 = y_min2 + (y_max2 - y_min2) / 2
if al == "z":
    mid1 = z_min1 + (z_max1 - z_min1) / 2
    mid2 = z_min2 + (z_max2 - z_min2) / 2

numPoints1 = pd1.GetNumberOfPoints()
als1 = vtk.vtkDoubleArray()
als1.SetName("some_component")
als1.SetNumberOfValues(numPoints1)

numPoints2 = pd2.GetNumberOfPoints()
als2 = vtk.vtkDoubleArray()
als2.SetName("some_component")
als2.SetNumberOfValues(numPoints2)

pd1.GetPointData().SetScalars(als1)
pd2.GetPointData().SetScalars(als2)


# ## ##
maxNumCurves = 0
elong = 0
delta = 0
increment = 0
value = 0
maxx = 0
minn = 0

if al == "x":
    maxNumCurves = 100
    elong = 100
    delta = abs(x_max1 - x_min1)/1000
    increment = abs(x_max1 - x_min1)/100
    value = x_min1
    maxx = x_max1
    minn = x_min1

if al == "y":
    maxNumCurves = 100
    elong = 100
    delta = abs(y_max1 - y_min1)/10000
    increment = abs(y_max1 - y_min1)/100
    value = y_min1
    maxx = y_max1
    minn = y_min1

if al == "z":
    maxNumCurves = 100
    elong = 100
    delta = abs(z_max1 - z_min1)/10000
    increment = abs(z_max1 - z_min1)/200
    value = z_min1
    maxx = z_max1
    minn = z_min1


values = []
centersX = []
centersY = []
centersZ = []
MinXs = []
MaxXs = []
MinYs = []
XofMinYs = []
ZofMinYs = []
MaxYs = []
MinZs = []
XofMinZs = []
YofMinZs = []
MaxZs = []
MinZsStart = []
YofMinZsStart = []

numCurves = 0
minNumCells = 40
extremelyLow = 20

# starting the find contour curves
while numCurves < maxNumCurves and \
        value < (minn + elong) and \
        value < (maxx - 2*increment):

    value += increment

    print("trying level: ", value)

    # extract contour
    con1 = vtk.vtkContourFilter()
    con1.SetInputData(pd1)
    con1.SetValue(0, value)
    con1.SetArrayComponent(0)
    con1.ComputeScalarsOn()
    con1.Update()
    pdc1 = con1.GetOutput()

    con2 = vtk.vtkContourFilter()
    con2.SetInputData(pd2)
    con2.SetValue(0, value)
    con2.SetArrayComponent(0)
    con2.ComputeScalarsOn()
    con2.Update()

    pdc1 = con1.GetOutput()
    pdc2 = con2.GetOutput()
    # pdc = resample_points(pdc)

    [bc1, center1, xof_small_z1, yof_small_z1,
     small_z1, xof_small_y1, zof_small_y1, small_y1] = information(pdc1)

    MinXs.append(bc1[0])
    MaxXs.append(bc1[1])
    MaxYs.append(bc1[3])
    MinZs.append(small_z1)
    XofMinZs.append(xof_small_z1)
    YofMinZs.append(yof_small_z1)
    MinYs.append(small_y1)
    XofMinYs.append(xof_small_y1)
    ZofMinYs.append(zof_small_y1)
    MaxZs.append(bc1[5])
    centersX.append(center1[0])
    centersY.append(center1[1])
    centersZ.append(center1[2])

    numCells1 = pdc1.GetNumberOfCells()

    # some checks
    if value > maxx or \
            numCells1 < minNumCells and value > mid1:
        break

    # contour can contain multiple non-connected curves
    conn1 = vtk.vtkConnectivityFilter()
    conn1.SetInputData(pdc1)
    conn1.Update()
    numRegions1 = conn1.GetNumberOfExtractedRegions()

    conn2 = vtk.vtkConnectivityFilter()
    conn2.SetInputData(pdc2)
    conn2.Update()
    numRegions2 = conn2.GetNumberOfExtractedRegions()

    # array of sub polydata included in an individual contour
    if numRegions1 == 0 or numRegions2 == 0:
        print("no region found in at least one of geometry curves at the current level")

    if not (numRegions1 == 0 or numRegions2 == 0):
        pdc1 = resample_points(pdc1)  # expected to order points too
        # write_ordered(pdc1, numCurves, args.output, value)
        # write_ordered_check(pdc1, numCurves, args.output, value)

        pdc2 = resample_points(pdc2)  # expected to order points too
        # write_ordered(pdc2, numCurves, args.output, value)
        # write_ordered_check(pdc1, numCurves, args.output, value)

    numCurves += 1

    # adding to values array for saving all contours together in one file
    values.append(value)



con1 = vtk.vtkContourFilter()
con1.SetInputData(pd1)
for i in range(len(values)):
    con1.SetValue(i, values[i])
con1.SetArrayComponent(0)
con1.ComputeScalarsOn()
con1.Update()

# writing the contours output
writer = vtk.vtkPolyDataWriter()
writer.SetFileName(args.output + "contours1.ply")
writer.SetInputData(con1.GetOutput())
writer.Update()
writer.Write()

con2 = vtk.vtkContourFilter()
con2.SetInputData(pd2)
for i in range(len(values)):
    con1.SetValue(i, values[i])
con2.SetArrayComponent(0)
con2.ComputeScalarsOn()
con2.Update()

# writing the contours output
writer = vtk.vtkPolyDataWriter()
writer.SetFileName(args.output + "contours2.ply")
writer.SetInputData(con2.GetOutput())
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
    # else:
        # rx = MinXs[i]  # - MinXs[0]
        # rxx = MaxXs[i]  # - MaxXs[0]
        # ry = MinYs[i]  # - MinYs[0]
        # ryy = MaxYs[i]  # - MaxYs[0]
        # rz = MinZs[i]  # - MinZs[0]
        # rzz = MaxZs[i]  # - MaxZs[0]

    levelFile.write('%f\n' % (values[i]))

levelFile.close()













