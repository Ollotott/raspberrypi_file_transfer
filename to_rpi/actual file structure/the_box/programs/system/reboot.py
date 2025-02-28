from rpi_lcd import LCD
import time
import os

lcd = LCD()

time.sleep(0.5)

lcd.text("Rebooting...", 1)

time.sleep(1)
lcd.text("Ill be back!", 2)
time.sleep(2)
lcd.clear()

os.system("sudo reboot")
