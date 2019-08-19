import vtk 
import numpy as np 
import math

from argparse import ArgumentParser

parser = ArgumentParser()

parser.add_argument("-i1", "--input1", default= "", help="input1 file name")
parser.add_argument("-i2", "--input2", default= "", help="input2 file name")
parser.add_argument("-o", "--output", default="", help="calculate the distance")

args = parser.parse_args()

# read two input vtk
reader1 = vtk.vtkPLYReader()
reader1.SetFileName(args.input1)
reader1.Update()

pd1 = reader1.GetOutput()

reader2 = vtk.vtkPLYReader()
reader2.SetFileName(args.input2)
reader2.Update()

pd2 = reader2.GetOutput()

normals1 = vtk.vtkPolyDataNormals()
normals1.SetInputData(pd1)
normals1.Update()
# normalspd1 = normals.GetOutput()

normals2 = vtk.vtkPolyDataNormals()
normals2.SetInputData(pd2)
normals2.Update()
normalspd2 = normals2.GetOutput()

# n = normalspd1.GetNumberOfPoints()

arrayIndex = 1

for tupleIdx in range(10):
    # t = pd.GetPointData().GetArray(arrayIndex).GetTuple(tupleIdx)
    # t0 = t->GetComponent(tupleIdx, 0)
    # t1 = t->GetComponent(tupleIdx, 1)
    # t2 = t->GetComponent(tupleIdx, 2)
    mag = math.sqrt(t0*t0 + t1*t1 + t2*t2)
    t0 = t0/mag
    t1 = t1/mag
    t2 = t2/mag
    # pd.GetPointData().GetArray(arrayIndex).SetComponent(tupleIdx, 0, t0)
    # pd.GetPointData().GetArray(arrayIndex).SetComponent(tupleIdx, 1, t1)
    # pd.GetPointData().GetArray(arrayIndex).SetComponent(tupleIdx, 2, t2)

    




