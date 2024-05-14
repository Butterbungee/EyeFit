# Structure of apple demo
# Window class needed for the set_mouse_visibility
# Setup placed in Game View(change to Apple Minigame later) Needs to be called
# Player(pointer) is mouse can store states and switch sprites accordingly
# Enemy(basket) sprite moves along a path along the screen
# Apple sprites appear randomly on screen

import arcade
import math

# --- Constants ---
SPRITE_SCALING_PLAYER = 0.5
SPRITE_SCALING_BASKET = 0.2
BASKET_SPEED = 5.0

SCREEN_TITLE = "Sprite Follow Path Simple Example"


class Basket(arcade.Sprite):
    """
    This class represents the Basket on our screen.
    """

    def __init__(self, image, scale, position_list):
        super().__init__(image, scale)
        self.position_list = position_list
        self.cur_position = 0
        self.speed = BASKET_SPEED

    def update(self):
        """ Have a sprite follow a path """

        # Where are we
        start_x = self.center_x
        start_y = self.center_y

        # Where are we going
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
        speed = min(self.speed, distance)

        # Calculate vector to travel
        change_x = math.cos(angle) * speed
        change_y = math.sin(angle) * speed

        # Update our location
        self.center_x += change_x
        self.center_y += change_y

        # How far are we?
        distance = math.sqrt((self.center_x - dest_x) ** 2 + (self.center_y - dest_y) ** 2)

        # If we are there, head to the next point.
        if distance <= self.speed:
            self.cur_position += 1

            # Reached the end of the list, start over.
            if self.cur_position >= len(self.position_list):
                self.cur_position = 0


class MyGame(arcade.View):
    """ Our custom Window Class"""

    def __init__(self):
        """ Initializer """
        # Call the parent class initializer
        super().__init__()

        # Variables that will hold sprite lists
        self.player_list = None
        self.basket_list = None

        # Set up the player info
        self.player_sprite = None
        self.score = 0

        arcade.set_background_color(arcade.color.AMAZON)

    def setup(self):
        """ Set up the game and initialize the variables. """

        # Sprite lists
        self.player_list = arcade.SpriteList()
        self.basket_list = arcade.SpriteList()

        # Score
        self.score = 0

        # Set up the player
        # Character image from kenney.nl
        self.player_sprite = arcade.Sprite(":resources:images/animated_characters/female_person/"
                                           "femalePerson_idle.png", SPRITE_SCALING_PLAYER)
        self.player_sprite.center_x = 256
        self.player_sprite.center_y = 256
        self.player_list.append(self.player_sprite)

        # List of points the basket will travel too.
        left, right, bottom, top = arcade.get_viewport()
        position_list = [[left + 50, bottom + 50],
                         [right - 50, bottom + 50],
                         [right - 50, top - 50],
                         [left + 50, top - 50]]

        # Create the basket
        basket = Basket("basket.png",
                        SPRITE_SCALING_BASKET,
                        position_list)

        # Set initial location of the basket at the first point
        basket.center_x = position_list[0][0]
        basket.center_x = position_list[0][1]

        # Add the basket to the basket list
        self.basket_list.append(basket)

    def on_draw(self):
        """ Draw everything """
        self.clear()
        self.basket_list.draw()
        self.player_list.draw()

    def on_mouse_motion(self, x, y, dx, dy):
        """ Handle Mouse Motion """

        # Move the center of the player sprite to match the mouse x, y
        self.player_sprite.center_x = x
        self.player_sprite.center_y = y

    def on_update(self, delta_time):
        """ Movement and game logic """
        self.basket_list.update()


class GameWindow(arcade.Window):
    def __init__(self):
        super().__init__(title=SCREEN_TITLE,
                         resizable=False,
                         fullscreen=True)

        # Don't show the mouse cursor
        self.set_mouse_visible(False)

    def on_key_press(self, symbol: int, modifiers: int):
        # if symbol == 65307:
        if symbol == arcade.key.ESCAPE:
            arcade.exit()


def main():
    """ Main function """
    window = GameWindow()
    view = MyGame()
    view.setup()
    window.show_view(view)
    arcade.run()


if __name__ == "__main__":
    main()
