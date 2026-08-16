from ..define import ModifyType, ModifyValue
from .controller_base import ControllerBase

class Portamento(ControllerBase):
    class Parameter(ControllerBase.Parameter):
        TIME = "TIME"
        CONTROL = "CONTROL"

    def __init__(self):
        super().__init__()
        self.time = 0 # int tick
        self.control = None # int
        self.reset()

    def reset(self):
        super().reset()
        self._flg = False
        self._count = 0
        self._shift = 0

    def set_value(self, value_type, value):
        value_type = value_type.strip().upper()
        super().set_value(value_type, value)
        if value_type == Portamento.Parameter.TIME:
            self.time = max(int(value),1)
        elif value_type == Portamento.Parameter.CONTROL:
            c = max(int(value),-1)
            if c < 0:
                self.control = None
            else:
                self.control = c

    def set_value_list(self, value):
        data = str(value).upper().split(" ")
        if len(data) != 4:
            return
        self.set_value(self.Parameter.MODIFY_VALUE, data[0])
        self.set_value(self.Parameter.MODIFY_TYPE,  data[1])
        self.set_value(self.Parameter.TIME,         data[2])
        self.set_value(self.Parameter.CONTROL,      data[3])
    
    def tick(self, channel_work):
        if self.modify_value == ModifyValue.NOTE:
            note = channel_work.note.current
            oct =  channel_work.octave.current
            current = oct * 12 + note
        else:
            if self.modify_value == ModifyValue.PAN:
                current = channel_work.pan.current
            elif self.modify_value == ModifyValue.PITCH:
                current = channel_work.detune.current
            elif self.modify_value == ModifyValue.VOLUME:
                current = channel_work.volume.current
        if self.control is None:
            self.control = current

        # currentが変化したら動作開始
        if self.control != current:
            self._flg = True
            self._count = 0
            self._shift = current - self.control # 今回の変化量
            if self.modify_value == ModifyValue.NOTE:
                # portamentoはnote指定でdetune変化のため*100でセントにする
                self._shift *= 100
            self.control = current # 今回の値を記憶

        # 動作する
        if self._flg == True:
            self._output_value = -self._shift * (1.0 - self._count / self.time)
            self._count += 1
            if self._count > self.time:
                self.reset()

