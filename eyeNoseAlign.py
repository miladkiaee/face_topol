import pandas as pd
import vtk
import numpy as np
from argparse import ArgumentParser

import os

parser = ArgumentParser()
parser.add_argument("-p", "--plydir", default="", help="input polydata directory")
parser.add_argument("-n", "--eyenose", default="", help="input eye and nose information file location")
args = parser.parse_args()

data = pd.read_csv(args.eyenose)

data.set_index('subject', inplace=True)

for sub, row in data.iterrows():
    filepath = args.plydir + sub + ".ply"

    if os.path.isfile(filepath):
        unique_id = sub
        print("aligning ", unique_id)

        leftId = row[0]
        rightId = row[1]
        noseId = row[2]

        reader = vtk.vtkPLYReader()
        reader.SetFileName(filepath)
        reader.Update()

        pld = reader.GetOutput()

        noseXYZ = [0, 0, 0]
        leftXYZ = [0, 0, 0]
        rightXYZ = [0, 0, 0]

        print("leftId : ", leftId)
        print("rightId : ", rightId)
        print("noseId : ", noseId)

        pld.GetPoints().GetPoint(noseId, noseXYZ)
        pld.GetPoints().GetPoint(leftId, leftXYZ)
        pld.GetPoints().GetPoint(rightId, rightXYZ)

        print("leftCoord : ", leftXYZ)
        print("rightCoord : ", rightXYZ)
        print("noseCoord : ", noseXYZ)

        center = np.add(rightXYZ, leftXYZ)/2
        ex = np.add(rightXYZ, np.negative(leftXYZ))
        ex = ex/np.linalg.norm(ex)
        ey = np.add(center, np.negative(noseXYZ))
        ey = ey/np.linalg.norm(ey)
        # cross product to calculate a normal vector to plane of ex and ey
        ez = np.cross(ex, ey)
        ez = ez/np.linalg.norm(ez)

        rotM = vtk.vtkMatrix4x4()
        rotM.Identity()

        for i in range(0, 3):
            rotM.SetElement(0, i, ex[i])
            rotM.SetElement(1, i, ey[i])
            rotM.SetElement(2, i, ez[i])

        trans = vtk.vtkTransform()
        trans.Translate(-center[0], -center[1], -center[2])
        # trans.PostMultiply()
        # trans.Concatenate(rotM)

        # implement the transformation
        transF = vtk.vtkTransformPolyDataFilter()
        transF.SetInputData(pld)
        transF.SetTransform(trans)
        transF.Update()

        pld = transF.GetOutput()

        # transform object stores the transformation information
        trans2 = vtk.vtkTransform()
        # trans2.Translate(-center[0], -center[1], -center[2])
        trans2.PostMultiply()
        trans2.Concatenate(rotM)

        # transform filter performs the actual operation
        transF2 = vtk.vtkTransformPolyDataFilter()
        transF2.SetInputData(pld)
        transF2.SetTransform(trans2)
        transF2.Update()

        pld = transF2.GetOutput()

        writer = vtk.vtkPLYWriter()
        writer.SetInputData(pld)
        writer.SetFileName(args.plydir + sub + "Aligned.ply")
        writer.SetFileTypeToASCII()
        writer.Write()

    else:
        print(filepath, " doesnt exist!")
