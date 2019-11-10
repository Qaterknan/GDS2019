import numpy as np
from glumpy import app

class Rectangle:
    def __init__(self, x, y, width, height, color):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color

    def render(self, pixels):
        pixels[self.x:self.x+self.width, self.y:self.y+self.height] = self.color

class KernelPainter:
    def __init__(self, x, y, kernel):
        self.x = x
        self.y = y
        self.kernel = kernel
    
    def render(self, pixels):
        width, height = self.kernel.shape
        pixels[self.x:self.x+width, self.y:self.y+height] = self.kernel

class Slider:
    def __init__(self, x, y, width, height, min_val, max_val, values, value_key):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.min_val = min_val
        self.max_val = max_val
        # self.current_val = min_val

        self.values = values
        self.value_key = value_key

        self.rect_bg = Rectangle(self.x, self.y, self.width, self.height, 0.0)
        self.rect_fg = Rectangle(self.x, self.y, self.width, self.height, 1.0)


        self.set_value(values[value_key])
    
    def set_value(self, val):
        diff = self.max_val - self.min_val
        self.set_value_relative((val - self.min_val)/diff)

    def set_value_relative(self, val):
        # val between 0 and 1, sets current val to between min_val and max_val according to this relative val
        assert val >= 0 and val <= 1
        diff = self.max_val - self.min_val
        # self.current_val = val*diff + self.min_val
        self.values[self.value_key] = val*diff + self.min_val
        self.rect_fg.height = int(self.height * val)
    
    def render(self, pixels):
        self.rect_bg.render(pixels)
        self.rect_fg.render(pixels)
    
    def on_mouse_press(self, x, y, button):
        self.on_mouse(x, y)
    
    def on_mouse_drag(self,x, y, dx, dy, buttons):
        self.on_mouse(x, y)

    def on_mouse(self, x, y):
        if x >= self.x and x <= self.x+self.width and y >= self.y and y <= self.y + self.height:
            y_diff = y - self.y
            self.set_value_relative(y_diff/self.height)

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
        self.objects.append(Slider(0, 0, 30, 100, 0.0, 1.0, self.values, "deadMin"))
        self.objects.append(Slider(40, 0, 30, 100, 0.0, 1.0, self.values, "popMax"))
        self.objects.append(Slider(80, 0, 30, 100, 0.0, 1.0, self.values, "birthMin"))
        self.objects.append(Slider(120, 0, 30, 100, 0.0, 1.0, self.values, "lifeMin"))
        self.objects.append(Rectangle(0, self.height-1, self.width, 1, 0.5))

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

    def on_mouse_drag(self, x, y, dx, dy, buttons):
        for o in self.objects:
            if hasattr(o, 'on_mouse_drag'):
                o.on_mouse_drag(x, y, dx, dy, buttons)

    def on_mouse_motion(self, x, y, dx, dy):
        for o in self.objects:
            if hasattr(o, 'on_mouse_motion'):
                o.on_mouse_motion(x, y, dx, dy)
