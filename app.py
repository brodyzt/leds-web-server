#!flask/bin/python

from flask import Flask, jsonify, render_template, request
from flask_restful import Resource, Api
import thread
import pigpio
import time

RED_PIN = 15
GREEN_PIN = 18
BLUE_PIN = 14

pi = pigpio.pi()

app = Flask(__name__)
api = Api(app)

mode = "static"

def setPin(pin, brightness):
    pi.set_PWM_dutycycle(pin, brightness)

class Color():
    def __init__(self, name="", red=0, green=0, blue=0):
        self.name = name
        self.red = str(red)
        self.green = str(green)
        self.blue = str(blue)

myColor = Color("color", 100, 100, 100)
myColors = {"color": myColor}

@app.route("/setColor", methods=['PUT'])
def put():
    mode = "static"
    setPin(RED_PIN, request.get_json()['red'])
    setPin(GREEN_PIN, request.get_json()['green'])
    setPin(BLUE_PIN, request.get_json()['blue'])
    print("Color Set")
    return "Complete"

@app.route("/flash", methods=['PUT'])
def flash():
    state = "ON"
    mode = "flash"
    while mode == "flash":
        if state == "OFF":
            setPin(RED_PIN, 255)
            setPin(GREEN_PIN, 255)
            setPin(BLUE_PIN, 255)
            state = "ON"

        else:
            setPin(RED_PIN, 0)
            setPin(GREEN_PIN, 0)
            setPin(BLUE_PIN, 0)
            state = "OFF"
        time.sleep(1)
    return "Flash Complete"

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0")


