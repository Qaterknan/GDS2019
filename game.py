# -----------------------------------------------------------------------------
# Copyright (c) 2009-2016 Nicolas P. Rougier. All rights reserved.
# Distributed under the (new) BSD License.
# -----------------------------------------------------------------------------
import numpy as np
import scipy
import scipy.signal
from glumpy import app, gl, glm, gloo
import gui
from simulation import Simulation


render_vertex = """
attribute vec2 position;
attribute vec2 texcoord;
varying vec2 v_texcoord;
void main()
{
    gl_Position = vec4(position, 0.0, 1.0);
    v_texcoord = texcoord;
}
"""

render_fragment = """
uniform sampler2D texture;
varying vec2 v_texcoord;
void main()
{
    float v;
    v = texture2D(texture, v_texcoord.yx).r;
    gl_FragColor = vec4(v, v, v, 1.0);
}
"""

window = app.Window(width=512, height=512+100)
gui_height = 100
cwidth, cheight = 512, 512

all_pixels = np.zeros((cwidth, cheight+gui_height, 4))

GUI = gui.GUI(cwidth, gui_height)
simulation = Simulation(cwidth, cheight, GUI)

GUI.objects.append(gui.KernelPainter(160, 0, simulation.kernel))
GUI.objects.append(gui.KernelPainter(190, 0, simulation.gaussian_kernel))
GUI.objects.append(gui.KernelPainter(220, 0, simulation.circle_kernel))

@window.event
def on_draw(dt):
    simulation.on_draw(dt)
    GUI.on_draw(dt)

    render["texture"][:, gui_height:gui_height+cheight, 0] = simulation.cells
    render["texture"][:, :gui_height, 0] = GUI.pixels

    # gl.glDisable(gl.GL_BLEND)
    # gl.glClear(gl.GL_COLOR_BUFFER_BIT)
    gl.glViewport(0, 0, window.width, window.height)
    render.draw(gl.GL_TRIANGLE_STRIP)

# ===== MOUSE EVENTS =====

@window.event
def on_mouse_drag(x, y, dx, dy, button):
    GUI.on_mouse_drag(x, window.height-y, dx, dy, button)
    # normalizovaná myš
    if window.height - y > gui_height:
        simulation.on_mouse_drag(x/window.width, (window.height-y-gui_height)/cheight, dx, -dy, button)
    # print('Mouse drag (x=%.1f, y=%.1f, dx=%.1f, dy=%.1f, button=%d)' % (x, y, dx, dy, button), window.width, window.height)


@window.event
def on_mouse_motion(x, y, dx, dy):
    GUI.on_mouse_motion(x, window.height-y, dx, dy)
    # print('Mouse motion (x=%.1f, y=%.1f, dx=%.1f, dy=%.1f)' % (x, y, dx, dy))

# ===== KEYBOARD EVENTS =====

@window.event
def on_key_press(symbol, modifiers):
    GUI.on_key_press(symbol, modifiers)

@window.event
def on_character(text):
    GUI.on_character(text)

render = gloo.Program(render_vertex, render_fragment, count=4)
render["position"] = [(-1, -1), (-1, +1), (+1, -1), (+1, +1)]
render["texcoord"] = [(0, 0), (0, 1), (1, 0), (1, 1)]
render["texture"] = all_pixels
# render["texture"] = np.random.uniform(0, 1, (cwidth, cheight, 4)) > 0.5
render["texture"].interpolation = gl.GL_LINEAR
render["texture"].wrapping = gl.GL_CLAMP_TO_EDGE

app.run(framerate=0)
