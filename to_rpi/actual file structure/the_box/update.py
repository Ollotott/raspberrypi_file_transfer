import time
import os
from pathlib import Path

time.sleep(2)

if Path("/media/moi/update/the_box").exists():
    os.system("sudo rm -r /home/moi/the_box")
    time.sleep(1)
    os.system("sudo cp -r /media/moi/update/the_box /home/moi")
    time.sleep(1)
    print("The deed is done!")
    os.system("sudo reboot")
else:
    print("No files!")