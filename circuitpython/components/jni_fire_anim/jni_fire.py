# Ensure to have "neopixel" installed
#
# pip3 install circup
# circup install adafruit_neopixel
# circup install adafruit_fancyled
#

import time
import board
import neopixel
import random
from microcontroller import Pin
import array

import adafruit_fancyled.adafruit_fancyled as fancy


class Spark:
    
    def __init__(self, position: int, radius_cells: int, peak_energy: int, start_cycle: int, 
                 duration: int) -> None:
        self.position = position
        self.radius_cells = radius_cells
        self.current_cycle = 0
        self.start_cycle = start_cycle
        self.end_cycle = start_cycle + duration
        self.energy_cycle_index = 0
        self.current_energy = 0
        
        peak_frame = int(duration / 2)
        a = [0] * duration
        self.energy_per_frame = array.array('B', a)
        for i in range(duration):
            if i <= peak_frame:
                # Rising
                ratio = (i + 1) / (peak_frame + 1)
                self.energy_per_frame[i] = int(ratio * peak_energy)
            else:
                # Falling
                y = duration - peak_frame
                x = abs(duration - peak_frame - i) 
                ratio = x / y
                self.energy_per_frame[i] = peak_energy - int(ratio * peak_energy)
                
        self.active_frame_index = 0
        self.dead = False
    
    def cycle_loop(self) -> None:
        if not self.dead:
            if self.current_cycle >= self.start_cycle:
                if self.current_cycle < self.end_cycle:
                    # In the energy cycle
                    try:
                        self.current_energy = self.energy_per_frame[self.energy_cycle_index]
                    except Exception as err:
                        print(f"Energy frames: {len(self.energy_per_frame)}")
                        print(f"Energy cycle index: {self.energy_cycle_index}")
                        print(f"Start cycle: {self.start_cycle}")
                        print(f"End cycle: {self.end_cycle}")
                        print(f"Current cycle: {self.current_cycle}")
                        raise err
                    self.energy_cycle_index += 1 
                else:
                    # End of energy cycle
                    self.current_energy = 0
                    self.dead = True
            self.current_cycle += 1


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
        self.sparks_min_amount = 3
        self.sparks_max_amount = 10
        self.spark_min_width_pct = 10
        self.spark_max_width_pct = 30
        self.spark_min_peak_energy = 50
        self.spark_max_peak_energy = 100
        self.spark_min_duration = 6  # Frames
        self.spark_max_duration = 40


class SparkEngine:
    
    OVER_TIME_PCT_WARNING = 10
    
    BLUE_RED_PALETTE = [
        0x0a015c,  # Blue
        0xff0000,  # Red  
        0x0a015c,  # Blue
    ]

    WEIGHTED_HEAT_GRADIENT = [
        (0.1, 0x0a015c),  # Blue
        (0.3, 0x410070),  
        (0.35, 0x70006e),  # Purple
        (0.47, 0x9c0048),  
        (0.5, 0xef0017),  # Red
        (0.53, 0x9c0048),  
        (0.65, 0x70006e),  # Purple
        (0.7, 0x410070),  
        (0.9, 0x0a015c),  # Blue
    ]

    def __init__(self, config: SparkEngineConfig, 
                 pixels: neopixel.NeoPixel | None = None) -> None:  
        self.leds_number = config.leds_number
        self.frame_time = 1 / config.frequence
        self.generation_cycle = config.frequence * 5
        # self.palette = fancy.expand_gradient(self.WEIGHTED_HEAT_GRADIENT, 100)
        self.palette = self.BLUE_RED_PALETTE
        if (pixels is None):
            self.pixels = neopixel.NeoPixel(config.pin, config.leds_number, 
                brightness=config.brightness, auto_write=False)
        else:
            self.pixels = pixels
        self.offset = 0
        self.time_after_last_rendering = time.monotonic()
        self.time_before_last_rendering = time.monotonic()
        cells = [0] * config.leds_number
        self.cells = array.array('B', cells)  # raw array with unsingned chars (translates to int)
        self.cycle_counter = self.generation_cycle
        self.config = config
        self.sparks: list[Spark] = []
        self.time_in_frame = True

    def loop(self) -> None:
        time_now = time.monotonic()
        time_last_frame = time_now - self.time_before_last_rendering
        if time_last_frame >= self.frame_time:

            # Problem detection
            if not self.time_in_frame:
                time_over_frame = time_last_frame - self.frame_time
                pct_over_frame = (time_over_frame / self.frame_time) * 100

                if pct_over_frame > self.OVER_TIME_PCT_WARNING:
                    rendering_time = self.time_after_last_rendering - \
                        self.time_before_last_rendering 
                    headroom_time = self.frame_time - rendering_time
                    if headroom_time <= 0:
                        print(f"{pct_over_frame:.0f}% over frame time! No headroom in rendering.")
                    else:
                        headroom_pct = (headroom_time / self.frame_time) * 100
                        print(f"{pct_over_frame:.0f}% over frame time! {headroom_pct:.0f}% " + 
                              "rendering headroom.")
            
            # Regular loop
            self.time_before_last_rendering = time_now
            self._cooldown_loop()
            if self.cycle_counter == self.generation_cycle:
                self._new_spark_generation_loop()
                self.cycle_counter = 0
            else:
                self.cycle_counter += 1
            self._spark_warmup_loop()
            self._render_loop()
            self.time_after_last_rendering = time.monotonic()
            self.time_in_frame = False
        else:
            # We don't need the exra time in the frame
            self.time_in_frame = True
        
    def _render_loop(self) -> None:
        for i in range(self.leds_number):
            color = self.cell_value_to_color(i)
            self.pixels[i] = color.pack()
        self.pixels.show()
    
    def _cooldown_loop(self) -> None:
        for i in range(self.leds_number):
            val = self.cells[i]
            if val > 0:
                val -= self.config.cool_down_per_cycle
                if val < 0:
                    val = 0
                self.cells[i] = val
    
    def _new_spark_generation_loop(self) -> None:
        c = self.config
        amount_of_sparks = random.randint(c.sparks_min_amount, c.sparks_max_amount)
        for _ in range(amount_of_sparks):
            position = random.randint(0, self.leds_number - 1)
            width_pct = random.randint(c.spark_min_width_pct, c.spark_max_width_pct)
            # Calculates the amount of cells/leds that will be occupied by the spark
            radius_cells = int((self.leds_number * (width_pct / 100)) / 2)
            start_cycle = random.randint(0, self.generation_cycle - 1)
            peak_energy = random.randint(c.spark_min_peak_energy, c.spark_max_peak_energy)
            duration = random.randint(c.spark_min_duration, c.spark_max_duration)
            new_spark = Spark(position, radius_cells, peak_energy, start_cycle, duration)
            self.sparks.append(new_spark)
    
    def _spark_warmup_loop(self) -> None:
        for spark in self.sparks:
            if spark.dead:
                self.sparks.remove(spark)
            else:
                spark.cycle_loop()
                if spark.current_energy > 0:

                    cells_affected = 2 * spark.radius_cells + 1
                    i = [0] * cells_affected

                    for i in range(cells_affected):
                        center = spark.radius_cells + 1
                        cell_index = -1
                        energy_ratio = -1
                        if i < center:
                            # Rising
                            cell_index = spark.position - spark.radius_cells + i
                            if cell_index < 0:
                                cell_index = self.leds_number + cell_index
                            energy_ratio = (i + 1) / center
                        else:
                            # Falling
                            cell_index = spark.position + i - spark.radius_cells
                            if cell_index >= self.leds_number: 
                                cell_index -= self.leds_number
                            x = cells_affected - i
                            energy_ratio = x / (spark.radius_cells + 1)
                        energy_from_spark = int(energy_ratio * spark.current_energy) 

                        cell_value = self.cells[cell_index]
                        if (energy_from_spark > cell_value):
                            cell_value = energy_from_spark
                        if cell_value > 100:
                            cell_value = 100
                        self.cells[cell_index] = cell_value
    
    def cell_value_to_color(self, cell_index: int):
        value_100 = self.cells[cell_index]
        lookup = value_100 / 200
        color = fancy.palette_lookup(self.palette, lookup)
        return color


def main() -> None:
    # LED strip
    config = SparkEngineConfig(board.IO14, brightness=0.5,  # type: ignore
            leds_number=166, frequence=6)
    engine = SparkEngine(config)

    # # Keyboard settings
    # config = SparkEngineConfig(board.IO14, brightness=0.1,  # type: ignore
    #         leds_number=18, frequence=30)
    # engine = SparkEngine(config)

    while True:
        engine.loop()


if __name__ == "__main__":
    main()
