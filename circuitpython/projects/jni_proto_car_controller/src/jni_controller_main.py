import asyncio
import time
import jni_controller_mqtt_bridge
import jni_controller_display
import jni_home_socket
import jni_joyfw
import jni_feathers3
import jni_global_settings as settings


def get_battery_info() -> str: 
	on_usbc_power = jni_feathers3.get_vbus_present()
	voltage: float | None = None
	text = "USB power"
	if not on_usbc_power:
		voltage = jni_feathers3.get_battery_voltage()
		text = f"Bat: {voltage:.2f}V"
	return text


class ControllerListener(jni_joyfw.JniJoyFwListener):

	def __init__(
		self, 
		controller_display: jni_controller_display.ControllerDisplay,
		home_socket: jni_home_socket.HomeSocket
	) -> None:
		self._controller_display = controller_display	
		self._home_socket = home_socket
	
	def on_button_a(self) -> None:
		self._home_socket.inform_joy_button_a(pressed=True)
	
	def on_button_b(self) -> None:
		self._home_socket.inform_joy_button_b(pressed=True)
	
	def on_move(self, x: int, y: int) -> None:
		self._home_socket.inform_joy_move(x, y)
		self._controller_display.update_xy(x, y)


class ControllerMain:
	
	EXIT_COMMAND = "exit"
	
	def __init__(
		self,
		service_name: str,
		home_socket: jni_home_socket.HomeSocket
	) -> None:
		self._display = jni_controller_display.ControllerDisplay() 
		self._service_name = service_name
		self._home_socket = home_socket
		self._keep_running = True
		self._last_battery_check = 0
		self._mqtt_bridge: jni_controller_mqtt_bridge.ControllerMqttBridge | None = None
		self.sub_command_topic = f"jniHome/services/{self._service_name}/command"

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
	
	async def loop_async(self, loop_sleeps: float = 0):
		if self._mqtt_bridge is None:
			raise Exception("No MQTT bridge set!")
		listener = ControllerListener(self._display, self._home_socket)
		self._wing.set_listener(listener)
		self._display.update_state("Ready")
		print("Ready.")
		while self._keep_running:
			self._loop()
			await asyncio.sleep(loop_sleeps)
	
	def _loop(self):
		self._wing.loop()
		self._loop_battery_check()
	
	def _loop_battery_check(self):
		now = time.monotonic()
		time_passed = now - self._last_battery_check
		if time_passed > settings.BATTERY_CHECK_FREQUENCY_SECONDS:
			battery_info = get_battery_info()
			self._display.update_battery(battery_info)
			self._last_battery_check = now
