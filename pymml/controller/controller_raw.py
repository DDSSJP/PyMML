from .controller_base import ControllerBase

class ControllerRaw(ControllerBase):
    class Parameter(ControllerBase.Parameter):
        HEAD = "HEAD"
        BODY = "BODY"
        RELEASE = "RELEASE"
        DATA = "DATA"

    _ENV_OFF = "_ENV_OFF"
    _ENV_HEAD = "_ENV_HEAD"
    _ENV_BODY = "_ENV_BODY"
    _ENV_RELEASE = "_ENV_RELEASE"
    _ENV_KEEP = "_ENV_KEEP"

    @staticmethod
    def expand_length(values):
        if type(values) != list:
            return values
        ret = []
        for i in range(len(values)):
            if "*" in values[i]:
                idx = values[i].index("*")
                val = float(values[i][0:idx])
                num = int(values[i][idx+1:])
                ret.extend([val] * num)
            else:
                ret.append(float(values[i]))
        return ret

    def __init__(self):
        super().__init__()
        self.head    = []
        self.body    = []
        self.release = []
        self.reset()

    def reset(self):
        super().reset()
        self._env_step = self._ENV_HEAD
        self._index = 0
        self._output_value = 0

    def set_value(self, value_type, value):
        value_type = value_type.strip().upper()
        super().set_value(value_type, value)
        if value_type == ControllerRaw.Parameter.HEAD:
            if type(value) == str:
                value = value.split(" ")
            self.head = self.expand_length(value)
        elif value_type == ControllerRaw.Parameter.BODY:
            if type(value) == str:
                value = value.split(" ")
            self.body = self.expand_length(value)
        elif value_type == ControllerRaw.Parameter.RELEASE:
            if type(value) == str:
                value = value.split(" ")
            self.release = self.expand_length(value)
        elif value_type == ControllerRaw.Parameter.DATA:
            data = str(value).upper().split(" ")
            idxL = data.index("L") if "L" in data else -1
            idxR = data.index("R") if "R" in data else -1
            if idxL >= 0 and idxR >= 0:
                self.set_value(self.Parameter.HEAD, data[:idxL])
                self.set_value(self.Parameter.BODY, data[idxL+1:idxR])
                self.set_value(self.Parameter.RELEASE, data[idxR+1:])
            if idxL >= 0 and idxR < 0:
                self.set_value(self.Parameter.HEAD, data[:idxL])
                self.set_value(self.Parameter.BODY, data[idxL+1:idxR])
                self.set_value(self.Parameter.RELEASE, [])
            if idxL < 0 and idxR >= 0:
                self.set_value(self.Parameter.HEAD, [])
                self.set_value(self.Parameter.BODY, data[:idxR])
                self.set_value(self.Parameter.RELEASE, data[idxR+1:])
            if idxL < 0 and idxR < 0:
                self.set_value(self.Parameter.HEAD, [])
                self.set_value(self.Parameter.BODY, data)
                self.set_value(self.Parameter.RELEASE, [])

    def set_value_list(self, value):
        data = str(value).upper().split(" ")
        if len(data) < 3:
            return
        self.set_value(self.Parameter.MODIFY_VALUE, data[0])
        self.set_value(self.Parameter.MODIFY_TYPE,  data[1])
        self.set_value(self.Parameter.DATA,         data[2])

    def tick(self, channel_work):
        if channel_work.get_key_on_edge():
            self._env_step = self._ENV_HEAD
            self._index = 0

        if channel_work.get_key_off_edge() and self._env_step != self._ENV_OFF:
            self._env_step = self._ENV_RELEASE
            self._index = 0

        if self._env_step == self._ENV_HEAD:
            if self._index >= len(self.head) or len(self.head) == 0:
                self._env_step = self._ENV_BODY
                self._index = 0

        if self._env_step == self._ENV_BODY:
            if self._index >= len(self.body):
                self._env_step = self._ENV_BODY
                self._index = 0 # loop
            elif  len(self.body) == 0:
                self._env_step = self._ENV_KEEP

        if self._env_step == self._ENV_RELEASE:
            if self._index >= len(self.release):
                self._env_step = self._ENV_OFF
                self._index = 0

        if self._env_step in [self._ENV_HEAD, self._ENV_BODY, self._ENV_RELEASE]:
            if self._env_step == self._ENV_HEAD:
                self._output_value = self.head[self._index]
            elif self._env_step == self._ENV_BODY:
                self._output_value = self.body[self._index]
            elif self._env_step == self._ENV_RELEASE:
                self._output_value = self.release[self._index]
            self._index += 1
