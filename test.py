import arcade
import random
import math

SCREEN_TITLE = "Apple Collecting Game"
SPRITE_SCALING_APPLE = 0.1
SPRITE_SCALING_BASKET = 0.2
APPLE_COUNT = 10
BASKET_SPEED = 10
SPEED_INCREMENT = 2
OFFSET = 100


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
            dest_x = self.position_list[self.cur_position - 1][0]
            dest_y = self.position_list[self.cur_position - 1][1]

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


class TestPointerApple(arcade.View):
    def __init__(self):
        super().__init__()

        # Sprite lists
        self.player_list = None
        self.apple_list = None
        self.basket_list = None

        # Set up the player info
        self.player_sprite = None
        self.score = 0
        self.old_score = 0
        self.picked_up_state = False

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

        self.player_list = arcade.SpriteList()
        self.apple_list = arcade.SpriteList()
        self.basket_list = arcade.SpriteList()

        # Score
        self.score = 0

        # State of picking
        self.picked_up_state = False

        # Set up the player
        player = self.player_sprite = arcade.Sprite("resources/apple.png",
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
        basket = Basket("resources/basket.png",
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
            apple = arcade.Sprite("resources/apple.png",
                                  SPRITE_SCALING_APPLE)
            # Position the apple
            width, height = int(arcade.get_viewport()[1]), int(arcade.get_viewport()[3])
            apple.center_x = random.randrange(OFFSET, (width - OFFSET))
            apple.center_y = random.randrange(OFFSET, (height - OFFSET))

            # Add the apple to the lists
            self.apple_list.append(apple)

    def on_draw(self):
        self.clear()
        arcade.start_render()  # Start rendering first

        # Draw all sprites
        self.apple_list.draw()
        self.player_list.draw()
        self.basket_list.draw()

        arcade.draw_circle_outline(self.pointer_x,
                                   self.pointer_y,
                                   self.pointer_radius,
                                   arcade.color.LILAC,
                                   border_width=2,
                                   num_segments=20)

        # Put the text on the screen.
        output = f"Score: {self.score}"
        arcade.draw_text(text=output, start_x=10, start_y=20,
                         color=arcade.color.WHITE, font_size=14)

    def on_update(self, delta_time: float):
        """ Movement and game logic """
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
                self.score += 1
                self.player_sprite.alpha = 0
                self.picked_up_state = False

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

    def on_key_press(self, symbol: int, modifiers: int):
        arcade.exit()


class GameWindow(arcade.Window):
    def __init__(self):
        super().__init__(title="EyeFit",
                         resizable=False,
                         fullscreen=True)

        # Don't show the mouse cursor
        # self.set_mouse_visible(False)

    def on_key_press(self, symbol: int, modifiers: int):
        if symbol == arcade.key.ESCAPE:
            arcade.exit()


def main():
    """ Main function """
    window = GameWindow()
    view = TestPointerApple()
    view.setup()
    window.show_view(view)
    arcade.run()


if __name__ == "__main__":
    main()
