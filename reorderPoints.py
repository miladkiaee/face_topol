import vtk
import sys


def initial_reorder(poly, option):

    num_cells = poly.GetNumberOfCells()
    closed = True
    prev_id = -1
    ipid = -1
    cell_ids = vtk.vtkIdList()

    for i in range(num_cells):
        # for each cell get point id of the two sides
        point_id1 = poly.GetCell(i).GetPointId(0)

        if point_id1 == prev_id:
            point_id1 = poly.GetCell(i).GetPointId(1)

        prev_id = point_id1

        # cell ids for firs point of the cell
        big = 1000
        xx = big
        poly.GetPointCells(point_id1, cell_ids)
        nc = cell_ids.GetNumberOfIds()

        if nc == 1:
            # print("curve is open at point", pointId1)
            ipid = point_id1
            closed = False
            p = [0, 0, 0]
            poly.GetPoint(point_id1, p)
            if option == "z" or option == "y":
                xx = p[0]
            if option == "x":
                xx = p[2]
            if xx < big:
                big = xx
                point_id = point_id1
        if (nc == 0) or (nc > 2):
            print("number of cells for ", point_id1, " is ", nc)
            sys.exit("probably there is branching")

    if closed:
        # print("curve is closed")
        # for closed curve we want to start at point with smallest x??
        # if in zy plane we want smallest z
        point_id = 0
        p = [0, 0, 0]
        big = 1000
        np = poly.GetNumberOfPoints()
        zz = big

        for i in range(np):
            poly.GetPoint(i, p)

            if option == "z" or option == "y":
                zz = p[0]
            if option == "x":
                zz = p[2]

            if zz < big:
                big = zz
                point_id = i

        ipid = point_id

    return ipid


def reorder(poly, ipid):

    opid = vtk.vtkIdList()
    opid.InsertNextId(ipid)
    cell_ids = vtk.vtkIdList()
    num_points = poly.GetNumberOfPoints()

    for i in range(num_points - 2):

        next_point_id = opid.GetId(i)
        poly.GetPointCells(next_point_id, cell_ids)

        if cell_ids.GetNumberOfIds() > 0:

            cell_id = cell_ids.GetId(0)
            # check if this cell is the correct one by checking its points
            point_id1 = poly.GetCell(cell_id).GetPointId(0)
            point_id2 = poly.GetCell(cell_id).GetPointId(1)

            if opid.IsId(point_id1) != -1 and \
                    opid.IsId(point_id2) != -1:

                cell_id = cell_ids.GetId(1)
                point_id1 = poly.GetCell(cell_id).GetPointId(0)
                point_id2 = poly.GetCell(cell_id).GetPointId(1)

                if opid.IsId(point_id1) != -1 \
                        and opid.IsId(point_id2) != -1:
                    break
            else:
                point_id1 = poly.GetCell(cell_id).GetPointId(0)
                point_id2 = poly.GetCell(cell_id).GetPointId(1)

            if opid.IsId(point_id1) != -1:
                point_id = point_id2
                if opid.IsId(point_id2) != -1:
                    print("this is not right! second check not passed!")
                else:
                    opid.InsertNextId(point_id2)
            else:
                opid.InsertNextId(point_id1)

    return opid
