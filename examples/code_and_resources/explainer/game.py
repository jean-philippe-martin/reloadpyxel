import pyxel
import reloadpyxel
from anim import Animation

STATE_OLD_CODE = 0
STATE_NEW_CODE = 1

class App:
    @staticmethod
    def init_pyxel():
        """Init pyxel, set window size and title."""
        pyxel.init(204, 120, title="ReloadPyxel Explainer")

    def __init__(self, ryxel):
        """Initialize your App object here."""
        # You may choose to save the ryxel object
        self.ryxel = ryxel
        # Load all the resources via ryxel
        ryxel.load("my_resource.pyxres")
        self.anim = None
        self.initial_state()
        self.old_color = 7
        self.new_color = 10
        self.next_new_color = [6,8,7,10]
        # Do not call ryxel.run (main does it for you)

    def reload(self, old_self):
        """Called after a hot reload, on the newly-created updated app object."""
        reloadpyxel.copy_all_attributes(old_self, self)
        if self.anim:
            self.anim = Animation().reload(self.anim)
        return self

    def update(self):
        """Called every frame, here update the game state as needed."""
        if pyxel.btnr(pyxel.KEY_1): 
            self.initial_state()
            self.start_new_code_anim()
        if self.anim:
            more = self.anim.update()
            if not more: self.anim = None

    def initial_state(self):
        self.state = STATE_OLD_CODE
        self.bottom_text = "Press 1 to show the effect of hot-reloading code."

    def state_one(self):
        self.state = STATE_NEW_CODE

    def set_bottom_text(self, new_text):
        self.bottom_text = new_text

    def new_code_sliding_in(self, step):
        self.set_bottom_text("1a: Code is reloaded, new App object is created.")
        self.draw_initial_state(3,3, show_first_arrow=True)
        self.draw_new_code(203-step, 3, show_incoming_arrow=False, show_old_enemy=False)

    def blinking_arrow_1(self, step):
        self.set_bottom_text('1b: new App object is set as the running app.')
        self.draw_initial_state(3,3, show_first_arrow=(step%4==0))
        self.draw_new_code(3, 3, show_incoming_arrow=False, show_old_enemy=False)

    def blinking_arrow_2(self, step):
        self.draw_initial_state(3,3, show_first_arrow=False)
        self.draw_new_code(3, 3, show_incoming_arrow=(step%4==0), show_old_enemy=False)

    def new_code_in_place(self, step):
        self.draw_initial_state(3,3, show_first_arrow=False)
        self.draw_new_code(3, 3, show_incoming_arrow=True, show_old_enemy=False)

    def blinking_arrow_3(self, step):
        self.set_bottom_text("2a: App.reload is called, and the state is copied.")
        self.draw_initial_state(3,3, show_first_arrow=False)
        self.draw_new_code(3, 3, show_incoming_arrow=True, show_old_enemy=(step%4==0))

    def old_values_copied(self, step):
        self.draw_initial_state(3,3, show_first_arrow=False)
        self.draw_new_code(3, 3, show_incoming_arrow=True, show_old_enemy=True)

    def new_enemy_sliding_in(self, step):
        self.set_bottom_text("2b: App.reload creates a new Enemy and links it in.")
        self.draw_initial_state(3,3, show_first_arrow=False)
        self.draw_new_code(3, 3, show_incoming_arrow=True, show_old_enemy=True)
        self.draw_new_enemy(203-step,3)

    def blinking_arrow_4(self, step):
        self.draw_initial_state(3,3, show_first_arrow=False)
        self.draw_new_code(3, 3, show_incoming_arrow=True, show_old_enemy=(step%4==0))
        self.draw_new_enemy(3,3, show_incoming_arrow=False)

    def blinking_arrow_5(self, step):
        self.draw_initial_state(3,3, show_first_arrow=False)
        self.draw_new_code(3, 3, show_incoming_arrow=True, show_old_enemy=False)
        self.draw_new_enemy(3,3, show_incoming_arrow=(step%4==0))

    def new_objects_initialized(self, step):
        self.draw_initial_state(3,3, show_first_arrow=False)
        self.draw_new_code(3, 3, show_incoming_arrow=True, show_old_enemy=False)
        self.draw_new_enemy(3,3, show_incoming_arrow=True)

    def old_objects_gone(self, step):
        self.set_bottom_text("3: Python removes the old unreferenced objects")
        self.draw_initial_state(3,3, show_first_arrow=False, show_old_objects=(step<30 and step%4==0))
        self.draw_new_code(3, 3, show_incoming_arrow=True, show_old_enemy=False)
        self.draw_new_enemy(3,3, show_incoming_arrow=True)

    def new_objects_sliding_up(self, step):
        self.draw_initial_state(3,3, show_first_arrow=False, show_old_objects=False)
        self.draw_new_code(3, 3, oy=40-step, show_incoming_arrow=True, show_old_enemy=False)
        self.draw_new_enemy(3,3, oy=40-step, show_incoming_arrow=True)

    def switch_colors(self):
        self.old_color = self.new_color
        self.next_new_color = self.next_new_color[1:] + [self.next_new_color[0]]
        self.new_color = self.next_new_color[0]
        self.draw_initial_state(3,3)
        self.state = STATE_OLD_CODE

    def start_new_code_anim(self):

        self.anim = Animation()
        self.anim.add_multi(
            range(0,200,4), 
            self.new_code_sliding_in)
        self.anim.add_multi(
            range(0,30), 
            self.blinking_arrow_1)
        self.anim.add_multi(
            range(0,30), 
            self.blinking_arrow_2)
        self.anim.add_multi(
            range(0,60), 
            self.new_code_in_place)
        self.anim.add_multi(
            range(0,30), 
            self.blinking_arrow_3)
        self.anim.add_multi(
            range(0,60), 
            self.old_values_copied)
        self.anim.add_multi(
            range(0,200,4), 
            self.new_enemy_sliding_in)
        self.anim.add_multi(
            range(0,30), 
            self.blinking_arrow_4)
        self.anim.add_multi(
            range(0,30), 
            self.blinking_arrow_5)
        self.anim.add_multi(
            range(0,60), 
            self.new_objects_initialized)
        self.anim.add_multi(
            range(0,60), 
            self.old_objects_gone)
        self.anim.add_multi(
            range(0,40),
            self.new_objects_sliding_up)
        self.anim.add_single(self.switch_colors)
        
    def draw(self):
        """Called every frame, here draw the world."""
        pyxel.cls(0)
        if self.anim:
            self.anim.draw()
        else:
            if self.state == STATE_OLD_CODE:
                self.initial_state()
                self.draw_initial_state(3,3, show_first_arrow=True)
                # self.draw_new_code(3, 3, show_incoming_arrow=True, show_old_enemy=False)
                # self.draw_new_enemy(3,3, show_incoming_arrow=True)

            else:
                self.initial_state()
        pyxel.text(1,110,self.bottom_text, 7)

    def color_blt(self, x, y, tx, ty, w, h, color):
        pyxel.rect(x,y,w,h,color)
        pyxel.blt(x,y,0, tx*8, ty*8, w, h, colkey=7)

    def draw_initial_state(self, rx, ry, show_first_arrow=True, show_old_objects=True):
        # ReloadPyxel
        pyxel.blt(rx,ry,0, 0,0,80,8)
        pyxel.blt(rx,ry+8,0, 0,0+8,32,12)
        pyxel.rectb(rx-2,ry-2,42,23,7)
        pyxel.rectb(rx-2,ry+10,42,1,7)
        color = self.old_color
        # App
        ax=50 + rx
        ay=9 + ry
        if show_old_objects:
            self.color_blt(ax+2,ay+2, 0,3, 32,32, color)
            pyxel.rectb(ax,ay,42,33,color)
            pyxel.rectb(ax,ay+11,42,1,color)
        # Arrow
        if show_first_arrow:
            pyxel.rectb(rx+16,ry+14,25,1,color)
            self.color_blt(rx+16+25,ry+11, 4,1, 8,8, color)
        if show_old_objects:
            # Arrow 2
            pyxel.rectb(ax+26,ay+27,20,1,color)
            self.color_blt(ax+16+26,ay+24, 4,1, 8,8, color)
            # Enemy
            ex = 101 + rx
            ey = 30 + ry
            self.color_blt(ex+2,ey+2, 0,7, 32,32, color)
            pyxel.rectb(ex,ey,42,22,color)
            pyxel.rectb(ex,ey+11,42,1,color)

    def draw_new_code(self, rx, ry, ox=0, oy=40, show_incoming_arrow=True, show_old_enemy=True):
        # rx,ry are the reference position for the ReloadPyxel rectangle
        # ox, oy are the offset from that
        color = self.new_color
        old_color = self.old_color

        if show_incoming_arrow:
            # App Arrow (yellow)
            pyxel.rectb(rx+16,ry+14, 10,1,color)
            pyxel.rectb(rx+26,ry+14,1,oy,color)
            pyxel.rectb(rx+26,ry+oy+14, 20,1,color)
            self.color_blt(rx+46-5,ry+oy+14-3, 4,1,8,8,color)

        # App
        ax=50 + rx + ox
        ay=9 + ry + oy
        pyxel.rect(ax+2,ay+2,30,30, color)
        pyxel.blt(ax+2,ay+2,0, 0,3*8,32,32, colkey=7)
        pyxel.rectb(ax,ay,42,33,color)
        pyxel.rectb(ax,ay+11,42,1,color)

        if show_old_enemy:
            pyxel.rectb(ax+27,ay+27, 8,1, old_color)
            pyxel.rectb(ax+27+7,ay+27-oy, 1,oy, old_color)

    def draw_new_enemy(self, rx, ry, ox=0, oy=40, show_incoming_arrow=False):
        # rx,ry are the reference position for the ReloadPyxel rectangle
        # ox, oy are the offset from that
        color = self.new_color
        # App
        ax=50 + rx + ox
        ay=9 + ry + oy
        # Enemy
        ex = 101 + rx + ox
        ey = 30 + ry + oy
        self.color_blt(ex+2,ey+2, 0,7, 32,32, color)
        pyxel.rectb(ex,ey,42,22,color)
        pyxel.rectb(ex,ey+11,42,1,color)

        if show_incoming_arrow:
            pyxel.rectb(ax+26,ay+27,20,1,color)
            self.color_blt(ax+16+26,ay+24, 4,1, 8,8, color)






