import board
import adafruit_vl53l1x
import adafruit_icm20x


class CarSensors:

	def __init__(self) -> None:
		self._initialize_distance_sensor()
		self._free_distance: float = -1
		self._initialize_accelerometer()
		self._acc: tuple[float, float, float] = (0, 0, 0)
		self._gyro: tuple[float, float, float] = (0, 0, 0)

	def _initialize_distance_sensor(self) -> None:
		print("Initializing distance sensor...")
		MODE_LONG = 2
		i2c = board.I2C()
		vl53 = adafruit_vl53l1x.VL53L1X(i2c)
		vl53.distance_mode = MODE_LONG
		vl53.timing_budget = 100
		vl53.start_ranging()
		self._distance_sensor = vl53
		print("Distance sensor initialized.")
	
	def _initialize_accelerometer(self) -> None:
		print("Initializing accelerometer...")
		i2c = board.I2C()
		self.icm = adafruit_icm20x.ICM20649(i2c)
		print("Accelerometer initialized.")

	def loop(self) -> None:
		self._loop_distance_sensor()
		self._loop_accelerometer()

	def _loop_distance_sensor(self) -> None:
		if self._distance_sensor.data_ready:
			value: float | None = self._distance_sensor.distance
			if value is not None:
				self._free_distance = value
			self._distance_sensor.clear_interrupt()
	
	def _loop_accelerometer(self) -> None:
		(acc_x, acc_y, acc_z) = self.icm.acceleration
		self._acc = (acc_x, acc_y, acc_z)

		(gyr_x, gyr_y, gyr_z) = self.icm.gyro
		self._gyro = (gyr_x, gyr_y, gyr_z)

	def get_free_distance(self) -> float:
		return self._free_distance
	
	def get_acceleration(self) -> tuple[float, float, float]:
		return self._acc
	
	def get_gyro(self) -> tuple[float, float, float]:
		return self._gyro
