# circup install adafruit_vl53l1x

# Time of Flight
# Documentation: https://learn.adafruit.com/adafruit-vl53l1x/overview

# Used the UM FeatherS3

# Connected just the I2C pins (VIN, SCL, SDA, GND) 2nd to 5th pin
# Note that SDA and SCL are twisted (compared to FeatherS3)


import time
import board
import adafruit_vl53l1x


def main() -> None:
	MODE_SHORT = 1
	MODE_LONG = 2

	i2c = board.I2C()
	vl53 = adafruit_vl53l1x.VL53L1X(i2c)

	# OPTIONAL: can set non-default values
	vl53.distance_mode = MODE_LONG
	vl53.timing_budget = 100

	print("VL53L1X Simple Test.")
	print("--------------------")
	model_id, module_type, mask_rev = vl53.model_info
	print("Model ID: 0x{:0X}".format(model_id))
	print("Module Type: 0x{:0X}".format(module_type))
	print("Mask Revision: 0x{:0X}".format(mask_rev))
	print("Distance Mode: ", end="")
	if MODE_SHORT == vl53.distance_mode:
		print("SHORT")
	elif MODE_LONG == vl53.distance_mode:
		print("LONG")
	else:
		print("UNKNOWN")
	print("Timing Budget: {}".format(vl53.timing_budget))
	print("--------------------")

	vl53.start_ranging()

	while True:
		if vl53.data_ready:
			print("Distance: {} cm".format(vl53.distance))
			vl53.clear_interrupt()
			time.sleep(1.0)


if __name__ == "__main__":
	main()
