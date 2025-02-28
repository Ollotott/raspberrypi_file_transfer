import time
from ..modules import rotary_encoder
from rpi_lcd import LCD
from pathlib import Path

lcd = LCD()

txt_file = Path("/home/moi/the_box/programs/llm_display_text.txt")
global_counter = 0

print("Running Display!")
while True:
    with txt_file.open(mode="r", encoding="utf-8") as readfile:
        tmp_text = readfile.read()
    if tmp_text == "":
        lcd.text("---", 1)
        time.sleep(0.25)
        lcd.text("+--", 1)
        time.sleep(0.25)
        lcd.text("-+-", 1)
        time.sleep(0.25)
        lcd.text("--+", 1)
        time.sleep(0.25)
    else:
        break

while True:
    with txt_file.open(mode="r", encoding="utf-8") as readfile:
        display_text = readfile.read()

    print(display_text)

    rotary_encoder.setup()
    go_on, global_counter = rotary_encoder.show_text(display_text, global_counter)
    rotary_encoder.destroy()

    if go_on:
        continue
    else:
        break

exit("Exited displaying text!")
