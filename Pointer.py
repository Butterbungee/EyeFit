import arcade
import os

class EyeFitWindow(arcade.Window):
    def __init__(self, width, height, title):
        super().__init__(width, height, title)
        self.set_location(400, 200)

        arcade.set_background_color(arcade.color.AMAZON)

        self.pointer_x = 500
        self.pointer_y = 500

        self.vel_x = 0
        self.vel_y = 0

        self.deadzone = 50
        self.pointer_radius = 50

    def on_draw(self):
        arcade.start_render()
        arcade.draw_circle_outline(self.pointer_x, self.pointer_y, self.pointer_radius, arcade.color.AERO_BLUE, 2, 20)

    def on_update(self, delta_time: float):
        pass

    def on_mouse_motion(self, x: int, y: int, dx: int, dy: int):
        self.pointer_x = x
        self.pointer_y = y


EyeFitWindow(1280, 720, "EyeFit")
arcade.run()
