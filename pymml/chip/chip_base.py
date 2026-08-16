from ..define import ChipType

class RegisterBase():
    def __init__(self):
        raise NotImplementedError()
    def write(self, adr, data):
        raise NotImplementedError()
    def read(self, adr):
        raise NotImplementedError()
    def diff(self, other):
        raise NotImplementedError()
    def copy(self, other):
        raise NotImplementedError()

class ParameterBase():
    def __init__(self):
        raise NotImplementedError()
    def read(reg, prm, ch):
        raise NotImplementedError()
    def write(reg, prm, value):
        raise NotImplementedError()

class ToneDataBase:
    ...

class ChipBase():
    CHANNEL_NUMBER = 1
    TONE_PRM_NUM = 1
    tone_data_dic = {}

    def __init__(self):
        self.chip_type = ChipType.UNKNOWN
    def tuning(self, a_hz):
        raise NotImplementedError()
    def setup_master_work(self, master_work):
        raise NotImplementedError()
    def setup_channel_work(self, channel_work):
        raise NotImplementedError()
    def send_init(self, device):
        raise NotImplementedError()
    def master_work_to_prm(self, master_work):
        raise NotImplementedError()
    def channel_work_to_prm(self, channel_work):
        raise NotImplementedError()
    def write_parameter(self, prm, value):
        raise NotImplementedError()
    def get_reg_list(self):
        raise NotImplementedError()
    def tick_reset(self):
        raise NotImplementedError()
    def write_register(self, address, value):
        raise NotImplementedError()
    def send_register(self, device, reg_list):
        raise NotImplementedError()
    def unique(self, cmd, ch):
        raise NotImplementedError()
    def tone_prm_check(prm_index, value):
        raise NotImplementedError()
