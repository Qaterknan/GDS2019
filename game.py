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

window = app.Window(width=1024, height=1024)
cwidth, cheight = 512, 512

GUI = gui.GUI()
simulation = Simulation(cwidth, cheight)

@window.event
def on_draw(dt):
    simulation.on_draw(dt)

    render["texture"][:, :, 0] = simulation.cells

    # gl.glDisable(gl.GL_BLEND)
    # gl.glClear(gl.GL_COLOR_BUFFER_BIT)
    gl.glViewport(0, 0, window.width, window.height)
    render.draw(gl.GL_TRIANGLE_STRIP)

@window.event
def on_mouse_drag(x, y, dx, dy, button):
    simulation.on_mouse_drag(x/window.width, (window.height-y)/window.height, dx, -dy, button)
    print('Mouse drag (x=%.1f, y=%.1f, dx=%.1f, dy=%.1f, button=%d)' % (x, y, dx, dy, button))


# @window.event
# def on_mouse_motion(x, y, dx, dy):
#     print('Mouse motion (x=%.1f, y=%.1f, dx=%.1f, dy=%.1f)' % (x, y, dx, dy))

@window.event
def on_key_press(symbol, modifiers):
    GUI.on_key_press(symbol, modifiers)

render = gloo.Program(render_vertex, render_fragment, count=4)
render["position"] = [(-1, -1), (-1, +1), (+1, -1), (+1, +1)]
render["texcoord"] = [(0, 0), (0, 1), (1, 0), (1, 1)]
render["texture"] = np.zeros((cwidth, cheight, 4))
# render["texture"] = np.random.uniform(0, 1, (cwidth, cheight, 4)) > 0.5
render["texture"].interpolation = gl.GL_LINEAR
render["texture"].wrapping = gl.GL_CLAMP_TO_EDGE

app.run(framerate=0)
