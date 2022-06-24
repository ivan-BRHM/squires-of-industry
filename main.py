"""
this is the the game file for the project
"""


import arcade


# screen size/name
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 700
SCREEN_NAME = "Squires of industry"
SCREEN_BACKGROUND_COLOR = arcade.color.ORANGE


class MyGame(arcade.Window):
    """
    main class for setup and running
    """

    def __init__(self, width, height, name, background_color):

        # open the window
        super().__init__(width, height, name)

        # set the variables we will need:

        # player info

        # other sprites

        # keyboard tracking

        # set background color
        arcade.set_background_color(background_color)


    def setup(self):
        """
        initialize the variables we sat up
        """


    def on_draw(self):
        """
        draw everything
        """

        # prepare for drawing
        arcade.start_render()

        # draw sprites

        # draw UI


    def on_update(self, delta_time):
        """
        keyboard interpretation and other game mechanics
        """

        # player movement

        # update all sprites

        # player

        # other sprites


    def on_key_press(self, key, modifiers):
        """
        when a key is pressed...
        """

        # track the state of each key

        # perform operations based on which key was pressed


    def on_key_release(self, key, modifiers):
        """
        when a key is released...
        """

        # track the state of each key

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
