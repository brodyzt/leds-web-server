#!flask/bin/python

from flask import Flask, jsonify, render_template, request
from flask_restful import Resource, Api
import thread
import pigpio
import time

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


last_color = {RED_PIN: 0,
              GREEN_PIN:0,
              BLUE_PIN:0 }

def setPins(red, green, blue):
    global is_off, last_color
    if not is_off:
        pi.set_PWM_dutycycle(RED_PIN, red)
        pi.set_PWM_dutycycle(GREEN_PIN, green)
        pi.set_PWM_dutycycle(BLUE_PIN, blue)
    if not (red == 0 and green == 0 and blue == 0):
        last_color[RED_PIN] = red
        last_color[GREEN_PIN] = green
        last_color[BLUE_PIN] = blue


def setPin(pin, brightness):
    global is_off, last_color
    if not is_off:
        pi.set_PWM_dutycycle(pin, brightness)
        last_color[pin] = brightness



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
    mode = "fade"
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
    global last_color, mode, is_off
    is_off = False
    if mode == "static":
        setPins(last_color[RED_PIN],last_color[GREEN_PIN],last_color[BLUE_PIN])
    return "Done"

@app.route("/turnOff", methods=['PUT'])
def execute_turn_off():
    global mode, is_off
    is_off = True
    pi.set_PWM_dutycycle(RED_PIN, 0)
    pi.set_PWM_dutycycle(GREEN_PIN, 0)
    pi.set_PWM_dutycycle(BLUE_PIN, 0)
    return "Done"


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0")


