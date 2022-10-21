from umqttsimple import MQTTClient
import ubinascii
try:
    import usocket as socket
except:
    import socket
import time, network, json
import esp, gc, machine
from button_control import ButtonControl
from status_viewer import StatusViewer

class ButtonStateClient:
    topic_button = b"iot_showcase/button_state"
    topic_exit = b"iot_showcase/exit"
    server_ip = "192.168.4.2"
    client_id = ubinascii.hexlify("iot_showcase")
    max_changes = 6

    def __init__(self):
        self.button_active = False
        self.publish_change = False
        self.keep_running = True
        self.click_counter = 0
        self.mqtt = MQTTClient(
            client_id=ButtonStateClient.client_id, 
            server=ButtonStateClient.server_ip, 
            keepalive=30)
        self.mqtt.connect()
        print(f"Connected to MQTT server at {ButtonStateClient.server_ip}")

    def loop(self) -> bool:
        self.mqtt.check_msg()
        
        if self.publish_change:
            self.click_counter += 1
            clicks_left = ButtonStateClient.max_changes - self.click_counter
            x = {"active": self.button_active, "clicks_left": clicks_left}
            msg = json.dumps(x)
            print(f"Publishing: {msg}")
            self.mqtt.publish(self.topic_button, msg)
            self.publish_change = False
            self.time_last_change = time.time()
            if self.click_counter == ButtonStateClient.max_changes:
                print(f"Max of {ButtonStateClient.max_changes} changes reached")
                self.keep_running = False
            else:
                print(f"Button clicks left: {clicks_left}")
        return self.keep_running
    
    def button_clicked(self, button_active: bool) -> None:
        self.button_active = button_active
        self.publish_change = True

    def disconnect(self):
        self.mqtt.disconnect()
        print("Disconnected from MQTT broker")


def main() -> None:
    esp.osdebug(None)
    gc.collect()

    viewer = StatusViewer()
    viewer.to_idle()
    
    print("Press button 38 to start...")
    push_button = machine.Pin(38, machine.Pin.IN, machine.Pin.PULL_UP)
    while push_button.value() == 1:
        pass

    # Setup WLAN Access Point
    ssid = 'IoT_Showcase_AP'
    password = 'esp32'
    print(f"Creating Access Point '{ssid}'")
    viewer.to_prep_ap()
    ap = network.WLAN(network.AP_IF)
    ap.active(True)
    ap.config(essid=ssid, password=password)
    while ap.active() is False:
        pass
    print("Access Point is up")
    print(ap.ifconfig())

    state_client: ButtonStateClient | None = None
    try:
        print("Waiting for MQTT Server to connect to...")
        viewer.to_await_client()
        state_client = ButtonStateClient()
        print("Send 'EXIT' to topic 'iot_showcase/exit' to exit")

        # Preparing exit callback
        def exit_callback(topic, msg):
            if topic == b"iot_showcase/exit" and msg == b"EXIT":
                print("Exit command received")
                state_client.keep_running = False

        state_client.mqtt.set_callback(exit_callback)
        state_client.mqtt.subscribe(ButtonStateClient.topic_exit)

        def callback_function(button_active: bool) -> None:
            state_client.button_clicked(button_active)

        button_control = ButtonControl(callback_function)
        viewer.to_operative()
        while state_client.loop():
            pass
        print("All done")
        button_control.stop()
    except OSError as e:
        print(f"Error: {e}")
        viewer.to_error()
        time.sleep(3)

    try:
        if state_client is not None:
            state_client.disconnect()
    except Exception as e:
        print(f"ERROR when disconnecting: {e}")

    print("Deactivating Access Point")
    ap.active(False)
    while ap.active():
        pass
    print("Access Point deactiviated.")
    viewer.shutdown()
    print("Going into endless idle...")
    int_led = machine.Pin(13, machine.Pin.OUT)
    while True:
        int_led.value(ButtonControl.LED_ON)
        time.sleep(0.1)
        int_led.value(ButtonControl.LED_OFF)
        time.sleep(1)


if __name__ == "__main__":
    main()
