from pathlib import Path
from rpi_lcd import LCD
import time
import os
import json
import RPi.GPIO as GPIO
from ...modules import rotary_encoder
import shutil
from datetime import datetime

BtnPin = 29
show_me_time = True


def card_data(card_path):
    card_path = str(card_path)
    return list(shutil.disk_usage(card_path))  # ALL, USED, FREE


def get_directory_size(directory):
    """Returns the `directory` size in GB."""
    total = 0
    try:
        # print("[+] Getting the size of", directory)
        for entry in os.scandir(directory):
            if entry.is_file():
                # if it's a file, use stat() function
                total += entry.stat().st_size
            elif entry.is_dir():
                # if it's a directory, recursively call this function
                try:
                    total += get_directory_size(entry.path)
                except FileNotFoundError:
                    pass
    except NotADirectoryError:
        # if `directory` isn't a directory, get the file size then
        return os.path.getsize(directory)
    except PermissionError:
        # if for whatever reason we can't open the folder, return 0
        return 0
    return total


def restart():
    os.system("sudo python -m the_box.programs.system.settings")
    lcd.clear()
    exit("Restart/Back")


def check_btn(hold):
    global show_me_time
    show_me_time = False


def setup_button():
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(BtnPin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.add_event_detect(BtnPin, GPIO.FALLING, callback=check_btn)


rotary_encoder.setup()

# Settings... Back button goes home.

lcd = LCD()

lcd.text("Settings", 1)
settings_options = ["Show Time", "Reboot", "Exit All", "Eject Disks", "Install New", "Remove Apps", "Ej. ALL Disks", "Update", "Mounted Disks", "Home"]

selected = settings_options[rotary_encoder.loop(settings_options)]
rotary_encoder.destroy()

time.sleep(0.5)

options = ["No", "Yes"]

# rebooting
if selected == "Reboot":
    os.system("sudo python /home/moi/the_box/programs/system/reboot.py")
    exit()

# resetting the time
elif selected == "Set Time":
    lcd.clear()
    lcd.text("This function does not exist yet!", 1)
    time.sleep(1)
    restart()

    '''time.sleep(0.5)
    lcd.clear()
    lcd.text("Web connection?", 1)

    # asks for yes, btn 2 does nothing.
    rotary_encoder.setup()
    res = rotary_encoder.loop(options) # yes is 1, no is 0
    rotary_encoder.destroy()
    if res == 1:
        command = "sh /home/moi/the_box/programs/system/reset_rtc.sh"
        os.system(command)
    else:
        restart()'''

# exit all, must be verified
elif selected == "Exit All":
    time.sleep(0.2)
    lcd.clear()

    lcd.text("Exit?", 1)

    rotary_encoder.setup()
    res = rotary_encoder.loop(options) # y is 1, n is 0
    rotary_encoder.destroy()

    # exit!
    if res == 1:
        lcd.clear()
        lcd.text("Exiting...", 2)
        time.sleep(1)
        lcd.clear()
        exit("Exit!")

    # rather not...
    else:
        lcd.text("Wise.", 2)
        time.sleep(1)
        lcd.clear()
        restart()

# eject external nr_of_disks
elif selected == "Eject Disks":
    disk_path = Path("/media/moi")

    connected_disks = os.listdir(disk_path)
    disk_directory = []

    for disk in connected_disks:
        if disk != "SSD" and disk != "HDD":
            disk_directory.append(disk)

    if len(disk_directory) > 0:
        for disk in disk_directory:
            command = "sudo eject /media/moi/" + disk
            os.system(command)
        lcd.text("Disks ejected!", 2)
    else:
        lcd.text("None connected!", 2)
    time.sleep(1)
    restart()

elif selected == "Install New":

    disk_directory = os.listdir(Path("/media/moi/"))
    time.sleep(0.5)

    # gets the disk name!
    if len(disk_directory) == 0:
        lcd.text("No Disk!", 2)
        time.sleep(1)
        restart()

    elif len(disk_directory) > 1:
        rotary_encoder.setup()
        chosen_disk = disk_directory[rotary_encoder.loop(disk_directory)]
        rotary_encoder.destroy()

    elif len(disk_directory) == 1:
        chosen_disk = disk_directory[0]

    # gets which program to copy.
    file_parents = Path("/media/moi/") / chosen_disk
    potential_files = []
    for file in os.listdir(file_parents):
        if file.endswith(".py"):
            potential_files.append(file)

    # several py files
    if len(potential_files) > 1:
        lcd.text("Choose Program!", 1)
        time.sleep(0.5)

        rotary_encoder.setup()
        file_index = rotary_encoder.loop(potential_files)
        if file_index == -1:
            lcd.text("Cancelled.", 1)
            time.sleep(1)
            restart()

        chosen_file = potential_files[file_index]
        rotary_encoder.destroy()

    elif len(potential_files) == 1:
        chosen_file = potential_files[0]

    else:
        chosen_file = "HI!"
        time.sleep(1)
        lcd.clear()
        lcd.text("No py files!", 1)
        time.sleep(2)
        restart()

    lcd.text(f"Inst. {chosen_file}", 1)

    time.sleep(0.5)
    rotary_encoder.setup()
    y_n = rotary_encoder.loop(("Yes", "No"))
    rotary_encoder.destroy()
    if y_n != 0:
        lcd.text("Cancelled.", 1)
        time.sleep(1)
        restart()

    to_be_copied = file_parents / chosen_file
    copy_to = Path("/home/moi/the_box/programs")
    process_name = chosen_file.replace(".py", "")
    app_path = Path("/home/moi/the_box/programs/apps.json")

    # write new app to app file:
    # get current contents
    with app_path.open(mode="r", encoding="utf-8") as read_file:
        contents = json.load(read_file)

    contents[0][process_name] = str(copy_to) + "/" + chosen_file

    if not chosen_file.startswith("b_"):
        with app_path.open(mode="w", encoding="utf-8") as write_file:
            json.dump(contents, write_file, indent=4)

    # copy the files
    command = "sudo cp " + str(to_be_copied) + " " + str(copy_to)
    os.system(command)

    time.sleep(2)
    lcd.text(process_name, 1)
    lcd.text("Inst. Success.", 2)
    time.sleep(2)
    restart()

elif selected == "Remove Apps":
    # get app names
    app_info_path = Path("/home/moi/the_box/programs/apps.json")

    with app_info_path.open(mode="r", encoding="utf-8") as read_file:
        apps = json.load(read_file)

    potential_deletes = []
    for app_name in apps[0]:
        if app_name != "Settings" and app_name != "Shutdown":
            potential_deletes.append(app_name)

    if len(potential_deletes) == 0:
        lcd.clear()
        lcd.text("Nothing to delete", 2)
        time.sleep(2)
        restart()

    lcd.clear()
    lcd.text("What to remove?", 1)

    rotary_encoder.setup()
    to_be_deleted_ind = rotary_encoder.loop(potential_deletes)
    rotary_encoder.destroy()

    if to_be_deleted_ind == -1:
        restart()

    lcd.clear()
    lcd.text("Del " + potential_deletes[to_be_deleted_ind] + "?", 1)
    rotary_encoder.setup()
    time.sleep(0.5)
    res = rotary_encoder.loop(options)
    rotary_encoder.destroy()

    if res == 1:
        dict_key = potential_deletes[to_be_deleted_ind]
        command = "sudo rm " + apps[0][dict_key]
        os.system(command)
        del apps[0][potential_deletes[to_be_deleted_ind]]

        with app_info_path.open(mode="w", encoding="utf-8") as write_file:
            json.dump(apps, write_file, indent=4)
        lcd.text("Deleted:", 1)
        lcd.text(potential_deletes[to_be_deleted_ind], 2)
        time.sleep(1)
    else:
        lcd.text("Cancel.", 2)
        time.sleep(0.5)
    restart()

elif selected == "Ej. ALL Disks":
    lcd.text("Includes SSD/HDD", 1)
    time.sleep(1)
    lcd.text("Continue?", 1)

    rotary_encoder.setup()
    res = rotary_encoder.loop(options) # 1 is y
    rotary_encoder.destroy()

    if res == 1:
        disk_path = Path("/media/moi")

        disk_directory = os.listdir(disk_path)

        if len(disk_directory) > 0:
            for disk in disk_directory:
                command = "sudo eject /media/moi/" + disk
                os.system(command)
            lcd.text("Disks ejected!", 2)
        else:
            lcd.text("None connected!", 2)
    else:
        lcd.text("  Thank God!", 2)

    time.sleep(1)
    restart()

elif selected == "Update":
    drive_path = Path("/media/moi/update/the_box")
    if drive_path.exists():
        lcd.text("Starting Update.", 1)
        time.sleep(2)
        lcd.text("Hold on to your", 1)
        lcd.text("    helmets!", 2)
        command = "sudo python /home/moi/update.py"
        os.system(command)
        exit("Updating.")
    else:
        lcd.clear()
        lcd.text("No Update Drive", 1)
        time.sleep(2)
        restart()

elif selected == "Mounted Disks":
    while True:
        lcd.clear()
        disks = os.listdir(Path("/media/moi"))
        if len(disks) == 0:
            lcd.text("None Connected.", 2)
            time.sleep(2)
            restart()

        disks.append("Back")
        lcd.text("Mounted Disks:", 1)
        rotary_encoder.setup()
        selected = rotary_encoder.loop(disks)
        rotary_encoder.destroy()
        time.sleep(0.5)

        if disks[selected] == "Back":
            restart()

        else:
            lcd.text(disks[selected], 1)
            disk_path = Path("/media/moi") / disks[selected]
            size_gb = round(card_data(disk_path)[0] / 1000 / 1000 / 1000, 2)
            used_gb = round(card_data(disk_path)[1] / 1000 / 1000 / 1000, 2)
            free_gb = round(card_data(disk_path)[2] / 1000 / 1000 / 1000, 2)

            display = [f"Size:{size_gb} GB", f"Used:{used_gb} GB", f"Free:{free_gb} GB"]

            rotary_encoder.setup()
            rotary_encoder.loop(display)
            rotary_encoder.destroy()

            restart()

elif selected == "Show Time":
    lcd.clear()
    lcd.text("No rtc!", 1)

    '''setup_button()
    time.sleep(0.5)
    lcd.clear()
    change_timer = 60 - datetime.now().second
    lcd.text("----THE TIME----", 1)
    while show_me_time:
        start_time = time.perf_counter()
        text = "-->  " + str(datetime.now().time().replace(microsecond=0))[:-3] + "  <---"
        lcd.text(text, 2)
        while time.perf_counter() - start_time < change_timer and show_me_time:
            time.sleep(1)

        change_timer = 60

    GPIO.cleanup()
    restart()'''

# home & error
time.sleep(0.1)
lcd.clear()

os.system("sudo python -m the_box.main")
exit()
