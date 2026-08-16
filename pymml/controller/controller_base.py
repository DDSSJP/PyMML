from ..define import ModifyValue, ModifyType

class ControllerBase:
    class Parameter:
        RESET = "RESET"
        ENABLE = "ENABLE"
        MUTE = "MUTE"
        MODIFY_VALUE = "MODIFY_VALUE"
        MODIFY_TYPE = "MODIFY_TYPE"

    def __init__(self):
        self._output_value = 0
        self.enable = False
        self.mute = False
        self.modify_type = ModifyType.RELATIVE
        self.modify_value = ModifyValue.VOLUME

    def reset(self):
        self._output_value = 0

    def get_output_value(self):
        if self.mute:
            if self.modify_type == ModifyType.RELATIVE:
                return 0
            elif self.modify_type == ModifyType.MULTIPLE:
                return 1.0
        return self._output_value

    def set_value(self, value_type, value):
        if value_type == ControllerBase.Parameter.RESET:
            self.reset()
        elif value_type == ControllerBase.Parameter.ENABLE:
            self.enable = self.to_bool(value)
        elif value_type == ControllerBase.Parameter.MUTE:
            self.mute = self.to_bool(value)
        elif value_type == ControllerBase.Parameter.MODIFY_VALUE:
            self.modify_value = str(value).upper()
        elif value_type == ControllerBase.Parameter.MODIFY_TYPE:
            self.modify_type = str(value).upper()

    def set_value_list(self, value):
        raise NotImplementedError()

    def tick(self, channel_work):
        raise NotImplementedError()

    @staticmethod
    def to_bool(value):
        if type(value) == int or type(value) == float:
            return value != 0
        if type(value) == str:
            value = value.strip().lower()
            if value=="false" or value=="0":
                return False
            if value=="true" or value=="1":
                return True
        return None
