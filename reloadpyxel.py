"""
reloadpyxel module: will autoreload (i) resources and (ii) your code.

For it to autoreload your resources, you must
1. use reloadpyxel.load for it instead of pyxel.load, and
2. use reloadpyxel.run to start your app.

For it to autoreload your code, you must
1. put your code in a module that is loaded from main,
2. your code must be in a class called 'App'
3. 'App' must have a "reload" method.
   This method will be called on the newly-reloaded code,
   so you can copy the old state over. You can use
   the helper function 
   reloadpyxel.copy_all_attributes(old_self, self)
   Note that we will call "reload" when the game starts (with itself as argument)
   to weed out any bug there.
4. Optionally, App may have a "reload_resources" method.
   It will be called every time we have reloaded the resources.
"""

import importlib
import pyxel
import os
import sys


def copy_all_attributes(source_object, dest_object):
    """Shallow copy all the attributes from the source to the destination."""
    dest_object.__dict__.update(source_object.__dict__)


class ReloadPyxel:
    """ReloadPyxel helps add hot reload for code and resources for your Pyxel game."""
    def __init__(self, hotreload_resources=True, hotreload_code=True):
        """ReloadPyxel remembers the resource files you're loading so it can reload them.

        Set hotreload_resources or hotreload_code to False to disable resource
        or code hot reload, respectively."""
        # list of commands to "load"
        self.load_list = []
        # fname -> last known update time for resources
        self.fstats = {}
        self.ticks = 0
        # We check for updates every check_period ticks
        # An advantage of not doing it immediately is we reduce
        # the likelihood of reading a file mid-save.
        self.check_period = 10
        self.hotreload_resources = hotreload_resources
        self.hotreload_code = hotreload_code
        self.images = []
        self.tilemaps = []
        for i in range(3):
            self.images += [_ReloadImage(self, i)]
            self.tilemaps += [_ReloadTilemap(self, i)]

    def load(self, name_of_resource_file, **kwargs):
        """Load the resource file, then reload it if it changes."""
        kwargs['filename'] = name_of_resource_file
        command = _PyxelLoad_Command(name_of_resource_file, kwargs)
        if self.hotreload_resources:
            self.load_list += [command]
            self._update_file_time(name_of_resource_file)
        command.exec()

    def image_load(self, image_index, x, y, filename, incl_colors=None):
        """Load this image file into the specified image bank at the specified offset
        (and reload it if it changes)."""
        command = _ImageLoad_Command(image_index, x, y, filename, incl_colors)
        if self.hotreload_resources:
            self.load_list += [command]
            self._update_file_time(filename)
        command.exec()

    def tilemap_load(self, tilemap_index, x, y, filename, layer):
        """Load this TMX tilemap file to the specified tilemap bank at the
        specified offset (and reload it if it changes)."""
        command = _TilemapLoad_Command(tilemap_index, x, y, filename, layer)
        if self.hotreload_resources:
            self.load_list += [command]
            self._update_file_time(filename)
        command.exec()

    def watch_resource(self, filename):
        """Call App.reload_resource if this file is modified."""
        command = _Watch_Command(filename)
        if self.hotreload_resources:
            self.load_list += [command]
            self._update_file_time(filename)        

    def run(self, the_app):
        """Run your game, also periodically check for file changes."""
        self.app = the_app
        if (not hasattr(the_app, 'update')):
            raise 'App needs to have an "update" method'
        if (not hasattr(the_app, 'draw')):
            raise 'App needs to have a "draw" method'
        if self.hotreload_code and  (not hasattr(the_app, 'reload')):
            print('App does not have a "reload" method, code hot reload disabled.')
            self.hotreload_code = False
        if self.hotreload_code:
            self._build_modules_list()
            # Double-check that the reload method does not crash.
            self.app.reload(self.app)
        pyxel.run(self._update, self._draw)


    # You don't need to call any of the below methods yourself.

    def _update_file_time(self, filename, mtime=None):
        if mtime is None: mtime = os.stat(filename).st_mtime
        self.fstats[filename] = mtime

    def _get_module_mtime(self, m):
        if (not hasattr(m, '__file__')) or (not m.__file__): return None
        try:
            _path, ext = os.path.splitext(m.__file__)
            if ext.lower() != '.py': return None
            return os.stat(m.__file__).st_mtime
        except OSError:
            return None

    def _build_modules_list(self):
        """populate state.mstats"""
        self.mstats = {}
        for (mname,m) in sys.modules.items():
            # We can't reload ourselves
            if mname == 'reloadpyxel': continue
            mtime = self._get_module_mtime(m)
            if not mtime: continue
            self.mstats[mname] = mtime

    def _check_for_resource_updates(self):
        """Call pyxel.load on all modified resource files."""
        # Update mtime and list files that changed
        changed = {}
        for (fname,last_loaded) in self.fstats.items():
            mtime = os.stat(fname).st_mtime
            if mtime != last_loaded:
                # measure only once, to avoid a race condition
                self._update_file_time(fname, mtime=mtime)
                changed[fname]=True
        # reload all changed files (in the correct order, with the correct arguments)
        for command in self.load_list:
            if command.filename() in changed:
                command.exec()
        # inform the program we have reloaded some resources
        if changed:
            reload_resources = getattr(self.app, 'reload_resources')
            if reload_resources:
                reload_resources(self.load_list)


    def _check_for_module_updates(self):
        """Reload any module whose source file changed, return True if any did."""
        reloaded = False
        for (mname, mtime) in list(self.mstats.items()):
            m = sys.modules.get(mname)
            new_mtime = self._get_module_mtime(m)
            if new_mtime > mtime:
                self.mstats[mname] = new_mtime
                importlib.reload(m)
                reloaded = True
        return reloaded

    def _renew_app(self):
        """Called after we reloaded the module and created a new instance of App."""
        # Here we don't make assumptions about the name of the module
        # the main app is in.
        mname = self.app.__module__
        m = sys.modules.get(mname)
        # We require the main app class be called "App"
        class_name = self.app.__class__.__name__
        # Create a new instance
        new_app = getattr(m, class_name)(self)
        # Call it so it can transfer state
        new_app.reload(self.app)
        self.app = new_app

    def _update(self):
        """Called every frame, forwards to the game's update but also
        checks for updates to resources or source files."""
        self.ticks += 1
        if (self.ticks%self.check_period==0):
            self.ticks = 0
            # hotreload code, if needed
            if self.hotreload_code:
                reloaded = self._check_for_module_updates()
                if reloaded:
                    self._renew_app()
            # hotreload resources, if needed
            if self.hotreload_resources:
                self._check_for_resource_updates()
        self.app.update()

    def _draw(self):
        """Called every frame, forwards to the game's draw."""
        # We do this instead of passing draw to pyxel.run because
        # self.app may change in case of hot reload.
        self.app.draw()


class _ReloadImage:
    """This allows us to offer ryxel.images[0].load(...)"""
    def __init__(self, repyxel, index):
        self.index = index
        self.repyxel = repyxel

    def load(self, x, y, filename, incl_colors=None):
        self.repyxel.image_load(self.index, x, y, filename, incl_colors)

class _ReloadTilemap:
    """This allows us to offer ryxel.tilemaps[0].load(...)"""
    def __init__(self, repyxel, index):
        self.index = index
        self.repyxel = repyxel
    def load(self, x, y, filename, layer):
        self.repyxel.tilemap_load(self.index, x, y, filename, layer)


class _PyxelLoad_Command:
    """Command for pyxel.load"""
    def __init__(self, filename, args_dict):
        self._filename = filename
        self.args = args_dict
    def filename(self):
        return self._filename
    def exec(self):
        pyxel.load(**self.args)

class _ImageLoad_Command:
    """Command for pyxel.images[i].load"""
    def __init__(self, image_index, x, y, filename, incl_colors):
        self.image_index = image_index
        self.x = x
        self.y = y
        self._filename = filename
        self.incl_colors = incl_colors
    def filename(self):
        return self._filename
    def exec(self):
        pyxel.images[self.image_index].load(self.x, self.y, self._filename, incl_colors=self.incl_colors)

class _TilemapLoad_Command:
    """Command for pyxel.tilemap[i].load"""
    def __init__(self, tilemap_index, x, y, filename, layer):
        self.tilemap_index = tilemap_index
        self.x = x
        self.y = y
        self._filename = filename
        self.layer = layer
    def filename(self):
        return self._filename
    def exec(self):
        pyxel.tilemaps[self.tilemap_index].load(self.x, self.y, self._filename, self.layer)

class _Watch_Command:
    """Command for the code manually asking us to watch a file."""
    def __init__(self, filename):
        self._filename = filename
    def filename(self):
        return self._filename
    def exec(self):
        pass




