#!/usr/bin/env bash
set euo pipefail
echo "Running main.py on esp32..."
ampy --port /dev/cu.usbserial-D309CAI4 run main.py
echo "All done."
exit 0
