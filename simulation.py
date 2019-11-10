import numpy as np
import scipy
from scipy.ndimage import gaussian_filter

class Simulation:
    averaging = False
    metricPoints = 100

    brush_size = 5

    def __init__(self, width, height, GUI):
        self.width = width
        self.height = height
        self.GUI = GUI

        self.derivative_metric = np.zeros(self.metricPoints)
        self.gaussian_metric = np.zeros(self.metricPoints)

        self.cells = np.zeros((self.width, self.height))
        self.simulation_cells = (np.random.uniform(0, 1, (self.width, self.height)) > 0.5).astype(np.float)
        self.new_cells = np.zeros_like(self.cells)

        # gaussian kernel
        self.gaussian_kernel_size = 33
        mu = self.gaussian_kernel_size // 2
        sigma = 30
        self.gaussian_kernel = np.fromfunction(lambda x, y: np.exp(-(x-mu)**2 / sigma - (y-mu)**2 / sigma), (self.gaussian_kernel_size, self.gaussian_kernel_size))
        self.gaussian_kernel = self.gaussian_kernel/np.max(self.gaussian_kernel)
        self.gaussian_kernel_fft = np.fft.rfft2(self.gaussian_kernel, self.cells.shape)

        # circle kernel
        self.circle_kernel_size = 33
        center = self.circle_kernel_size // 2
        radius = 2
        sigma = 2
        def circle_fn(x,y):
            dist = np.sqrt((x-center)**2 + (y-center)**2)
            return np.exp(-(dist-radius)**2 / sigma)
        self.circle_kernel = np.fromfunction(circle_fn, (self.circle_kernel_size, self.circle_kernel_size))
        self.circle_kernel = self.circle_kernel/np.max(self.circle_kernel)
        self.circle_kernel_fft = np.fft.rfft2(self.circle_kernel, self.cells.shape)

        # checkerboard kernel
        self.kernel_size = 16
        half_size = self.kernel_size//2
        self.kernel = np.zeros((self.kernel_size, self.kernel_size))
        self.kernel[:half_size, :half_size] = 1.0
        self.kernel[half_size:, half_size:] = 1.0

        self.kernel = gaussian_filter(self.kernel, 0.1)
        self.kernel_fft = np.fft.rfft2(self.kernel, self.cells.shape)

    def on_draw_random(self, dt):
        rnd = np.random.uniform(0, 1, (self.width, self.height))
        self.cells = rnd
    
    def on_mouse_drag(self, x, y, dx, dy, button):
        x = int(x*self.width)
        y = int(y*self.height)
        size = self.brush_size
        self.simulation_cells[x-size:x+size, y-size:y+size] = 1.0
        # self.cells = np.clip(self.cells, 0, 1)

    def fast_conv2d(self, cells, kernel_fft, kernel_size):
        conv_cells = np.fft.irfft2(np.fft.rfft2(cells) * kernel_fft)

        conv_cells = np.roll(conv_cells, -kernel_size//2+1, 0)
        conv_cells = np.roll(conv_cells, -kernel_size//2+1, 1)

        return conv_cells

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
        # self.new_cells = scipy.signal.convolve2d(self.cells, self.kernel, "same", "wrap")

        gaussian_cells = self.fast_conv2d(self.simulation_cells, self.gaussian_kernel_fft, self.gaussian_kernel_size)
        circle_cells = self.fast_conv2d(self.simulation_cells, self.circle_kernel_fft, self.circle_kernel_size)
        checkerboard_cells = self.fast_conv2d(self.simulation_cells, self.kernel_fft, self.kernel_size)

        # new_cells = new_cells[1:, 1:]
        # new_cells = np.pad(new_cells, [(1, 0), (1, 0)])
        # new_cells = new_cells[1:-1, 1:-1]
        # new_cells = scipy.signal.fftconvolve(old_cells, self.kernel, mode='same')

        # new_cells[:decay_size, :decay_size] = self.kernel
        # weird
        # self.new_cells -= (circle_cells/np.sum(self.circle_kernel) > 0.8).astype(float)
        # self.new_cells += (circle_cells/np.sum(self.circle_kernel) < 0.2).astype(float)
        # self.new_cells += (self.new_cells - gaussian_cells/np.sum(self.gaussian_kernel))*0.1

        # self.new_cells = self.cells
        # self.new_cells += (1-((gaussian_cells > 0.1) & (gaussian_cells < 0.3) & (circle_cells > 0.1) & (circle_cells < 0.3)).astype(float))*0.1
        # self.new_cells += (-((gaussian_cells < 0.1) | (gaussian_cells > 0.3)).astype(float))*0.1

        # self.new_cells = ((self.new_cells < 3.1) & (self.new_cells > 2.5)).astype(float)
        # new_cells[:decay_size, :decay_size] = self.distance_exp_decay
        # self.new_cells /= np.sum(self.distance_exp_decay)
        #
        # self.new_cells= 4*self.new_cells*(1-self.new_cells)
        # print(self.new_cells.max(), self.new_cells.min(), np.mean(self.new_cells))

        # self.new_cells = self.cells + (self.new_cells - self.cells)*0.1
        # new_cells /= np.max(new_cells)
        # new_cells = ((new_cells >= 2) & (new_cells <= 3) & (old_cells == 1)) | ((new_cells == 3) & (old_cells==0))
        # new_cells = new_cells.astype(float)
        self.new_cells = checkerboard_cells/np.sum(self.kernel)
        self.new_cells = ((self.new_cells < self.GUI.values["popMax"]) & ((self.new_cells > self.GUI.values["birthMin"]) | ((self.new_cells > self.GUI.values["deadMin"]) & (self.simulation_cells > self.GUI.values["lifeMin"])))).astype(float)
        # Determines the derivative
        derivative = np.absolute(self.new_cells - self.simulation_cells)
        derivative_sum = np.log(np.sum(derivative)+1)/np.log(2)
        # fourierSum = np.sum(self.new_cells[3*self.width//4:][3*self.height//4:])
        g_filtered = gaussian_filter(derivative, 6)
        gaussian_sum = np.sum(g_filtered)
        np.roll(self.derivative_metric, 1)
        np.roll(self.gaussian_metric, 1)
        self.derivative_metric[0] = derivative_sum
        self.gaussian_metric[0] = gaussian_sum
        # print(derivative_sum, gaussian_sum, gaussian_sq_sum)
        # Update metrics
        # self.new_cells = np.exp(-(self.new_cells - 0.5 + 0.2*self.simulation_cells) ** 2/(0.1+0.2*self.simulation_cells))

        if self.averaging:
            self.cells = 0.3*self.simulation_cells+0.7*self.cells
        else:
            self.cells = self.simulation_cells
            if self.GUI.values["showFourier"] == 1:
                fourier = np.absolute(np.fft.fft2(self.new_cells))
                fourier = np.log(fourier+1)
                fourier = fourier / fourier.max()
                self.cells = fourier
            if self.GUI.values["showFourier"] == 2:
                self.cells = derivative
            if self.GUI.values["showFourier"] == 3:
                self.cells = g_filtered
        self.simulation_cells, self.new_cells = self.new_cells, self.simulation_cells

        # debug view na kernel konvoluce
        # self.cells[:self.kernel_size, :self.kernel_size] = self.kernel
