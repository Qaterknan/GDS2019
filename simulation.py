import numpy as np
import scipy

class Simulation:
    def __init__(self, width, height):
        self.width = width
        self.height = height

        self.cells = (np.random.uniform(0, 1, (self.width, self.height)) > 0.5).astype(np.float)
        self.new_cells = np.zeros_like(self.cells)

        self.decay_size = 33
        mu = self.decay_size // 2
        sigma = 30
        distance_exp_decay = np.fromfunction(lambda x, y: np.exp(-(x-mu)**2 / sigma - (y-mu)**2 / sigma), (self.decay_size, self.decay_size))
        self.distance_exp_decay = distance_exp_decay/np.max(distance_exp_decay)
        self.distance_exp_decay_fft = np.fft.rfft2(self.distance_exp_decay, self.cells.shape)

    def on_draw_random(self, dt):
        rnd = np.random.uniform(0, 1, (self.width, self.height))
        self.cells = rnd

    def on_mouse_drag(self, x, y, dx, dy, button):
        x = int(x*self.width)
        y = int(y*self.height)
        size = 10
        self.cells[x-size:x+size, y-size:y+size] += 0.5
        self.cells = np.clip(self.cells, 0, 1)
        
    def on_draw(self, dt):
        # random example
        # rnd = np.random.uniform(0, 1, (cwidth, cheight))
        # rnd = np.repeat(np.expand_dims(rnd, -1), 4, -1)
        # rnd[:, :, 0] = 0
        # render["texture"] = rnd
        # render["texture"][:, :, 0] = rnd

        # game of life wat version
        # print(render["texture"].shape)
        # old_cells = render["texture"][:, :, 0]
        # for x, row in enumerate(old_cells):
        #     for y, cell in enumerate(row):
        #         suma = np.sum(old_cells[x-2:x+1, y-2:y+1]) - cell
        #         # old_cells[x, y] = 0.5
        #         if suma < 2 or suma > 3:
        #             new_cells[x, y] = 0
        #         else:
        #             new_cells[x, y] = 1

        # neighbours_filter = np.array([[1,1,1], [1,0,1], [1,1,1]])
        # self.new_cells = scipy.signal.convolve2d(self.cells, self.distance_exp_decay, "same", "wrap")

        self.new_cells = np.fft.irfft2(np.fft.rfft2(self.cells) * self.distance_exp_decay_fft)
        self.new_cells = np.roll(self.new_cells, -self.decay_size//2+1, 0)
        self.new_cells = np.roll(self.new_cells, -self.decay_size//2+1, 1)
        # new_cells = new_cells[1:, 1:]
        # new_cells = np.pad(new_cells, [(1, 0), (1, 0)])
        # new_cells = new_cells[1:-1, 1:-1]
        # new_cells = scipy.signal.fftconvolve(old_cells, self.distance_exp_decay, mode='same')

        # new_cells[:decay_size, :decay_size] = self.distance_exp_decay
        # self.new_cells /= np.sum(self.distance_exp_decay)

        self.new_cells = ((self.new_cells < 3.1) & (self.new_cells > 2.5)).astype(float)

        # self.new_cells = self.cells + (self.new_cells - self.cells)*0.1
        # new_cells /= np.max(new_cells)
        # new_cells = ((new_cells >= 2) & (new_cells <= 3) & (old_cells == 1)) | ((new_cells == 3) & (old_cells==0))
        # new_cells = new_cells.astype(float)


        self.cells, self.new_cells = self.new_cells, self.cells


        # debug view na kernel konvoluce
        self.cells[:self.decay_size, :self.decay_size] = self.distance_exp_decay