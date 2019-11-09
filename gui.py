from glumpy import app

class GUI:

    values = {
        "deadMin": 0.2,
        "popMax" : 0.6,
        "birthMin" : 0.3,
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

    def __init__(self):
        print("===== settings =====")
        for valKey, value in self.values.items():
            print(valKey, "=", value)
        print("========================")

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
