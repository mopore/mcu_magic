RELAY CONTROL ADAFRUIT ESP32 FEATHER V2
=======================================

- Setup Webflow to prepare MC as deployment platform (see webflow.md)
- Use the deploy script to deploy
- Set service details in `secrets/jni_secrets.py`
- The key `mqtt_service_name` sets the name the relay service is available

# Two Modes
## Ignition
- Used to turn on PC
- Connect cables at relay at slots "NO" (normally open) and "COMM".
- To use send "1" to `jniHome/services/<service name>/command` this will close
the connection for 1 second.

## Cutoff
- Used to restart Raspberry PI which is configured to be in "always on" mode.
- Connect cables at relay at slots "NC" (normally closed) and "COMM".
- To use send "ON" to `jniHome/services/<service name>/command` this will open
the connection. Wait at least 10 seconds. Then send "OFF" to close the power
connection again.

