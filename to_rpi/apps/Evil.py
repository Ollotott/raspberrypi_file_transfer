from ..modules import rotary_encoder
from rpi_lcd import LCD
from time import sleep
import os

lcd = LCD()
lcd.clear()
sleep(1)

lcd.text("You stink!", 1)
sleep(5)
lcd.text("Dog breath!", 2)
sleep(2)

lcd.clear()

lcd.text("I hate yee!", 1)
sleep(1)

options = ["No I'm Not", "What?", "Is that true?", "I disagree.", "Same here.", "Escargot."]

while True:

    rotary_encoder.setup()
    res = options[rotary_encoder.loop(options)]
    rotary_encoder.destroy()

    if res == "Same here.":
        break

sleep(2)

lcd.clear()
lcd.text("Well, you stink", 1)
sleep(3)
lcd.text("Get out of here!", 2)
sleep(3)

os.system("sudo python -m the_box.main")
exit()
