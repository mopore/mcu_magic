import asyncio
import board
import displayio
import terminalio
import json
import time

from digitalio import DigitalInOut, Pull
from adafruit_display_text import label
import adafruit_displayio_sh1107


class Move:

	@classmethod
	def zfl(cls, s, width):
		# Pads the provided string with leading 0's to suit the specified 'chrs' length
		# Force # characters, fill with leading 0's
		return '{:0>{w}}'.format(s, w=width)

	@classmethod
	def secs_to_min_str(cls, number: float) -> str:
		# More than a minute
		if number > 60:
			minutes = number // 60
			sec_remainder = (number % 60)
			sec_remainder_text = cls.zfl(f"{sec_remainder:.0f}", 2)
			return f"{minutes:.0f}:{sec_remainder_text}m"
		return f"{number}s"

	def __init__(self, sensorName: str, start: float, end: float):
		self.sensorName = sensorName
		self.start_txt = self.secs_to_min_str(start)
		
		end_text = "*"
		if end >= 0:
			end_text = f"{self.secs_to_min_str(end)}" 
		self.end_txt = end_text
	
	def to_display_line(self) -> str:
		return f"{self.sensorName} {self.end_txt} {self.start_txt}"
	
	def simplify(self, number: float) -> str:
		# More than a minute
		if number > 60:
			minutes = number // 60
			sec_remainder = (number % 60)
			sec_remainder_text = f"{sec_remainder:.0f}".zfill(2)
			return f"{minutes:.0f}:{sec_remainder_text}m"
		return str(number)


class MoveDisplay:

	WHITE = 0xFFFFFF
	WIDTH = 128
	HEIGHT = 64
	LINE_HEIGHT = 10
	SCROLLING_HEIGHT = LINE_HEIGHT * 4
	Y_FONT_OFFSET = 4
	# SEC_IDLE_BEFORE_SLEEP = 120
	SEC_IDLE_BEFORE_SLEEP = 20
	HZ_60 = 0.017

	def __init__(self) -> None:
		self.button_a = DigitalInOut(board.D9)
		self.button_a.switch_to_input(pull=Pull.UP)  
		self.button_b = DigitalInOut(board.D6)
		self.button_b.switch_to_input(pull=Pull.UP)
		self.button_c = DigitalInOut(board.D5)
		self.button_c.switch_to_input(pull=Pull.UP)
		self.button_pressed = False

		# Screen saving
		self.last_wake_up = time.monotonic()
		self.awake = True
		self.repaint_request = True
		
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
		display.brightness = 0.5
		display.show(self.main_group)
		self.main_y_min = self.main_group.y
		self.main_height = MoveDisplay.HEIGHT - 4
		self.display = display
		self.display_startup()
	
	async def loop(self):
		print("Display is ready to receive Move History!")
		while True:
			if not self.button_pressed:
				if not self.button_a.value:
					self.button_pressed = True
					self.wake()
					self.move_down()
				elif not self.button_b.value:
					self.button_pressed = True
					self.wake()
				elif not self.button_c.value:
					self.button_pressed = True
					self.wake()
					self.move_up()
			else:
				# Check for release of button
				if self.button_a.value and self.button_b.value and self.button_c.value:
					# All buttons a released
					self.button_pressed = False

			if self.awake:
				# Check for going to sleep
				now = time.monotonic()
				time_passed = now - self.last_wake_up
				stay_awake = time_passed < MoveDisplay.SEC_IDLE_BEFORE_SLEEP

				if stay_awake:
					if self.repaint_request:
						self.display.refresh()
				else:
					self.sleep()
			await asyncio.sleep(0)

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
		text_label = label.Label(terminalio.FONT, text=text, color=self.WHITE, x=0, y=30)
		self.main_group.append(text_label)
		self.display.refresh()

	def rebuild_display_group(self, moves: list[Move]) -> None:
		self.reset_display_group()
		counter = 0
		total_height = 0
		for move in moves:
			text = f"{counter}.{move.to_display_line()}"
			label_y = MoveDisplay.Y_FONT_OFFSET + (counter * MoveDisplay.LINE_HEIGHT)
			text_label = label.Label(terminalio.FONT, text=text, color=self.WHITE, x=0, y=label_y)
			total_height += text_label.height
			self.main_group.append(text_label)
			counter += 1
		self.main_y_min = self.main_group.y
		self.main_height = MoveDisplay.Y_FONT_OFFSET + (counter * MoveDisplay.LINE_HEIGHT)

	def display_json(self, moves_json: str) -> None:
		self.wake()
		moves: list[Move] = self.translate(moves_json)
		print(f"Showing {len(moves)} new moves.")
		self.rebuild_display_group(moves)

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
		self.last_wake_up = time.monotonic()
		self.repaint_request = True
		if not self.awake:
			print("Waking up...")
			self.display.wake()
			self.awake = True
	
	def sleep(self) -> None:
		print("Going to sleep...")
		self.awake = False
		self.display.sleep()


RAW_TEXT = '[{"sensorName":"hobby","start":9.7,"end":0},{"sensorName":"center","start":12.7,"end":2},{"sensorName":"bedroom","start":13.9,"end":4.1},{"sensorName":"messe","start":20.6,"end":10.9},{"sensorName":"living","start":26.8,"end":11.9},{"sensorName":"floor","start":27.8,"end":18},{"sensorName":"center","start":31.6,"end":21.9},{"sensorName":"hobby","start":32.6,"end":22.9}]'


async def test_display_json(move_display: MoveDisplay): 
	await asyncio.sleep(5)
	print("Triggering display_json")
	move_display.display_json(RAW_TEXT)


async def main():
	print("Testing...")
	move_display = MoveDisplay()
	display_task = asyncio.create_task(move_display.loop())
	test_task = asyncio.create_task(test_display_json(move_display))
	await asyncio.gather(display_task, test_task)


if __name__ == "__main__":
	asyncio.run(main())
