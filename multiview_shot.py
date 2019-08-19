import vtk
import pandas as pd
import math
import sys

base_dir = '/home/milad/osa_topol/'
base_dirw = '/home/milad/dataset/multiview/'
plydir = base_dir + 'polydata/'

maxx = 10
dtheta = 10

subdata = pd.read_csv(base_dir+'subx.lis', sep='\t', header=1)
nSub = subdata.shape[0]

for subjectIndex in range(nSub):
    name = subdata.loc[subjectIndex].record_id
    sev = subdata.loc[subjectIndex].OSAclass

    print('name: ', name)
    print('sev:', sev)

    if not math.isnan(sev):
        sev = int(sev)
        reader = vtk.vtkPLYReader()
        reader.SetFileName(plydir + name + '.ply')
        reader.Update()

        train_dir = ''
        val_dir = ''

        if sev == 1:
            train_dir = base_dirw + 'train/1/'
            val_dir = base_dirw + 'validation/1/'
        if sev == 2:
            train_dir = base_dirw + 'train/2/'
            val_dir = base_dirw + 'validation/2/'
        if sev == 3:
            train_dir = base_dirw + 'train/3/'
            val_dir = base_dirw + 'validation/3/'
        if sev == 4:
            train_dir = base_dirw + 'train/4/'
            val_dir = base_dirw + 'validation/4/'

        for imageIndex in range(-1*maxx, maxx):

            trans = vtk.vtkTransform()
            trans.RotateY(imageIndex*dtheta)

            transF = vtk.vtkTransformPolyDataFilter()
            transF.SetInputData(reader.GetOutput())
            transF.SetTransform(trans)
            transF.Update()

            # Visualize
            mapper = vtk.vtkPolyDataMapper()
            mapper.SetInputData(transF.GetOutput())

            actor = vtk.vtkActor()
            actor.SetMapper(mapper)

            renderer = vtk.vtkRenderer()
            renderWindow = vtk.vtkRenderWindow()
            renderWindow.SetAlphaBitPlanes(1)
            renderWindow.SetOffScreenRendering(1)
            renderWindow.AddRenderer(renderer)

            # renderWindowInteractor = vtk.vtkRenderWindowInteractor()
            # renderWindowInteractor.SetRenderWindow(renderWindow)

            renderer.AddActor(actor)
            renderer.SetBackground(1, 1, 1)

            renderWindow.Render()

            windowToImageFilter = vtk.vtkWindowToImageFilter()
            windowToImageFilter.SetInput(renderWindow)
            windowToImageFilter.SetScale(3)

            windowToImageFilter.SetInputBufferTypeToRGBA()

            windowToImageFilter.ReadFrontBufferOff()

            windowToImageFilter.Update()

            writer = vtk.vtkPNGWriter()
            writer.SetFileName(train_dir + name + '_' + str(imageIndex+maxx) + '.png')
            writer.SetInputConnection(windowToImageFilter.GetOutputPort())
            writer.Write()

            # renderWindow.Render()
            # renderer.ResetCamera()
            # renderWindow.Render()
            # renderWindowInteractor.Start()




