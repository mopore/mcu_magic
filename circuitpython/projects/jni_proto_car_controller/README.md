# Async IO Tasks

## 1. MQTT Loop Task
- JNI MQTT Broker listening on command topic.
- Loop sleeps 1s

## 2. Main Loop
- ControllerListener (Checks constantly for controller input, updates display and 
updates the home base)
- Reads battery information every 10 seconds (checks each loop via time.monotonic, 
could be replaced)
- Sleeps 0s

## 3. Homebase Loop
- Pushes input updates to homebase via socket connection
- Sleeps .1s