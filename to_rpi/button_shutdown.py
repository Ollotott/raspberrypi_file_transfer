import RPi.GPIO as GPIO
import time
import os

BtnPin = 7

select = False


def check_btn(y):
    global select
    select = True


def setup():
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(BtnPin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.add_event_detect(BtnPin, GPIO.FALLING, callback=check_btn)


setup()
while True:
    print("Running...")
    time.sleep(2)
    if select:
        print("----Shutdown!")
        os.system("sudo shutdown now")
