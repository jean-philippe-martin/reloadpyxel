"""
This is the "Hello, Pyxel" demo from the original Pyxel distribution,
modified so it has hot-reload of the image, and code.

So if while this is running you change the code of the logo file,
you will see your changes live in the running program.
"""
import pyxel
import reloadpyxel


class App:

    @staticmethod
    def init_pyxel():
        pyxel.init(160, 120, title="Hello Pyxel")

    def __init__(self, repyxel: reloadpyxel.ReloadPyxel):
        repyxel.images[0].load(0, 0, "assets/pyxel_logo_38x16.png")
        repyxel.run(self)

    def update(self):
        if pyxel.btnp(pyxel.KEY_Q):
            pyxel.quit()

    def draw(self):
        pyxel.cls(0)
        # Try changing the text while the game is running, and
        # saving your change.
        msg = "Hello, Pyxel!"
        pyxel.text(80-2*len(msg), 41, msg, pyxel.frame_count % 16)
        pyxel.blt(61, 66, 0, 0, 0, 38, 16)

    def reload(self, old_self):
        # We don't need to do anything in this case,
        # but having this method signals to reloadpyxel that
        # we would like to opt-in to code hot reload.
        pass