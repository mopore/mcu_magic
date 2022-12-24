# circup install adafruit_st7789
# circup install adafruit_display_text
import board
import displayio
from digitalio import DigitalInOut, Pull

# from adafruit_st7789 import ST7789
from adafruit_display_text import bitmap_label
from adafruit_bitmap_font import bitmap_font
import adafruit_displayio_sh1107
import terminalio


class ButtonListener():

	def on_navi_up(self):
		...

	def on_navi_down(self):
		...

	def on_navi_select(self):
		...


class ButtonNavigation():

	def __init__(self) -> None:
		self.listener: ButtonListener | None = None

	def loop(self):
		...


class OledButtonNavigation(ButtonNavigation):

	def __init__(
		self,
	) -> None:
		self.button_a = DigitalInOut(board.D9)
		self.button_a.switch_to_input(pull=Pull.UP)
		self.button_b = DigitalInOut(board.D6)
		self.button_b.switch_to_input(pull=Pull.UP)
		self.button_c = DigitalInOut(board.D5)
		self.button_c.switch_to_input(pull=Pull.UP)
		self.button_down = False
	
	def loop(self) -> None:
		if not self.button_down:
			if not self.button_a.value:
				if self.listener is not None:
					self.listener.on_navi_up()
				self.button_down = True
			elif not self.button_b.value:
				if self.listener is not None:
					self.listener.on_navi_select()
				self.button_down = True
			elif not self.button_c.value:
				if self.listener is not None:
					self.listener.on_navi_down()
				self.button_down = True
		else:
			if self.button_a.value and self.button_b.value and self.button_c.value:
				self.button_down = False


class JniMenuItem():

	BACK_ITEM_TEXT = "<<"

	def __init__(self, text: str | None, childs=None, cb=None, back_item=False) -> None:
		""" Set text to None for root element."""
		self.text = text
		self.cb = cb
		self.selected = False
		self.main_y = 0
		self.is_back_item = back_item
		self.is_root = self.text is None
		if childs is None:
			childs = []
		if len(childs) > 0 and not self.is_root:
			back_item = JniMenuItem(self.BACK_ITEM_TEXT, back_item=True)
			childs.insert(0, back_item)
		self.children: list[JniMenuItem] = childs


class JniMenu(ButtonListener):
	INIT_INDICES = (-1, -1, -1)
	BRIGHT = 0xFFFFFF
	DARK = 0x000000
	UPDATE_FREQ = 1
	X_START = 10

	def __init__(
		self, 
		button_navigation: ButtonNavigation,
		display: displayio.Display, 
		row_height: int,
		menu_items: list[JniMenuItem],
		font: bitmap_font.Bitmap | None = None
	) -> None:
		self.selected_indeces = self.INIT_INDICES
		self.root_menu = JniMenuItem(text=None, childs=menu_items)
		self.current_parent_menu = self.root_menu
		self.row_height = row_height
		if font is None:
			font = terminalio.FONT  # type: ignore
		self.font = font
		self.display = display
		splash = displayio.Group()
		self.main_dgroup = displayio.Group()
		splash.append(self.main_dgroup)
		self._build_dgroup(self.root_menu)
		self._update_selection((0, -1, -1))

		self.secondary_dgroup = displayio.Group()
		self.secondary_dgroup.hidden = True
		splash.append(self.secondary_dgroup)		

		display.show(splash)	
		self.navigation = button_navigation
		button_navigation.listener = self

	def loop(self) -> None:
		self.navigation.loop()
	
	def on_navi_up(self) -> None:
		current_level = self._determine_level(self.selected_indeces)
		new_index = self.selected_indeces[current_level]
		new_index -= 1
		if new_index >= 0:
			new_indices = self._new_indices(self.selected_indeces, current_level, new_index)
			self._update_selection(new_indices)
			move_group_criteria = self._space_to_top(new_index) < 0
			if move_group_criteria: 
				jump_up_amount = self.row_height
				if new_index == 0:
					jump_up_amount = self.row_height
				self.main_dgroup.y += jump_up_amount
				self.current_parent_menu.main_y = self.main_dgroup.y

	def on_navi_down(self) -> None:
		current_level = self._determine_level(self.selected_indeces)
		new_index = self.selected_indeces[current_level]
		new_index += 1
		not_overreached = new_index < len(self.current_parent_menu.children)
		if not_overreached:
			new_indices = self._new_indices(self.selected_indeces, current_level, new_index)
			self._update_selection(new_indices)
			space_to_bottom = self._space_to_bottom(new_index)
			move_group_criteria = space_to_bottom < (self.row_height // 3)
			if move_group_criteria:
				self.main_dgroup.y -= self.row_height
				self.current_parent_menu.main_y = self.main_dgroup.y

	def on_navi_select(self) -> None:
		selected_item = self._find_item(self.selected_indeces)
		# Fire callback function if any
		if selected_item.cb is not None:
			# FIXME Remove the following code later...
			self.main_dgroup.hidden = True
			text = "Hello"	
			text_label = bitmap_label.Label(terminalio.FONT, text=text, color=self.BRIGHT, x=0, y=30)
			self.secondary_dgroup.append(text_label)
			self.secondary_dgroup.hidden = False

			selected_item.cb()
		# Dive into sub menus if any
		if len(selected_item.children) > 0:
			self.current_parent_menu = selected_item
			self._build_dgroup(selected_item)
			level = self._determine_level(self.selected_indeces)
			level += 1
			new_index = 0
			new_indices = self._new_indices(self.selected_indeces, level, new_index)
			self._update_selection(new_indices)
		# Move one menu level up
		elif selected_item.is_back_item:
			level = self._determine_level(self.selected_indeces)
			level -= 1
			new_indices = self._new_indices(self.selected_indeces, level)
			new_selected_item = self._find_item_parent(new_indices)
			self.current_parent_menu = new_selected_item
			self._build_dgroup(new_selected_item)
			self._update_selection(new_indices)

	def _space_to_bottom(self, new_index: int) -> int:
		space_needed = (new_index + 1) * self.row_height  
		space_available = (self.main_dgroup.y * -1) + self.display.height
		return space_available - space_needed

	def _space_to_top(self, new_index: int) -> int:
		space_to_top = (new_index * self.row_height) - (self.main_dgroup.y * -1) 
		return space_to_top

	def _determine_level(self, indices: tuple) -> int:
		level = -1
		for v in indices:
			if v >= 0:
				level += 1
			else:
				break
		return level
	
	def _new_indices(self, old_indices: tuple, level: int, new_index: int | None = None) -> tuple:
		new_indices_list = list(old_indices)
		if new_index is None:
			# Set all indeces after current level to -1
			for i in range(level + 1, len(new_indices_list)):
				new_indices_list[i] = -1
		else:
			new_indices_list[level] = new_index

		return tuple(new_indices_list)

	def _build_dgroup(self, menu_item: JniMenuItem) -> None:
		y = - (self.row_height // 2)
		group = self.main_dgroup
		while len(group) > 0:
			group.pop()
		for item in menu_item.children:
			item_group = displayio.Group()
			text_label = bitmap_label.Label(self.font, text=item.text)
			item_group.x = self.X_START
			y += self.row_height
			item_group.y = y
			item_group.append(text_label)
			group.append(item_group)
		group.y = menu_item.main_y
	
	def _find_item(self, indeces: tuple) -> JniMenuItem:
		current_children = self.root_menu.children
		selected_level = self._determine_level(self.selected_indeces)
		for current_level in range(selected_level + 1):
			current_index = indeces[current_level]
			if current_level == selected_level:
				return current_children[current_index]
			else:
				new_children = current_children[current_index].children
				current_children = new_children
		raise Exception(f"Could not find an item for level {selected_level} and indeces {indeces}")
	
	def _find_item_parent(self, indeces: tuple) -> JniMenuItem:
		current_parent = self.root_menu
		target_level = self._determine_level(indeces)
		for current_level in range(target_level + 1):
			if current_level == target_level:
				return current_parent
			else:
				current_index = indeces[current_level]
				current_parent = current_parent.children[current_index]
		raise Exception(f"Could not find the parent item for level {target_level} and indeces {indeces}")
		
	def _update_selection(self, new_indeces: tuple) -> None:
		old_level = self._determine_level(self.selected_indeces)
		old_index = self.selected_indeces[old_level]
		if old_index >= 0:
			item = self._find_item(self.selected_indeces)
			item.selected = False
			if old_index < len(self.main_dgroup):
				text_label: bitmap_label.Label = self.main_dgroup[old_index][0]  # type: ignore
				text_label.color = self.BRIGHT
				text_label.background_color = self.DARK
		self.selected_indeces = new_indeces
		new_level = self._determine_level(self.selected_indeces)
		new_index = self.selected_indeces[new_level]
		item = self._find_item(self.selected_indeces)
		item.selected = True
		text_label: bitmap_label.Label = self.main_dgroup[new_index][0]  # type: ignore
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


def create_menu_tree() -> list[JniMenuItem]:
	return [
		JniMenuItem("Action", cb=lambda: print("ACTION!!!")),
		JniMenuItem("Sub Menu A", childs=[
			JniMenuItem("Action 1", cb=lambda: print("Hello from sub menu 1"))
		]),
		JniMenuItem("Three"),
		JniMenuItem("Four"),
		JniMenuItem("Five"),
		JniMenuItem("Six"),
		JniMenuItem("Seven"),
		JniMenuItem("Sub Menu 2", childs=[
			JniMenuItem("Action 2", cb=lambda: print("Hello from sub menu 2")),
			JniMenuItem("Sub Sub Menu 3", childs=[
				JniMenuItem("Action 3", cb=lambda: print("ACTION 3!!!")),
			])
		]),
	]


def main() -> None:
	print("Starting demo...")
	button_navigation = OledButtonNavigation()
	display = create_i2c_oled_display()
	menu_tree = create_menu_tree()

	# font_file = "fonts/RobotoCondensed-Regular-16.pcf"
	# custom_font = bitmap_font.load_font(font_file)
	# menu = JniMenu(button_navigation, display, menu_tree, 18, font=custom_font)  # type: ignore

	menu = JniMenu(button_navigation, display, row_height=16, menu_items=menu_tree)
	# button_navigation.listener = menu
	while True:
		menu.loop()


if __name__ == "__main__":
	main()
