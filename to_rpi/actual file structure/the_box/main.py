import random
from pathlib import Path
from rpi_lcd import LCD
import time
import os
import json
from the_box.modules import rotary_encoder
import RPi.GPIO as GPIO


def restart():
    os.system("sudo python -m the_box.main")
    lcd.clear()
    exit("Restart/Back")


lcd = LCD()

app_info_path = Path("/home/moi/the_box/programs/apps.json")
if not app_info_path.exists():
    lcd.text("Settings things up", 1)
    time.sleep(2)
    lcd.text("This may take a while", 1)
    lcd.text("ETA: " + random.choice(list("123456789")) + " " + random.choice("Days,Years,Cent.,Secs,Hours,Mins".split(",")), 2)

    app_info_path.touch()
    clean = [{"Settings": "/home/moi/the_box/programs/system/settings", "Shutdown": "/home/moi/the_box/programs/system/shutdown"}]
    with app_info_path.open(mode="w", encoding="utf-8") as write_file:
        json.dump(clean, write_file, indent=4)

    time.sleep(2)
    lcd.clear()

# gets the apps
with app_info_path.open(mode="r", encoding="utf-8") as read_file:
    app_options = json.load(read_file)[0]

lcd.text("Home", 1)
app_list = []
for app in app_options:
    app_list.append(app)

rotary_encoder.setup()
int_res = rotary_encoder.loop(app_list)
rotary_encoder.destroy()
app_path = app_options[app_list[int_res]]
if int_res == -1:
    app_path = app_options["Shutdown"]

module_path = app_path.replace("/home/moi/", "").replace("/", ".").replace(".py", "")


command = "sudo python -m " + module_path
os.system(command)

lcd.clear()
exit()
