import vtk
import sys


def initial_reorder(poly, option):

    num_points = poly.GetNumberOfPoints()
    ip_id = -1
    cell_ids = vtk.vtkIdList()
    small = 1000
    tmp = 0

    for i in range(num_points):

        poly.GetPointCells(i, cell_ids)
        nc = cell_ids.GetNumberOfIds()
        p = [0, 0, 0]
        poly.GetPoint(i, p)

        if nc == 1:
            if option == "z" or option == "y":
                tmp = p[0]
            if option == "x":
                tmp = p[2]
            if tmp < small:
                small = tmp
                ip_id = i

        if (nc == 0) or (nc > 2):
            print("number of cells for ", i, " is ", nc)
            sys.exit("probably there is branching")

    return ip_id


def reorder(poly, ip_id):

    ordered_p_ids = vtk.vtkIdList()
    ordered_p_ids.InsertNextId(ip_id)
    prev_nei_cell_ids = vtk.vtkIdList()
    num_points = poly.GetNumberOfPoints()

    for i in range(num_points - 2):
        prev_point_id = ordered_p_ids.GetId(i)
        poly.GetPointCells(prev_point_id, prev_nei_cell_ids)
        nnc = prev_nei_cell_ids.GetNumberOfIds()

        if nnc == 1:
            cell_id = prev_nei_cell_ids.GetId(0)
            p_id1 = poly.GetCell(cell_id).GetPointId(0)
            p_id2 = poly.GetCell(cell_id).GetPointId(1)

            if ordered_p_ids.IsId(p_id1) == -1:
                ordered_p_ids.InsertNextId(p_id1)
            elif ordered_p_ids.IsId(p_id2) == -1:
                ordered_p_ids.InsertNextId(p_id2)
            if ordered_p_ids.IsId(p_id1) == -1 and ordered_p_ids.IsId(p_id2) == -1:
                sys.exit("weird problem!")

        if nnc > 1:
            cell_id = prev_nei_cell_ids.GetId(0)
            p_id1 = poly.GetCell(cell_id).GetPointId(0)
            p_id2 = poly.GetCell(cell_id).GetPointId(1)

            if ordered_p_ids.IsId(p_id1) != -1 and ordered_p_ids.IsId(p_id2) != -1:
                cell_id = prev_nei_cell_ids.GetId(1)
                p_id1 = poly.GetCell(cell_id).GetPointId(0)
                p_id2 = poly.GetCell(cell_id).GetPointId(1)
                if ordered_p_ids.IsId(p_id1) != -1 and ordered_p_ids.IsId(p_id2) != -1:
                    break
            else:
                p_id1 = poly.GetCell(cell_id).GetPointId(0)
                p_id2 = poly.GetCell(cell_id).GetPointId(1)

            if ordered_p_ids.IsId(p_id1) != -1:
                if ordered_p_ids.IsId(p_id2) != -1:
                    print("this is not right! second check not passed!")
                else:
                    ordered_p_ids.InsertNextId(p_id2)
            else:
                ordered_p_ids.InsertNextId(p_id1)

        if nnc > 2:
            sys.exit("problem with branching!")

    return ordered_p_ids
