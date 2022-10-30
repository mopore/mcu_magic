# Documentation: https://learn.adafruit.com/adafruit-drv2605-haptic-controller-breakout
# circup install adafruit_drv2605
import time
import board

import adafruit_drv2605


def main() -> None:
	print("Presenting vibration effects...")

	# Effects library: https://cdn-learn.adafruit.com/assets/assets/000/072/594/original/adafruit_products_DRV_Waveforms.png?1552347698
	i2c = board.STEMMA_I2C()  # type: ignore
	driver = adafruit_drv2605.DRV2605(i2c)
	effect_id = 1
	while True:
		print(f"Playing effect: #{effect_id}")
		driver.sequence[0] = adafruit_drv2605.Effect(effect_id)
		driver.play()	
		time.sleep(2)
		driver.stop()
		effect_id += 1
		if effect_id > 123:
			effect_id = 1


if __name__ == "__main__":
	main()
