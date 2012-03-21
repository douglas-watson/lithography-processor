#!/usr/bin/env python
# -*- coding: UTF8 -*-
#
#   image_loading.py - an example of loading a png image into an array, for
#   later processing 
#
#   AUTHOR: Douglas Watson <douglas@watsons.ch>
#
#   DATE: started on 19th March 2012
#
#   LICENSE: GNU GPL
#
#################################################

from pylab import *
import Image

# Load a png image. This example is a sort of bragg reflector in black and
# white, sketched up in Inkscape and hastily exported as PNG:

im = Image.open('dbr.png')

# The image is RGB; convert to greyscale:
im = im.convert('L')

# Convert to numpy array:

arr = asarray(im)

# And plot:
# The key here is to use the 'nearest' interpolation, or it will blurr
# transitions.

gray()
figure(1)
title("As loaded from image")
imshow(arr, interpolation='nearest', aspect='auto')

# simulate patterning:
#######################

# basic image parameters

Ny, Nx = arr.shape
Lx, Ly = 3, 1 # size of picture in microns
x = linspace(-Lx/2, Lx/2, Nx)
y = linspace(-Ly/2, Ly/2, Ny)

# change the array to a boolean

arr_scaled = arr / max(flatten(arr))
arr_bool = arr_scaled.astype('bool')

print 'x\ty\texpose'

figure()
for i in range(Nx):
    for j in range(Ny):
        if arr_bool[j, i]:
            # only move if necessary
            # print "%.6f %.6f" % (x[i], y[j]), arr_bool[j, i]
            plot(x[i], y[j], 'k.')
show()
