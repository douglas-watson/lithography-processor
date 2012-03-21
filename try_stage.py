#!/usr/bin/env python
# -*- coding: UTF8 -*-
#
#   try_stage.py - Just playing around with my stage.py module. 
#
#   AUTHOR: Douglas Watson <douglas@watsons.ch>
#
#   DATE: started on 19 March 2012
#
#   LICENSE: GNU GPL
#
#################################################

import logging
from controllers import Stage

logging.basicConfig(level=logging.DEBUG)

c = Stage(port=
            '/dev/serial/by-id/usb-FTDI_FT232R_USB_UART_MMC-100-V102-if00-port0')

if __name__ == '__main__':
    
    c.move_abs(0, 0, 0)
    c.move_abs(1, 1, 1)
    c.move_abs(0, 0, 0)

    c.con.close()
    
