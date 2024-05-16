"""
Section Example 1:

In this Section example we divide the screen in two sections and let the user
pick a box depending on the selected Section

Note:
    - How View know nothing of what's happening inside the sections.
      Each section knows what to do.
    - Each event mouse input is handled by each Section even if the class
      it's the same (ScreenPart).
    - How on_mouse_enter/leave triggers in each Section when the mouse
      enter or leaves the section boundaries
"""
import arcade


class Record(arcade.Section):
    """
    This represents a part of the View defined by its
    boundaries (left, bottom, etc.)
    """

    def __init__(self, left: int, bottom: int, width: int, height: int,
                 **kwargs):
        super().__init__(left, bottom, width, height, **kwargs)

        self.selected: bool = False  # if this section is selected

    def on_draw(self):
        """ Draw this section """

        # Section is selected when mouse is within its boundaries
        arcade.draw_lrtb_rectangle_filled(self.left, self.right, self.top,
                                          self.bottom, arcade.color.GRAY)
        arcade.draw_text(f'{self.name}', self.left,
                         self.top - 50, arcade.color.BLACK, 16)


class GameView(arcade.View):

    def __init__(self):
        super().__init__()

        # add sections to the view

        # 1) First section holds half of the screen
        self.add_section(Record(300, 300, 200,
                                200, name='Recording Container'))

    def on_draw(self):
        # clear the screen
        self.clear(arcade.color.BEAU_BLUE)


def main():
    # create the window
    window = arcade.Window(height=600, width=600)

    # create the custom View. Sections are initialized inside the GameView init
    view = GameView()

    # show the view
    window.show_view(view)

    # run arcade loop
    window.run()


if __name__ == '__main__':
    main()
