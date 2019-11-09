# -----------------------------------------------------------------------------
# Copyright (c) 2009-2016 Nicolas P. Rougier. All rights reserved.
# Distributed under the (new) BSD License.
# -----------------------------------------------------------------------------
import numpy as np
import scipy
import scipy.signal
from glumpy import app, gl, glm, gloo

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
    v = texture2D(texture, v_texcoord).r;
    gl_FragColor = vec4(v, v, v, 1.0);
}
"""

window = app.Window(width=1024, height=1024)
cwidth, cheight = 1024, 1024

cells = (np.random.uniform(0, 1, (cwidth, cheight)) > 0.5).astype(np.float)
new_cells = np.zeros_like(cells)

distance_exp_decay = np.zeros((16, 16))


@window.event
def on_draw(dt):
    global cells, new_cells
    # random example
    # rnd = np.random.uniform(0, 1, (cwidth, cheight))
    # rnd = np.repeat(np.expand_dims(rnd, -1), 4, -1)
    # rnd[:, :, 0] = 0
    # render["texture"] = rnd
    # render["texture"][:, :, 0] = rnd


    # game of life wat version
    # print(render["texture"].shape)
    # cells = render["texture"][:, :, 0]
    # for x, row in enumerate(cells):
    #     for y, cell in enumerate(row):
    #         suma = np.sum(cells[x-2:x+1, y-2:y+1]) - cell
    #         # cells[x, y] = 0.5
    #         if suma < 2 or suma > 3:
    #             new_cells[x, y] = 0
    #         else:
    #             new_cells[x, y] = 1

    # neighbours_filter = np.array([[1,1,1], [1,0,1], [1,1,1]])
    # new_cells = scipy.signal.convolve2d(cells, neighbours_filter, "same", "wrap")
    # new_cells = ((new_cells >= 2) & (new_cells <= 3) & (cells == 1)) | ((new_cells == 3) & (cells==0))
    # new_cells = new_cells.astype(float)



    render["texture"][:, :, 0] = new_cells
    cells, new_cells = new_cells, cells

    # gl.glDisable(gl.GL_BLEND)
    gl.glClear(gl.GL_COLOR_BUFFER_BIT)
    gl.glViewport(0, 0, window.width, window.height)
    render.draw(gl.GL_TRIANGLE_STRIP)

# @window.event
# def on_mouse_drag(x, y, dx, dy, button):
#     print('Mouse drag (x=%.1f, y=%.1f, dx=%.1f, dy=%.1f, button=%d)' % (x, y, dx, dy, button))


# @window.event
# def on_mouse_motion(x, y, dx, dy):
#     print('Mouse motion (x=%.1f, y=%.1f, dx=%.1f, dy=%.1f)' % (x, y, dx, dy))


render = gloo.Program(render_vertex, render_fragment, count=4)
render["position"] = [(-1, -1), (-1, +1), (+1, -1), (+1, +1)]
render["texcoord"] = [(0, 0), (0, 1), (1, 0), (1, 1)]
render["texture"] = np.zeros((cwidth, cheight, 4))
# render["texture"] = np.random.uniform(0, 1, (cwidth, cheight, 4)) > 0.5
render["texture"].interpolation = gl.GL_LINEAR
render["texture"].wrapping = gl.GL_CLAMP_TO_EDGE

app.run(framerate=0)
