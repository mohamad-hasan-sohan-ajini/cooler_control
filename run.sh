#!/bin/bash
python3 /home/pi/cooler_control/control.py 1>/dev/null 2>/dev/null &
python3 /home/pi/cooler_control/update_client.py 1>/dev/null 2>/dev/null &
