import arcade
import os


class EyeFit(arcade.Window):

    def __init__(self):
        super().__init__(fullscreen=True)

        file_path = os.path.dirname(os.path.abspath(__file__))
        os.chdir(file_path)

        # This will get the size of the window, and set the viewport to match.
        # So if the window is 1000x1000, then so will our viewport. If
        # you want something different, then use those coordinates instead.
        width, height = self.get_size()
        self.set_viewport(0, width, 0, height)
        arcade.set_background_color(arcade.color.AMAZON)
        self.example_image = arcade.load_texture(":resources:images/tiles/boxCrate_double.png")

    def on_draw(self):
        """
        Render the screen.
        """

        self.clear()

        # Get viewport dimensions
        left, screen_width, bottom, screen_height = self.get_viewport()

        text_size = 18
        # Draw text on the screen so the user has an idea of what is happening
        arcade.draw_text("Collect the apples",
                         screen_width // 2, screen_height // 2 - 20,
                         arcade.color.WHITE, text_size, anchor_x="center")
        arcade.draw_text("Press Esc to exit",
                         screen_width // 2, screen_height // 2 + 20,
                         arcade.color.WHITE, text_size, anchor_x="center")

    def on_key_press(self, symbol: int, modifiers: int):
        if symbol == arcade.key.ESCAPE:
            arcade.exit()


class MenuView(arcade.View):
    def on_show_view(self):
        arcade.set_background_color(arcade.color.WHITE)

    def on_draw(self):
        self.clear()

        arcade.draw_text("Menu Screen", 500, 500,
                         arcade.color.BLACK, font_size=50, anchor_x="center")
        arcade.draw_text("Click to advance", 500, 500 - 75,
                         arcade.color.GRAY, font_size=20, anchor_x="center")

    def on_mouse_press(self, _x, _y, _button, _modifiers):
        game_view = GameView()
        self.window.show_view(game_view)


class GameView(arcade.View):
    def __init__(self):
        super().__init__()

        arcade.set_background_color(arcade.color.AMAZON)

        self.pointer_x = 0
        self.pointer_y = 0

        self.vel_x = 0
        self.vel_y = 0

        self.deadzone = 50
        self.pointer_radius = 50

    def on_draw(self):
        arcade.start_render()
        arcade.draw_circle_outline(self.pointer_x, self.pointer_y, self.pointer_radius,
                                   arcade.color.AERO_BLUE, 2, 20)

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


def main():
    window = EyeFit()
    # window.total_score = 0
    menu_view = MenuView()
    window.show_view(menu_view)
    arcade.run()


if __name__ == "__main__":
    main()
