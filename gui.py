import numpy as np
from glumpy import app

class Rectangle:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    def render(self, pixels):
        pixels[self.x:self.x+self.width, self.y:self.y+self.height] = 1.0

class Graph(Rectangle):
    def __init__(self, x, y, height, show_array_name, simulation_object):
        super().__init__(x,y,len(getattr(simulation_object, show_array_name)), height)
        self.show_array_name = show_array_name
        self.simulation_object = simulation_object

    def render(self, pixels):
        # Plot between max and min in the array
        show_array = getattr(self.simulation_object, self.show_array_name)
        bound = show_array.max()
        pixelated = (self.height-1) * show_array / bound
        pixelated = np.round(pixelated).astype(int)
        # Clear
        pixels[self.x:self.x+self.width, self.y:self.y+self.height] = 0.0
        # Choose coloured pixels
        for i in range(len(show_array)):
            pixels[self.x+i, self.y+pixelated[self.width-1-i]] = 1.0

class GUI:

    values = {
        "deadMin": 0.15,
        "popMax" : 0.5,
        "birthMin" : 0.4,
        "lifeMin" : 0.5,
        "showFourier" : 0,
    }
    actions = {
        app.window.key.Q: ("deadMin", 0.1),
        app.window.key.W: ("deadMin", -0.1),
        "q" : ("deadMin", 0.01),
        "w" : ("deadMin", -0.01),
        "a" : ("popMax", 0.01),
        "s" : ("popMax", -0.01),
        "y" : ("birthMin", 0.01),
        "x" : ("birthMin", -0.01),
        "+" : ("lifeMin", 0.01),
        "ě" : ("lifeMin", -0.01),
        "f" : ("showFourier", 1),
        "g" : ("showFourier", -1)
    }

    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.objects = []
        self.objects.append(Rectangle(20, 20, 40, 40))
        self.pixels = np.zeros((width, height))

        print("===== settings =====")
        for valKey, value in self.values.items():
            print(valKey, "=", value)
        print("========================")

    def on_draw(self, dt):
        for o in self.objects:
            o.render(self.pixels)

    def on_key_press(self, symbol, modifiers):
        changed = False
        for keyCode, (valKey, valDelta) in self.actions.items():
            if symbol == keyCode:
                self.values[valKey] += valDelta
                changed = True

        if changed:
            print("===== new settings =====")
            for valKey, value in self.values.items():
                print(valKey, "=", value)
            print("========================")

    def on_character(self, text):
        changed=False
        for char, (valKey, valDelta) in self.actions.items():
            if char == text:
                self.values[valKey] += valDelta
                changed = True
        if changed:
            print("===== new settings =====")
            for valKey, value in self.values.items():
                print(valKey, "=", value)
            print("========================")
