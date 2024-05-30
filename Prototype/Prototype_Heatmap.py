#

import time
import arcade
import numpy as np

RECORDING_DURATION = 5  # seconds

# Number of bins in each dimension
HEATMAP_RESOLUTION_X = 16 * 8
HEATMAP_RESOLUTION_Y = 9 * 8

KERNEL_RADIUS = 4  # Radius of the effect around the mouse position in bins


class Record(arcade.Section):
    """
    A Section represents a part of the View defined by its
    boundaries (left, bottom, etc.), Record Section acts as a container that contains the path of the players Gaze
    """

    def __init__(self, left: int, bottom: int, width: int, height: int, **kwargs):
        super().__init__(left, bottom, width, height, **kwargs)
        self.WIDTH = arcade.get_viewport()[1]
        self.HEIGHT = arcade.get_viewport()[3]
        self.RECORD_LEFT = int(self.WIDTH * 0.5)
        self.RECORD_BOTTOM = int(self.HEIGHT * 0.5)
        self.RECORD_WIDTH = int(self.WIDTH * 0.5)
        self.RECORD_HEIGHT = int(self.HEIGHT * 0.5)
        self.RECORD_OFFSET = int(self.WIDTH * 0.08)
        self.FONT_SIZE = 16
        self.mouse_positions = []
        self.recording = True
        self.mouse_inside = True
        self.kernel = self.create_circular_gaussian_kernel(KERNEL_RADIUS)
        self.mouse_x = 0
        self.mouse_y = 0

    @staticmethod
    def create_circular_gaussian_kernel(radius):
        """Creates a circular Gaussian kernel with the given radius."""
        size = radius * 2 + 1
        kernel = np.zeros((size, size))
        for x in range(size):
            for y in range(size):
                dx = x - radius
                dy = y - radius
                distance = np.sqrt(dx * dx + dy * dy)
                if distance <= radius:
                    kernel[x, y] = np.exp(-(dx * dx + dy * dy) / (2 * radius * radius))
        kernel /= np.sum(kernel)  # Normalize the kernel
        return kernel

    def on_draw(self):
        """ Draw this section """
        # arcade.start_render()
        # if self.recording:
        #     current_time = time.time()
        #     if current_time - self.window.start_time > RECORDING_DURATION:
        #         self.recording = False
        if not self.recording:
            self.draw_heatmap()

        arcade.draw_lrtb_rectangle_filled(self.left,
                                          self.right,
                                          self.top,
                                          self.bottom,
                                          arcade.make_transparent_color(arcade.color.WHITE_SMOKE, 100))
        arcade.draw_lrtb_rectangle_outline(self.left,
                                           self.right,
                                           self.top,
                                           self.bottom,
                                           arcade.make_transparent_color(arcade.color.DARK_SLATE_GRAY, 100), 5)

    def draw_heatmap(self):
        max_value = np.max(self.window.heatmap)
        for i in range(HEATMAP_RESOLUTION_X):
            for j in range(HEATMAP_RESOLUTION_Y):
                value = self.window.heatmap[i, j]
                if value > 0:
                    color = self.get_heatmap_color(value / max_value)
                    x = i * (self.RECORD_WIDTH / HEATMAP_RESOLUTION_X)
                    y = j * (self.RECORD_HEIGHT / HEATMAP_RESOLUTION_Y)
                    x += self.RECORD_LEFT - self.RECORD_OFFSET
                    y += self.RECORD_BOTTOM - self.RECORD_OFFSET
                    width = self.RECORD_WIDTH / HEATMAP_RESOLUTION_X
                    height = self.RECORD_HEIGHT / HEATMAP_RESOLUTION_Y
                    arcade.draw_lrtb_rectangle_filled(x, x + width, y + height, y, color)

    @staticmethod
    def get_heatmap_color(value):
        """Maps a value between 0 and 1 to a color on a gradient."""
        # Define a gradient from blue to red
        colors = [
            (0, 0, 255),  # Blue
            (0, 255, 255),  # Cyan
            (0, 255, 0),  # Green
            (255, 255, 0),  # Yellow
            (255, 0, 0)  # Red
        ]
        # Adjust the intensity of the colors
        colors = [(int(r * 0.8), int(g * 0.8), int(b * 0.8)) for r, g, b in colors]

        n = len(colors) - 1
        idx = int(value * n)
        t = (value * n) - idx

        if idx >= n:
            return colors[n]

        r1, g1, b1 = colors[idx]
        r2, g2, b2 = colors[idx + 1]

        r = int((1 - t) * r1 + t * r2)
        g = int((1 - t) * g1 + t * g2)
        b = int((1 - t) * b1 + t * b2)

        return r, g, b, 128


class HeatmapView(arcade.View):
    def __init__(self):
        super().__init__()
        self.WIDTH = arcade.get_viewport()[1]
        self.HEIGHT = arcade.get_viewport()[3]
        self.RECORD_LEFT = int(self.WIDTH * 0.5)
        self.RECORD_BOTTOM = int(self.HEIGHT * 0.5)
        self.RECORD_WIDTH = int(self.WIDTH * 0.5)
        self.RECORD_HEIGHT = int(self.HEIGHT * 0.5)
        self.RECORD_OFFSET = int(self.WIDTH * 0.08)
        self.FONT_SIZE = 16
        self.mouse_positions = []
        self.recording = True
        self.mouse_inside = True
        self.kernel = self.create_circular_gaussian_kernel(KERNEL_RADIUS)
        self.mouse_x = 0
        self.mouse_y = 0
        self.add_section(Record(self.RECORD_LEFT - self.RECORD_OFFSET,
                                self.RECORD_BOTTOM - self.RECORD_OFFSET,
                                self.RECORD_WIDTH,
                                self.RECORD_HEIGHT,
                                name='Recording Container'))

    def setup(self):

        self.mouse_positions = []
        self.window.start_time = time.time()
        self.window.heatmap = np.zeros((HEATMAP_RESOLUTION_X, HEATMAP_RESOLUTION_Y))

    @staticmethod
    def create_circular_gaussian_kernel(radius):
        """Creates a circular Gaussian kernel with the given radius."""
        size = radius * 2 + 1
        kernel = np.zeros((size, size))
        for x in range(size):
            for y in range(size):
                dx = x - radius
                dy = y - radius
                distance = np.sqrt(dx * dx + dy * dy)
                if distance <= radius:
                    kernel[x, y] = np.exp(-(dx * dx + dy * dy) / (2 * radius * radius))
        kernel /= np.sum(kernel)  # Normalize the kernel
        return kernel

    def on_draw(self):
        arcade.start_render()
        if self.recording:
            current_time = time.time()
            if current_time - self.window.start_time > RECORDING_DURATION:
                self.recording = False

    def on_mouse_motion(self, x, y, dx, dy):
        self.mouse_x = x
        self.mouse_y = y

    def update(self, delta_time):
        if self.recording:
            self.update_heatmap(self.mouse_x, self.mouse_y)

    def update_heatmap(self, x, y):
        """Updates the heatmap with a Gaussian kernel centered at (x, y).
        Recording process"""
        x_bin = int(x / self.WIDTH * HEATMAP_RESOLUTION_X)
        y_bin = int(y / self.HEIGHT * HEATMAP_RESOLUTION_Y)
        size = self.kernel.shape[0]
        half_size = size // 2

        for i in range(size):
            for j in range(size):
                xi = x_bin + i - half_size
                yj = y_bin + j - half_size
                if 0 <= xi < HEATMAP_RESOLUTION_X and 0 <= yj < HEATMAP_RESOLUTION_Y:
                    self.window.heatmap[xi, yj] += self.kernel[i, j]


class GameWindow(arcade.Window):

    def __init__(self):
        super().__init__(title="EyeFit", resizable=False, fullscreen=True)
        self.recording = []
        self.start_time = None
        self.heatmap = None

    def on_key_press(self, symbol: int, modifiers: int):
        if symbol == arcade.key.ESCAPE:
            arcade.exit()


def main():
    """ Main function """
    window = GameWindow()
    view = HeatmapView()
    view.setup()
    window.set_mouse_visible(True)
    window.show_view(view)
    arcade.run()


if __name__ == "__main__":
    main()
