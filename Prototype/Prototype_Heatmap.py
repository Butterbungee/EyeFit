import time

import arcade
import numpy as np

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Mouse Movement Heatmap"
RECORDING_DURATION = 5  # seconds
HEATMAP_RESOLUTION = 64  # Number of bins in each dimension
KERNEL_RADIUS = 5  # Radius of the effect around the mouse position in bins


class HeatmapWindow(arcade.Window):
    def __init__(self, width, height, title):
        super().__init__(width, height, title)
        self.mouse_positions = []
        self.start_time = None
        self.heatmap = None
        self.recording = True
        self.mouse_inside = True
        self.kernel = self.create_circular_gaussian_kernel(KERNEL_RADIUS)
        self.mouse_x = 0
        self.mouse_y = 0

    def setup(self):
        self.start_time = time.time()
        self.mouse_positions = []
        self.heatmap = np.zeros((HEATMAP_RESOLUTION, HEATMAP_RESOLUTION))

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
            if current_time - self.start_time > RECORDING_DURATION:
                self.recording = False
        if not self.recording:
            self.draw_heatmap()

    def on_mouse_motion(self, x, y, dx, dy):
        self.mouse_x = x
        self.mouse_y = y

    def on_mouse_leave(self, x, y):
        self.mouse_inside = False

    def on_mouse_enter(self, x, y):
        self.mouse_inside = True

    def update(self, delta_time):
        if self.recording and self.mouse_inside:
            self.update_heatmap(self.mouse_x, self.mouse_y)

    def update_heatmap(self, x, y):
        """Updates the heatmap with a Gaussian kernel centered at (x, y)."""
        x_bin = int(x / SCREEN_WIDTH * HEATMAP_RESOLUTION)
        y_bin = int(y / SCREEN_HEIGHT * HEATMAP_RESOLUTION)
        size = self.kernel.shape[0]
        half_size = size // 2

        for i in range(size):
            for j in range(size):
                xi = x_bin + i - half_size
                yj = y_bin + j - half_size
                if 0 <= xi < HEATMAP_RESOLUTION and 0 <= yj < HEATMAP_RESOLUTION:
                    self.heatmap[xi, yj] += self.kernel[i, j]

    def draw_heatmap(self):
        max_value = np.max(self.heatmap)
        for i in range(HEATMAP_RESOLUTION):
            for j in range(HEATMAP_RESOLUTION):
                value = self.heatmap[i, j]
                if value > 0:
                    alpha = value / max_value
                    color = (255, 0, 0, int(alpha * 255))
                    x = i * (SCREEN_WIDTH / HEATMAP_RESOLUTION)
                    y = j * (SCREEN_HEIGHT / HEATMAP_RESOLUTION)
                    width = SCREEN_WIDTH / HEATMAP_RESOLUTION
                    height = SCREEN_HEIGHT / HEATMAP_RESOLUTION
                    arcade.draw_lrtb_rectangle_filled(x, x + width, y + height, y, color)


def main():
    window = HeatmapWindow(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    window.setup()
    arcade.run()


if __name__ == "__main__":
    main()
