import time
from .device_base import DeviceBase, DeviceInfo
from ..define import DeviceType

class MockDevice(DeviceBase):
    PORT_NUM = 1
    def __init__(self):
        self.opend = False
        self.device_id = None
        self.device_type = DeviceType.MOCK
        self._reg = {}

    @staticmethod
    def search():
        info = []
        info.append(DeviceInfo(DeviceType.MOCK, "1234", {"description":"This is mock device."}))
        return info

    def open(self, device_id):
        self.device_id = device_id
        self.opend = True
        time.sleep(0.001)

    def close(self):
        self.opend = False

    def unique(self, cmd, ch):
        pass

    def send_reset_signal(self):
        time.sleep(0.001)
        pass

    def write_burst(self, adr, data:list):
        # print("b", f"{adr:02d}", *[f"{x:02x}" for x in data]) # debug
        self._reg[adr] = data[-1]
        time.sleep(0.001)

    def write_single(self, adr, data):
        self._reg[adr] = data
        # print(f"w {adr:02} {data:02X}") # debug
        time.sleep(0.001)

    def write_multi(self, item_list):
        for i in range(len(item_list)):
            self._reg[item_list[i][0]] = item_list[i][1]
        time.sleep(0.001)
        # print("w", end="") # debug
        # for i in range(len(item_list)):
        #     print(f" {item_list[i][0]:02} {item_list[i][1]:02X}", end="") # debug
        print() # debug

    def read_single(self, adr):
        if adr not in self._reg.keys():
            self._reg[adr] = 0
        time.sleep(0.001)
        return [self._reg[adr]]

    def read_multi(self, adr_list):
        ret_list = []
        for i in range(len(adr_list)):
            if adr_list[i] not in self._reg.keys():
                self._reg[adr_list[i]] = 0
            ret_list.append(self._reg[adr_list[i]])
        time.sleep(0.001)
        return ret_list

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    def __str__(self):
        return f"opend:{self.opend}  {self.info}"

class MockDevice4(MockDevice):
    PORT_NUM = 4
    def __init__(self):
        self.device_id = None
        self.device_type = DeviceType.MOCK4
        self._reg = {}

    @staticmethod
    def search():
        info = []
        info.append(DeviceInfo(DeviceType.MOCK4, "1234", {"description":"This is mock device."}))
        return info
