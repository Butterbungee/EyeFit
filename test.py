import math
import random

import arcade

# Set up the constants
SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080

# These constants control the particulars about the radar
CENTER_X = SCREEN_WIDTH // 2
CENTER_Y = SCREEN_HEIGHT // 2
RADIANS_PER_FRAME = 0.04
SWEEP_LENGTH = 400
SPRITE_SCALE = .5


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


class Radar:
    def __init__(self):
        self.WIDTH = int(arcade.get_viewport()[1])
        self.HEIGHT = int(arcade.get_viewport()[3])
        self.OFFSET = int(self.WIDTH * 0.08) * 2
        self.angle = 0
        self.target_angle = 0

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
            x = self.OFFSET * math.sin(self.angle) + CENTER_X
            y = self.OFFSET * math.cos(self.angle) + CENTER_Y
            return x, y
        if element == "left":
            x = self.OFFSET * math.sin(self.angle - SPRITE_SCALE) + CENTER_X
            y = self.OFFSET * math.cos(self.angle - SPRITE_SCALE) + CENTER_Y
            return x, y
        if element == "right":
            x = self.OFFSET * math.sin(self.angle + SPRITE_SCALE) + CENTER_X
            y = self.OFFSET * math.cos(self.angle + SPRITE_SCALE) + CENTER_Y
            return x, y

    def update_target_angle(self, mouse_x, mouse_y):
        self.target_angle = -math.atan2(mouse_y - CENTER_Y, mouse_x - CENTER_X) + math.pi / 2


class ShieldInstruction(arcade.View):
    def __init__(self):
        super().__init__()
        self.WIDTH = int(arcade.get_viewport()[1])
        self.HEIGHT = int(arcade.get_viewport()[3])

    def on_draw(self):
        arcade.Text(
            text="alu",
            start_x=self.WIDTH // 2,
            start_y=self.HEIGHT // 2 - 50,
            font_size=100,
            anchor_x="center",
        )

    def on_mouse_press(self, x: int, y: int, button: int, modifiers: int):
        view = ShieldMinigame()
        view.start_snowfall()
        self.window.show_view(view)


class ShieldMinigame(arcade.View):
    def __init__(self):
        super().__init__()
        self.WIDTH = int(arcade.get_viewport()[1])
        self.HEIGHT = int(arcade.get_viewport()[3])
        self.OFFSET = int(self.WIDTH * 0.08)
        self.text_color = arcade.color.WHITE
        self.travel_time = 7
        self.MOVEMENT_SPEED = 0

        self.side_list = {}

        self.radar = Radar()
        self.shield = RotatingSprite("resources/shield.png", SPRITE_SCALE)
        self.ship = arcade.Sprite("resources/ship.png", SPRITE_SCALE)
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

        self.ship_sprite_list.extend([self.ship])
        self.shield_sprite_list.extend([self.shield])
        self.left_sprite_list.extend([self.left])
        self.right_sprite_list.extend([self.right])

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

        # Set background color
        arcade.set_background_color(arcade.color.DARK_MIDNIGHT_BLUE)

    def setup(self):
        """ Set up the game and initialize the variables. """
        # Schedule a new enemy every second

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
        enemy_sprite = arcade.Sprite(":resources:images/space_shooter/meteorGrey_med1.png", SPRITE_SCALE * 4)
        if len(self.side_list) == 0:
            self.side_list = {"left", "right", "top", "bottom"}
        side = random.choice(list(self.side_list))
        self.side_list.remove(side)

        if side == "left":
            enemy_sprite.center_x = -enemy_sprite.width // 2
            enemy_sprite.center_y = random.randint(0, SCREEN_HEIGHT)
        elif side == "right":
            enemy_sprite.center_x = SCREEN_WIDTH + enemy_sprite.width // 2
            enemy_sprite.center_y = random.randint(0, SCREEN_HEIGHT)
        elif side == "top":
            enemy_sprite.center_x = random.randint(0, SCREEN_WIDTH)
            enemy_sprite.center_y = SCREEN_HEIGHT + enemy_sprite.height // 2
        else:  # "bottom"
            enemy_sprite.center_x = random.randint(0, SCREEN_WIDTH)
            enemy_sprite.center_y = -enemy_sprite.height // 2

        # Calculate the angle to the center
        dest_x = SCREEN_WIDTH // 2
        dest_y = SCREEN_HEIGHT // 2
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

        arcade.draw_circle_outline(self.pointer_x, self.pointer_y, self.pointer_radius, arcade.color.PASTEL_VIOLET,
                                   border_width=3, num_segments=40)

        output = f"Score: {self.window.total_score}"
        arcade.draw_text(text=output, start_x=self.WIDTH / 2, start_y=self.HEIGHT / 2 - self.OFFSET,
                         color=self.text_color, font_size=25,
                         anchor_x="center", anchor_y="top")

    def on_update(self, delta_time):
        # Gradually adjust the snowfall speed
        if self.snowfall_active:
            if self.snowfall_speed_multiplier < 1.0:
                self.snowfall_speed_multiplier += .01
                print(self.snowfall_speed_multiplier)
        else:
            if self.snowfall_speed_multiplier > 0.0:
                self.snowfall_speed_multiplier -= .01
                print(self.snowfall_speed_multiplier)

        # Animate all the snowflakes falling
        for snowflake in self.snowflake_list:
            snowflake.y -= snowflake.speed * delta_time * self.snowfall_speed_multiplier

            # Check if snowflake has fallen below screen
            if snowflake.y < 0:
                snowflake.reset_pos()

        # Update the radar
        self.radar.update()

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

        self.ship.center_x = CENTER_X
        self.ship.center_y = CENTER_Y

        self.move_pointer()

        if not self.enemy_list:
            self.add_enemy()

        self.enemy_list.update()

        # Check for collision between the player and enemy
        for enemy in self.enemy_list:
            if arcade.check_for_collision(self.shield, enemy):
                enemy.remove_from_sprite_lists()
                self.window.total_score += 1

        for enemy in self.enemy_list:
            if arcade.check_for_collision(self.ship, enemy):
                enemy.remove_from_sprite_lists()
                self.window.total_score -= 1

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

    def on_key_press(self, symbol: int, modifiers: int):
        if symbol == arcade.key.SPACE:
            self.snowfall_active = not self.snowfall_active


class GameWindow(arcade.Window):

    def __init__(self):
        super().__init__(title="EyeFit", resizable=False, fullscreen=True, )
        self.background_type = "default"
        self.tracking = False
        self.total_score = 0


def main():
    window = GameWindow()
    view = ShieldInstruction()
    window.set_mouse_visible(True)
    window.show_view(view)
    arcade.run()


if __name__ == "__main__":
    main()
