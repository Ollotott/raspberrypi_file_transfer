from ..modules import rotary_encoder
from rpi_lcd import LCD
from pathlib import Path
import shutil
import os
from datetime import date
import json
import time


lcd = LCD()


def back_to_home():
    lcd.clear()
    os.system("sudo python -m the_box.main")
    exit("home")


def end_all(why):
    lcd.text("END:", 1)
    lcd.text(why, 2)
    print(why)
    back_to_home()


def restart():
    os.system("sudo python -m the_box.programs.Transfer")
    lcd.clear()
    exit("Restart/Back")


def shared_items(possible_drives, connected_drives):
    """First the possible items, then the ones that are connected!"""
    res = []
    for item in connected_drives:
        if item in possible_drives or item.lower() in possible_drives or item.upper() in possible_drives:
            res.append(item)
    return res


def get_directory_size(directory):
    """Returns the `directory` size in bytes."""
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


def get_free_card_space(card_path):
    card_path = str(card_path)
    return list(shutil.disk_usage(card_path))[2]


time.sleep(1)

lcd.text("Transfer", 1)

pi_usr_name = "moi"
storage_directory = Path(f"/home/{pi_usr_name}/the_box/programs")

# make file for times
time_file = storage_directory / "average_time.json"
if not time_file.exists():
    lcd.text("Make time file", 2)
    time_file.touch()
    with time_file.open(mode="w", encoding="utf-8") as file:
        clean = [40, 1]
        json.dump(clean, file)

# get the current date
date_file = storage_directory / "today.json"
if not date_file.exists():
    date_file.touch()
    time.sleep(1)
    lcd.clear()

    months = ["01", "02", "03", "04", "05", "06", "07", "08", "09", "10", "11", "12"]
    lcd.text("Current Month:", 1)
    rotary_encoder.setup()
    month = months[rotary_encoder.loop(months)]
    rotary_encoder.destroy()
    time.sleep(0.5)

    days = ['01', '02', '03', '04', '05', '06', '07', '08', '09',
            '10', '11', '12', '13', '14',
            '15', '16', '17', '18', '19', '20', '21', '22',
            '23', '24', '25', '26', '27', '28', '29', '30', '31']
    lcd.text("Current day:", 1)
    rotary_encoder.setup()
    day = days[rotary_encoder.loop(days)]
    rotary_encoder.destroy()
    time.sleep(0.5)

    with date_file.open(mode="w", encoding="utf-8") as file:
        json.dump((month, day), file)

else:
    # get last date
    with date_file.open(mode="r", encoding="utf-8") as read_file:
        potential_day = json.load(read_file)
    lcd.text("Check date!", 1)
    time.sleep(1)

    display = f"Today: {potential_day[0]}/{potential_day[1]}?"
    lcd.text(display, 1)

    rotary_encoder.setup()
    if rotary_encoder.loop(("Yes", "No")) == 1:
        rotary_encoder.destroy()
        day_choices = []
        for day in range(int(potential_day[0]), 32):
            day_choices.append(day)
        for day in range(1, int(potential_day[0])):
            day_choices.append(day)

        lcd.text("Specify Day:", 1)
        rotary_encoder.setup()
        current_day = day_choices[rotary_encoder.loop(day_choices)]
        rotary_encoder.destroy()

        month_choices = []
        for month in range(int(potential_day[1]), 13):
            month_choices.append(month)
        for month in range(1, int(potential_day[1])):
            month_choices.append(month)

        lcd.text("Specify Month:", 1)
        rotary_encoder.setup()
        current_month = month_choices[rotary_encoder.loop(month_choices)]
        rotary_encoder.destroy()

        with date_file.open(mode="w", encoding="utf-8") as file:
            json.dump((current_day, current_month), file)

    else:
        rotary_encoder.destroy()
    time.sleep(0.5)

with date_file.open(mode="r", encoding="utf-8") as file:
    res = json.load(file)
    current_day = res[0]
    current_month = res[1]

# get times
with time_file.open(mode="r", encoding="utf-8") as file:
    time_file_contents = json.load(file)


mount_point = Path(f"/media/{pi_usr_name}")
drive_names_path = storage_directory / "backup_drives.json"

entries = os.listdir(mount_point)

# import master files
if "MASTER" in entries:
    time.sleep(5)

    # copies drives
    new_path = mount_point / "MASTER" / "backup_drives.json"
    shutil.copy(new_path, drive_names_path.parents[0])

    lcd.text("Copied Master.", 2)
    time.sleep(2)

    os.system("sudo eject /media/moi/MASTER")

    lcd.text("Ejected Master.", 2)
    time.sleep(1)
    restart()

# import contents from master files
try:
    with drive_names_path.open(mode="r", encoding="utf-8") as read_file:
        drive_list = json.load(read_file)


except FileNotFoundError:
    lcd.text("No known Drives", 1)
    time.sleep(1)
    rotary_encoder.setup()
    rotary_encoder.loop(["Dang."])
    rotary_encoder.destroy()
    time.sleep(2)
    back_to_home()


# ------------------------------ GO! ------------------------------------------------------------

# sd names and drive path
while True:
    # get names of connected drives
    try:
        connected_drive_path = mount_point / shared_items(drive_list, entries)[0]

    except IndexError:
        time.sleep(2)
        lcd.text("No drive!", 1)

        rotary_encoder.setup()
        res = rotary_encoder.loop(["Restart", "Quit"])
        rotary_encoder.destroy()

        if res == 0:
            restart()
        else:
            back_to_home()

    # finds connected sds
    connected_sd = []
    for item in entries:
        if item != shared_items(drive_list, entries)[0]:
            connected_sd.append(item)

    if len(connected_sd) == 0:
        time.sleep(1)
        lcd.text("No Sd!", 1)

        rotary_encoder.setup()
        res = rotary_encoder.loop(["Restart", "Quit"])
        rotary_encoder.destroy()

        if res == 0:
            restart()
        else:
            back_to_home()
    break

if len(connected_sd) > 1:
    print(connected_sd)
    time.sleep(1)
    lcd.text("Specify order?", 1)

    rotary_encoder.setup()
    res = rotary_encoder.loop(["No", "Yes", "Home"])  # y is 1
    rotary_encoder.destroy()

    if res == 1:
        lcd.text("Specify order.", 1)
        time.sleep(1)
        new_order = []
        for current_index in range(0, len(connected_sd)):
            lcd.text(f"Nr {current_index + 1}:", 1)
            rotary_encoder.setup()
            res = rotary_encoder.loop(connected_sd)
            rotary_encoder.destroy()

            new_order.append(connected_sd[res])
            connected_sd.pop(res)
            time.sleep(0.5)

        connected_sd = new_order
    elif res == -1 or res == 2:
        back_to_home()

est_time = 0
for sd in connected_sd:
    est_time += round(get_directory_size(mount_point / sd / 'DCIM') / 10 ** 6 / time_file_contents[0] / 60, 5)
lcd.text(f"ETA {round(est_time, 1)} Min", 2)
time.sleep(3)

today_tag = f"{current_day}-{current_month}"
# creates folder for current date, if needed
today_folder = connected_drive_path / today_tag
today_folder.mkdir(exist_ok=True)

start_all = time.perf_counter()

# copy
text = ""
avg_this_run = [0, 0]
try:
    for sd_name in connected_sd:
        drive_folder_path = today_folder / sd_name
        drive_folder_path.mkdir(exist_ok=True)
        drive_folder_path = drive_folder_path / f"Transfer {len(os.listdir(drive_folder_path))}"

        sd_path = mount_point / sd_name / "DCIM"

        # checks that the drive has enough space
        if get_free_card_space(connected_drive_path) < get_directory_size(sd_path):
            exit("Not enough space on drive!")

        start = time.perf_counter()
        shutil.copytree(sd_path, drive_folder_path)

        avg_this_run[0] += get_directory_size(sd_path) / 10 ** 6 / (time.perf_counter() - start)
        avg_this_run[1] += 1

        command_for_eject = f"sudo eject {str(mount_point / sd_name)}"
        os.system(command_for_eject)

        text = text + sd_name[:1]
        lcd.text(text, 1)

except FileNotFoundError:
    lcd.text("Card/Drive Gone!", 1)
    time.sleep(0.5)

    rotary_encoder.setup()
    res = rotary_encoder.loop(["Restart", "Quit"])
    rotary_encoder.destroy()

    if res == 0:
        lcd.text("Restarting...", 2)
        time.sleep(1)
        restart()
    else:
        lcd.text("Quitting...", 2)
        time.sleep(1)
        back_to_home()

# writes new average
with time_file.open(mode="w", encoding="utf-8") as file:
    try:
        new = [(time_file_contents[0] * time_file_contents[1] + (avg_this_run[0] / avg_this_run[1])) / (
            (time_file_contents[1] + avg_this_run[1])), (time_file_contents[1] + avg_this_run[1])]
    except ZeroDivisionError:
        new = time_file_contents

    json.dump(new, file)

lcd.text(f"Done {round((time.perf_counter() - start_all)  / 60, 1)}Min", 1)

rotary_encoder.setup()
res = rotary_encoder.loop(["Ok", "Who cares?"])
rotary_encoder.destroy()

if res == 1:
    lcd.text("  Woa. Chill.", 1)
    time.sleep(1)

back_to_home()
