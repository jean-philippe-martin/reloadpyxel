# Copy this file as a template in your own folder.
# Rename it to "game.py"

import pyxel
import reloadpyxel
import shutil

STATES = [
    "TEST_LOAD", "TEST_EXCL_IMAGES", "TEST_EXCL_TILEMAPS",
    "TEST_IMG_LOAD",
    "TEST_RELOAD", "TEST_RELOAD_EXCL_IMG"
]
STATE_DURATION = 30

class App:
    @staticmethod
    def init_pyxel():
        """Init pyxel, set window size and title."""
        pyxel.init(120, 120, title="Hot Reload Self-Test")

    def __init__(self, ryxel):
        """Initialize your App object here."""
        # You may choose to save the ryxel object
        self.ryxel = ryxel
        # Load all the resources via ryxel
        ryxel.load("hot_horiz.pyxres")
        ryxel.load("cold_vert.pyxres")
        shutil.copyfile("hot_horiz.pyxres", "test_resource_1.pyxres")
        shutil.copyfile("hot_horiz.pyxres", "test_resource_2.pyxres")
        self.set_state(0)
        self.state_index = 0
        self.state_countdown = STATE_DURATION
        self.running = True
        # Do not call ryxel.run (main does it for you)

    def set_state(self, state_index):
        self.state_index = state_index
        self.state_name = STATES[state_index]
        (self.temp, self.orient) = self._load_state(self.state_name)

    def _load_state(self, state_name):
        match state_name:
            case "TEST_LOAD":
                # Loading twice should override
                self.ryxel.load("cold_vert.pyxres")
                self.ryxel.load("hot_horiz.pyxres")
                return ("hot", "horiz")
            case "TEST_EXCL_IMAGES":
                # Test excl_images
                self.ryxel.load("hot_horiz.pyxres")
                self.ryxel.load("cold_vert.pyxres", excl_images=True)
                return ("hot", "vert")
            case "TEST_EXCL_TILEMAPS":
                # Test excl_tilemaps
                self.ryxel.load("hot_horiz.pyxres")
                self.ryxel.load("cold_vert.pyxres", excl_tilemaps=True)
                return ("cold", "horiz")
            case "TEST_IMG_LOAD":
                # Test images[].load
                self.ryxel.load("cold_vert.pyxres")
                self.ryxel.images[0].load(0,0,"hot_colors.png")
                return ("hot", "vert")
            case "TEST_RELOAD":
                # Test hotreload: that file was initially hot, but we'll replace it.
                shutil.copyfile("hot_horiz.pyxres", "test_resource_1.pyxres")
                self.ryxel.load("test_resource_1.pyxres")
                shutil.copyfile("cold_vert.pyxres", "test_resource_1.pyxres")
                return ("cold", "vert")
            case "TEST_RELOAD_EXCL_IMG":
                # Test that hotreload does the right thing: we'll trigger a reload of the
                # first file, but the later override must stay.
                shutil.copyfile("cold_vert.pyxres", "test_resource_1.pyxres")
                shutil.copyfile("cold_vert.pyxres", "test_resource_2.pyxres")
                self.ryxel.load("test_resource_1.pyxres")
                self.ryxel.load("test_resource_2.pyxres", excl_images=True)
                # Trigger reload of the first file. the tilemap override stay?
                shutil.copyfile("hot_horiz.pyxres", "test_resource_1.pyxres")
                return ("hot", "vert")
            case _:
                return ("?", "?")


    def reload(self, old_self):
        """Called after a hot reload, on the newly-created updated app object."""
        reloadpyxel.copy_all_attributes(old_self, self)
        # Do any other needed state updates here
        return self

    def update(self):
        """Called every frame, here update the game state as needed."""
        if (pyxel.btn(pyxel.KEY_P)):
            # Pause
            self.running = not self.running
        if not self.running: return
        if self.state_countdown <= 0:
            newstate = (self.state_index + 1) % len(STATES)
            self.set_state(newstate)
            self.state_countdown = STATE_DURATION
        else:
            self.state_countdown -= 1

    def draw(self):
        """Called every frame, here draw the world."""
        for x in range(20):
            for y in range(20):
                (tx,ty) = pyxel.tilemaps[0].pget(x,y)
                pyxel.blt(x*8,y*8,0, tx*8,ty*8,8,8)
        pyxel.rect(0,90, 120,26, 0);
        pyxel.rectb(0,90, 120,26, 7);
        pyxel.text(4,92, "Test " + str(self.state_index) + ": " + self.state_name, 7)
        image_colors = self.identify_images()
        ok = (image_colors == self.temp)
        if ok:
            color = 11
            text = "OK"
        elif self.state_countdown > STATE_DURATION-11:
            # Failed, but we're giving it more time
            color = 13
            text = "HMM"
        else:
            # Failed
            color = 9
            text = "FAIL"
        pyxel.text(4,100, "Image colors: " + image_colors + " " + text, color)
        tilemap_pattern = self.identify_tilemap()
        ok = (tilemap_pattern == self.orient)
        if ok:
            color = 11
            text = "OK"
        elif self.state_countdown > STATE_DURATION-11:
            # Failed, but we're giving it more time
            color = 13
            text = "HMM"
        else:
            # Failed
            color = 9
            text = "FAIL"
        pyxel.text(4,108, "Tilemap pattern: " + tilemap_pattern + " " + text, color)

    def identify_tilemap(self):
        is_horizontal = True
        is_vertical = True
        for y in range(15):
            for x in range(15):
                txy = pyxel.tilemaps[0].pget(x,y)
                if x==0:
                    ref_txy = txy
                else:
                    if txy!=ref_txy: is_horizontal = False
        for x in range(15):
            for y in range(15):
                txy = pyxel.tilemaps[0].pget(x,y)
                if y==0:
                    ref_txy = txy
                else:
                    if txy!=ref_txy: is_vertical = False
        if is_horizontal and is_vertical: return "fill"
        if is_horizontal: return "horiz"
        if is_vertical: return "vert"
        return "other"
    
    def identify_images(self):
        is_hot = True
        is_cold = True
        hot_colors = [7,8,9,10,14]
        cold_colors = [1,2,4,5]
        for x in range(2):
            color = pyxel.images[0].pget(4,4)
            if color in hot_colors: is_cold = False
            if color in cold_colors: is_hot = False
        #print(f'{color}')
        if is_hot and is_cold: return "mixed"
        if is_hot: return "hot"
        if is_cold: return "cold"
        return "other"

