# circup install adafruit_st7789
# circup install adafruit_display_text
import board
import displayio
from digitalio import DigitalInOut, Pull

# from adafruit_st7789 import ST7789
from adafruit_display_text import bitmap_label
from adafruit_bitmap_font import bitmap_font
import adafruit_displayio_sh1107


class ButtonNavigation():

	def __init__(
		self,
		up_cb,
		down_cb,
		select_cb,
	) -> None:
		self.button_a = DigitalInOut(board.D9)
		self.button_a.switch_to_input(pull=Pull.UP)
		self.button_b = DigitalInOut(board.D6)
		self.button_b.switch_to_input(pull=Pull.UP)
		self.button_c = DigitalInOut(board.D5)
		self.button_c.switch_to_input(pull=Pull.UP)
		self.button_down = False
		self.up_cb = up_cb
		self.down_cb = down_cb
		self.select_cb = select_cb
	
	def tick(self) -> None:
		if not self.button_down:
			if not self.button_a.value:
				self.up_cb()	
				self.button_down = True
			elif not self.button_b.value:
				self.select_cb()
				self.button_down = True
			elif not self.button_c.value:
				self.down_cb()
				self.button_down = True
		else:
			if self.button_a.value and self.button_b.value and self.button_c.value:
				self.button_down = False


class MenuItem():

	def __init__(self, text: str, childs=[]) -> None:
		self.text = text
		self.children: list[MenuItem] = childs
		self.selected = False


class JniMenu():
	BRIGHT = 0xFFFFFF
	DARK = 0x000000
	UPDATE_FREQ = 1
	X_START = 10

	def __init__(
		self, 
		display: displayio.Display, 
		menu_items: list[MenuItem],
		row_height: int,
	) -> None:
		self.selected_level = -1
		self.selected_indeces = [-1, -1, -1, -1, -1]
		self.menu_items = menu_items
		self.row_height = row_height
		self.display = display
		font_file = "fonts/RobotoCondensed-Regular-16.pcf"
		self.custom_font = bitmap_font.load_font(font_file)

		self.main_group = displayio.Group()
		self._create_menu(menu_items, self.main_group)
		self._select_item(0, [0, -1, -1, -1, -1])
		display.show(self.main_group)	
		self.navigation = ButtonNavigation(
			self.on_navi_up,
			self.on_navi_down,
			self.on_navi_select,
		)

	def tick(self) -> None:
		self.navigation.tick()
	
	def on_navi_up(self) -> None:
		print("Up")
		new_indeces = list(self.selected_indeces)
		new_index = new_indeces[self.selected_level]
		new_index -= 1
		if new_index >= 0:
			new_indeces[self.selected_level] = new_index
			self._select_item(self.selected_level, new_indeces)

	def on_navi_select(self) -> None:
		print("Select")

	def on_navi_down(self) -> None:
		print("Down")
		new_indeces = list(self.selected_indeces)
		new_index = new_indeces[self.selected_level]
		new_index += 1
		new_indeces[self.selected_level] = new_index
		self._select_item(self.selected_level, new_indeces)

	def _create_menu(self, menu_items: list[MenuItem], group: displayio.Group) -> None:
		y = - (self.row_height // 2)
		for item in menu_items:
			item_group = displayio.Group()
			text_label = bitmap_label.Label(self.custom_font, text=item.text)
			item_group.x = self.X_START
			y += self.row_height
			item_group.y = y
			item_group.append(text_label)
			group.append(item_group)
			if len(item.children) > 0:
				# TODO Implement sub menus
				raise Exception("not yet implemented!")
	
	def _find_item(self, selected_level: int, indeces: list) -> MenuItem:
		current_children = self.menu_items
		for current_level in range(selected_level + 1):
			current_index = indeces[current_level]
			if current_level == selected_level:
				return current_children[current_index]
			else:
				new_children = current_children[current_index].children
				current_children = new_children
		raise Exception(f"Could not find an item for level {selected_level} and indeces {indeces}")
	
	def _find_group(self, selected_level: int, indeces: list) -> displayio.Group:
		current_group = self.main_group
		for current_level in range(selected_level + 1):
			current_index = indeces[current_level]
			if current_level == selected_level:
				group = current_group[current_index]
				return group  # type: ignore
			else:
				# TODO Implement sub menus
				raise Exception("Not yet implemented")
		raise Exception(f"Could not find a group for level {selected_level} and indeces {indeces}")
	
	def _select_item(self, new_level: int, new_indeces: list) -> None:
		if self.selected_level >= 0:
			item = self._find_item(self.selected_level, self.selected_indeces)
			item.selected = False
			group = self._find_group(self.selected_level, self.selected_indeces)
			text_label: bitmap_label.Label = group[0]  # type: ignore
			text_label.color = self.BRIGHT
			text_label.background_color = self.DARK

		self.selected_level = new_level
		self.selected_indeces = new_indeces

		item = self._find_item(self.selected_level, self.selected_indeces)
		item.selected = True
		group = self._find_group(self.selected_level, self.selected_indeces)
		text_label: bitmap_label.Label = group[0]  # type: ignore
		text_label.color = self.DARK
		text_label.background_color = self.BRIGHT


def create_i2c_oled_display() -> displayio.Display:
	ADA_OLED_FWING_ADDRESS = 0x3C
	displayio.release_displays()
	i2c = board.I2C()
	display_bus = displayio.I2CDisplay(i2c, device_address=ADA_OLED_FWING_ADDRESS)
	WIDTH = 128
	HEIGHT = 64

	display = adafruit_displayio_sh1107.SH1107(display_bus, width=WIDTH, height=HEIGHT)
	return display


def create_menu_tree() -> list[MenuItem]:
	return [
		MenuItem("One"),
		MenuItem("Two"),
		MenuItem("Three"),
		MenuItem("Four"),
	]


def main() -> None:
	print("Starting demo...")
	display = create_i2c_oled_display()
	menu_tree = create_menu_tree()
	menu = JniMenu(display, menu_tree, 20)
	while True:
		menu.tick()


if __name__ == "__main__":
	main()
