#rlstack module

import readline as rl

def null_completer(text,state):
    return None

class rlstack:
    class state:
        def __init__(self):
            self.completer=rl.get_completer()
            self.delims=rl.get_completer_delims()
        def use(self):
            rl.set_completer(self.completer)
            rl.set_completer_delims(self.delims)

    def __init__(self):
        self.stack=[]
    def push(self):
        self.stack.append(rlstack.state())
    def pop(self):
        self.stack.pop().use()
