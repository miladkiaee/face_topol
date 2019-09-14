import vtk

from argparse import ArgumentParser

print('----------')
parser = ArgumentParser()
parser.add_argument("-i", "--input", default="", help="input polydata file name")

args = parser.parse_args()

reader = vtk.vtkPLYReader()
reader.SetFileName(args.input)
reader.Update()
pd = reader.GetOutput()

print("Number of points: ", pd.GetNumberOfPoints())

pd2 = vtk.vtkPolyData()

conn = vtk.vtkPolyDataConnectivityFilter()
conn.SetInputData(pd)
conn.InitializeSpecifiedRegionList()
conn.SetExtractionModeToSpecifiedRegions()
conn.AddSpecifiedRegion(0)
conn.Modified()
conn.Update()

n = conn.GetNumberOfExtractedRegions()

for i in range(1, n):

    conn.DeleteSpecifiedRegion(i-1)
    conn.Modified()
    conn.Update()
    conn.AddSpecifiedRegion(i)
    conn.Modified()
    conn.Update()
    print("Number of regions: ", conn.GetNumberOfExtractedRegions())

    pd2.DeepCopy(conn.GetOutput())

    clean = vtk.vtkCleanPolyData()
    clean.SetInputData(pd2)
    clean.Update()

    pd2 = clean.GetOutput()

    print("Number of points after extraction: ", pd2.GetNumberOfPoints())

    conn2 = vtk.vtkPolyDataConnectivityFilter()
    conn2.SetInputData(pd2)
    conn2.Update()

    print("Number of regions after extraction:", conn2.GetNumberOfExtractedRegions())

# writing the contours output
# writer = vtk.vtkPLYWriter()
# writer.SetFileName(args.input + "oneregion.ply")
# writer.SetInputData(pd2)
# writer.Update()
# writer.Write()
