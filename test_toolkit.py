#!/usr/bin/env python
# -*- coding: UTF8 -*-
#
#   test_toolkit.py - Test the lithography toolkit. Use with Nose.
#
#   AUTHOR: Douglas Watson <douglas@watsons.ch>
#
#   DATE: started on 21 March 2012
#
#   LICENSE: GNU GPL
#
#################################################

import nose

from numpy import all
from lithography_toolkit import *

def test_get_referential():
    ''' Make sure the calculated referential makes sense. '''

    O = array([0, 0, 0])
    A = array([1, 0, 0])
    B = array([0, 1, 0])

    eX, eY, eZ = get_referential(O, A, B)

    assert all(eX == array([1, 0, 0]))
    assert all(eY == array([0, 1, 0]))
    assert all(eZ == array([0, 0, 1]))

    # Not normalised:
    O = array([0, 0, 0])
    A = array([2, 0, 0])
    B = array([0, 1, 0])

    eX, eY, eZ = get_referential(O, A, B)

    assert all(eX == array([1, 0, 0]))
    assert all(eY == array([0, 1, 0]))
    assert all(eZ == array([0, 0, 1]))

    # Diagonal:
    O = array([0, 0, 0])
    A = array([2, 0, 0])
    B = array([2, 1, 0])

    eX, eY, eZ = get_referential(O, A, B)

    assert all(eX == array([1, 0, 0]))
    assert all(eY == array([0, 1, 0]))
    assert all(eZ == array([0, 0, 1]))

    # Off-center origin:
    O = array([0, 1, 0])
    A = array([1, 1, 0])
    B = array([0, 2, 0])

    eX, eY, eZ = get_referential(O, A, B)

    assert all(eX == array([1, 0, 0]))
    assert all(eY == array([0, 1, 0]))
    assert all(eZ == array([0, 0, 1]))

def test_get_black_points():

    ''' Make sure the proper coordinates are returned by get_black_points() '''

    arr = array([[1, 1, 1],
                 [0, 1, 1],
                 [1, 0, 1]])

    width = 2   # extend from -1 to 1 
    height = 4  # extend from -2 to 2

    x, y = get_black_points(arr, width, height) 
    
    assert all(x == array([-1, 0]))
    assert all(y == array([0, -2]))

def test_transform_coordinates():
    ''' Make sure the coordinates are transformed right '''

    P1 = array([1, 1, 1])
    P2 = array([0, 0, 0])

    # Simple translation of the origin
    O = array([1, 1, 1])
    eX = array([1, 0, 0])
    eY = array([0, 1, 0])
    eZ = array([0, 0, 1])

    X1, Y1, Z1 = transform_coordinates(P1[0], P1[1], P1[2], O, eX, eY, eZ)
    X2, Y2, Z2 = transform_coordinates(P2[0], P2[1], P2[2], O, eX, eY, eZ)

    assert (X1, Y1, Z1) == (2, 2, 2)
    assert (X2, Y2, Z2) == (1, 1, 1)
    
    # Simple 90 degree of the wafer around ez:
    O = array([0, 0, 0])
    eX = array([0, 1, 0])
    eY = array([-1, 0, 0])
    eZ = array([0, 0, 1])

    X1, Y1, Z1 = transform_coordinates(P1[0], P1[1], P1[2], O, eX, eY, eZ)
    X2, Y2, Z2 = transform_coordinates(P2[0], P2[1], P2[2], O, eX, eY, eZ)

    assert (X1, Y1, Z1) == (-1, 1, 1)
    assert (X2, Y2, Z2) == (0, 0, 0)
