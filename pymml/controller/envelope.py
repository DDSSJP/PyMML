from .controller_base import ControllerBase
from ..define import ModifyType

class Envelope(ControllerBase):
    class Parameter(ControllerBase.Parameter):
        INI_VALUE = "INI_VALUE"
        ATTACK_TICK = "ATTACK_TICK"
        ATTACK_VALUE = "ATTACK_VALUE"
        DECAY_TICK = "DECAY_TICK"
        DECAY_VALUE = "DECAY_VALUE"
        SUSTAIN_TICK = "SUSTAIN_TICK"
        SUSTAIN_VALUE = "SUSTAIN_VALUE"
        RELEASE_RATE = "RELEASE_RATE" # 1tickで減る値

    _ENV_OFF     = "_ENV_OFF"
    _ENV_ATTACK  = "_ENV_ATTACK"
    _ENV_DECAY   = "_ENV_DECAY"
    _ENV_SUSTAIN = "_ENV_SUSTAIN"
    _ENV_KEEP    = "_ENV_KEEP"
    _ENV_RELEASE = "_ENV_RELEASE"

    def __init__(self):
        super().__init__()
        self.ini_value = 0
        self.attack_tick = 0
        self.attack_value = 0
        self.decay_tick = 0
        self.decay_value = 0
        self.sustain_tick = 0
        self.sustain_value = 0
        self.release_rate = 0
        self.reset()

    def reset(self):
        super().reset()
        self._env_step = self._ENV_OFF
        self._tick = 0
        self._tick_count = 0
        self._output_value = 0
        self._from_value = 0
        self._to_value = 0

    def set_value(self, value_type:str, value):
        value_type = value_type.strip().upper()
        super().set_value(value_type, value)
        if value_type == Envelope.Parameter.INI_VALUE:
            self.ini_value = max(float(value),0)
        elif value_type == Envelope.Parameter.ATTACK_TICK:
            self.attack_tick = max(int(value),0)
        elif value_type == Envelope.Parameter.ATTACK_VALUE:
            self.attack_value = max(float(value),0)
        elif value_type == Envelope.Parameter.DECAY_TICK:
            self.decay_tick = max(int(value),0)
        elif value_type == Envelope.Parameter.DECAY_VALUE:
            self.decay_value = max(float(value),0)
        elif value_type == Envelope.Parameter.SUSTAIN_TICK:
            self.sustain_tick = max(int(value),0)
        elif value_type == Envelope.Parameter.SUSTAIN_VALUE:
            self.sustain_value = max(float(value),0)
        elif value_type == Envelope.Parameter.RELEASE_RATE:
            self.release_rate = max(float(value),0)

    def set_value_list(self, value):
        data = str(value).upper().split(" ")
        if len(data) != 10:
            return
        self.set_value(Envelope.Parameter.MODIFY_VALUE,  data[0])
        self.set_value(Envelope.Parameter.MODIFY_TYPE,   data[1])
        self.set_value(Envelope.Parameter.INI_VALUE,     data[2])
        self.set_value(Envelope.Parameter.ATTACK_TICK,   data[3])
        self.set_value(Envelope.Parameter.ATTACK_VALUE,  data[4])
        self.set_value(Envelope.Parameter.DECAY_TICK,    data[5])
        self.set_value(Envelope.Parameter.DECAY_VALUE,   data[6])
        self.set_value(Envelope.Parameter.SUSTAIN_TICK,  data[7])
        self.set_value(Envelope.Parameter.SUSTAIN_VALUE, data[8])
        self.set_value(Envelope.Parameter.RELEASE_RATE,  data[9])

    def tick(self, channel_work):
        if channel_work.get_key_on_edge():
            self._env_step = self._ENV_ATTACK
            self._from_value = self.ini_value
            self._to_value = self.attack_value
            self._tick = self.attack_tick
            self._tick_count = 0
            self._output_value = self.ini_value

        if channel_work.get_key_off_edge() and self._env_step != self._ENV_OFF:
            self._env_step = self._ENV_RELEASE
            self._from_value = self._output_value
            self._to_value = 0
            if self.release_rate == 0:
                self._tick = 0
            else:
                self._tick = int(self._output_value / self.release_rate + 0.9999) # 切り上げ
            self._tick_count = 1

        if self._env_step == self._ENV_ATTACK:
            if self._tick <= self._tick_count:
                self._env_step = self._ENV_DECAY
                self._from_value = self.attack_value
                self._to_value = self.decay_value
                self._tick = self.decay_tick
                self._tick_count = 0
        if self._env_step == self._ENV_DECAY:
            if self._tick <= self._tick_count:
                self._env_step = self._ENV_SUSTAIN
                self._from_value = self.decay_value
                self._to_value = self.sustain_value
                self._tick = self.sustain_tick
                self._tick_count = 0
        if self._env_step == self._ENV_SUSTAIN:
            if self._tick <= self._tick_count:
                self._env_step = self._ENV_KEEP
                self._from_value = 0
                self._to_value = 0
                self._tick = 0
                self._tick_count = 0
                self._output_value = self.sustain_value
        if self._env_step == self._ENV_RELEASE:
            if self._tick <= self._tick_count:
                self._env_step = self._ENV_OFF
                self._from_value = 0
                self._to_value = 0
                self._tick = 0
                self._tick_count = 0
                self._output_value = 0

        if self._env_step in [self._ENV_ATTACK, self._ENV_DECAY, self._ENV_SUSTAIN, self._ENV_RELEASE]  :
            self._output_value = self._from_value + (self._to_value - self._from_value)  * self._tick_count / self._tick
            if self.modify_type in [ModifyType.CURRENT, ModifyType.RELATIV]:
                if self._from_value > self._to_value:
                    self._output_value += 0.9999 # intにしたとき切り上げになるように
            self._tick_count += 1
