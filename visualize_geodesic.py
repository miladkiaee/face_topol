import vtk
import math
import csv

numberOfLevels = 160
numberOfGeo = 50

origin_subject = "CC031"
destination_subject = "CC077"

d = "/home/milad/face_topol/geodesic/"
d2 = "/home/milad/face_topol/polys/aligned/"

d2_ws_1 = d2 + origin_subject + "Aligned.ply-ws/"
d2_ws_2 = d2 + destination_subject + "Aligned.ply-ws/"

centersX_1 = []
centersZ_1 = []
relMaxsZ_1 = []
relMinX_1 = []

centersX_2 = []
centersZ_2 = []
relMaxsZ_2 = []
relMinX_2 = []

with open(d2_ws_1 + "levels.txt") as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=',')
    line_count = 0
    for row in csv_reader:
        line_count += 1
        centersX_1.append(float(row[1]))
        centersZ_1.append(float(row[3]))
        relMinX_1.append(float(row[4]))
        relMaxsZ_1.append(float(row[5]))

with open(d2_ws_2 + "levels.txt") as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=',')
    line_count = 0
    for row in csv_reader:
        line_count += 1
        centersX_2.append(float(row[1]))
        centersZ_2.append(float(row[3]))
        relMinX_2.append(float(row[4]))
        relMaxsZ_2.append(float(row[5]))

for i in range(numberOfGeo):
    for j in range(numberOfLevels):

        filename = d + "c_lev" + str(j) + "_geo" + str(i+1)
        print("adding curve: ", filename)
        reader = vtk.vtkDelimitedTextReader()
        reader.SetFileName(filename + '.csv')
        reader.SetFieldDelimiterCharacters(",")
        reader.SetHaveHeaders(False)
        reader.SetDetectNumericColumns(True)
        # reader.SetForceDouble(True)
        reader.Update()

        table = reader.GetOutput()
        points = vtk.vtkPoints()

        for k in range(table.GetNumberOfRows()):
            # print("x: ", table.GetValue(, 0), " y: ", table.GetValue(i, 1), "z: ", table.GetValue(i, 2))
            p = [(table.GetValue(k, 0)).ToDouble(), (table.GetValue(k, 1)).ToDouble(), (table.GetValue(k, 2)).ToDouble()]
            points.InsertNextPoint(p[0], p[1], p[2])

        # check distance between consequent points
        # if more than certain amount populate with more points
        nop = points.GetNumberOfPoints()
        p0 = [0, 0, 0]
        p1 = [0, 0, 0]
        newDist = 0.5
        extra = 1
        big = 100

        if nop > 100:
            for k in range(nop - 1):
                points.GetPoint(k, p0)
                points.GetPoint(k+1, p1)
                if p0[1] != p1[1]:
                    print("the points should have same y coordinate")
                    break
                dist = math.sqrt((p0[0]-p1[0])**2 + (p0[2]-p1[2])**2)

                if (dist > newDist) and (dist < big):
                    vec = [p1[0] - p0[0], 0, p1[2] - p0[2]]
                    counts = dist / newDist

                    for q in range(1, int(counts)):
                        ptemp = [p0[0] + q*newDist*vec[0]/dist, p0[1], p0[2] + q*newDist*vec[2]/dist]
                        points.InsertPoint(extra + nop - 1, ptemp[0], p0[1], ptemp[2])
                        extra = extra + 1

        poly = vtk.vtkPolyData()
        poly.SetPoints(points)

        com = vtk.vtkCenterOfMass()
        com.SetInputData(poly)
        com.SetUseScalarsAsWeights(False)
        com.Update()
        center = com.GetCenter()

        b = poly.GetBounds()
        x_min = b[0]
        z_max = b[5]

        trans = vtk.vtkTransform()
        frac_1 = 1 - float(i)/float(numberOfGeo)
        frac_2 = float(i)/float(numberOfGeo)
        trans.Translate(-x_min + frac_1*relMinX_1[j] + frac_2*relMinX_2[j],
                        0,
                        -z_max + frac_1*relMaxsZ_1[j] + frac_2*relMaxsZ_2[j])
        transF = vtk.vtkTransformPolyDataFilter()
        transF.SetInputData(poly)
        transF.SetTransform(trans)
        transF.Update()

        glyphFilter = vtk.vtkVertexGlyphFilter()
        glyphFilter.SetInputData(transF.GetOutput())
        glyphFilter.Update()

        filename = d + "vtkFiles/" + "c_lev" + str(j) + "_geo" + str(i+1)

        writer = vtk.vtkPolyDataWriter()
        writer.SetFileName(filename + ".vtk")
        writer.SetInputData(glyphFilter.GetOutput())
        writer.Update()
        writer.Write()


