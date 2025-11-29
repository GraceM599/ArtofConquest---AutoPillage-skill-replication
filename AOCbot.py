import ctypes
from operator import truediv

import mss
import mss.tools
import win32gui
import os
import cv2
import numpy as np
import pyautogui
import time
import keyboard


#fix scaling issues
ctypes.windll.user32.SetProcessDPIAware()
os.makedirs("images", exist_ok=True)
screenshot_path = "images/aoc_image.png"
template_path = "images/game_screen.png"
#height to 698
if not os.path.isfile(template_path):
    raise Exception(f"Template not found at {template_path}")

hwnd = win32gui.FindWindow(None, "BlueStacks App Player")
if not hwnd:
    raise Exception("BlueStacks window not found")

client_left, client_top, client_right, client_bottom = win32gui.GetClientRect(hwnd)
left_top = win32gui.ClientToScreen(hwnd, (client_left, client_top))
right_bottom = win32gui.ClientToScreen(hwnd, (client_right, client_bottom))

global left, top
left, top= left_top
right, bottom = right_bottom
global width
width = right - left
global height
height = bottom - top
print(f"Window rectangle: left={left}, top={top}, width={width}, height={height}")

with mss.mss() as sct:
    monitor = {"top": top, "left": left, "width": width, "height": height}
    img = sct.grab(monitor)
    img_cv2 = np.array(img)
    mss.tools.to_png(img.rgb, img.size, output=screenshot_path)


client_rect = win32gui.GetClientRect(hwnd)
client_width = client_rect[2] - client_rect[0]
client_height = client_rect[3] - client_rect[1]
aspect_ratio = client_width / client_height

# Desired client height
desired_client_height = 698
desired_client_width = int(desired_client_height * aspect_ratio)

# Convert desired client size to outer window size
window_rect = win32gui.GetWindowRect(hwnd)
current_width = window_rect[2] - window_rect[0]
current_height = window_rect[3] - window_rect[1]
width_diff = current_width - client_width
height_diff = current_height - client_height

# Final window size
new_width = desired_client_width + width_diff
new_height = desired_client_height + height_diff

# Move/resize window
x, y = window_rect[0], window_rect[1]
win32gui.MoveWindow(hwnd, x, y, new_width, new_height, True)

#returns screen information of an element possibly on the image
def getUIElement(element):
    global template_gray
    img = getScreen()
    template = cv2.imread("images/" + element + ".png")
    template_gray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    res = cv2.matchTemplate(img_gray, template_gray, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)

    h, w = template_gray.shape
    local_cx = max_loc[0] + w // 2
    local_cy = max_loc[1] + h // 2
    screen_cx = left + local_cx
    screen_cy = top + local_cy
    if element == "exclamation_indicator":
        screen_cy += 100
    center = (screen_cx, screen_cy)
    if element == "moving_dot":
        print("\n")

    return {
        "confidence": max_val,
        "top_left": max_loc,
        "center": center,
        "shape": (w, h)
    }

def getAllUIElementsLocation(element):

    img = getScreen()
    template_path = f"images/{element}.png"
    template = cv2.imread(template_path)
    template_gray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    res = cv2.matchTemplate(img_gray, template_gray, cv2.TM_CCOEFF_NORMED)
    print("Max match:", np.max(res))
    loc = np.where(res >= 0.4)

    h, w = template_gray.shape

    points = []
    for pt in zip(*loc[::-1]):
        local_cx = pt[0] + w // 2
        local_cy = pt[1] + h // 2

        # convert to absolute screen coords
        screen_cx = left + local_cx
        screen_cy = top + local_cy

        points.append((screen_cx, screen_cy))
    print(str(points[0][0]))
    return points

def clickButton(button):
    button_info = getUIElement(button)
    while(button_info["confidence"] < 0.80):
        #print(button + str(button_info["confidence"]))

        button_info = getUIElement(button)

        if(button == "exclamation_indicator" and button_info["confidence"] > 0.35 and not isMoving()):
            pyautogui.click(button_info["center"])
            pyautogui.click(left + width // 2 + 200, top + height // 2 - 30)
            return
    time.sleep(.3)
    pyautogui.click(button_info["center"])


def getScreen():
    with mss.mss() as sct:
        monitor = {"top": top, "left": left, "width": width, "height": height}
        img = sct.grab(monitor)

    img = np.array(img)
    return img
def isMoving():
    movementDots = True if getUIElement("moving_dot")["confidence"] > 0.75 else False
    img1 = getScreen()
    time.sleep(0.5)
    img2 = getScreen()
    diff = cv2.absdiff(img1, img2)
    gray = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 25, 255, cv2.THRESH_BINARY)

    movement = np.sum(thresh) / 255
    #img1_gray = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
    #img2_gray = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)

    #res = cv2.matchTemplate(img1_gray, img2_gray, cv2.TM_CCOEFF_NORMED)
    #min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
    #print(str(max_val))
    if (movementDots and movement > 100000):
        # its probably at the top then and character has arrived
        return True
    return False
def clearDungeon():
    #click map
    #click dungeon symbol
    clickButton("map_button")
    clickButton("dungeon_marker")

    time.sleep(0.5)
    clickButton("go_button")
    #click go
    #wait till find exclamation mark
    while(getUIElement("exclamation_indicator")["confidence"] <= 0.50):
        continue
        if(getUIElement("purple_golem")["confidence"] > 0.90):
            attackGolem("purple_golem")
        if (getUIElement("grey_golem")["confidence"] > 0.90):
            attackGolem("purple_golem")
    while not isMoving():
        time.sleep(0.1)
    clickButton("exclamation_indicator")
    #click under exclamation mark
    clickButton("enter_button")
    print("Clicked enter button")
    #click enter
    #click attack
    clickButton("attack_button")
    #wait till "red fight" button visible
    #click preset
    time.sleep(4)
    clickButton("preset_button")
    #click last
    clickButton("last_preset_button")
    time.sleep(3)
    #wait x seconds or until green fight button
    #Press green fight button
    clickButton("green_fight_button")
    #Wait till victory screen (where ok button is)
    clickButton("green_okay_button")
    clickButton("green_okay_button")
    while(getUIElement("castle_button")["confidence"] < 0.8):
        clickButton("green_okay_button")

    #press green okay
    #press orange okay
    #press blue okay
    #press green okay
    return True
    pass

def attackGolem(golem_type):
    clickButton(golem_type)
    clickButton("attack_button")
    # wait till "red fight" button visible
    # click preset
    clickButton("preset_button")
    time.sleep(0.3)
    # click last
    if(getUIElement("last_preset_button")["confidence"] < 0.8):
        clickButton("preset_button")
    clickButton("last_preset_button")
    time.sleep(3)
    # wait x seconds or until green fight button
    # Press green fight button
    clickButton("green_fight_button")
    clickButton("green_fight_button")

    # Wait till victory screen (where ok button is)
    while (getUIElement("castle_button")["confidence"] < 0.8):
        clickButton("green_okay_button")

def deliverWagon():
    clickButton("map_button")
    clickButton("resource_marker")

    time.sleep(0.5)
    clickButton("go_button")
    while (getUIElement("exclamation_indicator")["confidence"] <= 0.50):
        continue
        if (getUIElement("purple_golem")["confidence"] > 0.90):
            attackGolem("purple_golem")
        if (getUIElement("grey_golem")["confidence"] > 0.90):
            attackGolem("purple_golem")

    clickButton("exclamation_indicator")
    clickButton("deliver_button")
def dailyTasks():
    for i in range (4):

        clearDungeon()
        time.sleep(1)
    for i in range (4):
        deliverWagon()
        time.sleep(1)
    #transmute
    #tower challenge
    #claim tasks

#with mss.mss() as sct:
#    monitor = {"top": top, "left": left, "width": width, "height": height}
#    count = 0
#    while not (keyboard.is_pressed("q")):
#        if(keyboard.is_pressed("c")):
#            count += 1
#            img = sct.grab(monitor)
#            mss.tools.to_png(img.rgb, img.size, output= str("images/game_screen_" + str(count)))
#            print("Saved screenshot!")
def getScreenshots():
    with mss.mss() as sct:
        monitor = {"top": top, "left": left, "width": width, "height": height}
        count = 0
        while not (keyboard.is_pressed("q")):
            if(keyboard.is_pressed("c")):
                count += 1
                img = sct.grab(monitor)
                mss.tools.to_png(img.rgb, img.size, output= str("images/game_screen_" + str(count)))
                print("Saved screenshot!")
def tester():

    print(f"Saved BlueStacks capture to {screenshot_path}")

    screenshot = cv2.imread(screenshot_path)
    template = cv2.imread(template_path)

    if screenshot is None or template is None:
        raise Exception("Failed to load screenshot or template")

    screenshot_gray = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)
    template_gray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)

    res = cv2.matchTemplate(screenshot_gray, template_gray, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
    print(f"Max confidence: {max_val}")

    threshold = 0.5  # Adjust if necessary

    if max_val >= threshold:
        top_left = max_loc
        h, w = template_gray.shape
        bottom_right = (top_left[0] + w, top_left[1] + h)
        cv2.rectangle(screenshot, top_left, bottom_right, (0, 255, 0), 2)
        cv2.imshow("Identifications", screenshot)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    else:
        print("Template not found")

button = getUIElement("exclamation_indicator")
#print("Confidence that exclamation was found: " + str(button["confidence"]))

#getScreenshots()
#clickButton("map_button")
dailyTasks()
#if (button["confidence"] > 0.6):
#attackGolem("purple_golem")
#    pyautogui.click(button["center"])
