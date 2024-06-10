import math
import random
import time

import arcade
import arcade.gui
import numpy as np
from arcade.experimental.uislider import UISlider
from arcade.gui import UIManager, UILabel, UISpace, UIBoxLayout, UIFlatButton, UITextureButton, \
    UIAnchorWidget, UITextArea, UITexturePane
from arcade.gui.events import UIOnChangeEvent, UIOnClickEvent

SPRITE_SCALING_APPLE = 0.1
SPRITE_SCALING_BASKET = 0.2
APPLE_COUNT = 1
BASKET_SPEED = 5
SPEED_INCREMENT = 1
MAX_SPEED = 10
OFFSET_MULTIPLIER = 0.08
# Number of bins in each dimension
HEATMAP_RESOLUTION_X = 16 * 8
HEATMAP_RESOLUTION_Y = 9 * 8
# Radius of the effect around the mouse position in bins
KERNEL_RADIUS = 4
SPRITE_SCALE = .5
# acceleration of shield when following the mouse
RADIANS_PER_FRAME = 0.08


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


def sign_recording(list_a, last_view):
    for _ in list_a:
        if _[0] == 0 and _[1] == 0:
            list_a.pop(list_a.index(_))

    list_a[0] = list_a[0][0:-1] + ("start",)
    list_a[-1] = list_a[-1][0:-1] + ("point",)
    score = 0

    if "Shield" in str(last_view):
        list_a[0] = list_a[0][0:-1] + ("normal",)
    # Create a copy of the list for iteration
    list_b = list_a.copy()
    if "Apple" in str(last_view):
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


class DustAnim(arcade.Sprite):
    def __init__(self, x, y, scale):
        super().__init__()
        self.cur_texture = 1
        self.dust_anim = []
        self.timer = 10
        self.center_x = x
        self.center_y = y
        self.scale = scale

        # --- Load Textures ---
        main_path = "resources/dust_anim/dust_"

        for i in range(1, 9):
            texture = arcade.load_texture(f"{main_path}{i}.png")
            self.dust_anim.append(texture)

    def update_animation(self, delta_time: float = 1 / 60):
        if self.timer == 10:
            if self.cur_texture == 8:
                self.remove_from_sprite_lists()
            else:
                self.texture = self.dust_anim[self.cur_texture]
                self.alpha -= 20
                self.cur_texture += 1
                self.timer = 0
        self.timer += 1


class RotatingSprite(arcade.Sprite):
    def __init__(self, texture: str, scale):
        super().__init__()
        self.texture = arcade.load_texture(texture)
        self.scale = scale
        self.angle = 0
        self.target_angle = 0

    def set_rotation(self, angle):
        # If change_angle is true, change the sprite's angle
        self.angle = angle


class Snowflake:
    def __init__(self):
        self.WIDTH = int(arcade.get_viewport()[1])
        self.HEIGHT = int(arcade.get_viewport()[3])
        self.x = 0
        self.y = 0

    def reset_pos(self):
        # Reset flake to random position above screen
        self.y = random.randrange(self.HEIGHT, self.HEIGHT + 100)
        self.x = random.randrange(self.WIDTH)


class ShakeSprite(arcade.Sprite):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.original_x = self.center_x
        self.shaking = False
        self.shake_start_time = 0
        self.last_shake_time = 0

    def shake(self):
        self.shaking = True
        self.shake_start_time = time.time()
        self.last_shake_time = self.shake_start_time

    def update(self):
        if self.shaking:
            current_time = time.time()
            if current_time - self.shake_start_time < .5:
                if current_time - self.last_shake_time >= .05:
                    self.center_x = self.original_x + random.randint(-10, 10)
                    self.last_shake_time = current_time
            else:
                self.shaking = False
                self.center_x = self.original_x


class Radar:
    def __init__(self):
        self.WIDTH = int(arcade.get_viewport()[1])
        self.HEIGHT = int(arcade.get_viewport()[3])
        self.OFFSET = int(self.WIDTH * 0.08) * 2
        self.angle = 0
        self.target_angle = 0
        self.CENTER_X = self.WIDTH // 2
        self.CENTER_Y = self.HEIGHT // 2

    def update(self):
        # Move the angle of the sweep towards the target angle.
        angle_diff = self.target_angle - self.angle

        # Ensure the shortest rotation direction
        if angle_diff > math.pi:
            angle_diff -= 2 * math.pi
        elif angle_diff < -math.pi:
            angle_diff += 2 * math.pi

        self.angle += angle_diff * RADIANS_PER_FRAME

        # Normalize the angle to keep it between 0 and 2 * math.pi
        self.angle %= 2 * math.pi

    def get_coordinates(self, element: str):
        """available elements are: "shield", "left", "right" """
        if element == "shield":
            x = self.OFFSET * math.sin(self.angle) + self.CENTER_X
            y = self.OFFSET * math.cos(self.angle) + self.CENTER_Y
            return x, y
        if element == "left":
            x = self.OFFSET * math.sin(self.angle - SPRITE_SCALE) + self.CENTER_X
            y = self.OFFSET * math.cos(self.angle - SPRITE_SCALE) + self.CENTER_Y
            return x, y
        if element == "right":
            x = self.OFFSET * math.sin(self.angle + SPRITE_SCALE) + self.CENTER_X
            y = self.OFFSET * math.cos(self.angle + SPRITE_SCALE) + self.CENTER_Y
            return x, y

    def update_target_angle(self, mouse_x, mouse_y):
        self.target_angle = -math.atan2(mouse_y - self.CENTER_Y, mouse_x - self.CENTER_X) + math.pi / 2


class Heatmap(arcade.Section):
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
                pass
            else:
                start_x, start_y = self.window.recording[index][0] + self.x_offset, self.window.recording[index][
                    1] + self.y_offset
                end_x = self.window.recording[index + 1][0] + self.x_offset
                end_y = self.window.recording[index + 1][1] + self.y_offset

                if self.line_counter == index:
                    draw_line(start_x, start_y, end_x, end_y, self.opacity)
                    self.line_counter += 1
            self.opacity_float += self.opacity_increment

        self.opacity_float = .0
        self.opacity = 1

        for index in range(self.window.recording.__len__()):
            self.opacity = int(self.opacity_float)

            if index == self.window.recording.__len__() - 1:
                start_x, start_y = self.window.recording[index][0] + self.x_offset, self.window.recording[index][
                    1] + self.y_offset
                draw_point(start_x, start_y, 255, self.window.recording[index][-1])
                draw_number(start_x, start_y, self.window.recording[index][-2], 255)
            else:
                start_x, start_y = self.window.recording[index][0] + self.x_offset, self.window.recording[index][
                    1] + self.y_offset
                end_x = self.window.recording[index + 1][0] + self.x_offset
                end_y = self.window.recording[index + 1][1] + self.y_offset

                if self.line_counter == index:
                    draw_line(start_x, start_y, end_x, end_y, self.opacity)
                    self.line_counter += 1
                if self.circle_counter == index:
                    if self.window.recording[index][-1] == "start":
                        draw_point(start_x, start_y, 255, "start")
                        draw_number(start_x, start_y, self.window.recording[index][-2], 255)
                    elif self.window.recording[index][-1] == "point":
                        draw_point(start_x, start_y, 255, "point")
                        draw_number(start_x, start_y, self.window.recording[index][-2], 255)
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

    def on_show_section(self):
        Heatmap.enabled = False

    def on_mouse_press(self, x: int, y: int, button: int, modifiers: int):
        Heatmap.enabled = not Heatmap.enabled


class ModalSection(arcade.Section):
    """ A modal section that represents a popup that waits for user input """

    def __init__(self, left: int, bottom: int, width: int, height: int, offset: int, font_size: int):
        super().__init__(left, bottom, width, height, modal=True, enabled=False)

        # modal button
        self.offset = offset

        self.manager = UIManager()
        self.manager.enable()

        # Create a vertical BoxGroup to align buttons
        self.v_box = arcade.gui.UIBoxLayout(vertical=True)

        # Create the button styles
        self.continue_button_style = {
            "font_name": "calibri",
            "font_size": font_size,
            "font_color": arcade.color.BLACK,
            "border_color": arcade.color.BLACK,
            "border_width": 4,
            "bg_color": arcade.color.PASTEL_GREEN,
            "bg_color_pressed": arcade.color.PASTEL_GREEN,
            "border_color_pressed": arcade.color.WHITE,
            "font_color_pressed": arcade.color.WHITE_SMOKE,

        }
        self.return_button_style = {
            "font_name": "calibri",
            "font_size": font_size,
            "font_color": arcade.color.BLACK,
            "border_color": arcade.color.BLACK,
            "border_width": 4,
            "bg_color": arcade.color.PASTEL_YELLOW,
            "bg_color_pressed": arcade.color.PASTEL_YELLOW,
            "border_color_pressed": arcade.color.WHITE,
            "font_color_pressed": arcade.color.WHITE_SMOKE,

        }

        self.continue_button = arcade.gui.UIFlatButton(text="Continue",
                                                       width=offset * 2,
                                                       height=offset,
                                                       style=self.continue_button_style
                                                       )
        self.return_button = arcade.gui.UIFlatButton(text="Return to Menu",
                                                     width=offset * 2,
                                                     height=offset,
                                                     style=self.return_button_style
                                                     )
        self.v_box.add(self.continue_button.with_space_around(bottom=int(offset / 10)))
        self.v_box.add(self.return_button)

        @self.continue_button.event()
        def on_click(event: UIOnClickEvent):
            print("Continue:", event)
            self.enabled = False

        @self.return_button.event()
        def on_click(event: UIOnClickEvent):
            print("Return to Menu:", event)
            view = MenuView()
            self.window.show_view(view)

        self.manager.add(UIAnchorWidget(child=self.v_box))

    def on_draw(self):
        # draw modal frame and buttons
        arcade.draw_lrtb_rectangle_filled(self.left, self.right, self.top,
                                          self.bottom, arcade.color.GRAY)
        arcade.draw_lrtb_rectangle_outline(self.left, self.right, self.top,
                                           self.bottom, arcade.color.BLACK, int(self.offset * .1))
        self.manager.draw()
        self.manager.disable()
        self.manager.enable()

    def on_hide_section(self):
        self.manager.disable()
        self.window.set_mouse_visible(False)

    def on_show_section(self):
        self.window.set_mouse_visible(True)

    def on_key_press(self, symbol: int, modifiers: int):
        if symbol == arcade.key.ESCAPE:
            self.enabled = False


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
        # Change destination
        else:
            dest_x = self.position_list[self.cur_position][0]
            dest_y = self.position_list[self.cur_position][1]

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

        # Distance to target location
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
        print("offset is ", self.OFFSET)

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
        if self.window.webcam_mode:
            self.mode_checkbox = UITextureButton(texture=arcade.load_texture("resources/checked.png"))
        if not self.window.webcam_mode:
            self.mode_checkbox = UITextureButton(texture=arcade.load_texture("resources/unchecked.png"))
        # Track the state of the mode_checkbox
        self.mode_enabled = self.window.webcam_mode

        @self.mode_checkbox.event()
        def on_click(event: UIOnClickEvent):
            print("mode_checkbox: ", event, self.mode_enabled)
            if not self.mode_enabled:
                self.mode_checkbox.texture = arcade.load_texture("resources/checked.png")
                self.mode_enabled = True
            else:
                self.mode_checkbox.texture = arcade.load_texture("resources/unchecked.png")
                self.mode_enabled = False

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
            if self.mode_enabled:
                self.window.webcam_mode = True
            if not self.mode_enabled:
                self.window.webcam_mode = False
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
        self.apples_button = self.minigame_button("resources/minigame_apples.png",
                                                  "resources/minigame_apples_hover.png",
                                                  "resources/minigame_apples_click.png")
        self.shield_button = self.minigame_button("resources/minigame_shield.png",
                                                  "resources/minigame_shield_hover.png",
                                                  "resources/minigame_shield_click.png")

        self.title_label = UILabel(text="Apple minigame settings and instructions", font_size=self.OFFSET / 3,
                                   text_color=arcade.color.BLACK, bold=True)

        self.h_row_1.add(self.apples_button.with_space_around(10, 10, 10, 10))
        self.h_row_1.add(self.shield_button.with_space_around(10, 10, 10, 10))

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

        @self.shield_button.event()
        def on_click(event: UIOnClickEvent):
            print("Shield:", event)
            view = ShieldInstruction()
            self.window.show_view(view)

    def minigame_button(self, texture, texture_hover, texture_click):
        return UITextureButton(texture=arcade.load_texture(texture),
                               texture_hovered=arcade.load_texture(texture_hover),
                               texture_pressed=arcade.load_texture(texture_click),
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
        self.apple_slider = UISlider(value=self.window.apple_slider_value,
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
        if self.window.background_type == "cam":
            self.cam_background = UITextureButton(
                texture=arcade.load_texture("resources/bg_cam_selected.png"),
                texture_hovered=arcade.load_texture("resources/bg_cam_selected.png"),
                texture_pressed=arcade.load_texture("resources/bg_cam_selected.png")
            )
            self.normal_background = UITextureButton(
                texture=arcade.load_texture("resources/apple_bg_default.png"),
                texture_hovered=arcade.load_texture("resources/apple_bg_default_hovered.png"),
                texture_pressed=arcade.load_texture("resources/apple_bg_default_selected.png")
            )
        if self.window.background_type == "default":
            self.cam_background = UITextureButton(
                texture=arcade.load_texture("resources/bg_cam.png"),
                texture_hovered=arcade.load_texture("resources/bg_cam_hovered.png"),
                texture_pressed=arcade.load_texture("resources/bg_cam_selected.png")
            )
            self.normal_background = UITextureButton(
                texture=arcade.load_texture("resources/apple_bg_default_selected.png"),
                texture_hovered=arcade.load_texture("resources/apple_bg_default_selected.png"),
                texture_pressed=arcade.load_texture("resources/apple_bg_default_selected.png")
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

        @self.cam_background.event()
        def on_click(event: UIOnClickEvent):
            print("Cam background set:", event)
            if self.window.background_type == "default":
                self.window.background_type = "cam"
                self.cam_background.texture = arcade.load_texture("resources/bg_cam_selected.png")
                self.cam_background.texture_pressed = arcade.load_texture("resources/bg_cam_selected.png")
                self.cam_background.texture_hovered = arcade.load_texture("resources/bg_cam_selected.png")
                self.normal_background.texture = arcade.load_texture("resources/apple_bg_default.png")
                self.normal_background.texture_pressed = arcade.load_texture("resources/apple_bg_default_selected.png")
                self.normal_background.texture_hovered = arcade.load_texture("resources/apple_bg_default_hovered.png")

        @self.normal_background.event()
        def on_click(event: UIOnClickEvent):
            print("Normal background set:", event)
            if self.window.background_type == "cam":
                self.window.background_type = "default"
                self.normal_background.texture = arcade.load_texture("resources/apple_bg_default_selected.png")
                self.normal_background.texture_pressed = arcade.load_texture("resources/apple_bg_default_selected.png")
                self.normal_background.texture_hovered = arcade.load_texture("resources/apple_bg_default_selected.png")
                self.cam_background.texture = arcade.load_texture("resources/bg_cam.png")
                self.cam_background.texture_pressed = arcade.load_texture("resources/bg_cam_selected.png")
                self.cam_background.texture_hovered = arcade.load_texture("resources/bg_cam_hovered.png")

        @self.play_button.event()
        def on_click(event: UIOnClickEvent):
            print("Play:", event)
            self.window.apple_count = int(self.apple_slider.value)
            view = AppleMinigame()
            view.setup()
            self.window.show_view(view)

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
        self.window.last_view = self.window.current_view

    def on_draw(self):
        self.clear()
        self.manager.draw()

    def on_hide_view(self):
        self.manager.disable()


class AppleMinigame(arcade.View):
    def __init__(self):
        super().__init__()
        self.WIDTH = int(arcade.get_viewport()[1])
        self.HEIGHT = int(arcade.get_viewport()[3])
        self.OFFSET = int(self.WIDTH * OFFSET_MULTIPLIER)
        self.FONT_SIZE = int(self.OFFSET / 4)
        # constant kernel for heatmap creation
        self.kernel = self.create_circular_gaussian_kernel(KERNEL_RADIUS)
        self.window.game_lost = False
        self.section_list = []
        self.section_list_index = random.randint(1, 4)

        for sec_x in range(1, self.window.apple_sections[0] + 1):
            for sec_y in range(1, self.window.apple_sections[1] + 1):
                print(sec_x, sec_y)
                sec_width = (self.WIDTH // self.window.apple_sections[0]) * sec_x
                sec_height = (self.HEIGHT // self.window.apple_sections[1]) * sec_y
                print(sec_width, sec_height)
                self.section_list.append((sec_width, sec_height))
        print(self.section_list)

        if self.window.background_type == "cam":
            self.shape_list = None

            # Calculate the diagonal of the screen
            self.DIAGONAL = int((self.WIDTH ** 2 + self.HEIGHT ** 2) ** 0.5)

            # Set shape size to be larger than the screen diagonal
            self.SHAPE_SIZE = self.DIAGONAL + 100
            self.text_color = arcade.color.RED

        elif self.window.background_type == "default":
            arcade.set_background_color(arcade.color.PASTEL_GREEN)
            self.text_color = arcade.color.WHITE

        self.modal_section = ModalSection(int(self.WIDTH / 4) + self.OFFSET,
                                          int(self.HEIGHT / 3) - int(self.OFFSET / 2),
                                          int(self.WIDTH / 4) + self.OFFSET,
                                          int(self.HEIGHT / 3) + self.OFFSET, self.OFFSET, self.FONT_SIZE)
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

        # Declarations of constants
        self.pointer_x = 0
        self.pointer_y = 0

        self.mouse_x = 0
        self.mouse_y = 0

        if self.window.webcam_mode:
            self.deadzone_radius = 50
        else:
            self.deadzone_radius = 0
        self.pointer_radius = 50

        self.section_manager.add_section(self.modal_section)

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

    def setup(self):
        """ Set up the game and initialize the variables. """
        # clear score
        self.window.total_score = 0
        # self.window.apple_count = APPLE_COUNT

        # clear recording
        self.window.recording = []

        # clear score timings
        self.window.apple_timing = []

        self.window.start_time = time.time()
        self.window.heatmap = np.zeros((HEATMAP_RESOLUTION_X, HEATMAP_RESOLUTION_Y))

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
        if self.window.background_type == "cam":
            player = self.player_sprite = arcade.Sprite("resources/cam_apple.png",
                                                        SPRITE_SCALING_APPLE,
                                                        center_x=0,
                                                        center_y=0)
        else:
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

    def create_apple(self, ):
        """Create a single apple and add it to the apple list."""
        max_attempts = 50
        for _ in range(max_attempts):
            if self.window.background_type == "cam":
                apple = arcade.Sprite("resources/cam_apple.png", SPRITE_SCALING_APPLE)
            else:
                apple = arcade.Sprite("resources/apple.png", SPRITE_SCALING_APPLE)
            # apple.center_x = random.randrange(+ self.OFFSET // 2, coord[0] - self.OFFSET // 2)
            # apple.center_y = random.randrange(self.OFFSET // 2, coord[1] - self.OFFSET // 2)
            if self.section_list_index == 1:
                apple.center_x = random.randrange(0 + self.OFFSET // 2, self.section_list[0][0] - self.OFFSET // 2)
                apple.center_y = random.randrange(0 + self.OFFSET // 2, self.section_list[0][1] - self.OFFSET // 2)
                print("Apple spawned in sec1")
            if self.section_list_index == 2:
                apple.center_x = random.randrange(0 + self.OFFSET // 2, self.section_list[0][0])
                apple.center_y = random.randrange(self.section_list[0][1] + self.OFFSET // 2,
                                                  self.section_list[1][1] - self.OFFSET // 2)
                print("Apple spawned in sec2")
            if self.section_list_index == 3:
                apple.center_x = random.randrange(self.section_list[0][0] + self.OFFSET // 2,
                                                  self.section_list[2][0] - self.OFFSET // 2)
                apple.center_y = random.randrange(0 + self.OFFSET // 2, self.section_list[0][1])
                print("Apple spawned in sec3")
            if self.section_list_index == 4:
                apple.center_x = random.randrange(self.section_list[0][0] + self.OFFSET // 2,
                                                  self.section_list[2][0] - self.OFFSET // 2)
                apple.center_y = random.randrange(self.section_list[0][1] + self.OFFSET // 2,
                                                  self.section_list[1][1] - self.OFFSET // 2)
                print("Apple spawned in sec4")

            self.section_list_index += 1
            if self.section_list_index == self.window.apple_sections[0] * self.window.apple_sections[1] + 1:
                self.section_list_index = 1

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

            # noinspection PyTypeChecker
            self.window.recording.append(
                self.move_pointer() + (self.total_time, self.window.total_score + 1, "normal"))

            self.update_heatmap(self.mouse_x, self.mouse_y)

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
                game_over_view = MinigameOverView()
                self.window.show_view(game_over_view)

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

    def on_show_view(self):
        # hide mouse
        self.window.set_mouse_visible(True)

    def on_hide_view(self):
        # show mouse
        self.window.set_mouse_visible(True)

    def paused(self):
        if self.modal_section.enabled:
            return True


class MinigameOverView(arcade.View):

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
                                name='Click to reveal Heatmap'))

        self.add_section(Heatmap(self.RECORD_LEFT - self.RECORD_OFFSET,
                                 self.RECORD_BOTTOM - self.RECORD_OFFSET,
                                 self.RECORD_WIDTH,
                                 self.RECORD_HEIGHT))

        text = ""
        self.text_area = UITextArea(x=self.RECORD_OFFSET + self.RECORD_OFFSET / 2,
                                    y=self.RECORD_OFFSET,
                                    width=(self.WIDTH - self.RECORD_WIDTH - self.RECORD_OFFSET) / 2,
                                    height=self.RECORD_HEIGHT - self.RECORD_OFFSET - self.RECORD_OFFSET / 2,
                                    text=text,
                                    text_color=(0, 0, 0, 255),
                                    font_size=self.FONT_SIZE / 2
                                    )
        bg_tex = arcade.load_texture("resources/grey_panel.png")

        self.manager.add(UITexturePane(
            self.text_area.with_space_around(
                top=int(self.RECORD_OFFSET / 4),
                bottom=int(self.RECORD_OFFSET / 4)),
            tex=bg_tex,
            padding=(0, 0, 0, (self.RECORD_OFFSET / 3) * 2))
        )

        # Create the buttons
        self.back_button = UIFlatButton(text="Menu",
                                        width=self.BUTTON_WIDTH,
                                        height=self.BUTTON_HEIGHT,
                                        style=self.back_button_style
                                        )
        self.play_button = UIFlatButton(text="Replay",
                                        width=self.BUTTON_WIDTH,
                                        height=self.BUTTON_HEIGHT,
                                        style=self.play_button_style
                                        )
        self.button_box = UIBoxLayout(vertical=False, align="left")
        self.button_box.add(self.play_button.with_space_around(right=self.BUTTON_WIDTH / 2,
                                                               left=self.BUTTON_WIDTH / 4)
                            )
        self.button_box.add(self.back_button)
        self.manager.add(
            UIAnchorWidget(
                anchor_x="left",
                anchor_y="bottom",
                align_x=self.WIDTH * 4 / 8 - self.RECORD_OFFSET,
                align_y=self.RECORD_BOTTOM - self.RECORD_OFFSET * 2 - self.BUTTON_WIDTH / 4,
                child=self.button_box)
        )

        @self.play_button.event()
        def on_click(event: UIOnClickEvent):
            print("Replay:", event)
            if "Apple" in str(self.window.last_view):
                view = AppleInstruction()
                print(view)
                self.window.show_view(view)
            if "Shield" in str(self.window.last_view):
                view = ShieldInstruction()
                print(view)
                self.window.show_view(view)

        @self.back_button.event()
        def on_click(event: UIOnClickEvent):
            print("Menu:", event)
            view = MenuView()
            self.window.show_view(view)

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

    def on_show_view(self):
        # Prepare score recording
        # Sign recording

        self.window.recording = sign_recording(self.window.recording, self.window.last_view)

        # Record point timing to a separate list

        for _ in self.window.recording:
            if _[-1] == "start":
                self.window.apple_timing.append(_[2:])
            if _[-1] == "point":
                self.window.apple_timing.append(_[2:])

        string = "".join([str(_[1]) + " - " + str(_[2]) + " - time: " +
                          f"{int(_[0]) // 60:02d}:{int(_[0]) % 60:02d}:{int((_[0] - int(_[0]) % 60) * 100):02d}" + "\n"
                          for _ in self.window.apple_timing])
        self.text_area.text = string

    def on_draw(self):
        # clear the screen
        self.clear(arcade.color.PASTEL_BLUE)

        font_size = int(self.RECORD_OFFSET / 2)
        if "Shield" in str(self.window.last_view) and self.window.game_lost:
            text = "You Lost!"
        else:
            text = "You Finished!"
        self.draw_text(text, 0, self.HEIGHT - self.RECORD_OFFSET * 0.1, font_size, self.WIDTH)

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

        # draw ui manager
        self.manager.draw()

    def on_hide_view(self):
        self.manager.disable()


class ShieldInstruction(arcade.View):
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
        self.apple_slider = UISlider(value=self.window.apple_slider_value,
                                     min_value=1,
                                     max_value=99,
                                     width=int(self.WIDTH / 3),
                                     height=self.OFFSET / 2
                                     )
        self.number = UILabel(text=f"{int(self.apple_slider.value):02.0f}",
                              font_size=self.OFFSET / 3,
                              text_color=arcade.color.BLACK
                              )

        self.slider_label = UILabel(text="Number of meteors",
                                    font_size=self.OFFSET / 3,
                                    text_color=arcade.color.BLACK
                                    )
        if self.window.background_type == "cam":
            self.cam_background = UITextureButton(
                texture=arcade.load_texture("resources/bg_cam_selected.png"),
                texture_hovered=arcade.load_texture("resources/bg_cam_selected.png"),
                texture_pressed=arcade.load_texture("resources/bg_cam_selected.png")
            )
            self.normal_background = UITextureButton(
                texture=arcade.load_texture("resources/shield_bg_default.png"),
                texture_hovered=arcade.load_texture("resources/shield_bg_default_hovered.png"),
                texture_pressed=arcade.load_texture("resources/shield_bg_default_selected.png")
            )
        if self.window.background_type == "default":
            self.cam_background = UITextureButton(
                texture=arcade.load_texture("resources/bg_cam.png"),
                texture_hovered=arcade.load_texture("resources/bg_cam_hovered.png"),
                texture_pressed=arcade.load_texture("resources/bg_cam_selected.png")
            )
            self.normal_background = UITextureButton(
                texture=arcade.load_texture("resources/shield_bg_default_selected.png"),
                texture_hovered=arcade.load_texture("resources/shield_bg_default_selected.png"),
                texture_pressed=arcade.load_texture("resources/shield_bg_default_selected.png")
            )

        self.background_label = UILabel(text="Background",
                                        font_size=self.OFFSET / 3,
                                        text_color=arcade.color.BLACK
                                        )
        self.title_label = UILabel(text="Shield minigame settings and instructions",
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

        @self.cam_background.event()
        def on_click(event: UIOnClickEvent):
            print("Cam background set:", event)
            if self.window.background_type == "default":
                self.window.background_type = "cam"
                self.cam_background.texture = arcade.load_texture("resources/bg_cam_selected.png")
                self.cam_background.texture_pressed = arcade.load_texture("resources/bg_cam_selected.png")
                self.cam_background.texture_hovered = arcade.load_texture("resources/bg_cam_selected.png")
                self.normal_background.texture = arcade.load_texture("resources/shield_bg_default.png")
                self.normal_background.texture_pressed = arcade.load_texture("resources/shield_bg_default_selected.png")
                self.normal_background.texture_hovered = arcade.load_texture("resources/shield_bg_default_hovered.png")

        @self.normal_background.event()
        def on_click(event: UIOnClickEvent):
            print("Normal background set:", event)
            if self.window.background_type == "cam":
                self.window.background_type = "default"
                self.normal_background.texture = arcade.load_texture("resources/shield_bg_default_selected.png")
                self.normal_background.texture_pressed = arcade.load_texture("resources/shield_bg_default_selected.png")
                self.normal_background.texture_hovered = arcade.load_texture("resources/shield_bg_default_selected.png")
                self.cam_background.texture = arcade.load_texture("resources/bg_cam.png")
                self.cam_background.texture_pressed = arcade.load_texture("resources/bg_cam_selected.png")
                self.cam_background.texture_hovered = arcade.load_texture("resources/bg_cam_hovered.png")

        @self.play_button.event()
        def on_click(event: UIOnClickEvent):
            print("Play:", event)
            self.window.enemy_count = int(self.apple_slider.value)
            view = ShieldMinigame()
            view.setup()
            self.window.show_view(view)

        @self.back_button.event()
        def on_click(event: UIOnClickEvent):
            print("Back:", event)
            view = MinigameSelect()
            self.window.show_view(view)

        @self.apple_slider.event()
        def on_change(event: UIOnChangeEvent):
            print("Shield Slider Change:", event)
            self.number.text = f"{int(self.apple_slider.value):02.0f}"
            self.number.fit_content()

    def on_show_view(self):
        arcade.set_background_color(arcade.color.DARK_PASTEL_BLUE)
        self.window.last_view = self.window.current_view

    def on_draw(self):
        self.clear()
        self.manager.draw()

    def on_hide_view(self):
        self.manager.disable()


class ShieldMinigame(arcade.View):
    def __init__(self):
        super().__init__()
        self.MOVEMENT_SPEED = None
        self.WIDTH = int(arcade.get_viewport()[1])
        self.HEIGHT = int(arcade.get_viewport()[3])
        self.OFFSET = int(self.WIDTH * 0.08)
        self.CENTER_X = self.WIDTH // 2
        self.CENTER_Y = self.HEIGHT // 2
        self.text_color = arcade.color.WHITE
        self.travel_time = 7
        self.FONT_SIZE = int(self.OFFSET / 4)
        self.lives = 3
        self.window.game_lost = False

        # Timer
        self.total_time = 0.0

        self.side_list = {}

        self.radar = Radar()
        self.shield = RotatingSprite("resources/shield.png", SPRITE_SCALE)
        self.ship = ShakeSprite("resources/ship.png",
                                center_x=self.CENTER_X,
                                center_y=self.CENTER_Y)
        self.left = arcade.Sprite("resources/left.png", SPRITE_SCALE)
        self.right = arcade.Sprite("resources/right.png", SPRITE_SCALE)
        self.player_sprite = arcade.SpriteCircle(50, (0, 0, 0))

        # Sprite lists
        self.snowflake_list = None
        self.shield_sprite_list = arcade.SpriteList()
        self.ship_sprite_list = arcade.SpriteList()
        self.left_sprite_list = arcade.SpriteList()
        self.right_sprite_list = arcade.SpriteList()
        self.enemy_list = arcade.SpriteList()
        self.lives_sprite_list = arcade.SpriteList()
        self.dust_list = arcade.SpriteList()

        self.ship_sprite_list.extend([self.ship])
        self.shield_sprite_list.extend([self.shield])
        self.left_sprite_list.extend([self.left])
        self.right_sprite_list.extend([self.right])
        for number in range(3):
            self.lives_sprite = arcade.Sprite("resources/ship.png", SPRITE_SCALE)
            self.lives_sprite.center_x = self.WIDTH - self.OFFSET // 5 - number * 75
            self.lives_sprite.center_y = self.HEIGHT - self.OFFSET // 5
            self.lives_sprite_list.extend([self.lives_sprite])

        # Declarations of constants
        self.pointer_x = 0
        self.pointer_y = 0

        self.mouse_x = 0
        self.mouse_y = 0

        self.deadzone_radius = 50
        self.pointer_radius = 50

        # Snowfall control variables
        self.snowfall_active = True
        self.snowfall_speed_multiplier = 1.0

        self.kernel = self.create_circular_gaussian_kernel(KERNEL_RADIUS)

        self.modal_section = ModalSection(int(self.WIDTH / 4) + self.OFFSET,
                                          int(self.HEIGHT / 3) - int(self.OFFSET / 2),
                                          int(self.WIDTH / 4) + self.OFFSET,
                                          int(self.HEIGHT / 3) + self.OFFSET, self.OFFSET, self.FONT_SIZE)

        if self.window.background_type == "cam":
            self.shape_list = None

            # Calculate the diagonal of the screen
            self.DIAGONAL = int((self.WIDTH ** 2 + self.HEIGHT ** 2) ** 0.5)

            # Set shape size to be larger than the screen diagonal
            self.SHAPE_SIZE = self.DIAGONAL + 100
            self.text_color = arcade.color.RED

        elif self.window.background_type == "default":
            arcade.set_background_color(arcade.color.DARK_MIDNIGHT_BLUE)
            self.text_color = arcade.color.WHITE

        self.section_manager.add_section(self.modal_section)

        # Timer
        self.total_time = 0.0
        self.timer_text = arcade.Text(
            text="00:00",
            start_x=self.WIDTH // 2,
            start_y=self.HEIGHT // 2 - self.OFFSET,
            color=self.text_color,
            font_size=self.OFFSET // 5,
            anchor_x="center",
        )

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

    def setup(self):
        """ Set up the game and initialize the variables. """
        # clear score
        self.window.total_score = 0
        self.start_snowfall()
        # clear recording
        self.window.recording = []
        # clear score timings
        self.window.apple_timing = []
        # Timer
        self.total_time = 0.0

        self.window.heatmap = np.zeros((HEATMAP_RESOLUTION_X, HEATMAP_RESOLUTION_Y))

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

    def start_snowfall(self):
        """ Set up snowfall and initialize variables. """
        self.snowflake_list = []

        for i in range(50):
            # Create snowflake instance
            snowflake = Snowflake()

            # Randomly position snowflake
            snowflake.x = random.randrange(self.WIDTH)
            snowflake.y = random.randrange(self.HEIGHT + 200)

            # Set other variables for the snowflake
            snowflake.size = random.randrange(4)
            snowflake.speed = random.randrange(80, 120)
            snowflake.angle = random.uniform(math.pi, math.pi * 2)

            # Add snowflake to snowflake list
            self.snowflake_list.append(snowflake)

    def add_enemy(self):
        """ Add a new enemy sprite that starts just outside the screen and heads to the center. """
        enemy_sprite = arcade.Sprite("resources/meteor.png", SPRITE_SCALE * 4)
        if len(self.side_list) == 0:
            self.side_list = {"left", "right", "top", "bottom"}
        side = random.choice(list(self.side_list))
        self.side_list.remove(side)

        if side == "left":
            enemy_sprite.center_x = -enemy_sprite.width // 2
            enemy_sprite.center_y = random.randint(0, self.HEIGHT)
        elif side == "right":
            enemy_sprite.center_x = self.WIDTH + enemy_sprite.width // 2
            enemy_sprite.center_y = random.randint(0, self.HEIGHT)
        elif side == "top":
            enemy_sprite.center_x = random.randint(0, self.WIDTH)
            enemy_sprite.center_y = self.HEIGHT + enemy_sprite.height // 2
        else:  # "bottom"
            enemy_sprite.center_x = random.randint(0, self.WIDTH)
            enemy_sprite.center_y = -enemy_sprite.height // 2

        # Calculate the angle to the center
        dest_x = self.CENTER_X
        dest_y = self.CENTER_Y
        x_diff = dest_x - enemy_sprite.center_x
        y_diff = dest_y - enemy_sprite.center_y
        angle = math.atan2(y_diff, x_diff)

        # Calculate distance to the center
        distance = arcade.get_distance_between_sprites(enemy_sprite, self.ship)

        # Set the enemy velocity
        self.MOVEMENT_SPEED = distance / (self.travel_time * 60)
        enemy_sprite.change_x = self.MOVEMENT_SPEED * math.cos(angle)
        enemy_sprite.change_y = self.MOVEMENT_SPEED * math.sin(angle)

        self.enemy_list.append(enemy_sprite)

    def on_draw(self):
        # Clear screen
        self.clear()
        arcade.start_render()

        if self.window.background_type == "cam":
            # --- Draw all the rectangles
            self.shape_list.draw()
            for snowflake in self.snowflake_list:
                arcade.draw_circle_filled(snowflake.x, snowflake.y, snowflake.size, arcade.color.BLUE)

        # Timer
        self.timer_text.draw()

        # Draw Default background
        if self.window.background_type == "default":
            for snowflake in self.snowflake_list:
                arcade.draw_circle_filled(snowflake.x, snowflake.y, snowflake.size, arcade.color.WHITE)

        arcade.draw_circle_outline(self.WIDTH // 2, self.HEIGHT // 2, self.OFFSET * 2,
                                   arcade.make_transparent_color(arcade.color.PASTEL_VIOLET, 100),
                                   border_width=5, num_segments=40)

        self.ship_sprite_list.draw()
        # Draw shield sprite
        self.shield_sprite_list.draw()
        # Draw left sprite
        self.left_sprite_list.draw()
        # Draw right sprite
        self.right_sprite_list.draw()
        # Draw enemy sprites
        self.enemy_list.draw()
        # Draw player lives
        self.lives_sprite_list.draw()
        # Draw dust animation
        self.dust_list.draw()

        arcade.draw_circle_outline(self.pointer_x, self.pointer_y, self.pointer_radius, arcade.color.PASTEL_VIOLET,
                                   border_width=3, num_segments=40)

        output = f"Score: {self.window.total_score}"
        arcade.draw_text(text=output, start_x=self.WIDTH / 2, start_y=self.HEIGHT / 2 - self.OFFSET * 1.1,
                         color=self.text_color, font_size=self.OFFSET // 5,
                         anchor_x="center", anchor_y="top")

    def on_update(self, delta_time):
        if self.paused():
            pass
        else:
            # Background Rotation
            if self.window.background_type == "cam":
                self.shape_list.angle += .1
            # Gradually adjust the snowfall speed
            if self.snowfall_active:
                if self.snowfall_speed_multiplier < 1.0:
                    self.snowfall_speed_multiplier += .01
            else:
                if self.snowfall_speed_multiplier > 0.0:
                    self.snowfall_speed_multiplier -= .01

            # Animate all the snowflakes falling
            for snowflake in self.snowflake_list:
                snowflake.y -= snowflake.speed * delta_time * self.snowfall_speed_multiplier

                # Check if snowflake has fallen below screen
                if snowflake.y < 0:
                    snowflake.reset_pos()

            # Update the radar
            self.radar.update()

            # ship update
            self.ship_sprite_list.update()

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

            # noinspection PyTypeChecker
            self.window.recording.append(
                self.move_pointer() + (self.total_time, self.window.total_score + 1, "normal"))

            self.update_heatmap(self.mouse_x, self.mouse_y)

            # Update the shield position
            shield_x, shield_y = self.radar.get_coordinates("shield")
            self.shield.center_x = shield_x
            self.shield.center_y = shield_y
            self.shield.angle = -math.degrees(self.radar.angle)

            # Update the left position
            left_x, left_y = self.radar.get_coordinates("left")
            self.left.center_x = left_x
            self.left.center_y = left_y
            self.left.angle = -math.degrees(self.radar.angle)

            # Update the right position
            right_x, right_y = self.radar.get_coordinates("right")
            self.right.center_x = right_x
            self.right.center_y = right_y
            self.right.angle = -math.degrees(self.radar.angle)

            self.move_pointer()

            if not self.enemy_list:
                self.add_enemy()

            self.enemy_list.update()

            if self.dust_list:
                self.dust_list[0].update_animation()

            # Check for collision between the player and enemy
            for enemy in self.enemy_list:
                if arcade.check_for_collision(self.shield, enemy):
                    self.dust_list.append(DustAnim(enemy.center_x, enemy.center_y, 2))
                    enemy.remove_from_sprite_lists()
                    self.window.total_score += 1

            for enemy in self.enemy_list:
                if arcade.check_for_collision(self.ship, enemy):
                    self.dust_list.append(DustAnim(enemy.center_x, enemy.center_y, 2))
                    enemy.remove_from_sprite_lists()
                    self.ship.shake()
                    self.lives_sprite_list.pop()
                    self.lives -= 1

            if self.window.total_score == self.window.enemy_count:
                game_over_view = MinigameOverView()
                self.window.show_view(game_over_view)

            if self.lives == 0:
                self.window.game_lost = True
                game_over_view = MinigameOverView()
                self.window.show_view(game_over_view)

            left_collision_list = arcade.check_for_collision_with_list(self.player_sprite, self.left_sprite_list)
            right_collision_list = arcade.check_for_collision_with_list(self.player_sprite, self.right_sprite_list)

            if left_collision_list or right_collision_list:
                self.window.tracking = True
            else:
                self.window.tracking = False

    def on_mouse_motion(self, x: int, y: int, dx: int, dy: int):
        if self.window.tracking:
            self.radar.update_target_angle(x, y)
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

    def on_hide_view(self):
        # show mouse
        self.window.set_mouse_visible(True)

    def on_key_press(self, symbol: int, modifiers: int):
        if symbol == arcade.key.ESCAPE:
            self.modal_section.enabled = True

    def paused(self):
        if self.modal_section.enabled:
            return True


class GameWindow(arcade.Window):

    def __init__(self):
        super().__init__(title="EyeFit",
                         resizable=False,
                         fullscreen=True)
        self.last_view = None
        self.total_score = 0
        self.apple_count = 0
        self.enemy_count = 0
        self.recording = []
        self.apple_timing = []
        self.time_elapsed = ""
        self.apple_slider_value = 4
        self.shield_slider_value = 4
        self.background_type = "default"
        self.start_time = None
        self.heatmap = None
        self.tracking = False
        self.game_lost = False
        # apple spawn sections parameter tuple(horizontal sections, vertical sections)
        self.apple_sections = (2, 2)
        self.webcam_mode = True

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
