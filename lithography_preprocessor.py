#!/usr/bin/env python
# -*- coding: UTF8 -*-
#
#   lithography_preprocessor.py - preprocess a PNG image for 2-photon 
#     lithography 
#
#     this program allows the user to choose a png image to be written, define
#     the wafer rotation and origin, and output a series of coordinates to be
#     exposed.
#
#   AUTHOR: Douglas Watson <douglas@watsons.ch>
#
#   DATE: started on 21 March 2012
#
#   LICENSE: GNU GPL
#
#################################################

'''
lithography_preprocessor.py
---------------------------

This little piece of software is designed to process png images into position
instructions for the Loncar lab's home-made two-photon lithography machine.

Briefly, the input is a black-and-white png image (and user-defined
dimensions), and the output are locations of pixels to expose. The software
performs two functions. The first is to import a PNG picture and convert it
into a 2D array of true-false values (true being 'expose', false being 'do not
expose'). The second is to assign, for each of these pixels, a spatial
position, in the coordinate system of the stage, and from there output the 3D
coordinates of each point to be exposed.

The interface is built using Traits UI. Most of this file is dedicated to
defining the interface. The actual operations on pictures are found in
lithography_toolkit.py (for importing and conversion of pictures, coordinate transforms and so on).

'''

__title__ = 'Lithography preprocessor'
__version__ = '0.1 alpha'

import os

# Select wx backend
from enthought.etsconfig.api import ETSConfig
ETSConfig.toolkit = 'wx'

# Math and plotting
from mpl_figure_editor import MPLFigureEditor, Figure
from mpl_toolkits.mplot3d import Axes3D
from matplotlib import cm
from numpy import array, transpose, r_, c_, zeros, ones, savetxt, size

# GUI
import wx
from enthought.traits.api import HasTraits, Float, Instance, Button, String, \
        File, Trait, Array, on_trait_change
from enthought.traits.ui.api import View, Item, Group, HGroup, Spring, HSplit, \
        Label
import enthought.traits.ui
from enthought.mayavi.core.api import PipelineBase
from enthought.mayavi.core.ui.api import MayaviScene, SceneEditor, \
        MlabSceneModel
from enthought.util.wx import dialog


# Application logic
import logging
from lithography_toolkit import path_to_array, get_referential, \
        get_black_points, transform_coordinates

##############################
# Helpers 
##############################

# Note that I do not distinguish vector and point.
Vector = Array(shape=(3,), dtype='float')

def nonzero_validator(object, name, value):
    ''' Verify that value is non-zero. '''

    # Coerce to float:
    value = float(value)

    if value == 0:
        raise ValueError("%s cannot be zero" % name)
    else:
        return float(value)

##############################
# Classes 
##############################

class Preview2D(HasTraits):
    
    '''
    A matplotlib plot. Used both for the 2D and 3D plots.

    '''

    figure = Instance(Figure, ())

    traits_view = View(Item('figure', editor=MPLFigureEditor(),
                            width=400,
                            height=300,
                            show_label=False),
                        resizable=True,
                        )

    def __init__(self):
        super(Preview2D, self).__init__()

        self.ax = self.figure.add_subplot(111)
        self.ax.set_aspect('equal')
        self.ax.hold(False)

    def plot_array(self, array, length, width):
        ''' Draw the array, with appropriately scaled axes '''

        lx = length/2
        ly = width/2
        self.ax.imshow(array, cmap=cm.gray, interpolation='nearest',
                      extent=[-lx, lx, -ly, ly])
        try:
            wx.CallAfter(self.figure.canvas.draw)
        except AttributeError, e:
            # Probably been called before the canvas was instantiated
            logging.error('Plot_array called too early')
        except:
            raise

class Preview3D(HasTraits):

    '''
    A 3D matplotlib plot
    '''

    scene = Instance(MlabSceneModel, ())
    points = Instance(PipelineBase)  # O, A, and B
    axes = Instance(PipelineBase)    # wafer referential axes
    picture = Instance(PipelineBase) # The image to draw

    traits_view = View(Item('scene', editor=SceneEditor(
        scene_class=MayaviScene),
        height=300, width=400, show_label=False),
        resizable=True,
    )

    # @on_trait_change('scene.activated')
    def update_points(self, O, A, B):
        Xs, Ys, Zs = c_[O, A, B]
        if self.points is None:
            self.points = self.scene.mlab.points3d(Xs, Ys, Zs, 
                                           color=(0,0,1), scale_factor=0.1)
        else:
            self.points.mlab_source.set(x=Xs, y=Ys, z=Zs)

    def update_axes(self, O, eX, eY, eZ):
        ''' Update the rendering of the wafer's axes 
        
        ARGUMENTS:
        O (Vector) - origin of the wafer's coordinate system
        eX, eY, eZ (Vector) - orthonormal basis

        '''

        # reshape:
        Ox, Oy, Oz = c_[O, O, O] # coordinates of origin
        Ex, Ey, Ez = c_[eX, eY, eZ] # stack of Xs coords, Ys, then Zs
        if self.axes is None:
            self.axes = self.scene.mlab.quiver3d(Ox, Oy, Oz, Ex, Ey, Ez,
                                                mode='arrow')
        else:
            self.axes.mlab_source.set(x=Ox, y=Oy, z=Oz, u=Ex, v=Ey, w=Ez)

    def update_picture(self, X, Y, Z, pixel_size=1):
        ''' Draw the points to be exposed

        ARGUMENTS:
        X, Y, Z (1D numpy arrays) - coordinates of points to expose

        '''

        point_size = pixel_size * ones(len(X))

        if self.picture is None:
            self.picture = self.scene.mlab.points3d(X, Y, Z, point_size,
                                                    scale_factor=1)
            # frame = self.scene.mlab.outline(self.picture)
        else:
            self.picture.mlab_source.set(x=X, y=Y, z=Z, scalars=point_size)

class Referential(HasTraits):
    ''' 
    Defines three points of the wafer plane in the referential of the stage.

    These are used to calculate the orientation of the wafer, relative to the
    stage, and use that to establish a 'wafer coordinate system', to convert
    points on the wafer plane to points in the space of the stage.

    There's a lot of messing about with transposing and stuff, mostly because
    it's convenient to have column vectors in the graphical interface

    '''

    # The wafer plane is given by three point, O, A, and B
    O = Vector
    A = Vector
    B = Vector

    # The following three vectors define the orientation. Origin is O.
    eX = Vector
    eY = Vector
    eZ = Vector

    preview = Instance(Preview3D)

    recalculate = Button

    traits_view = View(
        Group(
            Group(Item(name='O'),
                  Item(name='A'),
                  Item(name='B'),
                  show_border=False,
                  orientation='horizontal'),
            Item(name='recalculate', show_label=False),
            label='Wafer reference points [um]',
            show_border=True,),
    )

    def __init__(self, *args, **kwargs):
        super(Referential, self).__init__(*args, **kwargs)
        self.O = array([0., 0., 0.])
        self.A = array([1., 0., 0.])
        self.B = array([0., 1., 0.])

        self._recalculate_fired()

    def _recalculate_fired(self):
        self.eX, self.eY, self.eZ = get_referential(self.O, self.A, self.B)

        self.update_preview()

    def update_preview(self):
        ''' Update the 3D preview: plot O, A, and B, as well as eX, eY, eZ '''

        self.preview.update_axes(self.O, self.eX, self.eY, self.eZ)
        self.preview.update_points(self.O, self.A, self.B)

class Picture(HasTraits):
    '''
    Defines the image to be written, and extra information (size).

    '''

    path = File('/home/douglas/research/lno/lithography/' +
                  'raster_lithography/220px-Tux.png')
    # TODO set the size automatically based on number of pixels
    # It might make more sense to give a 'pixel size' instead.
    pixel_size = Trait(1.0, nonzero_validator) # in um
    pixel_spacing = Trait(1.0, nonzero_validator) # in um

    width = Trait(10.0, nonzero_validator)  # in um
    height = Trait(10.0, nonzero_validator) # in um

    data = Array(dtype='int') # 2D array of 1s and 0s
    stage_ref = Instance(Referential)

    preview2D = Instance(Preview2D)
    preview3D = Instance(Preview3D)

    update2D = Button(label='Update 2D')
    update3D = Button(label='Update 3D')

    X = Array(dtype='float')
    Y = Array(dtype='float')
    Z = Array(dtype='float')

    traits_view = View(
                Group(Item(name='path'),
                      Item(name='pixel_spacing', label='Pixel spacing [um]'),
                      Item(name='pixel_size', label='Pixel size [um]'),
                      Group(
                          Spring(),
                          Item(name='update2D', show_label=False),
                          Item(name='update3D', show_label=False),
                          orientation='horizontal'),
                      label='Picture configuration',
                      show_border=True,
                     )
                    )

    def _update2D_fired(self):
        self.update_preview2d()

    def _update3D_fired(self):
        self.update_preview3d()

    @on_trait_change('pixel_spacing', 'pixel_size')
    def update_dimensions(self):
        ''' Compute figure dimensions based on picture size '''

        logging.debug("Updating dimensions. Pixel size %f, spacing %f" % \
                     (self.pixel_size, self.pixel_spacing))

        if size(self.data) != 0: # Only if data has been loaded
            Ny, Nx = self.data.shape # number of pixels
            self.width = (Nx - 1) * self.pixel_spacing  # between centres
            self.height = (Ny - 1) * self.pixel_spacing # idem
            self.update_preview2d()
            self.update_preview3d()

    @on_trait_change('path')
    def update_data(self):
        ''' Read path and update the data Trait '''

        try:
            self.data = path_to_array(self.path)
        except IOError, e:
            dialog.error(None, "Invalid image file.")
        else:
            self.update_dimensions() # This will also update 2D and 3D.

    @on_trait_change('width', 'height')
    def update_preview2d(self):
        ''' Update the 2D image preview. '''

        if len(self.data) == 0: # Hasn't been initialised yet
            self.data = path_to_array(self.path)
            self.update_dimensions()
        self.preview2D.plot_array(self.data, self.width, self.height)

    def update_preview3d(self):
        ''' Update the 3D preview.

        This functions first finds the black pixels, then transforms the
        coordinates to stage coordinates, them updates the preview.

        '''

        if len(self.data) == 0:
            return

        O, eX, eY, eZ = self.stage_ref.O, self.stage_ref.eX, \
                self.stage_ref.eY, self.stage_ref.eZ

        x, y = get_black_points(self.data, self.width,
                                self.height)
        X, Y, Z = transform_coordinates(x, y, zeros(len(x)), O, eX, eY, eZ)
        self.X, self.Y, self.Z = X, Y, Z

        self.preview3D.update_picture(X, Y, Z, self.pixel_size)

class MainWindow(HasTraits):
    '''
    Contains all the components of the interface:
        - A column of config (picture file and size, referential settings)
        - A 2D preview of the image to draw, in the referential of the wafer
        - A 3D preview of the points to expose, in the ref. of the stage
        - A file path to export the points to
        - An export button, to export the coordinates of the points to expose

    '''

    export_path = File(os.path.abspath(os.curdir) + '/expose_points.dat')
    export_data = Button

    image_config = Instance(Picture)
    stage_config = Instance(Referential)
    preview2D = Instance(Preview2D)
    preview3D = Instance(Preview3D)

    traits_view = View(
        HSplit(
            Group(
                Item('image_config', style='custom', show_label=False,
                     springy=True),
                Item('stage_config', style='custom', show_label=False,
                    springy=True),
                Group(
                    Item('export_path', show_label=True, springy=False),
                    Item('export_data', show_label=False, springy=False),
                    label='Export points',
                    show_border=True,
                ),
            ),
            Item('preview2D', style='custom', show_label=False),
            Item('preview3D', style='custom', show_label=False),
        ),
        resizable=True,
        title="%s v. %s" % (__title__, __version__),
    )

    def _export_data_fired(self):
        ''' Export the points to expose to the specified file. ''' 

        print "Exporting data to %s" % self.export_path
        im = self.image_config
        points = c_[im.X, im.Y, im.Z]

        if os.path.exists(self.export_path):
            # make sure user wants to overwrite
            answer = dialog.confirmation(None, 
                                         'File already exists. Overwrite?')
            if answer == wx.ID_NO:
                return # exit function before saving.

        savetxt(self.export_path, points, fmt='%.6f')


##############################
# Main program 
##############################

if __name__ == '__main__':

    logging.basicConfig(level=logging.DEBUG)

    # Create objects saved between several components
    preview2D = Preview2D()
    preview3D = Preview3D()
    referential = Referential(preview=preview3D)
    image_config = Picture(preview2D=preview2D, preview3D=preview3D,
                           stage_ref=referential)

    mainwindow = MainWindow(image_config=image_config, 
                            stage_config=referential,
                            preview2D=preview2D, 
                            preview3D=preview3D
                           )

    mainwindow.configure_traits()
