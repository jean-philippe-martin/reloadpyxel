#!pyxel run
"""Game entry point using reloadpyxel.

This will cause your game to auto-reload, provided:
1. Your game code is in game.py, and
2. In there you define an App class, following the following pattern:
    class App:
        def init_pyxel():
        def __init__(self, ryxel):
        def update(self):
        def draw(self):
        def reload(self, old_self):

"""

import game
import reloadpyxel


# 1. Create the ReloadPyxel object
ryxel = reloadpyxel.ReloadPyxel()
# 2. Initialize pyxel
game.App.init_pyxel()
# 3. Create the app
#    (note the app will be recreated by reloadpyxel if the source file is changed)
app = game.App(ryxel)
# 4. Start the game (this call will not return)
ryxel.run(app)

