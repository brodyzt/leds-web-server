#!flask/bin/python

from flask import Flask, jsonify, render_template, request
from flask_restful import Resource, Api
import thread
import pigpio
import time
from copy import copy

RED_PIN = 15
GREEN_PIN = 18
BLUE_PIN = 14

STEPS = .1
FLASH_SPEED = 1

pi = pigpio.pi()

app = Flask(__name__)
api = Api(app)

mode = "static"
is_off = False


current_color = {RED_PIN: 0,
                 GREEN_PIN:0,
                 BLUE_PIN:0}

stored_color = current_color.copy()

def setPins(red, green, blue):
    global is_off, current_color, stored_color
    if not is_off:
        pi.set_PWM_dutycycle(RED_PIN, red)
        pi.set_PWM_dutycycle(GREEN_PIN, green)
        pi.set_PWM_dutycycle(BLUE_PIN, blue)
    if (red == 0 and green == 0 and blue == 0):
        stored_color = current_color.copy()
    current_color[RED_PIN] = red
    current_color[GREEN_PIN] = green
    current_color[BLUE_PIN] = blue



def setPin(pin, brightness):
    global is_off, current_color
    if not is_off:
        pi.set_PWM_dutycycle(pin, brightness)
        current_color[pin] = brightness

def fadeToColor(red, green, blue):
    global current_color
    fadeTime = 30000000.0
    redStep = (red - current_color[RED_PIN]) / fadeTime
    greenStep = (green - current_color[GREEN_PIN]) / fadeTime
    blueStep = (blue - current_color[BLUE_PIN]) / fadeTime
    for i in range(0, int(fadeTime)):
        setPins(current_color[RED_PIN]+redStep,current_color[GREEN_PIN]+greenStep,current_color[BLUE_PIN]+blueStep)

@app.route("/color", methods=['PUT'])
def returnColor():
    global current_color
    return {
            "Red": current_color[RED_PIN],
            "Green": current_color[GREEN_PIN],
            "Blue": current_color[BLUE_PIN]
        }

@app.route("/setColor", methods=['PUT'])
def put():
    global mode
    mode = "static"
    setPins(request.get_json()['red'],request.get_json()['green'],request.get_json()['blue'])
    print("Color Set")
    print(mode)
    return "Complete"

def flash():
    state = "ON"
    global mode
    mode = "flash"
    while mode == "flash":
        print(mode)
        if state == "OFF":
            setPins(255, 255, 255)
            state = "ON"
        else:
            setPins(0, 0, 0)
            state = "OFF"
        time.sleep(FLASH_SPEED)

@app.route("/flash", methods=['PUT'])
def execute_flash():
    thread.start_new_thread(flash, ())
    return "Flash Complete"

@app.route("/updateFlashSpeed", methods=['PUT'])
def execute_update_flash_speed():
    global FLASH_SPEED
    FLASH_SPEED = request.get_json()['FLASH_SPEED'] / 50.0
    return "Updated"

@app.route("/stopFlash", methods=['PUT'])
def execute_stop_flash():
    global mode
    if mode == "flash":
        mode="static"
    return "Done"

def updateColor(color, step):
    color += step

    if color > 255:
        return 255
    if color < 0:
        return 0

    return color

def fade():
    r = 255
    g = 0
    b = 100
    state = "ON"
    global mode
    while mode == "fade":
        if r == 255 and b == 0 and g < 255:
            g = updateColor(g, STEPS)
            setPin(GREEN_PIN, g)

        elif g == 255 and b == 0 and r > 0:
            r = updateColor(r, -STEPS)
            setPin(RED_PIN, r)

        elif r == 0 and g == 255 and b < 255:
            b = updateColor(b, STEPS)
            setPin(BLUE_PIN, b)

        elif r == 0 and b == 255 and g > 0:
            g = updateColor(g, -STEPS)
            setPin(GREEN_PIN, g)

        elif g == 0 and b == 255 and r < 255:
            r = updateColor(r, STEPS)
            setPin(RED_PIN, r)

        elif r == 255 and g == 0 and b > 0:
            b = updateColor(b, -STEPS)
            setPin(BLUE_PIN, b)

        else:
            b = updateColor(b, -STEPS)
            g = updateColor(g, STEPS)
            setPin(BLUE_PIN, b)
            setPin(GREEN_PIN, g)


@app.route("/fade", methods=['PUT'])
def execute_fade():
    global mode
    if(mode != "fade"):
        mode = "fade"
        thread.start_new_thread(fade, ())
    return "Flash Complete"

@app.route("/updateFadeSpeed", methods=['PUT'])
def execute_update_fade_speed():
    global STEPS
    STEPS = request.get_json()['STEPS'] / 1000.0
    return "Updated"

@app.route("/stopFade", methods=['PUT'])
def execute_stop_fade():
    global mode
    if mode == "fade":
        mode="static"
    return "Done"

@app.route("/turnOn", methods=['PUT'])
def execute_turn_on():
    global current_color, mode, is_off, stored_color
    is_off = False
    if mode == "static":
        fadeToColor(stored_color[RED_PIN], stored_color[GREEN_PIN], stored_color[BLUE_PIN])
    return "Done"

@app.route("/turnOff", methods=['PUT'])
def execute_turn_off():
    global mode, is_off
    stored_color = current_color.copy()
    fadeToColor(0,0,0)
    is_off = True
    return "Done"


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0")


