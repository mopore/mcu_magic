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

	def __init__(self, text: str, childs=None) -> None:
		self.text = text
		if childs is None:
			childs = []
		self.children: list[MenuItem] = childs
		self.selected = False
		self.main_y = 0


class JniMenu():
	INIT_INDICES = (-1, -1, -1)
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
		self.selected_indeces = self.INIT_INDICES
		self.root_menu = MenuItem("root", menu_items)
		self.current_parent_menu = self.root_menu
		self.row_height = row_height
		self.display = display
		font_file = "fonts/RobotoCondensed-Regular-16.pcf"
		self.custom_font = bitmap_font.load_font(font_file)

		self.main_group = displayio.Group()
		self._create_menu(menu_items, self.main_group)
		self._switch_item((0, -1, -1))
		display.show(self.main_group)	
		self.navigation = ButtonNavigation(
			self.on_navi_up,
			self.on_navi_down,
			self.on_navi_select,
		)

	def tick(self) -> None:
		self.navigation.tick()
	
	def on_navi_up(self) -> None:
		current_level = self._determine_level(self.selected_indeces)
		new_index = self.selected_indeces[current_level]
		new_index -= 1
		if new_index >= 0:
			new_indices = self._update_indices(self.selected_indeces, current_level, new_index)
			self._switch_item(new_indices)
			move_group_criteria = self._space_to_top(new_index) < 0
			if move_group_criteria: 
				jump_up_amount = self.row_height
				if new_index == 0:
					jump_up_amount = self.row_height
				self.main_group.y += jump_up_amount
				self.current_parent_menu.main_y = self.main_group.y

	def on_navi_down(self) -> None:
		current_level = self._determine_level(self.selected_indeces)
		new_index = self.selected_indeces[current_level]
		new_index += 1
		not_overreached = new_index < len(self.current_parent_menu.children)
		if not_overreached:
			new_indices = self._update_indices(self.selected_indeces, current_level, new_index)
			self._switch_item(new_indices)
			space_to_bottom = self._space_to_bottom(new_index)
			move_group_criteria = space_to_bottom < (self.row_height // 3)
			if move_group_criteria:
				self.main_group.y -= self.row_height
				self.current_parent_menu.main_y = self.main_group.y

	def on_navi_select(self) -> None:
		print("Select")

	def _space_to_bottom(self, new_index: int) -> int:
		space_needed = (new_index + 1) * self.row_height  
		space_available = (self.main_group.y * -1) + self.display.height
		return space_available - space_needed

	def _space_to_top(self, new_index: int) -> int:
		space_to_top = (new_index * self.row_height) - (self.main_group.y * -1) 
		return space_to_top

	def _determine_level(self, indices: tuple) -> int:
		level = -1
		for v in indices:
			if v >= 0:
				level += 1
			else:
				break
		return level
	
	def _update_indices(self, old_indices: tuple, level: int, new_index: int) -> tuple:
		new_indices_list = list(old_indices)
		new_indices_list[level] = new_index
		return tuple(new_indices_list)

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
	
	def _find_item(self, indeces: tuple) -> MenuItem:
		current_children = self.current_parent_menu.children
		selected_level = self._determine_level(self.selected_indeces)
		for current_level in range(selected_level + 1):
			current_index = indeces[current_level]
			if current_level == selected_level:
				return current_children[current_index]
			else:
				new_children = current_children[current_index].children
				current_children = new_children
		raise Exception(f"Could not find an item for level {selected_level} and indeces {indeces}")
	
	def _find_group(self, indeces: tuple) -> displayio.Group:
		current_group = self.main_group
		selected_level = self._determine_level(self.selected_indeces)
		for current_level in range(selected_level + 1):
			current_index = indeces[current_level]
			if current_level == selected_level:
				group = current_group[current_index]
				return group  # type: ignore
			else:
				# TODO Implement sub menus
				raise Exception("Not yet implemented")
		raise Exception(f"Could not find a group for level {selected_level} and indeces {indeces}")
	
	def _switch_item(self, new_indeces: tuple) -> None:
		if self.selected_indeces != self.INIT_INDICES:
			item = self._find_item(self.selected_indeces)
			item.selected = False
			group = self._find_group(self.selected_indeces)
			text_label: bitmap_label.Label = group[0]  # type: ignore
			text_label.color = self.BRIGHT
			text_label.background_color = self.DARK

		self.selected_indeces = new_indeces

		item = self._find_item(self.selected_indeces)
		item.selected = True
		group = self._find_group(self.selected_indeces)
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
		MenuItem("Five"),
		MenuItem("Six"),
		MenuItem("Seven"),
	]


def main() -> None:
	print("Starting demo...")
	display = create_i2c_oled_display()
	menu_tree = create_menu_tree()
	menu = JniMenu(display, menu_tree, 18)
	while True:
		menu.tick()


if __name__ == "__main__":
	main()
