# circup install adafruit_datetime
import json
from adafruit_datetime import datetime


def main() -> None:
	bvalue1 = True
	strvalue = "Test"
	now = datetime.now()

	json_string = json.dumps({
		"Value1": bvalue1, 
		"MyDate": now.isoformat(), 
		"StringValue": strvalue})
	print(f"JSON>>>{json_string}")

	dict_from_json = json.loads(json_string)
	print(f"Dictionary<<<{dict_from_json}")
	read_value = dict_from_json["StringValue"]
	print(f"Reading \"StringValue\": {read_value}")


if __name__ == "__main__":
	main()
