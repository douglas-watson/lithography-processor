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
from numpy import array, asarray, cross
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


if __name__ == '__main__':
    O = array([0, 0, 0])
    A = array([1, 0, 0])
    B = array([0, 1, 0])

    print get_referential(O, A, B)
