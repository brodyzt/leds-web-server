#!flask/bin/python

from flask import Flask, jsonify, render_template, request
from flask_restful import Resource, Api
import thread
import RPi.GPIO as GPIO

RED_PIN = 15
GREEN_PIN = 18
BLUE_Pin = 14

channel_list = [RED_PIN, GREEN_PIN, BLUE_Pin]

GPIO.setup(channel_list, GPIO.OUT)
GPIO.setmode(GPIO.BOARD)

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
class ColorAPI(Resource):
    def put(self, color):
        GPIO.output(RED_PIN, request.get_json()['red'])
        GPIO.output(GREEN_PIN, request.get_json()['green'])
        GPIO.output(BLUE_Pin, request.get_json()['blue'])
        print("Color Set")


if __name__ == '__main__':
    app.run(debug=True)


