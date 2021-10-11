class UndoRedo:
    def __init__(self, initial):
        self.prev_states = [initial]
        self.index = 0

    @property
    def current(self):
        if self.prev_states:
            return self.prev_states[self.index]
        else:
            return None

    def override_last(self, new_state):
        if self.prev_states:
            self.prev_states[self.index] = new_state
        else:
            self.prev_states.append(new_state)
            self.index = 0

    def push(self, new_state):
        if self.prev_states:
            prev = self.prev_states[self.index]
            if new_state != prev:
                self.prev_states = [*self.prev_states[: self.index + 1], new_state]
                self.index = len(self.prev_states) - 1
        else:
            self.prev_states.append(new_state)
            self.index = 0

    def undo(self):
        if self.prev_states:
            if self.index > 0:
                self.index -= 1
                return True
        return False

    def redo(self):
        if self.prev_states:
            if self.index + 1 < len(self.prev_states):
                self.index += 1
                return True
        return False
