"""
This will only work on supported boards!
CircuitPython I2S WAV file playback.
Plays a WAV file once.
"""
import audiocore
import board
import audiobusio

# Hot to connect:
# https://cdn-learn.adafruit.com/assets/assets/000/114/431/original/adafruit_products_FS3TFT_I2S_MAX98375A_bb.jpg?1661203934
# Pins for Feather ESP32 S3 TFT
audio = audiobusio.I2SOut(board.A1, board.A2, board.A3)

with open("StreetChicken.wav", "rb") as file_content:
    wave_handle = audiocore.WaveFile(file_content)

    print("Playing wav file!")
    audio.play(wave_handle)
    while audio.playing:
        pass

print("Done!")
