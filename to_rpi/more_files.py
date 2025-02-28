import os
import time

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


start_time = time.perf_counter()

try:
    while time.perf_counter() - start_time < (60 * int(input("Monitor for how long?"))):
        print(get_directory_size("/media/moi/'IHNO DRIVE I - 1TB'/IMAC/IMAC") / 1000 / 1000)
        time.sleep(10)
except ValueError:
    pass
