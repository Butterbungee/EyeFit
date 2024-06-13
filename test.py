import os
import arcade
from arcade.gui import UIManager, UITexturePane

class TextureCycler:
    def __init__(self, folder_path, window):
        self.folder_path = folder_path
        self.window = window
        self.textures = self.load_textures_from_folder()
        self.current_texture_index = 0
        self.manager = UIManager(window)
        self.manager.enable()

        if self.textures:
            self.texture_pane = UITexturePane(
                arcade.gui.widgets.UIWidget(),
                tex=self.textures[self.current_texture_index],
                width=400,
                height=400
            )
            self.manager.add(self.texture_pane)
        else:
            print("No textures found in the specified folder.")

    def load_textures_from_folder(self):
        textures = []
        for filename in os.listdir(self.folder_path):
            if filename.endswith('.png'):
                texture = arcade.load_texture(os.path.join(self.folder_path, filename))
                textures.append(texture)
        return textures

    def update(self):
        self.current_texture_index = (self.current_texture_index + 1) % len(self.textures)
        self.texture_pane.texture = self.textures[self.current_texture_index]
        print(f"Cycled to texture index: {self.current_texture_index}")

    def draw(self):
        self.manager.draw()

    def on_resize(self, width, height):
        self.manager.on_resize(width, height)

class MyWindow(arcade.Window):
    def __init__(self):
        super().__init__(800, 600, "Texture Cycler")
        self.texture_cycler = TextureCycler("assets/dust_anim/", self)

    def on_draw(self):
        arcade.start_render()
        self.texture_cycler.draw()

    def update(self, delta_time):
        self.texture_cycler.update()

    def on_resize(self, width, height):
        self.texture_cycler.on_resize(width, height)
        super().on_resize(width, height)

if __name__ == "__main__":
    window = MyWindow()
    arcade.run()
