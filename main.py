import arcade
import random
import math
import arcade.gui

SCREEN_TITLE = "Apple Collecting Game"
SPRITE_SCALING_APPLE = 0.1
SPRITE_SCALING_BASKET = 0.2
APPLE_COUNT = 2
BASKET_SPEED = 10
SPEED_INCREMENT = 2
OFFSET_MULTIPLIER = 0.1
RECORDING_SAMPLING = 6  # Recording every x viewport updates


def draw_line(start_x, start_y, end_x, end_y, opacity):
    arcade.draw_line(start_x, start_y, end_x, end_y, arcade.make_transparent_color(arcade.color.BLACK, opacity),
                     6)


def draw_point(start_x, start_y, opacity):
    arcade.draw_circle_filled(start_x, start_y, 30, arcade.make_transparent_color(arcade.color.SMOKE, opacity))
    arcade.draw_circle_outline(start_x, start_y, 30, arcade.make_transparent_color(arcade.color.DARK_SLATE_GRAY,
                                                                                   opacity), 5)


def draw_number(start_x, start_y, index, opacity):
    arcade.draw_text(f"{index}", start_x, start_y, arcade.make_transparent_color(arcade.color.BLACK, opacity),
                     16, anchor_x="center", anchor_y="center", bold=True)


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
        self.opacity_increment = 255 / GameWindow.recording.__len__()
        self.opacity = 1

    def on_draw(self):
        """ Draw this section """

        # Section is selected when mouse is within its boundaries
        arcade.draw_lrtb_rectangle_filled(self.left, self.right, self.top,
                                          self.bottom, arcade.color.WHITE_SMOKE)
        arcade.draw_lrtb_rectangle_outline(self.left, self.right, self.top,
                                           self.bottom, arcade.color.DARK_SLATE_GRAY, 5)
        arcade.draw_text(f'{self.name}', self.left + self.FONT_SIZE,
                         self.top - self.FONT_SIZE * 2, arcade.color.BLACK, self.FONT_SIZE)

        if GameWindow.recording[0] == (0, 0):
            GameWindow.recording.pop(0)
        else:
            pass
        for index in range(GameWindow.recording.__len__()):
            self.opacity = int(self.opacity_float)
            if index == GameWindow.recording.__len__() - 1:
                start_x, start_y = GameWindow.recording[index][0] + self.x_offset, GameWindow.recording[index][
                    1] + self.y_offset
                draw_point(start_x, start_y, 255)
                draw_number(start_x, start_y, self.number_counter, 255)

            else:
                start_x, start_y = GameWindow.recording[index][0] + self.x_offset, GameWindow.recording[index][
                    1] + self.y_offset
                end_x, end_y = GameWindow.recording[index + 1][0] + self.x_offset, GameWindow.recording[index + 1][
                    1] + self.y_offset
                if self.line_counter == index:
                    draw_line(start_x, start_y, end_x, end_y, self.opacity)
                    self.line_counter += 1
                if self.circle_counter == index:
                    draw_point(start_x, start_y, self.opacity)
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

        # --- Required for all code that uses UI element,
        # a UIManager to handle the UI.
        self.manager = arcade.gui.UIManager()
        self.manager.enable()

        # Set background color
        arcade.set_background_color(arcade.color.DARK_BLUE_GRAY)

        # Create a vertical BoxGroup to align buttons
        self.v_box = arcade.gui.UIBoxLayout()

        # Create the buttons
        start_button = arcade.gui.UIFlatButton(text="Start Game", width=200)
        self.v_box.add(start_button.with_space_around(bottom=20))

        settings_button = arcade.gui.UIFlatButton(text="Settings", width=200)
        self.v_box.add(settings_button.with_space_around(bottom=20))

        quit_button = arcade.gui.UIFlatButton(text="Quit", width=200)
        self.v_box.add(quit_button.with_space_around(bottom=20))

        # Method for handling click events,
        # Using a decorator to handle on_click events
        @start_button.event("on_click")
        def on_click_start(event):
            print("Start from decorator:", event)
            view = AppleInstruction()
            self.window.show_view(view)

        @settings_button.event("on_click")
        def on_click_start(event):
            print("Settings?:", event)
            print("modal window(section)")

        @quit_button.event("on_click")
        def on_click_start(event):
            print("Quit:", event)
            arcade.exit()

        # Create a widget to hold the v_box widget, that will center the buttons
        self.manager.add(
            arcade.gui.UIAnchorWidget(
                anchor_x="center_x",
                anchor_y="center_y",
                child=self.v_box)
        )

    def on_draw(self):
        self.clear()
        self.manager.draw()

    def on_mouse_press(self, _x, _y, _button, _modifiers):
        pass


class AppleInstruction(arcade.View):
    def __init__(self):
        super().__init__()

        self.WIDTH = arcade.get_viewport()[1]
        self.HEIGHT = arcade.get_viewport()[3]

    def on_show_view(self):
        arcade.set_background_color(arcade.color.PASTEL_ORANGE)

    def on_draw(self):
        self.clear()

        arcade.draw_text("Instructions Screen", self.WIDTH / 2, self.HEIGHT / 2,
                         arcade.color.BLACK, font_size=50, anchor_x="center")
        arcade.draw_text("Click to advance", self.WIDTH / 2, self.HEIGHT / 2 - 75,
                         arcade.color.GRAY, font_size=20, anchor_x="center")

    def on_mouse_press(self, _x, _y, _button, _modifiers):
        game_view = AppleMinigame()
        game_view.setup()
        self.window.show_view(game_view)

    def on_key_press(self, symbol: int, modifiers: int):
        if symbol == arcade.key.ESCAPE:
            arcade.exit()


class AppleMinigame(arcade.View):
    def __init__(self):
        super().__init__()

        self.WIDTH = arcade.get_viewport()[1]
        self.HEIGHT = arcade.get_viewport()[3]
        self.OFFSET = int(self.WIDTH * 0.08)

        # Timer
        self.total_time = 0.0
        self.timer_text = arcade.Text(
            text="00:00",
            start_x=self.WIDTH // 2,
            start_y=self.HEIGHT // 2 - 50,
            color=arcade.color.WHITE,
            font_size=100,
            anchor_x="center",
        )

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

        arcade.set_background_color(arcade.color.PASTEL_GREEN)

    def setup(self):
        """ Set up the game and initialize the variables. """
        # clear score
        GameWindow.total_score = 0

        # clear recording
        GameWindow.recording = []

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

        # Set up the player
        player = self.player_sprite = arcade.Sprite("apple.png",
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
        basket = Basket("basket.png",
                        SPRITE_SCALING_BASKET,
                        position_list)

        # Set initial location of the basket at the first point
        basket.center_x = position_list[0][0]
        basket.center_y = position_list[0][1]

        # Add the basket to the basket list
        self.basket_list.append(basket)

        # Create the apples
        for i in range(APPLE_COUNT):
            # Create the apple instance
            apple = arcade.Sprite("apple.png",
                                  SPRITE_SCALING_APPLE)
            # Position the apple
            width, height = int(arcade.get_viewport()[1]), int(arcade.get_viewport()[3])
            apple.center_x = random.randrange(self.OFFSET, (width - self.OFFSET))
            apple.center_y = random.randrange(self.OFFSET, (height - self.OFFSET))

            # Add the apple to the lists
            self.apple_list.append(apple)

    def on_draw(self):

        self.clear()

        # Start rendering
        arcade.start_render()

        # Timer
        self.timer_text.draw()

        # Put the text on the screen.
        output = f"Score: {GameWindow.total_score}"
        arcade.draw_text(text=output, start_x=self.WIDTH / 2, start_y=self.HEIGHT / 2 - self.OFFSET,
                         color=arcade.color.WHITE, font_size=25,
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

        # Timer
        self.total_time += delta_time

        # Calculate minutes
        minutes = int(self.total_time) // 60

        # Calculate seconds by using a modulus
        seconds = int(self.total_time) % 60

        # Use string formatting to create a new text string for our timer
        self.timer_text.text = f"{minutes:02d}:{seconds:02d}"
        GameWindow.time_elapsed = self.timer_text.text

        if self.counter == RECORDING_SAMPLING:
            GameWindow.recording.append(self.move_pointer())
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
                if Basket.speed < 20:
                    Basket.speed += SPEED_INCREMENT
                Basket.backwards = not Basket.backwards
                GameWindow.total_score += 1
                self.player_sprite.alpha = 0
                self.picked_up_state = False

        if GameWindow.total_score == APPLE_COUNT:
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
            arcade.exit()


class AppleMinigameOverView(arcade.View):

    def __init__(self):
        super().__init__()

        # Screensize variables
        self.WIDTH = arcade.get_viewport()[1]
        self.HEIGHT = arcade.get_viewport()[3]
        self.RECORD_LEFT = int(self.WIDTH * 0.5)
        self.RECORD_BOTTOM = int(self.HEIGHT * 0.5)
        self.RECORD_WIDTH = int(self.WIDTH * 0.5)
        self.RECORD_HEIGHT = int(self.HEIGHT * 0.5)
        self.RECORD_OFFSET = int(self.WIDTH * OFFSET_MULTIPLIER)
        self.BUTTON_WIDTH = int(self.RECORD_WIDTH / 3)
        self.BUTTON_HEIGHT = int(self.RECORD_HEIGHT / 3)

        # The Record section holds the Recording view
        self.add_section(Record(self.RECORD_LEFT - self.RECORD_OFFSET,
                                self.RECORD_BOTTOM - self.RECORD_OFFSET,
                                self.RECORD_WIDTH,
                                self.RECORD_HEIGHT,
                                name='Recording Container'))

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
        output_time = f"Time taken: {GameWindow.time_elapsed}"
        self.draw_text(output_time, 0, self.HEIGHT - self.RECORD_OFFSET * 2.2, font_size / 2,
                       self.RECORD_WIDTH - self.RECORD_OFFSET)

        # draw Pixels Traveled
        output_pixels = f"Pixels Traveled: {self.travel(GameWindow.recording)}"
        self.draw_text(output_pixels, 0, self.HEIGHT - self.RECORD_OFFSET * 3.2, font_size / 2,
                       self.RECORD_WIDTH - self.RECORD_OFFSET)

        # draw buttons
        self.draw_button_again()
        self.draw_button_menu()

    def on_mouse_press(self, x: int, y: int, button: int, modifiers: int):

        if button == 1:

            if self.button_again.collides_with_point((x, y)):
                game_view = AppleMinigame()
                game_view.setup()
                self.window.show_view(game_view)

            if self.button_menu.collides_with_point((x, y)):
                game_view = MenuView()
                self.window.show_view(game_view)

    def on_key_press(self, symbol: int, modifiers: int):
        if symbol == arcade.key.ESCAPE:
            arcade.exit()


class GameWindow(arcade.Window):
    total_score = 0

    def __init__(self):
        super().__init__(title="EyeFit",
                         resizable=False,
                         fullscreen=True)
        GameWindow.total_score = 0
        GameWindow.recording = []
        GameWindow.time_elapsed = ""

    def on_key_press(self, symbol: int, modifiers: int):
        if symbol == arcade.key.ESCAPE:
            arcade.exit()


def main():
    """ Main function """
    window = GameWindow()
    view = MenuView()
    window.set_mouse_visible(True)
    window.show_view(view)
    arcade.run()


if __name__ == "__main__":
    main()
