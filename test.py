import arcade
import random

x_y_list = []
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Drawing With Loops Example"

for each in range(10):
    x = random.randrange(SCREEN_WIDTH)
    y = random.randrange(SCREEN_HEIGHT)
    x_y_list.append((x, y))


def draw_background():
    """
    This function draws the background. Specifically, the sky and ground.
    """
    # Draw the sky in the top two-thirds
    arcade.draw_rectangle_filled(SCREEN_WIDTH / 2, SCREEN_HEIGHT * 2 / 3,
                                 SCREEN_WIDTH - 1, SCREEN_HEIGHT * 2 / 3,
                                 arcade.color.SKY_BLUE)

    # Draw the ground in the bottom third
    arcade.draw_rectangle_filled(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 6,
                                 SCREEN_WIDTH - 1, SCREEN_HEIGHT / 3,
                                 arcade.color.DARK_SPRING_GREEN)


def draw_line(start_x, start_y, end_x, end_y):
    arcade.draw_line(start_x, start_y, end_x, end_y, arcade.color.BLACK, 6)


def draw_point(start_x, start_y):
    arcade.draw_circle_filled(start_x, start_y, 30, arcade.color.SMOKE)
    arcade.draw_circle_outline(start_x, start_y, 30, arcade.color.DARK_SLATE_GRAY, 5)


def draw_number(start_x, start_y, index):
    arcade.draw_text(f"1233", start_x, start_y, arcade.color.BLACK,
                     16, anchor_x="center", anchor_y="center", bold=True)


def main():
    """
    This is the main program.
    """

    # Open the window
    arcade.open_window(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)

    # Start the render process. This must be done before any drawing commands.
    arcade.start_render()

    # Call our drawing functions.
    draw_background()
    for index in range(x_y_list.__len__()):
        if index == x_y_list.__len__() - 1:
            start_x, start_y = x_y_list[index][0], x_y_list[index][1]
            draw_point(start_x, start_y)
            draw_number(start_x, start_y, index)
        else:
            start_x, start_y = x_y_list[index][0], x_y_list[index][1]
            end_x, end_y = x_y_list[index + 1][0], x_y_list[index + 1][1]
            draw_line(start_x, start_y, end_x, end_y)
            draw_point(start_x, start_y)
            draw_number(start_x, start_y, index)

    # Finish the render.
    # Nothing will be drawn without this.
    # Must happen after all draw commands
    arcade.finish_render()

    # Keep the window up until someone closes it.
    arcade.run()


if __name__ == "__main__":
    main()
