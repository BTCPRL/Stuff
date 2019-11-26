#!/usr/bin/env python
# coding=utf-8
# requires lifxlan to be installed (https://github.com/mclarkk/lifxlan)

import os
import subprocess
import sys
import time
from time import sleep

from lifxlan import LifxLAN
from lifxlan.light import Light

# Paths
_BLOCK_FILE_ = '/home/pi/Dev/SmartHome/office_lamp_block'

# Office Lamp data
_office_lamp_MAC_ = 'd0:73:d5:3e:44:c3'

# Colors
RED = [65535, 65535, 65535, 3500]
RED2 = [65535, 65535, 30000, 3500]
GREEN = [16173, 65535, 65535, 3500]
GREEN_SOFT = [16173, 65535, 40000, 3500]
CYAN = [29814, 65535, 65535, 3500]
CYAN_SOFT = [29814, 65535, 30000, 3500]
BLUE = [43634, 65535, 65535, 3500]
PURPLE = [50486, 65535, 65535, 3500]
PURPLE_SOFT = [50486, 65535, 30000, 3500]
PINK = [58275, 65535, 47142, 3500]
ORANGE = [6500, 65535, 65535, 3500]
YELLOW = [9000, 65535, 65535, 3500]
WHITE = [58275, 0, 65535, 5500]
COLD_WHITE = [58275, 0, 65535, 9000]
WARM_WHITE = [65535, 262, 60000, 3000]
GOLD = [58275, 0, 65535, 2500]

# Time Blocks
MID_MORNING = range(3, 7)  # 3am to 6am
MORNING = range(6, 11)  # 6am to 10am
DAY = range(10, 18)  # 10am to 5pm
NIGHT = range(17, 22)  # 5pm to 10pm
MIDNIGHT = [0, 1, 2, 3, 22, 23, 24]  # 10pm to 3am
time_blocks = {
    'MID_MORNING': MID_MORNING,
    'MORNING': MORNING,
    'DAY': DAY,
    'NIGHT': NIGHT,
    'MIDNIGHT': MIDNIGHT,
}


def get_color_from_schedule(hour):
    """ Checks the time_blocks and returns a color
    """
    if hour in MID_MORNING:
        return GREEN_SOFT

    if hour in MORNING:
        return CYAN

    if hour in DAY:
        return COLD_WHITE

    if hour in NIGHT:
        return WARM_WHITE

    if hour in MIDNIGHT:
        return PURPLE_SOFT


def get_office_lamp():
    """ Returns an instance of Light, that points at the Office Lamp
    If the light is not connected, it returns False
    """
    try:
        lights = LifxLAN().get_lights()
        office_lamp = [l for l in lights if l.mac_addr == _office_lamp_MAC_][0]
        # Ips are hard and decided to use built-in method instead
        # mac_for_os = _offlightice_lamp_MAC_.replace(':', '-')
        # office_lamp_ip = get_lamp_ip(_office_lamp_MAC_)
        # office_lamp = Light(
        #     mac_addr=_office_lamp_MAC_,
        #     ip_addr=office_lamp_ip
        # )
        return office_lamp
    except:
        return False


def get_lamp_ip(mac_addr):
    """ In a extremely hacky way, it will ping the network and extract the
    ip of the office lamp using it's MAC address.
    This is very hardcoded and will likely fail at some point
    NOT USED ANYMORE
    """
    network_devices = subprocess.check_output(['arp', '-a'])

    # Hacky as hacky can get
    ip_to_format = network_devices.split(mac_addr)[0].split('(192')[-1].split(')')[0]
    ip = '192{}'.format(ip_to_format).strip()  # removing white spaces

    return ip


def load_current_hour_block():
    """ Checks which hour block lamp was las in.
    returns a String or None if there is nothing loaded
    """
    block_file = open(_BLOCK_FILE_, "r")
    content = block_file.readlines()
    if content:
        return content[0]
    else:
        return None


def update_saved_block(time_block):
    """ Changes the file that saves the current time block of the lamp
    """
    block_file = open(_BLOCK_FILE_, "w+")
    block_file.write(time_block)
    block_file.close()


def get_current_time_block(hour):
    """ Checks to which block the given hour belongs
    """
    for block in time_blocks:
        if hour in time_blocks[block]:
            return block
    print "Hour #{} not present in any defined block".format(hour)
    return False


def main():
    """ Small routine that checks the time and adjusts the office lamp color
    accordingly
    """
    # Check if the file we need is there
    if not os.path.isfile(_BLOCK_FILE_):
        print "{} file not found. Aborting light change".format(_BLOCK_FILE_)
        return False

    # load saved state of lamp
    saved_block = load_current_hour_block()

    # get current hour and block
    current_hr = time.localtime().tm_hour
    current_block = get_current_time_block(current_hr)
    if not current_block:
        return False

    # No need to continue if lamp doesn't need an update
    if saved_block == current_block:
        return False

    # Check if the lamp is on
    office_lamp = get_office_lamp()

    if not office_lamp:
        print "Office lamp not found. Aborting light change"
        return False

    # If blocks are different, update the color
    if saved_block != current_block:
        new_color = get_color_from_schedule(current_hr)
        office_lamp.set_color(new_color, 50000)
        update_saved_block(current_block)  # also update saved block

    # TODO: Implement what if lamp turns on in the same block but with
    #  wrong color, is this even possible?

    return True


if __name__ == "__main__":
    main()
