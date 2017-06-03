#!flask/bin/python

from flask import Flask, jsonify, render_template, request
from flask_restful import Resource, Api
import thread

app = Flask(__name__)
api = Api(app)

class Color():
    def __init__(self, name="", red=0, green=0, blue=0):
        self.name = name
        self.red = str(red)
        self.green = str(green)
        self.blue = str(blue)

    def json(self):
        return color_to_json(self)

purple = Color("Purple", 255,0,255)
turquoise = Color("Turquoise", 0,255,255)

def color_to_json(color):
    return {
        color.name: {
            "Red": color.red,
            "Green": color.green,
            "Blue": color.blue
        }
    }

myColor = Color("color", 100, 100, 100)
myColors = {"color": myColor}


class ColorAPI(Resource):
    def get(self, color_id):
        if color_id in myColors:
            return myColors[color_id].json()
        else:
            return Color("No Color Found",0,0,0).json()

    def put(self, color_id):
        myColors[color_id] = Color()
        myColors[color_id].name = color_id
        myColors[color_id].red = request.get_json()['red']
        myColors[color_id].green = request.get_json()['green']
        myColors[color_id].blue = request.get_json()['blue']
        print myColors[color_id].json()
        return myColors[color_id].json()

api.add_resource(ColorAPI, '/<string:color_id>')

if __name__ == '__main__':
    app.run(debug=True)


