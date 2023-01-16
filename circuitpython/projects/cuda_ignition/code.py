# circup install asyncio
# circup install adafruit_requests
# circup install adafruit_datetime
# circup install adafruit_minimqtt

import asyncio

import jni_wifi
import jni_mqtt_bridge
import jni_relay_control


class CudaIgnition:
    
    def __init__(self) -> None:
        self.relay_control = jni_relay_control.RelayControl()

    def command_cb(self, message: str) -> None:
        print(f"Received command: {message}")
        if "ON" == message.upper().strip():
            self.relay_control.turn_on()
        elif "OFF" == message.upper().strip():
            self.relay_control.turn_off()
        else:
            try:
                seconds_to_wait = float(message)
                self.relay_control.turn_on_for(seconds_to_wait)
            except ValueError:
                print(f"Unknown command: {message}")
    

async def main() -> None:
    ignition = CudaIgnition()
 
    print("Hello, world!")
    jni_wifi.connect_wifi()
    mqtt = jni_mqtt_bridge.MqttBridge("cudo_ignition", ignition.command_cb)
    mqtt_loop_task = asyncio.create_task(mqtt.loop())
    await asyncio.gather(mqtt_loop_task)


if __name__ == "__main__":
    asyncio.run(main())
