import vtk
import numpy as np
import math

from argparse import ArgumentParser

parser = ArgumentParser()

parser.add_argument("-i", "--input", default= "", help="input file name")
parser.add_argument("-o", "--output", default="", help="output file name")
parser.add_argument("-n", "--distancenumber", default="", help="number of thresholds for distances")
parser.add_argument("-u", "--upperthreshold", default="", help="upper threshold for distance")
parser.add_argument("-c", "--curvenumber", default="", help="number curvature threshold for distance")


args = parser.parse_args()

reader = vtk.vtkDataSetReader()
reader.SetFileName(args.input)
reader.Update()

cn = int(args.curvenumber)
ct = 0.1 # max threshold. we can set to different values

for citer in range(1, cn+1):

    pd = reader.GetOutput()

    uct = float(citer)*ct/float(cn)
    lct = -1.0*uct

    print "curvature thresh: "
    print uct
    print lct

    numPoints = pd.GetNumberOfPoints()
    
    thrPoints = vtk.vtkPoints()

    for ii in range ( 0, numPoints ):
        g = np.array(pd.GetPointData().GetArray(0).GetTuple(ii))
        g = np.array(g)
        g = g.item()
        if (g<uct) and (g>lct):
            p = [0,0,0]
            pd.GetPoint(ii, p)
            thrPoints.InsertNextPoint(p)

    ctpd = vtk.vtkPolyData()
    ctpd.SetPoints(thrPoints)

    p1 = [0, 0, 0]
    p2 = [0, 0, 0]

    nthr = int(args.distancenumber)
    uthr = float(args.upperthreshold) # in mm

    numctpdPoints = ctpd.GetNumberOfPoints()

    for t in range(1, nthr+1): 
        
        print "distance thre: "
        print t
        points = vtk.vtkPoints()
        lines = vtk.vtkCellArray()

        for i in range( 0, numctpdPoints ):

            ctpd.GetPoint(i, p1)  # get ith point

            points.InsertNextPoint(p1);

            for j in range(i+1, numctpdPoints ):

                ctpd.GetPoint(j, p2)  # get ith point

                sqrDist = vtk.vtkMath.Distance2BetweenPoints(p1, p2)
                dist = math.sqrt(sqrDist)

                t0 = float(t)*uthr/float(nthr)
                if dist < t0 :
                    line = vtk.vtkLine()
                    line.GetPointIds().SetId(0, i)
                    line.GetPointIds().SetId(1, j)
                    lines.InsertNextCell(line)

        linesPolyData = vtk.vtkPolyData()
        linesPolyData.SetPoints(points)
        linesPolyData.SetLines(lines)

        writer = vtk.vtkPolyDataWriter()
        writer.SetInputData(linesPolyData)
        writer.SetFileName("dthr" + str(t0) + "cthr" + str(uct) + args.output)
        writer.Write()
