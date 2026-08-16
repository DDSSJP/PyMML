from ..define import DeviceType

class DeviceInfo:
    def __init__(self, device_type:str, device_id:str, detail:dict):
        self.device_type = device_type
        self.device_id = device_id
        self.detail = detail
    def __str__(self):
        return f"DeviceType:{self.device_type}  DeviceID:{self.device_id}  detail:{self.detail}"

class DeviceBase:
    PORT_NUM = 1
    def __init__(self):
        self.opend = False
        self.device_id = None
        self.device_type = DeviceType.UNKNOWN
    @staticmethod
    def search():
        raise NotImplementedError()
    def open(self, device_id):
        raise NotImplementedError()
    def close(self):
        pass
    def is_open(self):
        return self.opend
    def reset(self):
        pass
    def unique(self, cmd):
        pass
    def write_burst(self, adr, data:list):
        raise NotImplementedError()
    def write_single(self, adr, data):
        raise NotImplementedError()
    def write_multi(self, item_list):
        raise NotImplementedError()
    def read_single(self, adr):
        raise NotImplementedError()
    def read_multi(self, adr_list):
        raise NotImplementedError()
    def __enter__(self):
        return self
    def __exit__(self, exc_type, exc_value, traceback):
        self.close()
    def __str__(self):
        return f"opend:{self.opend}  {self.info}"

