from .controller_base import ControllerBase

class Sweep(ControllerBase):
    class Parameter(ControllerBase.Parameter):
        VOLUME_INI = "VOLUME_INI"
        STEP       = "STEP"
        VOLUME     = "VOLUME"

    def __init__(self):
        super().__init__()
        self.volume_ini = 0 # int
        self.step       = 1 # int tick
        self.volume     = 0 # int
        self.reset()

    def reset(self):
        super().reset()
        self._step_count = 0
        self._output_value = self.volume_ini

    def set_value(self, value_type, value):
        value_type = value_type.strip().upper()
        super().set_value(value_type, value)
        if value_type == Sweep.Parameter.VOLUME_INI:
            self.volume_ini = int(value)
        elif value_type == Sweep.Parameter.STEP:
            self.step = max(int(value),1)
        elif value_type == Sweep.Parameter.VOLUME:
            self.volume = int(value)

    def set_value_list(self, value):
        data = str(value).upper().split(" ")
        if len(data) != 5:
            return
        self.set_value(self.Parameter.MODIFY_VALUE, data[0])
        self.set_value(self.Parameter.MODIFY_TYPE,  data[1])
        self.set_value(self.Parameter.VOLUME_INI,   data[2])
        self.set_value(self.Parameter.STEP,         data[3])
        self.set_value(self.Parameter.VOLUME,       data[4])

    def tick(self, channel_work):
        if channel_work.get_key_on_edge():
            self.reset()

        if channel_work.get_key_off():
            return

        if self._step_count >= self.step:
            self._step_count = 0
            self._output_value += self.volume
        self._step_count += 1
