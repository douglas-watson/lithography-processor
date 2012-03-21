#!/usr/bin/env python
# -*- coding: UTF8 -*-
#
#   png_toolkit.py - the PNG manipulation part of my lithography preprocessor
#
#   AUTHOR: Douglas Watson <douglas@watsons.ch>
#
#   DATE: started on 21 March 2012
#
#   LICENSE: GNU GPL
#
#################################################

import Image
from numpy import array, asarray

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
