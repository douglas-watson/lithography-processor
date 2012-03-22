#!/usr/bin/env python
# -*- coding: UTF8 -*-
#
#   lithography_toolkit.py - the application logic behind Lithography
#       Preprocessor.
#
#   AUTHOR: Douglas Watson <douglas@watsons.ch>
#
#   DATE: started on 21 March 2012
#
#   LICENSE: GNU GPL
#
#################################################

'''
Lithography Toolkit
--------------------

This is essentially the library that powers the Lithography Preprocessor. The
functions requiring actual calculations or data manipulation are described
here, and simply called from lithography_preprocessor.py, which mostly defines
the user interface.

'''

import Image
from numpy import array, asarray, cross, linspace, meshgrid
from numpy.linalg import norm

def path_to_array(image_path):
    ''' Load PNG image at 'image_path', return a 2D array of ones or zeroes.
    
    This is of course an image of either black or white pixels, where the black
    pixels are meant to be exposed.

    '''
    im = Image.open(image_path)
    arr = asarray(im.convert('L')) # convert to black and white

    # Scale values between 0 and 1, round off to int
    arr_scaled = arr.astype('float') / arr.max()
    arr_bin = arr_scaled.round().astype('int')

    # I call it 'bin', because pixels are either 1 or 0.
    return arr_bin

def get_referential(O, A, B):
    ''' Returns the wafer's referential (eX, eY, eZ) in stage's coordinates. 

    By convention, all uppercase points or vectors are expressed in the
    coordinate system of the stage.

    ARGUMENTS
    O, A, B (Vector) - Three points defining the wafer plane. Note that I do
        not distinguish vector and point.

    '''

    # For explanations, see 'coordinate_transformation.jpg'
    OA = A - O
    eX = OA / norm(OA)

    OB = B - O
    v = OB / norm(OB)
    eZ = cross(eX, v) / norm(cross(eX, v))

    eY = cross(eZ, eX)

    return eX, eY, eZ

def get_black_points(data, width, height):
    ''' Returns the x and y coordinates of all black pixels in the image.

    Returns two one-dimensional arrays of coordinates, one for x, one for y.
    These are expressed in the wafer referential.The origin is placed at the
    centre of the image. Extent and units are determined by 'width' and
    'height'.

    ARGUMENTS
    array (2D numpy array) - array of 1s and 0s, as returned by path_to_array.
        Black pixels are 0s.
    width (float) - width of the image in the desired units.
    height (float) - height of the image in the desired units.

    '''

    # Create coordinates
    Ny, Nx = data.shape
    x = linspace(-width/2, width/2, Nx)
    y = linspace(height/2, -height/2, Ny) # note inverted signs, y is upwards
    xx, yy = meshgrid(x, y)

    # Find black pixels
    black = data == 0
    black_x = xx[black]
    black_y = yy[black]

    return black_x, black_y # no need to flatten apparently

def transform_coordinates(x, y, z, O, eX, eY, eZ):
    ''' Return stage coordinates X, Y, Z from wafer coordinates x, y, z.

    x, y, and z must be the same shape. Point O and orthonormal basis eX,
    eY, eZ define the origin and orientation of the wafer coordinate system,
    expressed in stage coordinates. The function returns array X, Y, and Z of
    same shape as x, y, and z.

    ARGUMENTS
    x, y, z (numpy arrays) - points to be transformed
    O (Vector) - origin of the wafer coordinate system
    eX, eY, eZ (Vector) - orthonormal basis defining the wafer orientation

    RETURNS
    X, Y, Z (numpy arrays) - coordinates in the stage referential.

    '''

    X = O[0] + x * eX[0] + y * eY[0] + z * eZ[0]
    Y = O[1] + x * eX[1] + y * eY[1] + z * eZ[1]
    Z = O[2] + x * eX[2] + y * eY[2] + z * eZ[2]

    return X, Y, Z

if __name__ == '__main__':

    arr = array([[1, 1, 1],
                 [0, 1, 1],
                 [1, 0, 1]])

    width = 2
    height = 4

    x, y = get_black_points(arr, width, height) 
    print x, y
