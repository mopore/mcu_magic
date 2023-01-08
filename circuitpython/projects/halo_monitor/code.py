# circup install asyncio
# circup install adafruit_requests
# circup install adafruit_datetime
# circup install adafruit_minimqtt
# circup install adafruit_displayio_sh1107
# circup install adafruit_display_text
# circup install adafruit_neopixel

import board
import neopixel
import asyncio

import jni_wifi
import jni_mqtt_bridge
import jni_move_display


async def main():
	red = (255, 0, 0)
	green = (0, 255, 0)
	pixel = neopixel.NeoPixel(board.NEOPIXEL, 1)  # type: ignore
	pixel.fill(red)
	pixel.brightness = 1.0

	print("Preparing display...")
	move_display = jni_move_display.MoveDisplay()
	jni_wifi.connect_wifi()
	pixel.brightness = 0.03
	pixel.fill(green)

	new_move_history_cb = move_display.display_json
	mqtt_bridge = jni_mqtt_bridge.MqttBridge("move_history", new_move_history_cb)

	display_task = asyncio.create_task(move_display.loop())
	bridge_task = asyncio.create_task(mqtt_bridge.loop())
	await asyncio.gather(display_task, bridge_task)

if __name__ == "__main__":
	asyncio.run(main())
