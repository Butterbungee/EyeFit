import arcade
import random
import math

SCREEN_TITLE = "Apple Collecting Game"
SPRITE_SCALING_APPLE = 0.1
SPRITE_SCALING_BASKET = 0.2
APPLE_COUNT = 2
BASKET_SPEED = 10
SPEED_INCREMENT = 2
OFFSET = 100
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
    This represents a part of the View defined by its
    boundaries (left, bottom, etc.)
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


class AppleInstruction(arcade.View):
    def __init__(self):
        super().__init__()

        self.WIDTH = arcade.get_viewport()[1]
        self.HEIGHT = arcade.get_viewport()[3]

    def on_show_view(self):
        arcade.set_background_color(arcade.color.ORANGE_PEEL)

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

        self.vel_x = 0
        self.vel_y = 0

        self.deadzone_radius = 50
        self.pointer_radius = 50

        arcade.set_background_color(arcade.color.AMAZON)

    def setup(self):
        """ Set up the game and initialize the variables. """
        # clear score
        GameWindow.total_score = 0

        # clear recording
        GameWindow.recording = []

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
        left, right, bottom, top = arcade.get_viewport()
        position_list = [[left + OFFSET, bottom + OFFSET],
                         [right - OFFSET, bottom + OFFSET],
                         [right - OFFSET, top - OFFSET],
                         [left + OFFSET, top - OFFSET]]

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
            apple.center_x = random.randrange(OFFSET, (width - OFFSET))
            apple.center_y = random.randrange(OFFSET, (height - OFFSET))

            # Add the apple to the lists
            self.apple_list.append(apple)

    def on_draw(self):

        self.clear()

        # Start rendering
        arcade.start_render()

        # Timer
        self.timer_text.draw()

        # Draw all sprites
        self.apple_list.draw()
        self.player_list.draw()
        self.basket_list.draw()

        arcade.draw_circle_outline(self.pointer_x,
                                   self.pointer_y,
                                   self.pointer_radius,
                                   arcade.color.ROSE,
                                   border_width=2,
                                   num_segments=20)

        # Put the text on the screen.
        output = f"Score: {GameWindow.total_score}"
        arcade.draw_text(text=output, start_x=10, start_y=20,
                         color=arcade.color.WHITE, font_size=14)

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
        self.vel_x = x
        self.vel_y = y

    def move_pointer(self):
        x_dist = self.vel_x - self.pointer_x
        y_dist = self.vel_y - self.pointer_y

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
        self.RECORD_OFFSET = int(self.WIDTH * 0.1)
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
                                            arcade.color.AQUAMARINE)

        self.button_again.position = (self.WIDTH * 5 / 8 - self.RECORD_OFFSET,
                                      self.RECORD_BOTTOM - self.RECORD_OFFSET * 2)

        # add back to menu button
        self.button_menu = self.new_button(self.BUTTON_WIDTH,
                                           self.BUTTON_HEIGHT,
                                           arcade.color.AMETHYST)

        self.button_menu.position = (self.WIDTH * 7 / 8 - self.RECORD_OFFSET,
                                     self.RECORD_BOTTOM - self.RECORD_OFFSET * 2)

    @staticmethod
    def new_button(width, height, color):
        # helper to create new buttons
        button = arcade.SpriteSolidColor(width, height, color)
        return button

    def draw_button_again(self):
        arcade.draw_text('Play again', self.RECORD_LEFT,
                         self.RECORD_BOTTOM, arcade.color.LIGHT_CRIMSON, 10)
        self.button_again.draw()

    def draw_button_menu(self):
        arcade.draw_text('Back to menu', self.RECORD_LEFT,
                         self.RECORD_BOTTOM, arcade.color.LIGHT_CRIMSON, 10)
        self.button_menu.draw()

    def on_draw(self):
        # clear the screen
        self.clear(arcade.color.BEAU_BLUE)

        # draw score
        output_total = f"Total Score: {self.window.total_score}"
        arcade.draw_text(output_total, 10, 10, arcade.color.WHITE, 14)
        self.draw_button_again()
        self.draw_button_menu()

    def on_mouse_press(self, x: int, y: int, button: int, modifiers: int):
        print("mouse pressed")
        if button == 1:
            print("left mouse pressed")
            if self.button_again.collides_with_point((x, y)):
                print("here")

                game_view = AppleMinigame()
                game_view.setup()
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

    def on_key_press(self, symbol: int, modifiers: int):
        if symbol == arcade.key.ESCAPE:
            arcade.exit()


def main():
    """ Main function """
    window = GameWindow()
    view = AppleInstruction()
    window.set_mouse_visible(True)
    window.show_view(view)
    arcade.run()


if __name__ == "__main__":
    main()
