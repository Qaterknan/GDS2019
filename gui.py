from glumpy import app

class GUI:
    values = {
        "deadMin": 0.2
    }
    actions = {
        app.window.key.Q: ("deadMin", 0.1),
        app.window.key.W: ("deadMin", -0.1),
    }

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

