import json

class KernelState():
    def __init__(self, state_path, use_kernel=False):
        self.state = {}
        self.state_path = state_path
        self.use_kernel = use_kernel

    def init_state(self, **values):
        self.state = dict(values)

    def update_state(self, key, value):
        self.state[key] = value
        self.save_state()

    def get_state(self, key):
        return self.state[key]

    def save_state(self):
        if self.use_kernel:
            with open(self.state_path, 'w') as fp:
                json.dump(self.state, fp)

    def delete_state(self, key):
        del self.state[key]
