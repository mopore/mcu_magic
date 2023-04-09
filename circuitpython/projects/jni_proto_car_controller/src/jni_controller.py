import asyncio
import jni_controller_mqtt_bridge
import jni_controller_display
import jni_joyfw
import json


class ControllerListener(jni_joyfw.JniJoyFwListener):

	def __init__(
		self, 
		controller_display: jni_controller_display.ControllerDisplay,
		mqtt_bridge: jni_controller_mqtt_bridge.ControllerMqttBridge
	) -> None:
		self._controller_display = controller_display	
		self._mqtt_bridge = mqtt_bridge
	
	def on_button_a(self) -> None:
		print("Button A!")
	
	def on_move(self, x: int, y: int) -> None:
		json_string = json.dumps({
			"x": float(x) / 100,
			"y": float(y) / 100})
		self._mqtt_bridge.publish_xy(json_string)
		self._controller_display.update_xy(x, y)


class Controller:
	
	EXIT_COMMAND = "exit"
	
	def __init__(self, service_name: str) -> None:
		self._display = jni_controller_display.ControllerDisplay() 
		self._service_name = service_name
		self._keep_running = True
		self._mqtt_bridge: jni_controller_mqtt_bridge.ControllerMqttBridge | None = None
		self.pub_topic_battery = f"jniHome/services/{self._service_name}/battery"
		self.sub_command_topic = f"jniHome/services/{self._service_name}/command"
		self.sub_input_topic = f"jniHome/services/{self._service_name}/input"

		wing = jni_joyfw.JniJoyFw()
		calibration = wing.read_calibration()
		if calibration is not None:
			wing.calib = calibration
		else:
			wing.calibrate()
			print("Calibrated.")
		print("Normal mode...")
		self._wing = wing

	def get_subs(self) -> list[str]:
		subs = [
			self.sub_command_topic,
		]
		return subs

	def mqtt_cb(self, message: str, topic: str) -> None:
		if topic == self.sub_command_topic:
			print(f"Received command: {message}")
			if message.strip().lower() == self.EXIT_COMMAND:
				self._keep_running = False
				if self._mqtt_bridge is not None:
					self._mqtt_bridge.exit()
		else:
			print(f"Received unknown topic: {topic}") 
	
	async def loop_async(self):
		if self._mqtt_bridge is None:
			raise Exception("No MQTT bridge set!")
		listener = ControllerListener(self._display, self._mqtt_bridge)
		self._wing.set_listener(listener)
		self._display.update_state("Ready")
		print("Ready.")
		while self._keep_running:
			self._loop()
			await asyncio.sleep(0)
	
	def _loop(self):
		self._wing.loop()
