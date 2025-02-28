import time
from ..modules import rotary_encoder
from rpi_lcd import LCD
import socket
import json
from pathlib import Path
import os
import subprocess


def restart():
    os.system("sudo python -m the_box.programs.LLM")
    lcd.clear()
    exit("Restart/Back")


# Set up the client socket
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect(('10.20.1.80', 12345))  # pi 5 ip address


lcd = LCD()

save_path = Path("/home/moi/the_box/programs/llm_base_prompt.json")
display_txt_file = Path("/home/moi/the_box/programs/llm_display_text.txt")

# creates the pre-prompts
if not save_path.exists():
    save_path.touch(exist_ok=True)

    standard_base_prompts = ["How much ", "When is ", "When was ", "How do I ", "Tell me about ", "What is ", "Add", "Remove", "/bye"]

    with save_path.open(mode="w", encoding="utf-8") as json_write:
        json.dump(standard_base_prompts, json_write)

display_txt_file.touch(exist_ok=True)

while True:
    # makes a clean version of the text file
    with display_txt_file.open(mode="w", encoding="utf-8") as write_txt:
        write_txt.write("")
    # get pre-prompts from save
    with save_path.open(mode="r", encoding="utf-8") as read_json:
        pre_prompts = json.load(read_json)

    # gets the user to choose a pre-prompt
    rotary_encoder.setup()
    chosen_pre_prompt = pre_prompts[rotary_encoder.loop(pre_prompts)]
    rotary_encoder.destroy()
    time.sleep(0.25)

    # "maintenance"
    if chosen_pre_prompt == "Add":
        lcd.clear()
        lcd.text("Add new prompt!", 1)
        lcd.text("Cancels if Empty", 2)
        time.sleep(2)

        # get the new pre-prompt!
        rotary_encoder.setup()
        new_pre_prompt = rotary_encoder.write()
        rotary_encoder.destroy()

        if not new_pre_prompt == "":
            pre_prompts.insert(-2, new_pre_prompt)

            with save_path.open(mode="w", encoding="utf-8") as json_write:
                json.dump(pre_prompts, json_write)

        time.sleep(0.5)
        lcd.text("Done!", 1)
        lcd.text("", 2)
        time.sleep(1)
        restart()
    elif chosen_pre_prompt == "Remove":
        lcd.text("What to remove?", 1)
        rotary_encoder.setup()
        to_be_removed = rotary_encoder.loop(pre_prompts[0:-2])
        rotary_encoder.destroy()

        if not to_be_removed == -1:
            pre_prompts.pop(to_be_removed)
            with save_path.open(mode="w", encoding="utf-8") as json_write:
                json.dump(pre_prompts, json_write)
            time.sleep(0.5)
            lcd.clear()
            lcd.text("Removed!", 1)
        else:
            lcd.text("Cancelled.", 1)
        time.sleep(1)
        restart()

    if chosen_pre_prompt == "/end":
        client_socket.send("/end".encode())
        break

    # usr writes prompt
    rotary_encoder.setup()
    prompt = rotary_encoder.write(chosen_pre_prompt)
    rotary_encoder.destroy()

    # send res via socket to 10.20.1.80
    client_socket.send(prompt.encode())

    # get result from socket and display it.
    llm_received = ""
    last_transfer = time.perf_counter()

    process = subprocess.Popen(["sudo", "python", "-m", "the_box.programs.LLM"])

    # gets the answer and places them in the txt file.
    while True:
        temporary_receive = client_socket.recv(1024).decode()
        if temporary_receive == "ans-end":
            with display_txt_file.open(mode="w", encoding="utf-8") as write_txt:
                write_txt.write(llm_received)
            break

        else:
            llm_received += temporary_receive
            if time.perf_counter() - last_transfer > 2:
                last_transfer = time.perf_counter()
                with display_txt_file.open(mode="w", encoding="utf-8") as write_txt:
                    write_txt.write(llm_received)

    process.wait()

    lcd.text("Exit?", 1)
    rotary_encoder.setup()
    leave = rotary_encoder.loop(("Yes", "No"))
    rotary_encoder.destroy()

    if leave != 1:
        break


client_socket.close()
