import busio
import board
import time


STOP_BYTE_ARRAY = bytes([0x7E])
STOP_BYTE = 0x7E
BAUDRATE = 19200
DELAY_MICROSECS = (BAUDRATE / 10) * 2 + 100
DELAY_SECONDS = DELAY_MICROSECS / 1_000_000

uart = busio.UART(tx=board.TX, rx=board.RX, baudrate=BAUDRATE)

ping_data_bytes = bytes([0x7E, 0xFF, 0x03, 0xEE, 0xFE, 0xFF, 0xFF, 0x00, 0x15, 0x1C, 0x6C, 0x7E])


def transmit_ping() -> None:
    print("Sending ping...")
    uart.write(ping_data_bytes)
    time.sleep(DELAY_SECONDS)
    print("Ping sent.")


def wait_for_response() -> None:
    print("Waiting for response...")
    chars = []
    while True:
        data = uart.read(32)
        if data:
            print()
            for b in data:
                print(hex(b), end=" ")
                chars.append(chr(b))	
            if len(chars) > 0:
                word = "".join(chars)
                print(f"\n\nReceived: {word}\n")
                chars = []

def main() -> None:
    #  for _ in range(10):
    #      transmit_ping()
    #  
    wait_for_response()


if __name__ == "__main__":
    main()
