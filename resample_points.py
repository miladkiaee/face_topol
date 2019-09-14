import vtk
import math


def resample_points(poly):

    vs = vtk.vtkStripper()
    vs.SetInputData(poly)
    vs.JoinContiguousSegmentsOn()
    vs.Update()

    cpd2 = vtk.vtkCleanPolyData()
    cpd2.SetInputData(vs.GetOutput())
    cpd2.Update()

    bc = cpd2.GetOutput().GetBounds()
    yl = bc[3] - bc[2]
    zl = bc[5] - bc[4]
    yzl = math.sqrt(yl**2 + zl**2)

    spline = vtk.vtkCardinalSpline()
    spline.SetLeftConstraint(2)
    spline.SetLeftValue(0)
    spline.SetRightConstraint(2)
    spline.SetRightValue(0)

    sp_filter = vtk.vtkSplineFilter()
    sp_filter.SetInputData(cpd2.GetOutput())
    num_points = poly.GetNumberOfPoints()
    sp_filter.SetNumberOfSubdivisions(num_points * 40)
    sp_filter.SetSpline(spline)
    sp_filter.Update()

    def_tol = yzl/100

    print('bound diag = ', yzl)
    print('max p dist = ', def_tol)

    cpd = vtk.vtkCleanPolyData()
    cpd.SetInputData(sp_filter.GetOutput())
    cpd.ToleranceIsAbsoluteOn()
    cpd.PointMergingOn()
    cpd.ConvertStripsToPolysOn()
    cpd.GetConvertLinesToPoints()
    cpd.ConvertPolysToLinesOn()
    cpd.ToleranceIsAbsoluteOn()
    cpd.SetAbsoluteTolerance(def_tol)
    cpd.Update()

    return cpd.GetOutput()

