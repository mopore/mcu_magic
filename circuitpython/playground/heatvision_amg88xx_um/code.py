#  circup install adafruit_amg88xx
#  circup install adafruit_minimqtt
# Library documentation: https://docs.circuitpython.org/projects/amg88xx/en/latest/api.html
import time
import busio
import board
import adafruit_amg88xx
import json
import neopixel
import microcontroller
from wifi_mqtt import MqttConnection, connect_wifi, disconnect_wifi
from digitalio import DigitalInOut, Pull
from battery_on_oled import BatteryOnOled
import gc

gc.collect()
TOPIC_DATA_NAME = "jniHome/services/heatvision1/data"
TOPIC_COMMAND_NAME = "jniHome/services/heatvision1/command"
COMMAND_SNAPSHOT_NAME = "snapshot"


def setup(mqtt_connection: MqttConnection) -> None:
    connect_wifi()
    mqtt_connection.connect()
    print(f"Starting publishing sensor data to {TOPIC_DATA_NAME}")
    print("Press internal button to stop...")


def tear_down(mqtt_connection: MqttConnection) -> None:
    mqtt_connection.disconnect()
    disconnect_wifi()
    print("Stopped publishing sensor data.")
    print("Press internal button to start again...")


def main():

    print("Starting...")
    print("Preparing status LED...")
    pixel = neopixel.NeoPixel(board.NEOPIXEL, 1)
    pixel.brightness = 0.3

    PURPLE = (100, 0, 100)
    ORANGE = (100, 100, 0)
    RED = (255, 0, 0)
    GREEN = (0, 255, 0)
    pixel.fill(PURPLE)

    battery_oled: BatteryOnOled | None = None
    try:
        mqtt_connection = MqttConnection()

        print("Getting i2c bus...")
        i2c = busio.I2C(board.SCL, board.SDA)

        print("Searching oled for battery information...")
        battery_oled = BatteryOnOled(i2c)
        status_text = "Loading..."
        print("OLED display found!")

        print("Setting heat sensor up...")
        heat_sensor: adafruit_amg88xx.AMG88XX | None = None
        try:
            heat_sensor = adafruit_amg88xx.AMG88XX(i2c)
        except Exception as e:
            pixel.fill(RED)
            print("Could not set up heat sensor!")

        if heat_sensor is not None:
            BUTTON_DOWN_VALUE = False
            BUTTON_UP_VALUE = True
            a_button_state_pressed = False
            a_button = DigitalInOut(board.D9)
            a_button.switch_to_input(pull=Pull.UP)
            b_button_state_pressed = False
            b_button = DigitalInOut(board.D6)
            b_button.switch_to_input(pull=Pull.UP)
            publishing = False
            print("Press button to start publishing...")
            status_text = "Press 'A' to publish."

            while True:
                start_ts = time.monotonic()

                if publishing:
                    export = {"sensor_data": heat_sensor.pixels}
                    mqtt_connection.publish(TOPIC_DATA_NAME, json.dumps(export))

                # BUTTON HANDLING
                if a_button_state_pressed:
                    if BUTTON_UP_VALUE == a_button.value:
                        if publishing:
                            print("Stopping publishing...")
                            battery_oled.update_display("Stopping...")
                            publishing = False
                            pixel.fill(ORANGE)
                            tear_down(mqtt_connection)
                            pixel.fill(PURPLE)
                            print("Publishing stopped.")
                            battery_oled.update_display("Stopped.")
                            status_text = "Press 'A' to publish."
                        else:
                            print("Connecting...")
                            battery_oled.update_display("Connecting...")
                            pixel.fill(ORANGE)
                            setup(mqtt_connection)
                            publishing = True
                            pixel.fill(GREEN)
                            print("Publishing...")
                            battery_oled.update_display("Publishing...")
                            status_text = "Publishing..."

                        a_button_state_pressed = False
                else:
                    if BUTTON_DOWN_VALUE == a_button.value:
                        a_button_state_pressed = True
                if b_button_state_pressed:
                    if BUTTON_UP_VALUE == b_button.value:
                        print("B button up.")
                        if publishing:
                            print("Requesting snapshot.")
                            mqtt_connection.publish(TOPIC_COMMAND_NAME, COMMAND_SNAPSHOT_NAME)
                            battery_oled.update_display("SNAPSHOT!")
                        else:
                            print("Can not snapshot when not publishing.")
                        b_button_state_pressed = False
                else:
                    if BUTTON_DOWN_VALUE == b_button.value:
                        print("B button down.")
                        b_button_state_pressed = True

                # TICK HANDLING
                # Ensure a minimum processing tick of 0.1 seconds
                time_passed = time.monotonic() - start_ts
                time_to_sleep = 0.1 - time_passed
                if time_to_sleep > 0:
                    # print(f"Sleeping {time_to_sleep}")
                    time.sleep(time_to_sleep)
                if battery_oled is not None:
                    battery_oled.update_display(status_text)
    except Exception as e:
        print(f"An error occured: {e}")
        if battery_oled is not None:
            battery_oled.update_display("Reset in 3 secs.")
            time.sleep(3)
            microcontroller.on_next_reset(microcontroller.RunMode.NORMAL)
            microcontroller.reset()
        while True:
            pixel.fill(RED)
            time.sleep(0.1)
            pixel.fill(0)
            time.sleep(0.1)


if __name__ == "__main__":
    main()
