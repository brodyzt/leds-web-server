#!flask/bin/python

from flask import Flask, jsonify, render_template, request
from flask_restful import Resource, Api
import thread
import pigpio

RED_PIN = 15
GREEN_PIN = 18
BLUE_PIN = 14

pi = pigpio.pi()

app = Flask(__name__)
api = Api(app)

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
    pi.set_PWM_dutycycle(RED_PIN, request.get_json()['red'])
    pi.set_PWM_dutycycle(GREEN_PIN, request.get_json()['green'])
    pi.set_PWM_dutycycle(BLUE_PIN, request.get_json()['blue'])
    print("Color Set")
    return "Complete"


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0")


