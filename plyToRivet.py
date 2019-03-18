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

curv = vtk.vtkCurvatures()
curv.SetCurvatureType(vtk.VTK_CURVATURE_MEAN)
curv.SetInputData(reader.GetOutput())
curv.Update()

pd = curv.GetOutput()

writer0 = vtk.vtkPolyDataWriter()
writer0.SetInputData(pd);
writer0.SetFileName(args.curveFileFull);
writer0.Write();

## here we want to mask the input to reduce the load for TDA
mask = vtk.vtkMaskPoints()
mask.SetInputData(pd)
#mask.SingleVertexPerCellOn()
mask.RandomModeOn()
mask.SetRandomModeType(1) # spatially stratified based on woodring et al
mask.SetMaximumNumberOfPoints(1000)
mask.Update()

p = [0, 0, 0]

f = open(args.output, 'w+')

maxDist = 40

f.write('points\n')
f.write('3\n')
f.write('%d\n' %(maxDist))
f.write('curvature\n')

pd = mask.GetOutput()

n = pd.GetNumberOfPoints()

#print "number of points: ", n

index = 0

for i in range(n):
    pd.GetPoints().GetPoint(i, p)
    g = np.array(pd.GetPointData().GetArray(index).GetTuple(i))
    g = np.array(g)
    g = g.item()
    if (g > 0.1):
        g = 0.1
    if (g < -0.1):
        g = -0.1
    f.write( '%f %f %f %f\n' % (p[0], p[1], p[2], g) )

f.close()

writer = vtk.vtkPolyDataWriter()
writer.SetInputData(pd);
writer.SetFileName(args.curveFile);
writer.Write();


