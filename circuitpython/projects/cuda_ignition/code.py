# circup install asyncio
# circup install adafruit_requests
# circup install adafruit_datetime
# circup install adafruit_minimqtt

import jni_wifi
import jni_mqtt_bridge
import asyncio


def command_cb(message: str) -> None:
    print(f"Received command: {message}")


async def main() -> None:
    print("Hello, world!")
    jni_wifi.connect_wifi()
    mqtt = jni_mqtt_bridge.MqttBridge("cudo_ignition", command_cb)
    mqtt_loop_task = asyncio.create_task(mqtt.loop())
    await asyncio.gather(mqtt_loop_task)


if __name__ == "__main__":
    asyncio.run(main())
