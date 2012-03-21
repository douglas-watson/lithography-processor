#!/usr/bin/env python
# -*- coding: UTF8 -*-
#
#   stage.py - Python library to interface with the Micos MMC-100 stage
#
#   AUTHOR: Douglas Watson <douglas@watsons.ch>
#
#   DATE: started on 19 March 2012
#
#   LICENSE: GNU GPL
#
#################################################

import serial
import time
import logging

##############################
# Configuration
##############################

# Define
x_axis = 3
y_axis = 1
z_axis = 2

##############################
# Class definitions
##############################

def needs_serial(original_method):

    ''' Decorator for methods that need serial communication.

    Decorates the method with functions (such as error handling or delays) that
    are common to all methods sending serial commands.
    '''

    def decorated_method(*args, **kwargs):

        # wait a bit before executing the method.
        time.sleep(3) # time in seconds
        return_value = original_method(*args, **kwargs) 

        return return_value

    return decorated_method
        

class Stage:

    ''' Represents a connection to the stage 

    ARGUMENTS
    port (string) - the port to which the controller is connected

    ATTRIBUTES
    self.ser (serial.Serial) - actual connection to the controller.
    
    '''

    def __init__(self, port):
        # TODO implement error handling
        # 'con' stands for controller or connection. As you wish.
        self.con = serial.Serial(port=port, baudrate=38400, parity='N', 
                                 bytesize=8, stopbits=1)

    @needs_serial
    def write(self, string):

        ''' Send 'string' to the stage. Automatically append carriage return.

        This is just a wrapper around self.con.write(), to cut down on
        repetition in following methods.

        '''

        logging.info("Sending: " + string)
        return self.con.write(string + '\r')

    def move_abs(self, x=None, y=None, z=None):
        ''' Move the stage to position (x, y, z) [mm], somewhat synchronously. 
        
        If any of the coordinates are None, no instruction will be sent for
        that axis '''

        self.write('%dMSA%.6f; %dMSA%.6f; %dMSA%.6f' % (x_axis, x,
                                                             y_axis, y,
                                                             z_axis, z))
        self.write('0RUN')

    def move_rel(x, y, z):
        pass

    def read_pos(x, y, z):
        pass

    def clear_errors(self):
        ''' Clear errors in all three axes. '''

        for ax in (x_axis, y_axis, z_axis):
            self.write('%dERR?' % ax)

class Shutter:

    pass
