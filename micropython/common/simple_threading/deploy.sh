#!/usr/bin/env bash
set euo pipefail
echo "Deploying main.py to esp32..."
ampy --port /dev/cu.usbserial-D309CAI4 put main.py
echo "All done. Press RST button on device."
exit 0
