import time
import os
from rpi_lcd import LCD
import datetime
import random

time.sleep(0.5)

# os.system("sudo /home/moi/the_box/startup/rtc-pi")

time.sleep(0.5)

lcd = LCD()

lcd.clear()
lcd.text("----BOX 2000----", 1)
time.sleep(0.5)
lcd.text("____BOX 2000____", 1)
time.sleep(0.5)
lcd.text("----BOX 2000----", 1)
time.sleep(0.5)
lcd.clear()

'''lcd.clear()
time.sleep(0.5)
text = "    " + datetime.datetime.now().strftime("%H:%M:%S")
lcd.text(text, 2)
time.sleep(3)
lcd.clear()'''

if random.random() > 0.95:
    lcd.clear()
    lcd.text("Exploding in...", 1)
    lcd.text("   3", 2)
    time.sleep(1)
    lcd.text("   2", 2)
    time.sleep(1)
    lcd.text("   1", 2)
    time.sleep(1)
    lcd.clear()
    lcd.text("BOOM!", 1)
    time.sleep(0.3)
    lcd.text("   BAM!", 2)
    time.sleep(2)
    lcd.text("", 2)
    lcd.text("Ok just kidding.", 1)
    time.sleep(1)
elif random.random() > 0.95:
    lcd.text("FLAMMENWERFER!", 1)
    time.sleep(2)
    lcd.text("        --Felix", 2)
    time.sleep(1)

lcd.clear()
os.system("sudo python -m the_box.main")
