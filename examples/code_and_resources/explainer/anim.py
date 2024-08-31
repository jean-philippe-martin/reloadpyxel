import reloadpyxel

# A simple animation helper

class Animation:
    '''A sequence of callbacks that will be called in subsequent frames.'''

    def __init__(self):
        self.steps = []
        self.pretend_enditer = False

    def add_multi(self, iterable, function):
        """Add a new sequence of steps in the animation."""
        self.steps += [(iter(iterable), function)]

    def add_single(self, function):
        """Add a single step to the animation."""
        self.steps += [(None, function)]

    def update(self) -> bool:
        '''Move to the next item. self.val will contain the next iterator value.
        Return False if there's no next item.'''
        while True:
            if not self.steps: return False
            (it,_fn) = self.steps[0]
            if it is None:
                if self.pretend_enditer:
                    # "None" is consumed, move on
                    self.pretend_enditer = False
                    self.steps = self.steps[1:]
                    continue
                else:
                    # "None" isn't yet consumed, that's what we advanced to.
                    self.pretend_enditer = True
                    self.val = None
                    return True
            try:
                self.val = next(it)
            except StopIteration:
                # This step is exhausted, try the next one
                self.steps = self.steps[1:]
                continue
            return True

    def draw(self) -> bool:
        """Draw one frame. Returns False if we're done."""
        if not self.steps: 
            return False
        (it, fn) = self.steps[0]
        if it is None:
            fn()
        else:
            fn(self.val)
        return True
    
    def reload(self, old_self):
        """Called after a hot reload, on the newly-created updated Animation object."""
        reloadpyxel.copy_all_attributes(old_self, self)
        return self
