import math
import random

import arcade
import arcade.gui
from arcade.experimental.uislider import UISlider
from arcade.gui import UIManager, UILabel, UISpace, UIBoxLayout, UIFlatButton, UITextureButton, \
    UIAnchorWidget, UITextArea
from arcade.gui.events import UIOnChangeEvent, UIOnClickEvent

SCREEN_TITLE = "Apple Collecting Game"
SPRITE_SCALING_APPLE = 0.1
SPRITE_SCALING_BASKET = 0.2
APPLE_COUNT = 1
BASKET_SPEED = 5
SPEED_INCREMENT = 1
MAX_SPEED = 10
OFFSET_MULTIPLIER = 0.08
RECORDING_SAMPLING = 6  # Recording every x viewport updates


def draw_line(start_x, start_y, end_x, end_y, opacity):
    arcade.draw_line(start_x, start_y, end_x, end_y, arcade.make_transparent_color(arcade.color.BLACK, opacity),
                     6)


def draw_point(start_x, start_y, opacity, type_state):
    if type_state == "normal":
        arcade.draw_circle_filled(start_x,
                                  start_y,
                                  30,
                                  arcade.make_transparent_color(arcade.color.SMOKE, opacity)
                                  )
        arcade.draw_circle_outline(start_x,
                                   start_y,
                                   30,
                                   arcade.make_transparent_color(arcade.color.DARK_SLATE_GRAY, opacity),
                                   5
                                   )
    elif type_state == "start":
        arcade.draw_circle_filled(start_x,
                                  start_y,
                                  30,
                                  arcade.make_transparent_color(arcade.color.PASTEL_RED, opacity))
        arcade.draw_circle_outline(start_x,
                                   start_y,
                                   30,
                                   arcade.make_transparent_color(arcade.color.DARK_SLATE_GRAY, opacity),
                                   5
                                   )
    elif type_state == "point":
        arcade.draw_circle_filled(start_x,
                                  start_y,
                                  30,
                                  arcade.make_transparent_color(arcade.color.PASTEL_GREEN, opacity)
                                  )
        arcade.draw_circle_outline(start_x, start_y, 30,
                                   arcade.make_transparent_color(arcade.color.DARK_SLATE_GRAY, opacity),
                                   5
                                   )


def draw_number(start_x, start_y, index, opacity):
    arcade.draw_text(f"{index}", start_x, start_y, arcade.make_transparent_color(arcade.color.BLACK, opacity),
                     16, anchor_x="center", anchor_y="center", bold=True)


# noinspection PyUnusedLocal
def sign_recording(list_a):
    list_a[0] = list_a[0][0:-1] + ("start",)
    list_a[-1] = list_a[-1][0:-1] + ("point",)
    score = 0

    # Create a copy of the list for iteration
    list_b = list_a.copy()

    for _ in list_b:
        if _[3] == score:
            flag = False
        else:
            flag = True
        if flag:
            index = list_a.index(_)
            list_a[index] = _[0:-1] + ("start",)
            score += 1

    list_b = list_a.copy()
    score = list_a[-1][3]

    for _ in list_b[::-1]:
        if _[3] == score:
            flag = False
        else:
            flag = True
        if flag:
            index = list_a.index(_)
            list_a[index] = _[0:-1] + ("point",)
            score -= 1
    return list_a


class Record(arcade.Section):
    """
    A Section represents a part of the View defined by its
    boundaries (left, bottom, etc.), Record Section acts as a container that contains the path of the players Gaze
    """

    def __init__(self, left: int, bottom: int, width: int, height: int, **kwargs):
        super().__init__(left, bottom, width, height, **kwargs)
        self.FONT_SIZE = 16
        self.selected: bool = False  # if this section is selected
        self.x_offset, self.y_offset = self.get_xy_screen_relative(0, 0)
        self.line_counter = 0
        self.circle_counter = 0
        self.number_counter = 1
        self.opacity_float = .0
        self.opacity_increment = 255 / self.window.recording.__len__()
        self.opacity = 1
        self.start_list = []
        self.point_list = []

    def on_draw(self):
        """ Draw this section """
        arcade.draw_lrtb_rectangle_filled(self.left, self.right, self.top,
                                          self.bottom, arcade.color.WHITE_SMOKE)
        arcade.draw_lrtb_rectangle_outline(self.left, self.right, self.top,
                                           self.bottom, arcade.color.DARK_SLATE_GRAY, 5)
        arcade.draw_text(f'{self.name}', self.left + self.FONT_SIZE,
                         self.top - self.FONT_SIZE * 2, arcade.color.BLACK, self.FONT_SIZE)

        for index in range(self.window.recording.__len__()):
            self.opacity = int(self.opacity_float)
            if index == self.window.recording.__len__() - 1:
                start_x, start_y = self.window.recording[index][0] + self.x_offset, self.window.recording[index][
                    1] + self.y_offset
                draw_point(start_x, start_y, 255, self.window.recording[index][-1])
                draw_number(start_x, start_y, self.number_counter, 255)

            else:
                start_x, start_y = self.window.recording[index][0] + self.x_offset, self.window.recording[index][
                    1] + self.y_offset
                end_x = self.window.recording[index + 1][0] + self.x_offset
                end_y = self.window.recording[index + 1][1] + self.y_offset

                if self.line_counter == index:
                    draw_line(start_x, start_y, end_x, end_y, self.opacity)
                    self.line_counter += 1
                if self.circle_counter == index:
                    draw_point(start_x, start_y, self.opacity, "normal")
                    draw_number(start_x, start_y, self.number_counter, self.opacity)
                    self.circle_counter += 1
                    self.number_counter += 1
            self.opacity_float += self.opacity_increment

        self.line_counter = 0
        self.circle_counter = 0
        self.number_counter = 1
        self.opacity_float = .0
        self.opacity = 1

    def on_key_press(self, symbol: int, modifiers: int):
        if symbol == arcade.key.ESCAPE:
            arcade.exit()


class ModalSection(arcade.Section):
    """ A modal section that represents a popup that waits for user input """

    def __init__(self, left: int, bottom: int, width: int, height: int, offset: int):
        super().__init__(left, bottom, width, height, modal=True, enabled=False)

        # modal button
        self.offset = offset

        self.menu_button = arcade.SpriteSolidColor(int(self.width / 2), int(self.height / 4),
                                                   arcade.color.PASTEL_ORANGE)
        self.menu_pos = self.left + self.width / 2, self.bottom + self.height / 4
        self.menu_button.position = self.menu_pos

        self.continue_button = arcade.SpriteSolidColor(int(self.width / 2), int(self.height / 4),
                                                       arcade.color.PASTEL_GREEN)
        self.continue_pos = self.left + self.width / 2, self.bottom + (self.height / 4) * 3
        self.continue_button.position = self.continue_pos

    def on_draw(self):
        # draw modal frame and button
        arcade.draw_lrtb_rectangle_filled(self.left, self.right, self.top,
                                          self.bottom, arcade.color.GRAY)
        arcade.draw_lrtb_rectangle_outline(self.left, self.right, self.top,
                                           self.bottom, arcade.color.BLACK, int(self.offset * .1))
        self.draw_button()

    def draw_button(self):
        # draws the button and button text
        self.menu_button.draw()
        self.continue_button.draw()
        arcade.draw_text('Back to menu', self.menu_pos[0], self.menu_pos[1], arcade.color.BLACK,
                         italic=True, bold=True, anchor_x="center", anchor_y="center")
        arcade.draw_text('Continue', self.continue_pos[0], self.continue_pos[1], arcade.color.BLACK,
                         italic=True, bold=True, anchor_x="center", anchor_y="center")

    def on_mouse_press(self, x: float, y: float, button: int, modifiers: int):
        """ Check if the button is pressed """
        if self.continue_button.collides_with_point((x, y)):
            self.enabled = False
        if self.menu_button.collides_with_point((x, y)):
            self.enabled = False
            game_view = MenuView()
            self.window.show_view(game_view)


class Basket(arcade.Sprite):
    """
    This class represents the Basket on our screen.
    """
    speed = 0
    backwards = False

    def __init__(self, image, scale, position_list):
        super().__init__(image, scale)
        self.position_list = position_list
        self.cur_position = 0
        Basket.speed = BASKET_SPEED

    def update(self):
        """ Have a sprite follow a path """

        # Where are we
        start_x = self.center_x
        start_y = self.center_y

        # Where are we going
        if not Basket.backwards:
            dest_x = self.position_list[self.cur_position][0]
            dest_y = self.position_list[self.cur_position][1]
        else:
            dest_x = self.position_list[self.cur_position - 2][0]
            dest_y = self.position_list[self.cur_position - 2][1]

        # X and Y diff between the two
        x_diff = dest_x - start_x
        y_diff = dest_y - start_y

        # Calculate angle to get there
        angle = math.atan2(y_diff, x_diff)

        # How far are we?
        distance = math.sqrt((self.center_x - dest_x) ** 2 + (self.center_y - dest_y) ** 2)

        # How fast should we go? If we are close to our destination,
        # lower our speed, so we don't overshoot.
        speed = min(Basket.speed, int(distance))

        # Calculate vector to travel
        change_x = math.cos(angle) * speed
        change_y = math.sin(angle) * speed

        # Update our location
        self.center_x += change_x
        self.center_y += change_y

        # How far are we?
        distance = math.sqrt((self.center_x - dest_x) ** 2 + (self.center_y - dest_y) ** 2)

        # If we are there, head to the next point.
        if distance <= Basket.speed:
            if not Basket.backwards:
                self.cur_position += 1
                if self.cur_position >= len(self.position_list):
                    self.cur_position = 0
            else:
                self.cur_position -= 1
                if self.cur_position < 0:
                    self.cur_position = len(self.position_list) - 1


class MenuView(arcade.View):
    def __init__(self):
        super().__init__()

        self.WIDTH = arcade.get_viewport()[1]
        self.HEIGHT = arcade.get_viewport()[3]
        self.OFFSET = int(self.WIDTH * OFFSET_MULTIPLIER)
        self.BUTTON_WIDTH = self.WIDTH / 6
        self.BUTTON_HEIGHT = self.HEIGHT / 6
        self.FONT_SIZE = int(self.OFFSET / 4)

        # --- Required for all code that uses UI element,
        # a UIManager to handle the UI.
        self.manager = UIManager()
        self.manager.enable()

        # Set background color
        arcade.set_background_color(arcade.color.DARK_BLUE_GRAY)

        # Create a vertical BoxGroup to align buttons
        self.v_box = arcade.gui.UIBoxLayout()

        # Create the button style

        self.select_button_style = {
            "font_name": "calibri",
            "font_size": self.FONT_SIZE,
            "font_color": arcade.color.BLACK,
            "border_color": arcade.color.BLACK,
            "border_width": 4,
            "bg_color": arcade.color.PASTEL_GREEN,
            "bg_color_pressed": arcade.color.PASTEL_GREEN,
            "border_color_pressed": arcade.color.WHITE,
            "font_color_pressed": arcade.color.WHITE_SMOKE,

        }
        self.settings_button_style = {
            "font_name": "calibri",
            "font_size": self.FONT_SIZE,
            "font_color": arcade.color.BLACK,
            "border_color": arcade.color.BLACK,
            "border_width": 4,
            "bg_color": arcade.color.PASTEL_YELLOW,
            "bg_color_pressed": arcade.color.PASTEL_YELLOW,
            "border_color_pressed": arcade.color.WHITE,
            "font_color_pressed": arcade.color.WHITE_SMOKE,

        }

        self.quit_button_style = {
            "font_name": "calibri",
            "font_size": self.FONT_SIZE,
            "font_color": arcade.color.BLACK,
            "border_color": arcade.color.BLACK,
            "border_width": 4,
            "bg_color": arcade.color.PASTEL_RED,
            "bg_color_pressed": arcade.color.PASTEL_RED,
            "border_color_pressed": arcade.color.WHITE,
            "font_color_pressed": arcade.color.WHITE_SMOKE,

        }

        self.title_label = UILabel(text="EyeFit", font_size=self.OFFSET, font_name="calibri",
                                   text_color=arcade.color.BLACK, italic=True, bold=True)
        self.v_box.add(self.title_label.with_space_around(bottom=self.OFFSET / 2))
        # Create the buttons
        self.select_button = arcade.gui.UIFlatButton(text="Select minigame",
                                                     width=self.BUTTON_WIDTH,
                                                     height=self.BUTTON_HEIGHT,
                                                     style=self.select_button_style
                                                     )
        self.v_box.add(self.select_button.with_space_around(bottom=20))

        self.settings_button = arcade.gui.UIFlatButton(text="Settings",
                                                       width=self.BUTTON_WIDTH,
                                                       height=self.BUTTON_HEIGHT,
                                                       style=self.settings_button_style
                                                       )
        self.v_box.add(self.settings_button.with_space_around(bottom=20))

        self.quit_button = arcade.gui.UIFlatButton(text="Quit",
                                                   width=self.BUTTON_WIDTH,
                                                   height=self.BUTTON_HEIGHT,
                                                   style=self.quit_button_style)
        self.v_box.add(self.quit_button.with_space_around(bottom=20))

        # Method for handling click events,
        # Using a decorator to handle on_click events

        @self.select_button.event()
        def on_click(event: UIOnClickEvent):
            print("Minigame Select:", event)
            view = MinigameSelect()
            self.window.show_view(view)

        @self.settings_button.event()
        def on_click(event: UIOnClickEvent):
            print("Settings:", event)
            game_view = Settings()
            self.window.show_view(game_view)

        @self.quit_button.event()
        def on_click(event: UIOnClickEvent):
            print("Quit:", event)
            arcade.exit()

        # Create a widget to hold the v_box widget, that will center the buttons
        self.manager.add(
            UIAnchorWidget(
                anchor_x="center_x",
                anchor_y="center_y",
                child=self.v_box)
        )

    def on_draw(self):
        self.clear()
        self.manager.draw()

    def on_hide_view(self):
        self.manager.disable()


class Settings(arcade.View):

    def __init__(self):
        super().__init__()

        self.WIDTH = arcade.get_viewport()[1]
        self.HEIGHT = arcade.get_viewport()[3]
        self.OFFSET = int(self.WIDTH * OFFSET_MULTIPLIER)
        self.FONT_SIZE = int(self.OFFSET / 4)

        # --- Required for all code that uses UI element,
        # a UIManager to handle the UI.
        self.manager = UIManager()
        self.manager.enable()

        # Set background color
        arcade.set_background_color(arcade.color.DARK_BLUE_GRAY)

        # Create a horizontal BoxGroup to align volume label and slider
        self.h_volume_box = arcade.gui.UIBoxLayout(vertical=False)
        # Create volume label, space and slider
        self.volume_space = UISpace()
        self.volume_slider = UISlider(value=50, width=300, height=50)
        self.volume_label = UILabel(text="Sound Volume: "f"{self.volume_slider.value:02.0f}", font_size=self.FONT_SIZE)

        @self.volume_slider.event()
        def on_change(event: UIOnChangeEvent):
            print("Slider Change:", event)
            self.volume_label.text = "Sound Volume: "f"{self.volume_slider.value:02.0f}"
            self.volume_label.fit_content()

        # Add widgets to BoxGroup
        self.h_volume_box.add(self.volume_label)
        self.h_volume_box.add(self.volume_space)
        self.h_volume_box.add(self.volume_slider)

        # Create a horizontal BoxGroup to align mode label and textured button
        self.h_mode_box = UIBoxLayout(vertical=False)
        # Create mode label, tooltip, space and textured button
        self.mode_label = UILabel(text="Webcam mode", font_size=self.FONT_SIZE)
        self.mode_space = UISpace()
        self.mode_checkbox = UITextureButton(texture=arcade.load_texture("resources/unchecked.png"))

        # Track the state of the mode_checkbox
        self.mode_enabled = True

        @self.mode_checkbox.event()
        def on_click(event: UIOnClickEvent):
            print("mode_checkbox: ", event)
            if self.mode_enabled:
                self.mode_checkbox.texture = arcade.load_texture("resources/checked.png")
                self.mode_enabled = not self.mode_enabled
            else:
                self.mode_checkbox.texture = arcade.load_texture("resources/unchecked.png")
                self.mode_enabled = not self.mode_enabled

        self.h_mode_box.add(self.mode_label)
        self.h_mode_box.add(self.mode_space)
        self.h_mode_box.add(self.mode_checkbox)
        # Create a vertical BoxGroup to align buttons
        self.h_button_box = UIBoxLayout(vertical=False)

        # Create Button style
        self.apply_button_style = {
            "font_name": "calibri",
            "font_size": self.FONT_SIZE,
            "font_color": arcade.color.BLACK,
            "border_color": arcade.color.BLACK,
            "border_width": 4,
            "bg_color": arcade.color.PASTEL_GREEN,
            "bg_color_pressed": arcade.color.PASTEL_GREEN,
            "border_color_pressed": arcade.color.WHITE,
            "font_color_pressed": arcade.color.WHITE_SMOKE,

        }
        self.back_button_style = {
            "font_name": "calibri",
            "font_size": self.FONT_SIZE,
            "font_color": arcade.color.BLACK,
            "border_color": arcade.color.BLACK,
            "border_width": 4,
            "bg_color": arcade.color.PASTEL_YELLOW,
            "bg_color_pressed": arcade.color.PASTEL_YELLOW,
            "border_color_pressed": arcade.color.WHITE,
            "font_color_pressed": arcade.color.WHITE_SMOKE,

        }

        # Create the buttons
        self.apply_button = UIFlatButton(text="Apply", width=self.WIDTH / 6, height=self.HEIGHT / 6,
                                         style=self.apply_button_style)
        self.back_button = UIFlatButton(text="Back", width=self.WIDTH / 6, height=self.HEIGHT / 6,
                                        style=self.back_button_style)

        @self.apply_button.event()
        def on_click(event: UIOnClickEvent):
            print("Apply:", event)
            print("do apply stuff")
            view = MenuView()
            self.window.show_view(view)

        @self.back_button.event()
        def on_click(event: UIOnClickEvent):
            print("Back:", event)
            view = MenuView()
            self.window.show_view(view)

        # add buttons to BoxGroup
        self.h_button_box.add(self.apply_button.with_space_around(right=20))
        self.h_button_box.add(self.back_button.with_space_around(left=20))

        self.v_box = UIBoxLayout(vertical=True)
        self.v_box.add(self.h_volume_box)
        self.v_box.add(self.h_mode_box)
        self.v_box.add(self.h_button_box)

        # Create a widget to hold the BoxGroup widgets, that will center the buttons
        self.manager.add(
            UIAnchorWidget(anchor_x="center_x", anchor_y="center_y", child=self.v_box)
        )

    def on_draw(self):
        self.clear()
        self.manager.draw()

    def on_hide_view(self):
        self.manager.disable()


class MinigameSelect(arcade.View):

    def __init__(self):
        super().__init__()

        self.WIDTH = arcade.get_viewport()[1]
        self.HEIGHT = arcade.get_viewport()[3]
        self.OFFSET = int(self.WIDTH * OFFSET_MULTIPLIER)
        self.BUTTON_WIDTH = self.WIDTH / 6
        self.BUTTON_HEIGHT = self.HEIGHT / 6

        # --- Required for all code that uses UI element,
        # a UIManager to handle the UI.
        self.manager = UIManager()
        self.manager.enable()

        # Set background color
        arcade.set_background_color(arcade.color.DARK_BLUE_GRAY)

        # Create a vertical BoxGroup to align buttons
        self.v_box = UIBoxLayout(vertical=True)
        self.h_row_1 = UIBoxLayout(vertical=False)
        self.h_row_2 = UIBoxLayout(vertical=False)

        self.back_button_style = {
            "font_name": "calibri",
            "font_size": self.OFFSET / 3,
            "font_color": arcade.color.BLACK,
            "border_color": arcade.color.BLACK,
            "border_width": 4,
            "bg_color": arcade.color.PASTEL_YELLOW,
            "bg_color_pressed": arcade.color.PASTEL_YELLOW,
            "border_color_pressed": arcade.color.WHITE,
            "font_color_pressed": arcade.color.WHITE_SMOKE,

        }

        # Create the buttons
        self.back_button = UIFlatButton(text="Back",
                                        width=self.BUTTON_WIDTH,
                                        height=self.BUTTON_HEIGHT,
                                        style=self.back_button_style
                                        )
        self.apples_button = self.minigame_button("resources/minigame_apples.png")
        self.placeholder_1 = self.minigame_button("resources/placeholder_1.png")

        self.title_label = UILabel(text="Apple minigame settings and instructions", font_size=self.OFFSET / 3,
                                   text_color=arcade.color.BLACK, bold=True)

        self.h_row_1.add(self.apples_button.with_space_around(10, 10, 10, 10))
        self.h_row_1.add(self.placeholder_1.with_space_around(10, 10, 10, 10))

        self.v_box.add(self.title_label.with_space_around(bottom=self.OFFSET / 3))
        self.v_box.add(self.h_row_1)
        self.v_box.add(self.h_row_2)
        self.v_box.add(self.back_button.with_space_around(top=self.OFFSET / 3))

        # Create a widget to hold the v_box widget, that will center the buttons
        self.manager.add(
            UIAnchorWidget(
                anchor_x="center_x",
                anchor_y="center_y",
                child=self.v_box,
                size_hint_max=(10, 10))
        )

        # Method for handling click events,
        # Using a decorator to handle on_click events
        @self.back_button.event()
        def on_click(event: UIOnClickEvent):
            print("Back:", event)
            view = MenuView()
            self.window.show_view(view)

        @self.apples_button.event()
        def on_click(event: UIOnClickEvent):
            print("Apples:", event)
            view = AppleInstruction()
            self.window.show_view(view)

        @self.placeholder_1.event()
        def on_click(event: UIOnClickEvent):
            print("Placeholder_1:", event)
            # view = AppleInstruction()
            # self.window.show_view(view)

    def minigame_button(self, texture_name):
        return UITextureButton(texture=arcade.load_texture(texture_name),
                               height=self.HEIGHT * .3,
                               width=self.WIDTH * .3)

    def on_draw(self):
        self.clear()
        self.manager.draw()

    def on_hide_view(self):
        self.manager.disable()


class AppleInstruction(arcade.View):
    def __init__(self):
        super().__init__()

        self.WIDTH = arcade.get_viewport()[1]
        self.HEIGHT = arcade.get_viewport()[3]
        self.OFFSET = int(self.WIDTH * OFFSET_MULTIPLIER)
        print("offset is ", self.OFFSET)
        self.BUTTON_WIDTH = self.WIDTH / 6
        self.BUTTON_HEIGHT = self.HEIGHT / 6
        self.FONT_SIZE = int(self.OFFSET / 4)

        # --- Required for all code that uses UI element,
        # a UIManager to handle the UI.
        self.manager = UIManager()
        self.manager.enable()

        # Create a vertical BoxGroups to align buttons
        self.vertical_box = arcade.gui.UIBoxLayout(vertical=True)
        self.horizontal_box = arcade.gui.UIBoxLayout(vertical=False)
        self.right_box = arcade.gui.UIBoxLayout(vertical=True)
        self.left_box = arcade.gui.UIBoxLayout(vertical=True)
        self.slider_box = arcade.gui.UIBoxLayout(vertical=False)
        self.background_box = arcade.gui.UIBoxLayout(vertical=False)
        self.button_box = arcade.gui.UIBoxLayout(vertical=False)

        # Create the button style
        self.play_button_style = {
            "font_name": "calibri",
            "font_size": self.FONT_SIZE,
            "font_color": arcade.color.BLACK,
            "border_color": arcade.color.BLACK,
            "border_width": 4,
            "bg_color": arcade.color.PASTEL_GREEN,
            "bg_color_pressed": arcade.color.PASTEL_GREEN,
            "border_color_pressed": arcade.color.WHITE,
            "font_color_pressed": arcade.color.WHITE_SMOKE,

        }
        self.back_button_style = {
            "font_name": "calibri",
            "font_size": self.FONT_SIZE,
            "font_color": arcade.color.BLACK,
            "border_color": arcade.color.BLACK,
            "border_width": 4,
            "bg_color": arcade.color.PASTEL_YELLOW,
            "bg_color_pressed": arcade.color.PASTEL_YELLOW,
            "border_color_pressed": arcade.color.WHITE,
            "font_color_pressed": arcade.color.WHITE_SMOKE,

        }

        # Create the buttons
        self.back_button = UIFlatButton(text="Back",
                                        width=self.BUTTON_WIDTH,
                                        height=self.BUTTON_HEIGHT,
                                        style=self.back_button_style
                                        )
        self.play_button = UIFlatButton(text="Play",
                                        width=self.BUTTON_WIDTH,
                                        height=self.BUTTON_HEIGHT,
                                        style=self.play_button_style
                                        )
        self.gif_button = UIFlatButton(text="Gif",
                                       width=self.WIDTH / 2,
                                       height=self.HEIGHT / 2
                                       )
        self.apple_slider = UISlider(value=2,
                                     min_value=1,
                                     max_value=99,
                                     width=int(self.WIDTH / 3),
                                     height=self.OFFSET / 2
                                     )
        self.number = UILabel(text=f"{int(self.apple_slider.value):02.0f}",
                              font_size=self.OFFSET / 3,
                              text_color=arcade.color.BLACK
                              )

        self.slider_label = UILabel(text="Number of apples",
                                    font_size=self.OFFSET / 3,
                                    text_color=arcade.color.BLACK
                                    )
        self.cam_background = UITextureButton(texture=arcade.load_texture("resources/apple_cam.png")
                                              )
        self.normal_background = UITextureButton(texture=arcade.load_texture("resources/apple_default.png")
                                                 )
        self.background_label = UILabel(text="Background",
                                        font_size=self.OFFSET / 3,
                                        text_color=arcade.color.BLACK
                                        )
        self.title_label = UILabel(text="Apple minigame settings and instructions",
                                   font_size=self.OFFSET / 3,
                                   text_color=arcade.color.BLACK
                                   )

        self.button_box.add(self.play_button.with_space_around(right=self.BUTTON_WIDTH / 4))
        self.button_box.add(self.back_button.with_space_around(left=self.BUTTON_WIDTH / 4))
        self.right_box.add(self.gif_button.with_space_around(bottom=self.OFFSET / 2))
        self.right_box.add(self.button_box)
        self.slider_box.add(self.apple_slider)
        self.slider_box.add(self.number)
        self.background_box.add(self.normal_background.with_space_around(right=self.OFFSET / 4))
        self.background_box.add(self.cam_background.with_space_around(left=self.OFFSET / 4))
        self.left_box.add(self.background_label)
        self.left_box.add(self.background_box.with_space_around(bottom=self.OFFSET))
        self.left_box.add(self.slider_label)
        self.left_box.add(self.slider_box)
        self.horizontal_box.add(self.left_box.with_space_around(right=self.OFFSET / 4))
        self.horizontal_box.add(self.right_box.with_space_around(left=self.OFFSET / 4))
        self.vertical_box.add(self.title_label.with_space_around(bottom=self.OFFSET / 2))
        self.vertical_box.add(self.horizontal_box)

        # Create a widget to hold the v_box widget, that will center the buttons
        self.manager.add(
            UIAnchorWidget(
                anchor_x="center_x",
                anchor_y="center_y",
                child=self.vertical_box)
        )

        # Method for handling click events,
        # Using a decorator to handle on_click events
        @self.play_button.event()
        def on_click(event: UIOnClickEvent):
            print("Play:", event)
            self.window.apple_count = int(self.apple_slider.value)
            view = AppleMinigame()
            view.setup()
            self.window.show_view(view)

        @self.normal_background.event()
        def on_click(event: UIOnClickEvent):
            print("Default selected:", event)
            self.window.background_type = "default"

        @self.cam_background.event()
        def on_click(event: UIOnClickEvent):
            print("Cam selected:", event)
            self.window.background_type = "cam"

        @self.back_button.event()
        def on_click(event: UIOnClickEvent):
            print("Back:", event)
            view = MinigameSelect()
            self.window.show_view(view)

        @self.apple_slider.event()
        def on_change(event: UIOnChangeEvent):
            print("Apple Slider Change:", event)
            self.number.text = f"{int(self.apple_slider.value):02.0f}"
            self.number.fit_content()

    def on_show_view(self):
        arcade.set_background_color(arcade.color.PASTEL_ORANGE)

    def on_draw(self):
        self.clear()
        self.manager.draw()

    def on_hide_view(self):
        self.manager.disable()


# noinspection PyTypeChecker
class AppleMinigame(arcade.View):
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
            self.text_color = arcade.color.RED

        elif self.window.background_type == "default":
            arcade.set_background_color(arcade.color.PASTEL_GREEN)
            self.text_color = arcade.color.WHITE

        self.WIDTH = arcade.get_viewport()[1]
        self.HEIGHT = arcade.get_viewport()[3]
        self.OFFSET = int(self.WIDTH * OFFSET_MULTIPLIER)

        self.modal_section = ModalSection(int(self.WIDTH / 4) + self.OFFSET,
                                          int(self.HEIGHT / 3) - int(self.OFFSET / 2),
                                          int(self.WIDTH / 4) + self.OFFSET,
                                          int(self.HEIGHT / 3) + self.OFFSET, self.OFFSET)
        # Timer
        self.total_time = 0.0
        self.timer_text = arcade.Text(
            text="00:00",
            start_x=self.WIDTH // 2,
            start_y=self.HEIGHT // 2 - 50,
            color=self.text_color,
            font_size=100,
            anchor_x="center",
        )

        self.initial_apple_count = 0
        self.apples_created = 0
        self.total_apples_to_create = 0

        # Sprite lists
        self.player_list = None
        self.apple_list = None
        self.basket_list = None

        # Set up the player info
        self.player_sprite = None
        self.picked_up_state = False

        # Tick counter variable - tied to FPS(60)
        self.counter = 0

        # Declarations of constants
        self.pointer_x = 0
        self.pointer_y = 0

        self.mouse_x = 0
        self.mouse_y = 0

        self.deadzone_radius = 50
        self.pointer_radius = 50

        self.section_manager.add_section(self.modal_section)

    def setup(self):
        """ Set up the game and initialize the variables. """
        # clear score
        self.window.total_score = 0
        # self.window.apple_count = APPLE_COUNT

        # clear recording
        self.window.recording = []

        # clear score timings
        self.window.apple_timing = []

        # define screen
        left, right, bottom, top = arcade.get_viewport()

        # Timer
        self.total_time = 0.0

        # Sprite containers
        self.player_list = arcade.SpriteList()
        self.apple_list = arcade.SpriteList()
        self.basket_list = arcade.SpriteList()

        # Variable represents if player is holding an apple
        self.picked_up_state = False

        # background selection
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
        # Set up the player
        player = self.player_sprite = arcade.Sprite("resources/apple.png",
                                                    SPRITE_SCALING_APPLE,
                                                    center_x=0,
                                                    center_y=0)

        player.alpha = 0
        self.player_list.append(player)

        # List of points the basket will travel too.

        position_list = [[left + self.OFFSET, bottom + self.OFFSET],
                         [right - self.OFFSET, bottom + self.OFFSET],
                         [right - self.OFFSET, top - self.OFFSET],
                         [left + self.OFFSET, top - self.OFFSET]]

        # Create the basket
        basket = Basket("resources/basket.png",
                        SPRITE_SCALING_BASKET,
                        position_list)

        # Set initial location of the basket at the first point
        basket.center_x = position_list[0][0]
        basket.center_y = position_list[0][1]

        # Add the basket to the basket list
        self.basket_list.append(basket)

        # Create the apples
        self.initial_apple_count = 1
        self.apples_created = 0
        self.total_apples_to_create = self.window.apple_count

        for _ in range(self.initial_apple_count):
            self.create_apple()

    def create_apple(self):
        """Create a single apple and add it to the apple list."""
        width, height = int(arcade.get_viewport()[1]), int(arcade.get_viewport()[3])
        max_attempts = 50
        for _ in range(max_attempts):
            apple = arcade.Sprite("resources/apple.png", SPRITE_SCALING_APPLE)
            apple.center_x = random.randrange(self.OFFSET, width - self.OFFSET)
            apple.center_y = random.randrange(self.OFFSET, height - self.OFFSET)

            if not arcade.check_for_collision_with_list(apple, self.apple_list):
                self.apple_list.append(apple)
                self.apples_created += 1
                return

    def on_draw(self):

        self.clear()

        # Start rendering
        arcade.start_render()

        # Draw cam Background
        if self.window.background_type == "cam":
            # --- Draw all the rectangles
            self.shape_list.draw()

        # Timer
        self.timer_text.draw()

        # Put the text on the screen.
        output = f"Score: {self.window.total_score}"
        arcade.draw_text(text=output, start_x=self.WIDTH / 2, start_y=self.HEIGHT / 2 - self.OFFSET,
                         color=self.text_color, font_size=25,
                         anchor_x="center", anchor_y="top")

        # Draw all sprites
        self.apple_list.draw()
        self.player_list.draw()
        self.basket_list.draw()

        arcade.draw_circle_outline(self.pointer_x,
                                   self.pointer_y,
                                   self.pointer_radius,
                                   arcade.color.PASTEL_VIOLET,
                                   border_width=3,
                                   num_segments=40)

    def on_update(self, delta_time: float):
        """ Movement and game logic """
        if self.paused():
            pass
        else:
            # Background Rotation
            if self.window.background_type == "cam":
                self.shape_list.angle += .1

            # Timer
            self.total_time += delta_time

            # Calculate minutes
            minutes = int(self.total_time) // 60

            # Calculate seconds by using a modulus
            seconds = int(self.total_time) % 60

            # Calculate 100s of a second
            seconds_100s = int((self.total_time - seconds) * 100)

            # Use string formatting to create a new text string for our timer
            self.timer_text.text = f"{minutes:02d}:{seconds:02d}:{seconds_100s:02d}"
            self.window.time_elapsed = self.timer_text.text

            if self.counter == RECORDING_SAMPLING:
                self.window.recording.append(
                    self.move_pointer() + (self.total_time, self.window.total_score + 1, "normal"))
                self.counter = 0

            self.counter += 1
            self.move_pointer()
            self.basket_list.update()

            apple_collision_list = arcade.check_for_collision_with_list(self.player_sprite,
                                                                        self.apple_list)
            basket_collision_list = arcade.check_for_collision_with_list(self.player_sprite,
                                                                         self.basket_list)

            if apple_collision_list and not self.picked_up_state:
                for apple in apple_collision_list:
                    apple.remove_from_sprite_lists()
                    self.picked_up_state = True
                    self.player_sprite.alpha = 255

            if basket_collision_list and self.picked_up_state:
                for _ in basket_collision_list:
                    if Basket.speed < MAX_SPEED:
                        Basket.speed += SPEED_INCREMENT
                    Basket.backwards = not Basket.backwards
                    self.window.total_score += 1
                    self.player_sprite.alpha = 0
                    self.picked_up_state = False
                    if self.apples_created < self.total_apples_to_create:
                        self.create_apple()

            if self.window.total_score == self.window.apple_count:
                game_over_view = AppleMinigameOverView()
                self.window.show_view(game_over_view)

    def on_mouse_motion(self, x: int, y: int, dx: int, dy: int):
        self.mouse_x = x
        self.mouse_y = y

    def move_pointer(self):
        x_dist = self.mouse_x - self.pointer_x
        y_dist = self.mouse_y - self.pointer_y

        distance = (x_dist ** 2 + y_dist ** 2) ** 0.5

        if distance > self.deadzone_radius:
            self.pointer_x += x_dist * .4
            self.pointer_y += y_dist * .4
            self.player_sprite.center_x += x_dist * .4
            self.player_sprite.center_y += y_dist * .4
        return int(self.player_sprite.center_x * 0.5), int(self.player_sprite.center_y * 0.5)

    def on_key_press(self, symbol: int, modifiers: int):
        if symbol == arcade.key.ESCAPE:
            self.modal_section.enabled = True

    def paused(self):
        if self.modal_section.enabled:
            return True


class AppleMinigameOverView(arcade.View):

    def __init__(self):
        super().__init__()

        self.manager = UIManager()
        self.manager.enable()

        self.do_once = True

        # Screensize variables
        self.WIDTH = arcade.get_viewport()[1]
        self.HEIGHT = arcade.get_viewport()[3]
        self.OFFSET = int(self.WIDTH * 0.08)
        self.RECORD_LEFT = int(self.WIDTH * 0.5)
        self.RECORD_BOTTOM = int(self.HEIGHT * 0.5)
        self.RECORD_WIDTH = int(self.WIDTH * 0.5)
        self.RECORD_HEIGHT = int(self.HEIGHT * 0.5)
        self.RECORD_OFFSET = int(self.WIDTH * OFFSET_MULTIPLIER)
        self.BUTTON_WIDTH = int(self.RECORD_WIDTH / 3)
        self.BUTTON_HEIGHT = int(self.RECORD_HEIGHT / 3)
        self.FONT_SIZE = int(self.OFFSET / 4)

        # Create the button style
        self.play_button_style = {
            "font_name": "calibri",
            "font_size": self.FONT_SIZE,
            "font_color": arcade.color.BLACK,
            "border_color": arcade.color.BLACK,
            "border_width": 4,
            "bg_color": arcade.color.PASTEL_GREEN,
            "bg_color_pressed": arcade.color.PASTEL_GREEN,
            "border_color_pressed": arcade.color.WHITE,
            "font_color_pressed": arcade.color.WHITE_SMOKE,

        }
        self.back_button_style = {
            "font_name": "calibri",
            "font_size": self.FONT_SIZE,
            "font_color": arcade.color.BLACK,
            "border_color": arcade.color.BLACK,
            "border_width": 4,
            "bg_color": arcade.color.PASTEL_YELLOW,
            "bg_color_pressed": arcade.color.PASTEL_YELLOW,
            "border_color_pressed": arcade.color.WHITE,
            "font_color_pressed": arcade.color.WHITE_SMOKE,

        }

        # The Record section holds the Recording view
        self.add_section(Record(self.RECORD_LEFT - self.RECORD_OFFSET,
                                self.RECORD_BOTTOM - self.RECORD_OFFSET,
                                self.RECORD_WIDTH,
                                self.RECORD_HEIGHT,
                                name='Recording Container'))

        text = ""
        self.text_area = UITextArea(x=100,
                                    y=200,
                                    width=500,
                                    height=300,
                                    text=text,
                                    text_color=(0, 0, 0, 255),
                                    font_size=18
                                    )
        self.manager.add(self.text_area.with_space_around(right=20))

        # add play again button
        self.button_again = self.new_button(self.BUTTON_WIDTH,
                                            self.BUTTON_HEIGHT,
                                            arcade.color.PASTEL_GREEN)

        self.button_again.position = (self.WIDTH * 5 / 8 - self.RECORD_OFFSET,
                                      self.RECORD_BOTTOM - self.RECORD_OFFSET * 2)

        # add back to menu button
        self.button_menu = self.new_button(self.BUTTON_WIDTH,
                                           self.BUTTON_HEIGHT,
                                           arcade.color.PASTEL_YELLOW)

        self.button_menu.position = (self.WIDTH * 7 / 8 - self.RECORD_OFFSET,
                                     self.RECORD_BOTTOM - self.RECORD_OFFSET * 2)

        # Create the buttons
        self.back_button = UIFlatButton(text="Back",
                                        width=self.BUTTON_WIDTH,
                                        height=self.BUTTON_HEIGHT,
                                        style=self.back_button_style
                                        )
        self.play_button = UIFlatButton(text="Play",
                                        width=self.BUTTON_WIDTH,
                                        height=self.BUTTON_HEIGHT,
                                        style=self.play_button_style
                                        )
        self.button_box = UIBoxLayout(vertical=False, align="left")
        self.button_box.add(self.play_button.with_space_around(right=self.BUTTON_WIDTH/2,
                                                               left=self.BUTTON_WIDTH/4)
                            )
        self.button_box.add(self.back_button)
        self.manager.add(
            UIAnchorWidget(
                anchor_x="left",
                anchor_y="bottom",
                align_x=self.WIDTH * 4 / 8 - self.RECORD_OFFSET,
                align_y=self.RECORD_BOTTOM - self.RECORD_OFFSET * 2 - self.BUTTON_WIDTH/4,
                child=self.button_box)
        )

    @staticmethod
    def new_button(width, height, color):
        # helper to create new buttons
        button = arcade.SpriteSolidColor(width, height, color)
        return button

    @staticmethod
    def travel(coord_list: list):
        total = 0
        for index in range(coord_list.__len__()):
            if index + 1 not in range(coord_list.__len__()):
                return total
            x1 = coord_list[index][0]
            y1 = coord_list[index][1]
            x2 = coord_list[index + 1][0]
            y2 = coord_list[index + 1][1]
            total += int(((x1 - x2) ** 2 + (y1 - y2) ** 2) ** 0.5)

    @staticmethod
    def draw_text(text, x, y, font_size, width):
        return arcade.draw_text(text, x, y, arcade.color.BLACK, font_size, width,
                                "center", anchor_x="left", anchor_y="top", italic=True, bold=True)

    def draw_button_again(self):
        self.button_again.draw()
        arcade.draw_text('Play again', self.WIDTH * 5 / 8 - self.RECORD_OFFSET,
                         self.RECORD_BOTTOM - self.RECORD_OFFSET * 2,
                         arcade.color.BLACK, 30, bold=True, anchor_x="center", anchor_y="center")

    def draw_button_menu(self):
        self.button_menu.draw()
        arcade.draw_text('Back to menu', self.WIDTH * 7 / 8 - self.RECORD_OFFSET,
                         self.RECORD_BOTTOM - self.RECORD_OFFSET * 2,
                         arcade.color.BLACK, 30, bold=True, anchor_x="center", anchor_y="center")

    def on_show_view(self):
        # Prepare score recording
        # Sign recording
        for _ in self.window.recording:
            if [_][0] == 0 and [_][1] == 0:
                self.window.recording.pop(self.window.recording.index(_))
                print(_)
        self.window.recording = sign_recording(self.window.recording)

        # Record point timing to a separate list

        for _ in self.window.recording:
            if _[-1] == "start":
                self.window.apple_timing.append(_[2:])
            if _[-1] == "point":
                self.window.apple_timing.append(_[2:])

        string = "".join([str(_) + "\n" for _ in self.window.apple_timing])
        print(string)
        self.text_area.text = string

    def on_draw(self):
        # clear the screen
        self.clear(arcade.color.PASTEL_BLUE)

        font_size = int(self.RECORD_OFFSET / 2)

        self.draw_text("You Finished!", 0, self.HEIGHT - self.RECORD_OFFSET * 0.1, font_size, self.WIDTH)

        # draw Score
        output_total = f"Total Score: {self.window.total_score}"
        self.draw_text(output_total, 0, self.HEIGHT - self.RECORD_OFFSET * 1.2, font_size / 2,
                       self.RECORD_WIDTH - self.RECORD_OFFSET)

        # draw Time
        output_time = f"Time taken: {self.window.time_elapsed}"
        self.draw_text(output_time, 0, self.HEIGHT - self.RECORD_OFFSET * 2.2, font_size / 2,
                       self.RECORD_WIDTH - self.RECORD_OFFSET)

        # draw Pixels Traveled
        output_pixels = f"Pixels Traveled: {self.travel(self.window.recording)}"
        self.draw_text(output_pixels, 0, self.HEIGHT - self.RECORD_OFFSET * 3.2, font_size / 2,
                       self.RECORD_WIDTH - self.RECORD_OFFSET)

        # draw buttons
        self.draw_button_again()
        self.draw_button_menu()
        self.manager.draw()

    def on_mouse_press(self, x: int, y: int, button: int, modifiers: int):

        if button == 1:

            if self.button_again.collides_with_point((x, y)):
                game_view = AppleMinigame()
                game_view.setup()
                self.window.show_view(game_view)

            if self.button_menu.collides_with_point((x, y)):
                game_view = MenuView()
                self.window.show_view(game_view)


class GameWindow(arcade.Window):

    def __init__(self):
        super().__init__(title="EyeFit",
                         resizable=False,
                         fullscreen=True)
        self.total_score = 0
        self.apple_count = APPLE_COUNT
        self.recording = []
        self.apple_timing = []
        self.time_elapsed = ""
        self.background_type = "default"

    # def on_key_press(self, symbol: int, modifiers: int):
    #   if symbol == arcade.key.ESCAPE:
    #      arcade.exit()


def main():
    """ Main function """
    window = GameWindow()
    view = MenuView()
    window.set_mouse_visible(True)
    window.show_view(view)
    arcade.run()


if __name__ == "__main__":
    main()
