# See: https://learn.adafruit.com/adafruit-128x64-oled-featherwing?view=all#circuitpython
# Ensure to have "adafruit_displayio_sh1107" and "adafruit_display_text" installed
# circup install adafruit_displayio_sh1107
# circup install adafruit_display_text

import board
import displayio
import terminalio
import json
import asyncio
import time

from digitalio import DigitalInOut, Pull
from adafruit_display_text import label
import adafruit_displayio_sh1107

RAW_TEXT = '[{"sensorName":"hobby","start":9.7,"end":0},{"sensorName":"center","start":12.7,"end":2},{"sensorName":"bedroom","start":13.9,"end":4.1},{"sensorName":"messe","start":20.6,"end":10.9},{"sensorName":"living","start":26.8,"end":11.9},{"sensorName":"floor","start":27.8,"end":18},{"sensorName":"center","start":31.6,"end":21.9},{"sensorName":"hobby","start":32.6,"end":22.9}]'
WHITE = 0xFFFFFF


class Move:
	def __init__(self, sensorName: str, start: float, end: float):
		self.sensorName = sensorName
		self.start = start
		self.end = end
	
	def to_display_line(self) -> str:
		return f"{self.sensorName}: *{self.start} +{self.end}"


class MoveDisplay:

	WIDTH = 128
	HEIGHT = 64
	LINE_HEIGHT = 10
	SCROLLING_HEIGHT = LINE_HEIGHT * 2
	Y_FONT_OFFSET = 4
	SEC_IDLE_BEFORE_SLEEP = 30

	def __init__(self) -> None:
		self.button_a = DigitalInOut(board.D9)
		self.button_a.switch_to_input(pull=Pull.UP)  
		self.button_b = DigitalInOut(board.D6)
		self.button_b.switch_to_input(pull=Pull.UP)
		self.button_c = DigitalInOut(board.D5)
		self.button_c.switch_to_input(pull=Pull.UP)

		# Screen saving
		self.last_wake_up = time.time()
		self.awake = True
		
		displayio.release_displays()
		i2c = board.I2C()
		display_bus = displayio.I2CDisplay(i2c, device_address=0x3C)

		display = adafruit_displayio_sh1107.SH1107(
			display_bus, 
			width=MoveDisplay.WIDTH,
			height=MoveDisplay.HEIGHT
		)
		self.main_group = displayio.Group()
		display.auto_refresh = False
		display.show(self.main_group)
		self.main_y_min = self.main_group.y
		self.main_height = MoveDisplay.HEIGHT - 4
		self.display = display
		self.display_startup()
		asyncio.create_task(self.run())
	
	async def run(self):
		print("Display is ready to receive Move History!")
		while True:
			if not self.button_a.value:
				self.wake()
				self.move_down()
			elif not self.button_b.value:
				self.wake()
			elif not self.button_c.value:
				self.wake()
				self.move_up()

			if self.awake:
				now = time.time()
				time_passed = now - self.last_wake_up
				if time_passed > MoveDisplay.SEC_IDLE_BEFORE_SLEEP:
					self.sleep()
				else:
					self.display.refresh()
			await asyncio.sleep(0.1)

	def translate(self, moves_json: str) -> list[Move]:
		raw_moves = json.loads(moves_json)

		move_list: list[Move] = []	
		for raw_move in raw_moves:
			move = Move(raw_move['sensorName'], raw_move['start'], raw_move['end'])
			move_list.append(move)
		return move_list

	def reset_display_group(self) -> None:
		while len(self.main_group) > 0:
			self.main_group.pop()
		self.main_group.y = 0

	def display_startup(self) -> None:
		text = "Waiting for moves..."
		text_label = label.Label(terminalio.FONT, text=text, color=WHITE, x=0, y=30)
		self.main_group.append(text_label)

	def update_display_group(self, moves: list[Move]) -> None:
		self.reset_display_group()
		counter = 0
		total_height = 0
		for move in moves:
			text = move.to_display_line()
			label_y = MoveDisplay.Y_FONT_OFFSET + (counter * MoveDisplay.LINE_HEIGHT)
			text_label = label.Label(terminalio.FONT, text=text, color=WHITE, x=0, y=label_y)
			total_height += text_label.height
			self.main_group.append(text_label)
			counter += 1
		self.main_y_min = self.main_group.y
		self.main_height = MoveDisplay.Y_FONT_OFFSET + (counter * MoveDisplay.LINE_HEIGHT)

	def display_json(self, moves_json: str) -> None:
		moves: list[Move] = self.translate(moves_json)
		self.update_display_group(moves)

	def move_up(self) -> None:
		new_y = self.main_group.y - MoveDisplay.SCROLLING_HEIGHT
		y_boundary = (self.main_height - MoveDisplay.HEIGHT) * -1
		if new_y < y_boundary:
			self.main_group.y = y_boundary
		else:
			self.main_group.y = new_y
	
	def move_down(self) -> None:
		new_y = self.main_group.y + MoveDisplay.SCROLLING_HEIGHT
		y_boundary = 0
		if new_y > y_boundary:
			self.main_group.y = y_boundary
		else:	
			self.main_group.y = new_y
	
	def wake(self) -> None:
		self.last_wake_up = time.time()
		if not self.awake:
			print("Waking up...")
			self.display.wake()
			self.awake = True
	
	def sleep(self) -> None:
		print("Going to sleep...")
		self.awake = False
		self.display.sleep()


async def main():
	print("Starting...")
	move_display = MoveDisplay()
	move_display.display_json(RAW_TEXT)
	while True:
		print("Simulating new moves...")
		await asyncio.sleep(20)
		move_display.display_json(RAW_TEXT)

if __name__ == "__main__":
	asyncio.run(main())
