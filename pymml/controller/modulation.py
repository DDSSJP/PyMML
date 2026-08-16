from ..define import ModifyType, ModifyValue, WaveForm
from .controller_base import ControllerBase
import math
import random

class Modulation(ControllerBase):
    class Parameter(ControllerBase.Parameter):
        WAVE    = "WAVE"
        DELAY   = "DELAY"
        AMPLIFY = "AMPLIFY"
        PERIOD  = "PERIOD"

    def __init__(self):
        super().__init__()
        self.modify_value = ModifyValue.PITCH
        self.modify_type  = ModifyType.RELATIVE
        self.wave         = WaveForm.SIN 
        self.delay        = 0 # int   tick
        self.amplify      = 0 # float value
        self.period       = 2 # int   tick
        self.reset()

    def reset(self):
        super().reset()
        self._delay_tick   = 0
        self._period_tick  = 0
        self._wave_value   = 0
        self._output_value = 0

    def set_value(self, value_type, value):
        value_type = value_type.strip().upper()
        super().set_value(value_type, value)
        if value_type == Modulation.Parameter.WAVE:
            self.wave = str(value).upper()
        if value_type == Modulation.Parameter.DELAY:
            self.delay = max(int(value), 0)
        if value_type == Modulation.Parameter.AMPLIFY:
            self.amplify =  float(value)
        elif value_type == Modulation.Parameter.PERIOD:
            self.period = max(int(value), 1)

    def set_value_list(self, value):
        data = str(value).upper().split(" ")
        if len(data) != 6:
            return
        self.set_value(self.Parameter.MODIFY_VALUE, data[0])
        self.set_value(self.Parameter.MODIFY_TYPE,  data[1])
        self.set_value(self.Parameter.WAVE,         data[2])
        self.set_value(self.Parameter.DELAY,        data[3])
        self.set_value(self.Parameter.AMPLIFY,      data[4])
        self.set_value(self.Parameter.PERIOD,       data[5])

    def tick(self, channel_work):
        if channel_work.get_key_off():
            self._delay_tick = 0
            self._period_tick = 0
            self._output_value = 0
            return

        if channel_work.get_key_on_edge():
            self._delay_tick = 0
            self._period_tick = 0
            self._output_value = 0

        if self._delay_tick < self.delay:
            self._delay_tick += 1
            return

        if self.wave == WaveForm.SIN:
            self._wave_value = math.sin(math.pi * 2.0 * (self._period_tick + 1) / self.period)

        elif self.wave == WaveForm.SAW:
            self._wave_value = (self._period_tick + 1 ) / self.period

        elif self.wave == WaveForm.TRIANGLE:
            phase = self._period_tick / self.period
            if phase < 0.25:
                self._wave_value = phase * 4.0
            elif phase < 0.5:
                self._wave_value = 1.0 - (phase - 0.25) * 4.0
            elif phase < 0.75:
                self._wave_value = - (phase - 0.5) * 4.0
            else:
                self._wave_value = (phase - 0.75) * 4.0 - 1.0
        
        elif self.wave == WaveForm.SQUARE:
            phase = self._period_tick / self.period
            if phase < 0.5:
                self._wave_value = 1.0
            else:
                self._wave_value = -1.0
        
        elif self.wave == WaveForm.RANDOM:
            if self._period_tick == 0:
                self._wave_value = random.random() * 2.02 - 1.0 # 1.0と-1.0がちょっと出やすくする
                self._wave_value = min(1.0,max(-1.0, self._wave_value))

        self._period_tick += 1
        if self._period_tick == self.period:
            self._period_tick = 0

        # if self._wave_value > 1.0:
        #     self._wave_value = 1.0
        # if self._wave_value < -1.0:
        #     self._wave_value = -1.0

        self._output_value = self.amplify * self._wave_value

    def __str__(self):
        return f"{self._output_value:.2f},{self._wave_value:.2f},{self._period_tick / self.period:.2f},{self._delay_tick},{self._period_tick},{self.wave},{self.delay},{self.amplify},{self.period}"
