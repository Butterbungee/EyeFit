import arcade


class TestPointerApple(arcade.View):
    def __init__(self):
        super().__init__()

        arcade.set_background_color(arcade.color.AMAZON)

        self.pointer_x = 500
        self.pointer_y = 500

        self.vel_x = 0
        self.vel_y = 0

        self.deadzone = self.pointer_radius = 50

    def on_draw(self):
        arcade.start_render()
        arcade.draw_circle_outline(self.pointer_x,
                                   self.pointer_y,
                                   self.pointer_radius,
                                   arcade.color.LILAC,
                                   border_width=2,
                                   num_segments=20)

    def on_update(self, delta_time: float):
        self.move_pointer()

    def on_mouse_motion(self, x: int, y: int, dx: int, dy: int):
        self.vel_x = x
        self.vel_y = y

    def move_pointer(self):
        x_dist = self.vel_x - self.pointer_x
        y_dist = self.vel_y - self.pointer_y

        distance = pow(x_dist * x_dist + y_dist * y_dist, 0.5)

        if distance > self.deadzone:
            self.pointer_x += x_dist * .3
            self.pointer_y += y_dist * .3

    def on_key_press(self, symbol: int, modifiers: int):
        arcade.exit()


window = arcade.Window(1280, 720, "EyeFit", fullscreen=True, vsync=True)
test_view = TestPointerApple()
window.show_view(test_view)
arcade.run()
