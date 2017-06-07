#!flask/bin/python

from flask import Flask, jsonify, render_template, request
from flask_restful import Resource, Api
import thread
import time
from copy import copy
from math import ceil

RED_PIN = 15
GREEN_PIN = 18
BLUE_PIN = 14

STEPS = .1
FLASH_SPEED = 1


app = Flask(__name__)
api = Api(app)

mode = "static"
is_off = False

last_color = {RED_PIN: 0,
              GREEN_PIN:0,
              BLUE_PIN:0 }

redVal = 0
greenVal = 0
blueVal = 0

def setPins(red, green, blue):
    if red > 255:
        red = 255
    if red < 0:
        red = 0
    if green > 255:
        green = 255
    if green < 0:
        green = 0
    if blue > 255:
        blue = 255
    if blue < 0:
        blue = 0

    global is_off, last_color
    if not is_off:
        global redVal, greenVal, blueVal
        redVal = red
        greenVal = green
        blueVal = blue
    if not (ceil(red) == 0 and ceil(green) == 0 and ceil(blue) == 0):
        last_color[RED_PIN] = red
        last_color[GREEN_PIN] = green
        last_color[BLUE_PIN] = blue

'''def colorsAreClose(r1,g1,b1,r2,g2,b2,threshold):
    return r1+g1+b1-r2-g2-b2 < threshold'''

def fadeToColor(red, green, blue):
    fadeTime = 300000.0
    redStep = (red - redVal) / fadeTime
    greenStep = (green - greenVal) / fadeTime
    blueStep = (blue - blueVal) / fadeTime
    for i in range(0, int(fadeTime)):
        setPins(redVal+redStep,greenVal+greenStep,blueVal+blueStep)

def setPin(pin, brightness):
    global is_off, last_color, redVal, greenVal, blueVal
    if brightness > 255:
        brightness = 255
    if brightness < 0:
        brightness = 0
    if not is_off:
        if pin == RED_PIN:
            redVal = brightness
        if pin == GREEN_PIN:
            greenVal = brightness
        if pin == BLUE_PIN:
            blueVal = brightness
        last_color[pin] = brightness

@app.route("/color", methods=['GET'])
def returnColor():
    global last_color, redVal, greenVal, blueVal
    return jsonify({"color":{"Red": redVal, "Green": greenVal, "Blue": blueVal}})

@app.route("/setColor", methods=['PUT'])
def put():
    global mode
    mode = "static"
    red = request.get_json()['red']
    green = request.get_json()['green']
    blue = request.get_json()['blue']
    thread.start_new_thread(fadeToColor, (red,green,blue))
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

def fadeOn():
    fadeToColor(last_color[RED_PIN],last_color[GREEN_PIN],last_color[BLUE_PIN])

@app.route("/turnOn", methods=['PUT'])
def execute_turn_on():
    global is_off
    is_off = False
    if mode == "static":
        print last_color
        thread.start_new_thread(fadeOn, ())
    return "Done"

def setPinsForOff(red, green, blue):
    if red > 255:
        red = 255
    if red < 0:
        red = 0
    if green > 255:
        green = 255
    if green < 0:
        green = 0
    if blue > 255:
        blue = 255
    if blue < 0:
        blue = 0

    global is_off, last_color
    global redVal, greenVal, blueVal
    redVal = red
    greenVal = green
    blueVal = blue

def fadeOff():
    global last_color, is_off
    temp = copy(last_color)

    fadeTime = 300000.0
    redStep = (-redVal) / fadeTime
    greenStep = (-greenVal) / fadeTime
    blueStep = (-blueVal) / fadeTime
    for i in range(0, int(fadeTime)):
        setPinsForOff(redVal + redStep, greenVal + greenStep, blueVal + blueStep)

    last_color = temp

@app.route("/turnOff", methods=['PUT'])
def execute_turn_off():
    is_off = True
    thread.start_new_thread(fadeOff, ())
    return "Done"


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0")


