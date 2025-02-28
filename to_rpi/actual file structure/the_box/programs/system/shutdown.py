import random
from rpi_lcd import LCD
import time
import os
import RPi.GPIO as GPIO
from ...modules import rotary_encoder

lcd = LCD()

time.sleep(0.5)
lcd.text("Shutdown?", 1)
rotary_encoder.setup()

if rotary_encoder.loop(["Aye", "Nay"]) != 0:
    os.system("sudo python -m the_box.main")
    exit()
else:
    time.sleep(0.5)
    lcd.text("Shutting down...", 1)

    time.sleep(1)

    joke_options = ["See ya!", "Good day.", "PS. You smell.", "Hasta la vista, baby.", "Live long and prosper.",
                    "May the force be with you.", "GOTO END", "EOF", "EXIT()", "sudo shutdown", "Schleich dich!",
                    "We'll meet again, some sunny day.", "Eine 1. WirSehenUnsNichtWieder.", "Au revoir!", "Adois!",
                    "Ok, tschau.", "Ich geh jetzt.", "Terminated.", "Kalt gemacht."]

    display = random.choice(joke_options)

    lcd.text(display, 1)
    time.sleep(2)
    lcd.clear()
    os.system("sudo shutdown now")
