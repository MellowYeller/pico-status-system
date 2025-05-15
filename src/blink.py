from machine import Pin
from utime import sleep


blue = Pin(15, Pin.OUT)
led = Pin("LED", Pin.OUT)

led.on()
print("LED starts flashing...")
while True:
    try:
        blue.toggle()
        led.toggle()
        sleep(.5)
    except KeyboardInterrupt:
        break
blue.off()
led.off()
print("Finished.")
