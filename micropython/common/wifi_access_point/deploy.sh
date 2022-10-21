#!/usr/bin/env bash
set euo pipefail
echo "Deploying boot.py to esp32..."
ampy --port /dev/cu.usbserial-D309CAI4 put boot.py
echo "All done. Press RST button on device."
exit 0
