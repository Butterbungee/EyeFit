import arcade


class MyGame(arcade.View):
    """ Main application class. """

    def __init__(self):
        super().__init__()
        if self.window.background_type == "cam":
            self.shape_list = None

            self.WIDTH = arcade.get_viewport()[1]
            self.HEIGHT = arcade.get_viewport()[3]
            self.OFFSET = int(self.WIDTH * 0.08)

            # Calculate the diagonal of the screen
            self.DIAGONAL = int((self.WIDTH ** 2 + self.HEIGHT ** 2) ** 0.5)

            # Set shape size to be larger than the screen diagonal
            self.SHAPE_SIZE = self.DIAGONAL + 100

        elif self.window.background_type == "default":
            arcade.set_background_color(arcade.color.PASTEL_GREEN)

    def setup(self):
        if self.window.background_type == "cam":
            self.shape_list = arcade.ShapeElementList()

            # --- Create all the rectangles

            # We need a list of all the points and colors
            point_list = []
            color_list = []

            # Calculate the center offset
            x_offset = y_offset = self.SHAPE_SIZE // 2

            # Now calculate all the points
            for x in range(0, self.SHAPE_SIZE, self.OFFSET):
                for y in range(0, self.SHAPE_SIZE, self.OFFSET):
                    # Calculate where the four points of the rectangle will be if
                    # x and y are the center
                    top_left = (x - self.OFFSET - x_offset, y + self.OFFSET - y_offset)
                    top_right = (x + self.OFFSET - x_offset, y + self.OFFSET - y_offset)
                    bottom_right = (x + self.OFFSET - x_offset, y - self.OFFSET - y_offset)
                    bottom_left = (x - self.OFFSET - x_offset, y - self.OFFSET - y_offset)

                    # Add the points to the points list.
                    # ORDER MATTERS!
                    # Rotate around the rectangle, don't append points caty-corner
                    point_list.append(top_left)
                    point_list.append(top_right)
                    point_list.append(bottom_right)
                    point_list.append(bottom_left)

                    # Add a color for each point alternating between two colors
                    if (x // self.OFFSET + y // self.OFFSET) % 2 == 0:
                        color_list.extend([arcade.color.WHITE] * 4)
                    else:
                        color_list.extend([arcade.color.BLACK] * 4)

            shape = arcade.create_rectangles_filled_with_colors(point_list, color_list)
            self.shape_list.append(shape)

            self.shape_list._center_y = self.HEIGHT // 2
            self.shape_list._center_x = self.WIDTH // 2

    def on_update(self, delta_time: float):
        if self.window.background_type == "cam":
            self.shape_list.angle += .1

    def on_draw(self):
        """
        Render the screen.
        """
        # This command has to happen before we start drawing
        self.clear()

        if self.window.background_type == "cam":

            # --- Draw all the rectangles
            self.shape_list.draw()

        output = "contrast test"
        arcade.draw_text(output, 20, self.HEIGHT - 40, arcade.color.RED, 18)


class GameWindow(arcade.Window):

    def __init__(self):
        super().__init__(title="EyeFit",
                         resizable=False,
                         fullscreen=True)

        self.background_type = "cam"

    def on_key_press(self, symbol: int, modifiers: int):
        if symbol == arcade.key.ESCAPE:
            arcade.exit()


def main():
    window = GameWindow()
    view = MyGame()
    view.setup()
    window.show_view(view)
    arcade.run()


if __name__ == "__main__":
    main()
