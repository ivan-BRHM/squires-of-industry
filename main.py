"""
this is the game file for the project
"""

import arcade

# screen constants
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

PLAYER_PICK_UP_RANGE = 64

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
FURNACE_SENSING_RANGE = 98
FURNACE_UPDATES_PER_FRAME = 10
FURNACE_GRAPHICS = [
    "images/other_sprites/furnace_graphics_0.png",
    "images/other_sprites/furnace_graphics_1.png",
    "images/other_sprites/furnace_graphics_2.png",
    "images/other_sprites/furnace_graphics_3.png"
]
FURNACE_SELECTION_GRAPHICS = "images/UI/furnace_selection.png"


# goldmine constants
GOLDMINE_SCALE = 0.9
GOLDMINE_START_X = 890
GOLDMINE_START_Y = 600
GOLDMINE_SENSING_RANGE = 130
GOLDMINE_GRAPHICS = "images/other_sprites/gold_mine.png"
GOLDMINE_SELECTED_GRAPHICS = "images/other_sprites/gold_mine_selected.png"

# transport constants
TRANSPORT_SCALE = 1.5
TRANSPORT_START_X = 64
TRANSPORT_START_Y = 350
TRANSPORT_SENSING_RANGE = 224
TRANSPORT_SPEED = 1  # px per update
TRANSPORT_UPDATES_PER_FRAME = 12
TRANSPORT_GRAPHICS = "images/other_sprites/transport_{frame}.png"

# gold ore constants
GOLD_ORE_SCALE = 3
GOLD_ORE_GRAPHICS = "images/other_sprites/gold_ore.png"

# UI
# pick up sign constants
PICK_UP_SIGN_SCALE = 1
PICK_UP_SIGN_GRAPHICS = "images/UI/pick_up_sign.png"


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
        self.next_pickup = None
        self.can_pick_up = False
        self.carrying = []

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

        # update carrying
        if self.carrying:
            self.carrying[0].center_x = self.center_x
            self.carrying[0].center_y = self.center_y

        # update can_pick_up
        if self.next_pickup:
            dist_to_pickup = arcade.get_distance_between_sprites(self, self.next_pickup)
            if not self.carrying and dist_to_pickup < PLAYER_PICK_UP_RANGE:
                self.can_pick_up = True
            else:
                self.can_pick_up = False

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


class Furnace(arcade.Sprite):
    """a sprite that can track its heat based on how much coal is in it,
    and melt ore faster based on its heat"""

    def __init__(self, **kwargs):
        self.max_heat = FURNACE_MAX_HEAT
        self.cur_heat = 100
        self.max_fuel = FURNACE_MAX_FUEL
        self.cur_fuel = 5
        self.is_selected = False
        self.is_coal_filling = False
        self.processing = []

        super().__init__(**kwargs)

        self.selection = FurnaceSelection(
            filename=FURNACE_SELECTION_GRAPHICS,
            scale=FURNACE_SCALE,
            center_x=FURNACE_START_X,
            center_y=FURNACE_START_Y
        )

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

        # selection
        self.selection.alpha = 255 if self.is_selected else 0

        # update processing
        for obj in self.processing:
            obj.center_x = 2000  # off-screen

    def update_animation(self, delta_time: float = 1/60):

        self.cur_texture_index += 1
        if self.cur_texture_index > 3 * FURNACE_UPDATES_PER_FRAME:
            self.cur_texture_index = 0

        frame = self.cur_texture_index // FURNACE_UPDATES_PER_FRAME
        self.set_texture(frame)


class Transport(arcade.Sprite):
    """a sprite to let the players transport objects from floor to floor"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.transporting = set()
        self.is_selected = False
        self.cur_frame = 0
        self.append_texture(arcade.load_texture(TRANSPORT_GRAPHICS.format(frame=1)))

    def update(self):
        # update transporting
        if self.transporting:
            to_remove = []
            for sprite in self.transporting:
                sprite.center_x = self.center_x + 32
                sprite.center_y -= TRANSPORT_SPEED
                if sprite.center_y < self.center_y - 256:
                    to_remove.append(sprite)

            for obj in to_remove:
                self.transporting.remove(obj)

    def update_animation(self, delta_time: float = 1 / 60):

        self.cur_texture_index += 1
        if self.cur_texture_index > TRANSPORT_UPDATES_PER_FRAME:
            self.cur_texture_index = 0
            self.cur_frame = 1 if self.cur_frame == 0 else 0

        self.set_texture(self.cur_frame)


class GoldMine(arcade.Sprite):
    """a sprite to be interacted with to give the player gold ore
     - that can be put in the furnace"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.is_selected = False
        self.append_texture(arcade.load_texture(GOLDMINE_SELECTED_GRAPHICS))

    def update(self):
        if self.is_selected:
            self.set_texture(1)
        else:
            self.set_texture(0)


class CoalBox(arcade.Sprite):
    """a sprite to be interacted with to let the player fill the furnace"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.is_selected = False
        self.append_texture(arcade.load_texture(COALBOX_SELECTED_GRAPHICS))

    def update(self):
        if self.is_selected:
            self.set_texture(1)
        else:
            self.set_texture(0)


class GoldOre(arcade.Sprite):
    """an object to be transported around mostly graphics"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class FurnaceSelection(arcade.Sprite):
    """just graphics"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class PickUpSign(arcade.Sprite):
    """only graphics"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


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
        self.goldmine_sprite = None
        self.gold_ore_list = arcade.SpriteList()
        self.transport_sprite = None

        # UI sprites
        self.pick_up_sign_sprite = None

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

        self.goldmine_sprite = GoldMine(
            filename=GOLDMINE_GRAPHICS,
            scale=GOLDMINE_SCALE,
            center_x=GOLDMINE_START_X,
            center_y=GOLDMINE_START_Y
        )

        self.transport_sprite = Transport(
            filename=TRANSPORT_GRAPHICS.format(frame=0),
            scale=TRANSPORT_SCALE,
            center_x=TRANSPORT_START_X,
            center_y=TRANSPORT_START_Y,

        )

        # UI sprites setup
        self.pick_up_sign_sprite = PickUpSign(
            filename=PICK_UP_SIGN_GRAPHICS,
            scale=PICK_UP_SIGN_SCALE,
            center_x=1500,  # off screen
            center_y=1500,  # off screen
        )

    def on_draw(self):
        """
        draw everything
        """
        # note: drawing order dictates what overlaps what

        # prepare for drawing
        arcade.start_render()

        # draw sprites
        self.goldmine_sprite.draw()

        self.coalbox_sprite.draw()

        self.furnace_sprite.draw()

        self.transport_sprite.draw()

        self.furnace_sprite.selection.draw()

        self.player_sprite2.draw()

        self.player_sprite1.draw()

        self.gold_ore_list.draw()

        self.pick_up_sign_sprite.draw()

    def on_update(self, delta_time):
        """
        player movement and other game mechanics
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

        # check for closest gold ore (for pickup purposes)
        closest_gold_ore = None
        closest_gold_ore_dist = 99999
        for ore in self.gold_ore_list:
            if arcade.get_distance_between_sprites(ore, self.controlled_player_sprite) < closest_gold_ore_dist:
                closest_gold_ore = ore

        self.controlled_player_sprite.next_pickup = closest_gold_ore

        # other sprites
        # coalbox
        coalbox_player_dist = arcade.get_distance_between_sprites(self.coalbox_sprite, self.controlled_player_sprite)
        self.coalbox_sprite.is_selected = coalbox_player_dist < COALBOX_SENSING_RANGE
        self.coalbox_sprite.update()

        # goldmine
        goldmine_player_dist = arcade.get_distance_between_sprites(self.goldmine_sprite, self.controlled_player_sprite)
        self.goldmine_sprite.is_selected = goldmine_player_dist < GOLDMINE_SENSING_RANGE
        self.goldmine_sprite.update()

        # furnace
        furnace_player_dist = arcade.get_distance_between_sprites(self.furnace_sprite, self.controlled_player_sprite)
        if furnace_player_dist < FURNACE_SENSING_RANGE and self.controlled_player_sprite.carrying:
            self.furnace_sprite.is_selected = True
        else:
            self.furnace_sprite.is_selected = False

        self.furnace_sprite.update()
        self.furnace_sprite.update_animation()

        # transport
        transport_player_dist = arcade.get_distance_between_sprites(self.transport_sprite, self.controlled_player_sprite)
        if transport_player_dist < TRANSPORT_SENSING_RANGE and self.controlled_player_sprite.carrying:
            self.transport_sprite.is_selected = True
        else:
            self.transport_sprite.is_selected = False

        self.transport_sprite.update()
        self.transport_sprite.update_animation()

        # UI
        # pick up sign
        if self.controlled_player_sprite.can_pick_up:
            self.pick_up_sign_sprite.center_x = self.controlled_player_sprite.center_x
            self.pick_up_sign_sprite.center_y = self.controlled_player_sprite.center_y + 64 * PLAYER_SPRITE_SCALE
        else:
            self.pick_up_sign_sprite.center_x, self.pick_up_sign_sprite.center_y = 1500, 1500  # off screen

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
        # INTERACTIONS #
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

        # interact with furnace to put ore in the oven
        if key == INTERACT_KEY and self.furnace_sprite.is_selected:
            self.furnace_sprite.processing.append(self.controlled_player_sprite.carrying[0])
            self.controlled_player_sprite.carrying = []

        # interact with goldmine to get gold
        if key == INTERACT_KEY and self.goldmine_sprite.is_selected:
            if not self.controlled_player_sprite.carrying:
                new_gold_ore_obj = GoldOre(
                    filename=GOLD_ORE_GRAPHICS,
                    scale=GOLD_ORE_SCALE,
                    center_x=self.controlled_player_sprite.center_x,
                    center_y=self.controlled_player_sprite.center_y,
                )

                self.controlled_player_sprite.carrying.append(new_gold_ore_obj)
                self.gold_ore_list.append(new_gold_ore_obj)

        # pick up gold ore
        if key == INTERACT_KEY and self.controlled_player_sprite.can_pick_up:
            self.controlled_player_sprite.carrying.append(self.controlled_player_sprite.next_pickup)

            if self.controlled_player_sprite.next_pickup in self.transport_sprite.transporting:
                self.transport_sprite.transporting.remove(self.controlled_player_sprite.next_pickup)

        # interact with transport to transport gold
        if key == INTERACT_KEY and self.transport_sprite.is_selected:
            self.transport_sprite.transporting.add(self.controlled_player_sprite.carrying[0])
            self.controlled_player_sprite.carrying = []

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
