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
