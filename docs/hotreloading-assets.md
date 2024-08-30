# Hot-reloading assets in reloadpyxel

## Scope

The reloadpyxel library allows you to hot-reload any asset in your game. This includes:

- Pyxel resource files (pyxres)
- Image files (png/gif/jpg)
- Tilemaps (tmx)
- Custom files (with some work on your side)

## How to use it

Here is an example snippet from a Pyxel program that loads a few resources.

```python
def __init__(self):
    pyxel.init(160, 120, title="Resource Loading Demo")
    # Load tilemap and music
    pyxel.load("assets/resources.pyxres", excl_images=True)
    # Load image
    pyxel.images[0].load(0, 0, "assets/pyxel_logo_38x16.png")
    # Load tilemap
    pyxel.tilemaps[0] = pyxel.Tilemap.from_tmx("assets/urban_rpg.tmx", 0)
```

To add hot-reloading to this program, you need to copy over the `main.py` file and organize the code as described in the [README](../README.md), and then change the code like so:

```python
def __init__(self, ryxel):
    # Load tilemap and music
    ryxel.load("assets/resources.pyxres", excl_images=True)
    # Load image
    ryxel.images[0].load(0, 0, "assets/pyxel_logo_38x16.png")
    # Load tilemap
    ryxel.tilemaps[0] = pyxel.Tilemap.from_tmx("assets/urban_rpg.tmx", 0)
```

The change is subtle: we went from calling `pyxel` to calling `ryxel`, the second argument to your App's `__init__` method. That's all that's needed! Now as your game is running, if you change one of those files then it will be reloaded into your running game.

Note that this example loads tilemaps twice: first when it reads the resources file it will load tilemaps 0 to 3, and then later it overrides tilemap 0. Reloadpyxel will do the right thing if you modify the resources file: tilemap 0 will still be read from the tmx file as you specified.

## How it works

When you call e.g. `ryxel.load`, it keeps track of the name of the file you are loading, then calls `pyxel.load`. It keeps a list of every file that was loaded (in the order you loaded them).

Then, in the `update` method that's called at every frame it will check the last-modified time on that file. If it changed, then it will reload that file and everything that was loaded after it. This ensures that anything that was overwritten later (like the tilemap in the example above) gets correctly overwritten again.

Note that this may not be enough, in case your program modifies the images or tilemaps in some way after loading. Then, you may need to do these modifications again. That's why we have the `reload_resources` hook described below.

## Custom processing on reload

After reloading resources, Reloadpyxel will call your app's `reload_resources` method if it is present. It will pass as argument the list of files that were modified.

If you need to do some processing on your images (or tilemaps) on load, this is where you can do it again on reload.

You can see an example of this in the [offscreen example](../examples/resources_only/pyxel_originals/11_offscreen.py): this program uses the resources it loads to compute two new offscreen images, the "blt figure" and the "bltm figure". This needs to be redone if the resources are reloaded.

----

Next: [Hot-reloading *code* in reloadpyxel](hotreloading-code.md) <br/>
Up: [Hot-reload, explained](hotreload-explained.md)
