# Ensure to have "neopixel" installed
#
# pip3 install circup
# circup install adafruit_neopixel
# circup install adafruit_fancyled
#

import time
import board
import neopixel
from microcontroller import Pin
import array

import adafruit_fancyled.adafruit_fancyled as fancy


class SparkEngineConfig:
    
    DEF_FREQUENCE = 30
    DEF_LEDS_NUMBER = 166

    def __init__(self, pin: Pin, brightness: float, leds_number=DEF_LEDS_NUMBER,  # type: ignore
            frequence=DEF_FREQUENCE) -> None:  
        self.pin = pin
        self.brightness = brightness
        self.leds_number = leds_number
        self.frequence = frequence
        self.cool_down_per_cycle = 3


class SparkEngine:
    
    HEADROOM_PCT_WARNING = 5
    
    WEIGHTED_HEAT_GRADIENT = [
        (0.1, 0x090000),  # Brown
        (0.3, 0xa70f0d),  # Red
        (0.35, 0xFF660b),  # Orange
        (0.47, 0xffe20b),  # Yellow
        (0.5, 0xFFFFFF),  # White
        (0.53, 0xffe20b),  # Yellow
        (0.65, 0xFF660b),  # Orange
        (0.7, 0xa70f0d),  # Red
        (0.9, 0x090000),  # Brown
    ]

    def __init__(self, config: SparkEngineConfig) -> None:  
        self.leds_number = config.leds_number
        self.frame_time = 1 / config.frequence
        self.generation_cycle = config.frequence * 5
        self.palette = fancy.expand_gradient(self.WEIGHTED_HEAT_GRADIENT, 100)
        self.pixels = neopixel.NeoPixel(config.pin, config.leds_number, 
            brightness=config.brightness, auto_write=False)
        self.offset = 0
        self.time_after_last_rendering = time.monotonic()
        self.time_before_last_rendering = time.monotonic()
        cells = [0] * config.leds_number
        self.cells = array.array('B', cells)  # raw array with unsingned chars (translates to int)
        self.cycle_counter = self.generation_cycle
        self.config = config

    def loop(self) -> None:
        time_now = time.monotonic()
        time_passed = time_now - self.time_before_last_rendering
        if time_passed >= self.frame_time:
            headroom_time = time_now - self.time_after_last_rendering
            headroom_time = headroom_time if headroom_time > 0 else 0
            headroom_pct = (headroom_time / self.frame_time) * 100
            if headroom_pct <= self.HEADROOM_PCT_WARNING:
                print(f"Only {headroom_pct:.0f}% headroom available!")
            self.time_before_last_rendering = time_now
            self.cooldown_loop()
            if self.cycle_counter == self.generation_cycle:
                self.new_spark_generation_loop()
                self.cycle_counter = 0
            else:
                self.cycle_counter += 1
            self.spark_warmup_loop()
            self.render_loop()
            self.time_after_last_rendering = time.monotonic()
        
    def render_loop(self) -> None:
        for i in range(self.leds_number):
            color = self.cell_value_to_color(i)
            self.pixels[i] = color.pack()
        self.pixels.show()
    
    def cooldown_loop(self) -> None:
        for i in range(self.leds_number):
            val = self.cells[i]
            if val > 0:
                val -= self.config.cool_down_per_cycle
                if val < 0:
                    val = 0
                self.cells[i] = val
    
    def new_spark_generation_loop(self) -> None:
        ...
    
    def spark_warmup_loop(self) -> None:
        ...
    
    def cell_value_to_color(self, cell_index: int):
        value_100 = self.cells[cell_index]
        lookup = value_100 / 200
        color = fancy.palette_lookup(self.palette, lookup)
        return color


def main() -> None:
    config = SparkEngineConfig(board.IO14, brightness=0.1,  # type: ignore
            leds_number=166, frequence=10)
    engine = SparkEngine(config)

    # Keyboard settings
    # config = SparkEngineConfig(board.IO14, brightness=0.1,  # type: ignore
    #         leds_number=18, frequence=30)
    # engine = SparkEngine(config)

    while True:
        engine.loop()
        time.sleep(0.01)


if __name__ == "__main__":
    main()
