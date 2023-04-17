# main.py -- put your code here!
import machine
import ssd1306
from pyb import ADC, Pin, Timer
import framebuf
import time

rtc = machine.RTC()
rtc.datetime((0, 2023, 3, 16, 3, 59, 50, 0))

bpm = []

i2c = machine.SoftI2C(scl=machine.Pin('A8'), sda=machine.Pin('C13'))

# Power Display
machine.Pin('C10', machine.Pin.OUT).low()
machine.Pin('A15', machine.Pin.OUT).high()

machine.Pin('A0', machine.Pin.OUT).low()
machine.Pin('C3', machine.Pin.OUT).high()

# Display
oled = ssd1306.SSD1306_I2C(128, 64, i2c)

# global
last_y = 0
MAX_HISTORY = 128
TOTAL_BEATS = 30
HEART = [
[ 0, 0, 0, 0, 0, 0, 0, 0, 0],
[ 0, 1, 1, 0, 0, 0, 1, 1, 0],
[ 1, 1, 1, 1, 0, 1, 1, 1, 1],
[ 1, 1, 1, 1, 1, 1, 1, 1, 1],
[ 1, 1, 1, 1, 1, 1, 1, 1, 1],
[ 0, 1, 1, 1, 1, 1, 1, 1, 0],
[ 0, 0, 1, 1, 1, 1, 1, 0, 0],
[ 0, 0, 0, 1, 1, 1, 0, 0, 0],
[ 0, 0, 0, 0, 1, 0, 0, 0, 0],
]

def printhur(tuple):
    year = tuple[0]
    month = tuple[1]
    day = tuple[2]
    hour = tuple[4]
    minute = tuple[5]
    sec = tuple[6]
    oled.text(str(hour) + ":" + str(minute)+":"+str(sec), 73, 50)

#display
def refresh(bpm, v, minima, maxima):
    global last_y

    oled.vline(0, 0, 32, 0)
    oled.scroll(-1,0) # Scroll left 1 pixel

    if maxima-minima > 0:
        # Draw beat line.
        y = 32 - int(16 * (v-minima) / (maxima-minima))
        oled.line(125, last_y, 126, y, 1)
        last_y = y

    # Clear top text area.
    oled.fill_rect(0,0,128,16,0) # Clear the top text area
    oled.fill_rect(0,50,128,18,0)

    printhur(rtc.datetime())
    if bpm:
        if bpm < 220:
            oled.text("%d BPM" % bpm, 12, 0)
        else :
            oled.text("... BPM", 12, 0)
            

    # Draw heart if beating.
    for y, row in enumerate(HEART):
        for x, c in enumerate(row):
            oled.pixel(x, y, c)

    oled.show()


def calculate_bpm(beats):
    if beats:
        beat_time = beats[-1] - beats[0]
        if beat_time:
            return (len(beats) / (beat_time)) * 60

    
      
def main():
    # Maintain a log of previous values to
    # determine min, max and threshold.
    history = []
    beats = []
    beat = False
    bpm = None

    # Clear screen to start.
    oled.fill(0)

    while True:
        v = ADC("C2").read()
        history.append(v)

        # Get the tail, up to MAX_HISTORY length
        history = history[-MAX_HISTORY:]

        minima, maxima = min(history), max(history)
        tmp = sorted(history)
        place = 3*len(history)//4
        troiQurtile = tmp[place]

        # threshold_on = (troiQurtile * 3) // 4   # 3/4
        # threshold_off = (troiQurtile) // 2      # 1/2
        if v > troiQurtile and history[-1] > history[-2]:
            beats.append(time.time())
            # Truncate beats queue to max
            beats = beats[-TOTAL_BEATS:]
            bpm = calculate_bpm(beats)


        refresh(bpm, v, minima, maxima)

main()
