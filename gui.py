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

class GUI:

    values = {
        "deadMin": 0.15,
        "popMax" : 0.5,
        "birthMin" : 0.4,
        "lifeMin" : 0.5
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
        "ě" : ("lifeMin", -0.01)
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
