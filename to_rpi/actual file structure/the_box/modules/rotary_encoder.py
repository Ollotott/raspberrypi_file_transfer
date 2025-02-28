import time
import RPi.GPIO as GPIO
from rpi_lcd import LCD

lcd = LCD()
RoAPin = 7  # CLK Pin
RoBPin = 18  # DT Pin
BtnPin = 15  # Button Pin
BtnPin2 = 29  # Extra button

globalCounter = 0
back = False
select = False
flag = 0
Last_RoB_Status = 0
Current_RoB_Status = 0


def setup():
    GPIO.setmode(GPIO.BOARD)  # Numbers GPIOs by physical location
    GPIO.setup(RoAPin, GPIO.IN)  # input mode
    GPIO.setup(RoBPin, GPIO.IN)
    GPIO.setup(BtnPin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(BtnPin2, GPIO.IN, pull_up_down=GPIO.PUD_UP)


def rotaryDeal():
    global flag
    global Last_RoB_Status
    global Current_RoB_Status
    global globalCounter
    Last_RoB_Status = GPIO.input(RoBPin)
    while not GPIO.input(RoAPin):
        Current_RoB_Status = GPIO.input(RoBPin)
        flag = 1
    if flag == 1:
        flag = 0
        if (Last_RoB_Status == 0) and (Current_RoB_Status == 1):
            globalCounter = globalCounter + 1
        if (Last_RoB_Status == 1) and (Current_RoB_Status == 0):
            globalCounter = globalCounter - 1


def btnISR(channel):
    global select
    select = True


def btn2check(channel):
    global back
    back = True


def loop(options):
    global back
    global select
    global globalCounter

    lcd_options = []
    for item in options:
        if type(item) != 'str':
            lcd_options.append(str(item))
        else:
            lcd_options.append(item)

    globalCounter = 0

    tmp = 0  # Rotary Temporary

    GPIO.add_event_detect(BtnPin, GPIO.FALLING, callback=btnISR)  # checks the integrated button
    GPIO.add_event_detect(BtnPin2, GPIO.FALLING, callback=btn2check)  # checks the extra button

    display = str(globalCounter + 1) + " " + lcd_options[globalCounter]
    lcd.text(display, 2)
    while True:
        rotaryDeal()

        # keeps counter within limits
        if globalCounter < 0:
            globalCounter = len(lcd_options) + globalCounter
        elif globalCounter > (len(lcd_options) - 1):
            globalCounter = globalCounter - len(lcd_options)

        if tmp != globalCounter:
            print(globalCounter, lcd_options[globalCounter])
            tmp = globalCounter
            display = str(globalCounter + 1) + " " + lcd_options[globalCounter]
            lcd.text(display, 2)
        elif select:
            lcd.clear()
            select = False
            print("Select")
            return globalCounter
        elif back:
            lcd.clear()
            back = False
            print("Btn2")
            return -1


def get_section(options, section_length):
    final = []
    while len(options) > 0:
        try:
            final.append(options[:section_length])
            options = options[section_length:]
        except IndexError:
            final.append(options)
            options = ""
    return final


def to_be_shown(options, current_pos, highlights=("<", ">")):
    section_to_show = int(current_pos / len(options[0]))
    character = current_pos - section_to_show * len(options[0])
    res = options[section_to_show][:character] + highlights[0] + options[section_to_show][character] + highlights[1] + options[section_to_show][character+1:]
    return res


def write(pre_prompt, letter_options="abcdefghijklmnopqrstuvwxyz.!?,_D", section_length=10):
    global back
    global select
    global globalCounter

    time.sleep(0.5)

    globalCounter = 0
    tmp = 0  # Rotary Temporary
    final_text = pre_prompt + " "

    options = get_section(letter_options, section_length)

    GPIO.add_event_detect(BtnPin2, GPIO.FALLING, callback=btn2check)  # checks the extra button
    GPIO.add_event_detect(BtnPin, GPIO.FALLING, callback=btnISR)  # checks the integrated button

    lcd.text(to_be_shown(options, globalCounter), 2)
    while True:

        rotaryDeal()

        # keeps counter within limits
        if globalCounter < 0:
            globalCounter = len(letter_options) + globalCounter
        elif globalCounter > (len(letter_options) - 1):
            globalCounter = globalCounter - len(letter_options)

        if tmp != globalCounter:
            tmp = globalCounter

            # shows the "keyboard"
            print(to_be_shown(options, globalCounter))
            display = to_be_shown(options, globalCounter)
            lcd.text(display, 2)

        elif select:
            if letter_options[globalCounter] == "D":
                final_text = final_text[:-1]
            else:
                final_text += letter_options[globalCounter]

            if len(final_text) > 16:
                display = final_text[-15:]
            else:
                display = final_text

            lcd.text(display, 1)

            # "resets" the rotary encoder button
            time.sleep(0.25)
            select = False

        elif back:
            lcd.clear()
            back = False
            print("Btn2")
            return final_text.replace("_", " ")


def show_text(original_text, preset_global_counter=0):
    global globalCounter
    global select
    global back
    select = False
    back = False
    globalCounter = preset_global_counter
    tmp = globalCounter

    lines = get_section(original_text, 16)

    lines.insert(0, "---> START")
    lines.append("***END***")

    lcd.text(lines[0], 1)
    lcd.text(lines[1], 2)

    GPIO.add_event_detect(BtnPin, GPIO.FALLING, callback=btnISR)  # checks the integrated button
    GPIO.add_event_detect(BtnPin2, GPIO.FALLING, callback=btn2check)  # checks the extra button

    while True:
        rotaryDeal()

        # keeps counter within limits
        if globalCounter < 0:
            globalCounter = len(lines) - 2
        elif globalCounter > len(lines) - 2:
            globalCounter = 0

        if tmp != globalCounter:
            tmp = globalCounter

            # shows text
            lcd.text(lines[globalCounter], 1)
            lcd.text(lines[globalCounter + 1], 2)

        elif select:
            return True, globalCounter
        elif back:
            return False, 0


def destroy():
    GPIO.cleanup()  # Release resource


if __name__ == '__main__':  # Program start from here
    setup()
    try:
        oui = ["hi!"]
        loop(oui)
    except KeyboardInterrupt:  # When 'Ctrl+C' is pressed, the child program destroy() will be  executed.
        destroy()
