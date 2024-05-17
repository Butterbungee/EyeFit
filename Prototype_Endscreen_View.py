import arcade
import random

COLOR_1 = arcade.color_from_hex_string('#2A1459')
COLOR_2 = arcade.color_from_hex_string('#4B89BF')
SCREEN_TITLE = "Drawing With Loops Example"
x_y_list = []


def draw_line(start_x, start_y, end_x, end_y):
    arcade.draw_line(start_x, start_y, end_x, end_y, arcade.color.BLACK, 6)


def draw_point(start_x, start_y):
    arcade.draw_circle_filled(start_x, start_y, 30, arcade.color.SMOKE)
    arcade.draw_circle_outline(start_x, start_y, 30, arcade.color.DARK_SLATE_GRAY, 5)


def draw_number(start_x, start_y, index):
    arcade.draw_text(f"{index}", start_x, start_y, arcade.color.BLACK,
                     16, anchor_x="center", anchor_y="center", bold=True)


class Record(arcade.Section):
    """
    This represents a part of the View defined by its
    boundaries (left, bottom, etc.)
    """

    def __init__(self, left: int, bottom: int, width: int, height: int, **kwargs):
        super().__init__(left, bottom, width, height, **kwargs)
        self.FONT_SIZE = 16
        self.selected: bool = False  # if this section is selected
        self.x_offset, self.y_offset = self.get_xy_screen_relative(0, 0)

    def on_draw(self):
        """ Draw this section """

        # Section is selected when mouse is within its boundaries
        arcade.draw_lrtb_rectangle_filled(self.left, self.right, self.top,
                                          self.bottom, arcade.color.WHITE_SMOKE)
        arcade.draw_lrtb_rectangle_outline(self.left, self.right, self.top,
                                           self.bottom, arcade.color.DARK_SLATE_GRAY, 5)
        arcade.draw_text(f'{self.name}', self.left + self.FONT_SIZE,
                         self.top - self.FONT_SIZE * 2, arcade.color.BLACK, self.FONT_SIZE)

        # x_offset, y_offset = self.get_xy_screen_relative(0, 0)

        for index in range(x_y_list.__len__()):
            if index == x_y_list.__len__() - 1:
                start_x, start_y = x_y_list[index][0] + self.x_offset, x_y_list[index][1] + self.y_offset
                draw_point(start_x, start_y)
                draw_number(start_x, start_y, index)
            else:
                start_x, start_y = x_y_list[index][0] + self.x_offset, x_y_list[index][1] + self.y_offset
                end_x, end_y = x_y_list[index + 1][0] + self.x_offset, x_y_list[index + 1][1] + self.y_offset
                draw_line(start_x, start_y, end_x, end_y)
                draw_point(start_x, start_y)
                draw_number(start_x, start_y, index)


class GameView(arcade.View):

    def __init__(self):
        super().__init__()

        # Screensize variables
        self.WIDTH = arcade.get_viewport()[1]
        self.HEIGHT = arcade.get_viewport()[3]
        self.RECORD_LEFT = int(self.WIDTH * 0.5)
        self.RECORD_BOTTOM = int(self.HEIGHT * 0.5)
        self.RECORD_WIDTH = int(self.WIDTH * 0.5)
        self.RECORD_HEIGHT = int(self.HEIGHT * 0.5)
        self.RECORD_OFFSET = int(self.WIDTH * 0.1)

        # The Record section holds the Recording view
        self.add_section(Record(self.RECORD_LEFT - self.RECORD_OFFSET,
                                self.RECORD_BOTTOM - self.RECORD_OFFSET,
                                self.RECORD_WIDTH,
                                self.RECORD_HEIGHT,
                                name='Recording Container'))

    @staticmethod
    def new_button(color):
        # helper to create new buttons
        return arcade.SpriteSolidColor(100, 50, color)

    def on_draw(self):
        # clear the screen
        self.clear(arcade.color.BEAU_BLUE)


def main():
    # create the window
    window = arcade.Window(fullscreen=True)

    screen_width = int(arcade.get_viewport()[1])
    screen_height = int(arcade.get_viewport()[3])

    for each in range(10):
        x = random.randrange(screen_width)
        y = random.randrange(screen_height)
        x_y_list.append((x / 2, y / 2))

    # create the custom View. Sections are initialized inside the GameView init
    view = GameView()

    # show the view
    window.show_view(view)

    # run arcade loop
    window.run()


if __name__ == '__main__':
    main()
