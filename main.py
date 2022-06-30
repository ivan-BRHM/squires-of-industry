"""
this is the the game file for the project
"""

import arcade

# screen size/name
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 700
SCREEN_NAME = "Squires of industry"
SCREEN_BACKGROUND_COLOR = arcade.color.ORANGE

# player constants
PLAYER_SPRITE_SCALE = 0.75
PLAYER_X_SPEED = 5.5

PLAYER1_START_X = SCREEN_WIDTH / 2
PLAYER1_START_Y = 150

PLAYER2_START_X = SCREEN_WIDTH / 2
PLAYER2_START_Y = 550

PLAYER1_GRAPHICS = "images/player/red.png"
PLAYER2_GRAPHICS = "images/player/blue.png"

SHIFT_PLAYER_CONTROL_KEY = arcade.key.LSHIFT

# coalbox constants
COALBOX_SCALE = 3
COALBOX_GRAPHICS = "images/other_sprites/coal_box.png"
COALBOX_SELECTED_GRAPHICS = "images/other_sprites/coal_box_selected.png"
COALBOX_START_X = 250
COALBOX_START_Y = 150
COALBOX_SENSING_RANGE = COALBOX_SCALE * 36


class Player(arcade.Sprite):
    """
    a sprite controlled by the player
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def update(self):
        """
        update the sprites position
        """

        self.center_x += self.change_x
        self.center_y += self.change_y

        # check for out of bounds
        if self.left < 0:
            self.left = 0
        if self.right > SCREEN_WIDTH:
            self.right = SCREEN_WIDTH
        if self.top < 0:
            self.top = 0
        if self.bottom > SCREEN_HEIGHT:
            self.bottom = SCREEN_HEIGHT


class CoalBox(arcade.Sprite):
    """a sprite to be interacted with to give the player coal to
    put in the furnace"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.append_texture(arcade.load_texture(COALBOX_SELECTED_GRAPHICS))

    def track_selected(self, selected: bool):
        if selected:
            self.set_texture(1)
        else:
            self.set_texture(0)


class MyGame(arcade.Window):
    """
    main class for setup and running
    """

    def __init__(self, width, height, name, background_color):

        # open the window
        super().__init__(width, height, name)

        # set the variables we will need:

        # player info
        self.player_sprite1 = None
        self.player_sprite2 = None
        self.controlled_player_sprite = None
        self.non_controlled_player_sprite = None

        # other sprites
        self.coalbox_sprite = None

        # keyboard tracking
        self.a_pressed = False
        self.d_pressed = False

        # set background color
        arcade.set_background_color(background_color)

    def setup(self):
        """
        initialize the variables we sat up
        """

        # set up player objects
        self.player_sprite1 = Player(
            filename=PLAYER1_GRAPHICS,
            scale=PLAYER_SPRITE_SCALE,
            center_x=PLAYER1_START_X,
            center_y=PLAYER1_START_Y
        )

        self.player_sprite2 = Player(
            filename=PLAYER2_GRAPHICS,
            scale=PLAYER_SPRITE_SCALE,
            center_x=PLAYER2_START_X,
            center_y=PLAYER2_START_Y
        )

        self.controlled_player_sprite = self.player_sprite1
        self.non_controlled_player_sprite = self.player_sprite2

        # other sprites
        self.coalbox_sprite = CoalBox(
            filename=COALBOX_GRAPHICS,
            scale=COALBOX_SCALE,
            center_x=COALBOX_START_X,
            center_y=COALBOX_START_Y
        )

    def on_draw(self):
        """
        draw everything
        """

        # prepare for drawing
        arcade.start_render()

        # draw sprites
        self.player_sprite1.draw()
        self.player_sprite2.draw()
        self.coalbox_sprite.draw()

        # draw UI

    def on_update(self, delta_time):
        """
        keyboard interpretation and other game mechanics
        """

        # player movement
        self.player_sprite1.change_x = 0
        self.player_sprite2.change_x = 0

        if self.a_pressed and not self.d_pressed:
            self.controlled_player_sprite.change_x = -PLAYER_X_SPEED
        if self.d_pressed and not self.a_pressed:
            self.controlled_player_sprite.change_x = PLAYER_X_SPEED

        # update all sprites

        # player
        self.player_sprite1.update()
        self.player_sprite2.update()

        # other sprites
        coalbox_player_dist = arcade.get_distance_between_sprites(self.coalbox_sprite, self.controlled_player_sprite)
        self.coalbox_sprite.track_selected(coalbox_player_dist < COALBOX_SENSING_RANGE)

    def on_key_press(self, key, modifiers):
        """
        when a key is pressed...
        """

        # track the state of each key
        if key == arcade.key.A:
            self.a_pressed = True
        if key == arcade.key.D:
            self.d_pressed = True

        # perform operations based on which key was pressed
        if key == SHIFT_PLAYER_CONTROL_KEY:
            b = self.controlled_player_sprite
            self.controlled_player_sprite = self.non_controlled_player_sprite
            self.non_controlled_player_sprite = b

    def on_key_release(self, key, modifiers):
        """
        when a key is released...
        """

        # track the state of each key
        if key == arcade.key.A:
            self.a_pressed = False
        if key == arcade.key.D:
            self.d_pressed = False

        # perform operations based on which key was released


def main():
    """
    main method
    """

    window = MyGame(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_NAME, SCREEN_BACKGROUND_COLOR)
    window.setup()
    arcade.run()


if __name__ == "__main__":
    main()
