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
        pixels[self.x:self.x+width, self.y:self.y+height] = self.kernel.values

    def on_mouse_press(self, x, y, button):
        self.on_mouse(x, y, button)

    def on_mouse_drag(self, x, y, dx, dy, buttons):
        self.on_mouse(x, y, buttons)

    def on_mouse(self, x, y, button):
        width, height = self.kernel.shape
        if x >= self.x and x < self.x+width and y >= self.y and y < self.y + height:
            relx = x - self.x
            rely = y - self.y
            for kx in range(self.kernel.shape[0]):
                for ky in range(self.kernel.shape[1]):
                    dx, dy = relx - kx, rely - ky
                    sign = +1 if button == 2 else -1
                    sigma = 3
                    add = sign * np.exp(- (dx**2) / sigma - (dy**2) / sigma)
                    new_val = np.clip(self.kernel.values[kx, ky] + add, 0, 1)
                    self.kernel.values[kx, ky] = new_val
            self.kernel.update_fft()
            # self.kernel = np.clip(self.kernel, 0, 1)

            # if button == 2:
            # if button == 8:
            #     self.kernel[relx, rely] -= 0.3


# class Image:

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
    def __init__(self, x, y, height, show_array_name, simulation_object, top_limit = 10, bottom_limit = 5):
        super().__init__(x,y,len(getattr(simulation_object, show_array_name)), height, 0)
        self.show_array_name = show_array_name
        self.simulation_object = simulation_object
        self.top_limit = top_limit
        self.bottom_limit = bottom_limit
        self.time_within_bounds = 0

    def render(self, pixels):
        top_limit = self.top_limit
        bottom_limit = self.bottom_limit
        # Plot between max and min in the array
        show_array = getattr(self.simulation_object, self.show_array_name)
        bounds = [show_array.min(), show_array.max()]
        boundedUp, boundedDown = False, False
        if top_limit > bounds[1]:
            bounds[1] = top_limit
            boundedUp = True
        if bottom_limit < bounds[0]:
            bounds[0] = bottom_limit
            boundedDown = True
        if boundedUp and boundedDown:
            self.time_within_bounds += 1
            if self.time_within_bounds > 100:
                self.simulation_object.win_condition[self.show_array_name] = True
        else:
            self.time_within_bounds = 0
            self.simulation_object.win_condition[self.show_array_name] = False
        pixelated = (self.height-1) * (show_array - bounds[0]) / (bounds[1] - bounds[0])
        top_limit = (self.height-1) * (top_limit - bounds[0]) / (bounds[1] - bounds[0])
        bottom_limit = (self.height-1) * (bottom_limit - bounds[0]) / (bounds[1] - bounds[0])
        top_limit = int(np.round(top_limit))
        bottom_limit = int(np.round(bottom_limit))
        # print(pixelated.min())
        pixelated = np.round(pixelated).astype(int)
        # print(min(pixelated))
        # Clear
        pixels[self.x:self.x+self.width, self.y:self.y+self.height] = 0.0
        # Choose coloured pixels
        for i in range(len(show_array)):
            pixels[self.x+i, self.y+pixelated[self.width-1-i]] = 1.0
            # Draw target lines
            pixels[self.x+i, self.y+top_limit] = 0.5
            pixels[self.x+i, self.y+bottom_limit] = 0.5

class Glyph(Rectangle):

    map = {
        "a" : [[0, 1, 0], [1, 0, 1], [1, 1, 1], [1, 0, 1], [1, 0, 1]],
        "b" : [[1,1,0],[1,0,1],[1,1,0],[1,0,1],[1,1,0]],
        "c" : [[1,1,1],[1,0,0],[1,0,0],[1,0,0],[1,1,1]],
        "d" : [[1, 1, 0], [1, 0, 1], [1, 0, 1], [1, 0, 1], [1, 1, 0]],
        "e" : [[1, 1, 1], [1, 0, 0], [1, 1, 1], [1, 0, 0], [1, 1, 1]],
        "f" : [[1, 1, 1], [1, 0, 0], [1, 1, 1], [1, 0, 0], [1, 0, 0]],
        "g" : [[1, 1, 1], [1, 0, 0], [1, 0, 1], [1, 0, 1], [1, 1, 1]],
        "h" : [[1, 0, 1], [1, 0, 1], [1, 1, 1], [1, 0, 1], [1, 0, 1]],
        "i" : [[1, 1, 1], [0, 1, 0], [0, 1, 0], [0, 1, 0], [1, 1, 1]],
        "j" : [[1, 1, 1], [0, 0, 1], [0, 0, 1], [1, 0, 1], [1, 1, 1]],
        "k" : [[1, 0, 1], [1, 1, 0], [1, 0, 0], [1, 1, 0], [1, 0, 1]],
        "l" : [[1, 0, 0], [1, 0, 0], [1, 0, 0], [1, 0, 0], [1, 1, 1]],
        "m" : [[1, 0, 1], [1, 1, 1], [1, 0, 1], [1, 0, 1], [1, 0, 1]],
        "n" : [[1, 1, 0], [1, 0, 1], [1, 0, 1], [1, 0, 1], [1, 0, 1]],
        "o" : [[1, 1, 1], [1, 0, 1], [1, 0, 1], [1, 0, 1], [1, 1, 1]],
        "p" : [[1, 1, 1], [1, 0, 1], [1, 1, 1], [1, 0, 0], [1, 0, 0]],
        "q" : [[1, 1, 1], [1, 0, 1], [1, 0, 1], [1, 1, 0], [0, 1, 1]],
        "r" : [[1, 1, 1], [1, 0, 1], [1, 1, 1], [1, 1, 0], [1, 0, 1]],
        "s" : [[1, 1, 1], [1, 0, 0], [1, 1, 1], [0, 0, 1], [1, 1, 1]],
        "t" : [[1, 1, 1], [0, 1, 0], [0, 1, 0], [0, 1, 0], [0, 1, 0]],
        "u" : [[1, 0, 1], [1, 0, 1], [1, 0, 1], [1, 0, 1], [1, 1, 1]],
        "v" : [[1, 0, 1], [1, 0, 1], [1, 0, 1], [1, 0, 1], [0, 1, 0]],
        "w" : [[1, 0, 1], [1, 0, 1], [1, 0, 1], [1, 1, 1], [1, 0, 1]],
        "x" : [[1, 0, 1], [1, 0, 1], [0, 1, 0], [1, 0, 1], [1, 0, 1]],
        "y" : [[1, 0, 1], [1, 0, 1], [0, 1, 0], [0, 1, 0], [0, 1, 0]],
        "z" : [[1, 1, 1], [0, 0, 1], [0, 1, 0], [1, 0, 0], [1, 1, 1]],
        " " : [[0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0]],
        "," : [[0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 1, 0], [0, 1, 0]],
        ">" : [[1, 0, 0], [0, 1, 0], [0, 0, 1], [0, 1, 0], [1, 0, 0]],
        "-" : [[0, 0, 0], [0, 0, 0], [1, 1, 1], [0, 0, 0], [0, 0, 0]]
    }

    def __init__(self, x,y, character, scale=1):
        super().__init__(x,y,3,5,1.0)
        self.character = character
        self.scaled_map = np.repeat(np.repeat(self.map[character], scale, axis=1), scale, axis=0)
        self.scaled_map = self.scaled_map.transpose()
        self.scaled_map = np.flip(self.scaled_map, axis=1)
        self.scale = scale

    def render(self, pixels):
        pixels[self.x:self.x+self.width*self.scale, self.y:self.y+self.height*self.scale] = self.scaled_map

class GUIText(Rectangle):
    def __init__(self, x,y, text, scale=1):
        super().__init__(x,y,(3+2)*len(text),5,1.0)
        self.characters = []
        for i in range(len(text)):
            self.characters.append(Glyph(x+i*4*scale, y, text[i], scale))
        self.scale = scale

    def render(self, pixels):
        for i in range(len(self.characters)):
            self.characters[i].render(pixels)

class GUI:

    values = {
        "deadMin": 0.15,
        "popMax" : 0.5,
        "birthMin" : 0.6,
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
        self.objects.append(GUIText(0, 70, "death", 2))
        self.objects.append(Slider(60, 0, 30, 100, 0.0, 1.0, self.values, "popMax"))
        self.objects.append(GUIText(60, 70, "crowd", 2))
        self.objects.append(Slider(120, 0, 30, 100, 0.0, 1.0, self.values, "birthMin"))
        self.objects.append(GUIText(120,70, "birth", 2))
        self.objects.append(GUIText(160, 50, "make choices",2))
        self.objects.append(GUIText(160, 30, "create system",2))
        self.objects.append(GUIText(160, 10, "within limits->",2))
        # self.objects.append(Slider(120, 0, 30, 100, 0.0, 1.0, self.values, "lifeMin"))
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

    def on_mouse_press(self, x, y, button):
        for o in self.objects:
            if hasattr(o, 'on_mouse_press'):
                o.on_mouse_press(x, y, button)
