import arcade

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
MOVEMENT_SPEED = 200  # pixels per second
DURATION = 3  # seconds
DISTANCE = 600  # pixels


class MyGame(arcade.Window):
    def __init__(self, width, height, title):
        super().__init__(width, height, title)
        self.sprite = None
        self.total_time = 0
        self.speed = DISTANCE / DURATION  # Calculate speed

    def setup(self):
        # Create the sprite and set its initial position
        self.sprite = arcade.Sprite(center_x=100, center_y=100)

    def on_draw(self):
        arcade.start_render()
        self.sprite.draw()

    def update(self, delta_time):
        # Increment total time
        self.total_time += delta_time

        # Move the sprite only for the duration of the travel
        if self.total_time <= DURATION:
            self.sprite.center_x += self.speed * delta_time


def main():
    window = MyGame(SCREEN_WIDTH, SCREEN_HEIGHT, "Sprite Movement Example")
    window.setup()
    arcade.run()


if __name__ == "__main__":
    main()
