#!flask/bin/python

from flask import Flask, jsonify, render_template, request
from flask_restful import Resource, Api

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

myColors = {}

myColor = Color("Custom", 100, 100, 100)


class ColorAPI(Resource):
    def get(self, color_id):
        return myColors[color_id].json()

    def put(self, color_id):
        myColors[color_id] = Color()
        myColors[color_id].name = color_id
        myColors[color_id].red = request.get_json()['red']
        myColors[color_id].green = request.get_json()['green']
        myColors[color_id].blue = request.get_json()['blue']
        print myColors[color_id].json()
        return myColors[color_id].json()

api.add_resource(ColorAPI, '/<string:color_id>')

@app.route('/templates')
def display():
    return render_template("index.html")

if __name__ == '__main__':
    app.run(debug=True)
