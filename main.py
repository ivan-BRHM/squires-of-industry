"""
this is the the game file for the project
"""

import arcade

# screen size/name
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 700
SCREEN_NAME = "Squires of industry"
SCREEN_BACKGROUND_COLOR = arcade.color.ORANGE

# controls
SHIFT_PLAYER_CONTROL_KEY = arcade.key.LSHIFT
INTERACT_KEY = arcade.key.E

# player constants
PLAYER_SPRITE_SCALE = 1
PLAYER_X_SPEED = 5.5

PLAYER1_START_X = SCREEN_WIDTH / 2
PLAYER1_START_Y = 150

PLAYER2_START_X = SCREEN_WIDTH / 2
PLAYER2_START_Y = 550

RIGHT = 0  # for the purpose of witch direction the player is facing
LEFT = 1
PLAYER_IDLE_UPDATES_PER_FRAME = 18
PLAYER_RUN_UPDATES_PER_FRAME = 6
PLAYER_SHOVEL_UPDATES_PER_FRAME = 20
PLAYER1_INITIAL_GRAPHICS = "images/player/player_red_idle_0.png"
PLAYER2_INITIAL_GRAPHICS = "images/player/player_blue_idle_0.png"

# coalbox constants
COALBOX_SCALE = 3
COALBOX_START_X = 250
COALBOX_START_Y = 150
COALBOX_GRAPHICS = "images/other_sprites/coal_box.png"
COALBOX_SELECTED_GRAPHICS = "images/other_sprites/coal_box_selected.png"
COALBOX_SENSING_RANGE = COALBOX_SCALE * 36

# furnace constants
FURNACE_SCALE = 1
FURNACE_START_X = 360
FURNACE_START_Y = 165
FURNACE_HEAT_LOSS = 500  # how many frames between the furnace losing heat.
FURNACE_MAX_HEAT = 100
FURNACE_MAX_FUEL = 50
FURNACE_FUEL_GAIN = 3  # fuel per sec
FURNACE_UPDATES_PER_FRAME = 10
FURNACE_GRAPHICS = [
    "images/other_sprites/furnace_graphics_0.png",
    "images/other_sprites/furnace_graphics_1.png",
    "images/other_sprites/furnace_graphics_2.png",
    "images/other_sprites/furnace_graphics_3.png"
]


def load_texture_pair(filename):
    return [
        arcade.load_texture(filename),
        arcade.load_texture(filename, flipped_horizontally=True)
    ]


class Player(arcade.Sprite):
    """
    a sprite controlled by the player
    """

    def __init__(self, texture_color: str = 'red', **kwargs):
        self.dir_facing = RIGHT
        self.is_shoveling = False

        super().__init__(**kwargs)

        # load textures
        self.idle_anim = []
        for i in range(4):
            self.idle_anim.append(load_texture_pair(f"images/player/player_{texture_color}_idle_{i}.png"))

        self.run_anim = []
        for i in range(5):
            self.run_anim.append(load_texture_pair(f"images/player/player_{texture_color}_run_{i}.png"))

        self.shovel_anim = []
        for i in range(6):
            self.shovel_anim.append(load_texture_pair(f"images/player/player_{texture_color}_shovel_{i}.png"))

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

    def update_animation(self, delta_time: float = 1 / 60):

        # update direction
        if self.change_x < 0 and self.dir_facing == RIGHT:
            self.dir_facing = LEFT

        if self.change_x > 0 and self.dir_facing == LEFT:
            self.dir_facing = RIGHT

        self.cur_texture_index += 1

        # idle
        if self.change_x == 0 and not self.is_shoveling:
            if self.cur_texture_index > 3 * PLAYER_IDLE_UPDATES_PER_FRAME:
                self.cur_texture_index = 0

            frame = self.cur_texture_index // PLAYER_IDLE_UPDATES_PER_FRAME
            self.texture = self.idle_anim[frame][self.dir_facing]

        # run
        if self.change_x != 0:
            if self.cur_texture_index > 4 * PLAYER_RUN_UPDATES_PER_FRAME:
                self.cur_texture_index = 0

            frame = self.cur_texture_index // PLAYER_RUN_UPDATES_PER_FRAME
            self.texture = self.run_anim[frame][self.dir_facing]

        # shovel
        if self.is_shoveling:
            self.dir_facing = LEFT
            if self.cur_texture_index > 5 * PLAYER_SHOVEL_UPDATES_PER_FRAME:
                self.cur_texture_index = 0

            frame = self.cur_texture_index // PLAYER_SHOVEL_UPDATES_PER_FRAME
            self.texture = self.shovel_anim[frame][self.dir_facing]


class CoalBox(arcade.Sprite):
    """a sprite to be interacted with to give the player coal to
    put in the furnace"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.is_selected = False
        self.append_texture(arcade.load_texture(COALBOX_SELECTED_GRAPHICS))

    def update(self):
        if self.is_selected:
            self.set_texture(1)
        else:
            self.set_texture(0)


class Furnace(arcade.Sprite):
    """a sprite that can track its heat based on how much coal is in it,
    and melt ore faster based on its heat"""

    def __init__(self, **kwargs):
        self.max_heat = FURNACE_MAX_HEAT
        self.cur_heat = 100
        self.max_fuel = FURNACE_MAX_FUEL
        self.cur_fuel = 5
        self.is_coal_filling = False

        super().__init__(**kwargs)
        for i in range(3):
            self.append_texture(arcade.load_texture(FURNACE_GRAPHICS[1 + i]))

        self.cur_texture_index = 0

    def update(self):

        if self.is_coal_filling:
            self.cur_fuel += FURNACE_FUEL_GAIN/60

        if self.cur_fuel > self.max_fuel:
            self.cur_fuel = self.max_fuel

        if self.cur_heat > self.max_heat:
            self.cur_heat = self.max_heat - 1

        if self.cur_fuel > 0:
            self.cur_heat += 1/60
            self.cur_fuel -= 1/120

        else:
            self.cur_heat = max(0, self.cur_heat - ((101 - self.cur_heat) / FURNACE_HEAT_LOSS))

    def update_animation(self, delta_time: float = 1/60):

        self.cur_texture_index += 1
        if self.cur_texture_index > 3 * FURNACE_UPDATES_PER_FRAME:
            self.cur_texture_index = 0

        frame = self.cur_texture_index // FURNACE_UPDATES_PER_FRAME
        self.set_texture(frame)


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
        self.furnace_sprite = None

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
            texture_color='red',
            filename=PLAYER1_INITIAL_GRAPHICS,
            scale=PLAYER_SPRITE_SCALE,
            center_x=PLAYER1_START_X,
            center_y=PLAYER1_START_Y
        )

        self.player_sprite2 = Player(
            texture_color='blue',
            filename=PLAYER2_INITIAL_GRAPHICS,
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

        self.furnace_sprite = Furnace(
            filename=FURNACE_GRAPHICS[0],
            scale=FURNACE_SCALE,
            center_x=FURNACE_START_X,
            center_y=FURNACE_START_Y
        )

    def on_draw(self):
        """
        draw everything
        """
        # note: drawing order dictates what overlaps what

        # prepare for drawing
        arcade.start_render()

        # draw sprites
        self.coalbox_sprite.draw()
        self.furnace_sprite.draw()
        self.player_sprite2.draw()
        self.player_sprite1.draw()

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

        self.player_sprite1.update_animation()
        self.player_sprite2.update_animation()

        # other sprites
        coalbox_player_dist = arcade.get_distance_between_sprites(self.coalbox_sprite, self.controlled_player_sprite)
        self.coalbox_sprite.is_selected = coalbox_player_dist < COALBOX_SENSING_RANGE
        self.coalbox_sprite.update()

        self.furnace_sprite.update()
        self.furnace_sprite.update_animation()

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
        # shift control between player sprites
        if key == SHIFT_PLAYER_CONTROL_KEY:
            b = self.controlled_player_sprite
            self.controlled_player_sprite = self.non_controlled_player_sprite
            self.non_controlled_player_sprite = b

        # interact with the coalbox to fill the furnace
        if self.coalbox_sprite.is_selected:
            if key == INTERACT_KEY:
                self.furnace_sprite.is_coal_filling = True
                self.controlled_player_sprite.is_shoveling = True

            elif key != SHIFT_PLAYER_CONTROL_KEY:  # otherwise we stop filling when we shift control
                self.furnace_sprite.is_coal_filling = False
                self.controlled_player_sprite.is_shoveling = False

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
