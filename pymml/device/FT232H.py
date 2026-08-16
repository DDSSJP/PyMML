import time
from . import FTD2xx_lib as lib
from .device_base import DeviceBase, DeviceInfo
from ..define import DeviceType, UniqueType

class FT232H(DeviceBase):
    class UniqueCommandType:
        YMF825_RESET_SIGNAL = "YMF825_RESET_SIGNAL"

    def __init__(self):
        self.device_id = None
        self.device_type = DeviceType.FT232H
        self.opend = False
        self._handle = None

        # ?,?,?,RST_N,SS,MISO,MOSI,clock SS,RST_N=low-active
        self.pin_rstn_high = 0b0001_1000 
        self.pin_rstn_low  = 0b0000_1000
        self.pin_ss_high   = 0b0001_1000
        self.pin_ss_low    = 0b0001_0000
        self.pin_direction = 0b0001_1011 # 1=out/0=in D0～D7
        self.bytes_ss_high = bytes([0x80, self.pin_ss_high, self.pin_direction])
        self.bytes_ss_low = bytes([0x80, self.pin_ss_low, self.pin_direction])

    @staticmethod
    def search():
        lib.load_dll()
        num = lib.FT_CreateDeviceInfoList()
        if num == 0:
            return []
        device_list = lib.FT_GetDeviceInfoList(num)
        info = []
        for i in range(len(device_list)):
            di = DeviceInfo(
                device_type = DeviceType.FT232H,
                device_id = device_list[i][4], # serial number
                detail = {
                    "flag":device_list[i][0],
                    "type":device_list[i][1],
                    "id":device_list[i][2],
                    "locaton":device_list[i][3],
                    "serial number":device_list[i][4],
                    "description":device_list[i][5],
                    "handle":device_list[i][6]
                }
            )
            info.append(di)
        lib.unload_dll()
        return info

    def is_open(self):
        return self.opend

    def open(self, device_id):
        lib.load_dll()
        self.device_id = device_id
        self._handle = lib.FT_OpenEx(lib.FT_OPEN_BY_SERIAL_NUMBER, self.device_id)

        # setup device
        lib.FT_ResetDevice(self._handle)
        lib.FT_SetUSBParameters(self._handle, 0xffff, 0xffff)
        lib.FT_SetChars(self._handle, 0, 0, 0, 0)
        lib.FT_SetTimeouts(self._handle, 3000, 0)
        lib.FT_SetLatencyTimer(self._handle, 1)
        lib.FT_SetFlowControl(self._handle, lib.FT_FLOW_RTS_CTS, 0, 0)
        lib.FT_SetBitMode(self._handle, 0x00, lib.FT_BITMODE_RESET)
        lib.FT_SetBitMode(self._handle, 0x00, lib.FT_BITMODE_MPSSE)

        # read all read_buffer
        size = lib.FT_GetQueueStatus(self._handle)
        if size > 0:
            ret = lib.FT_Read(self._handle, size)

        # bogus opcode test
        ret = lib.FT_Write(self._handle, bytes([0xaa]))
        if ret != 1:
            raise Exception(f"failed to write test. -> ret_data:{ret}")
        ret = lib.FT_Read(self._handle, 2)
        if len(ret) != 2 or ret[0] != 0xfa or ret[1] != 0xaa:
            raise Exception(f"failed to read test. -> ret_data:{ret}")
        
        # setup MPSSE
        lib.FT_Write(self._handle, bytes([0x85])) # disable loopback
        lib.FT_Write(self._handle, bytes([0x86, 0x02, 0x00])) # set clock divisor (60MHz / 6 = 10MHz)
        lib.FT_Write(self._handle, bytes([0x8a])) # disable /5 divider
        lib.FT_Write(self._handle, bytes([0x80, self.pin_ss_high, self.pin_direction])) # set out-pin low byte
        lib.FT_Write(self._handle, bytes([0x82, 0x00, 0x00])) # set out-pin high byte

        self.info = DeviceInfo(DeviceType.FT232H, self.device_id, {"serial number":self.device_id})
        self.opend = True

    def close(self):
        if self.opend:
            lib.FT_Close(self._handle)
            lib.unload_dll()
            self.id = ""
            self.opend = False
            self._handle = None

    def reset(self):
        if self.opend:
            self.close()
            self.open(self.id)

    def YMF825_reset_signal(self):
        lib.FT_Write(self._handle, bytes([0x80, self.pin_rstn_low, self.pin_direction]))
        time.sleep(10/1000)
        lib.FT_Write(self._handle, bytes([0x80, self.pin_rstn_high, self.pin_direction]))

    def write_burst(self, adr, data):
        length = 1 + len(data) - 1
        buf = [0x11, length%256, length//256, adr]
        buf.extend(data)
        buf = bytes(buf)
        lib.FT_Write(self._handle, self.bytes_ss_low)
        lib.FT_Write(self._handle, buf)
        lib.FT_Write(self._handle, self.bytes_ss_high)

    def write_single(self, adr, data):
        if adr == 27:
            self.read_single(5)
            return
        buf = bytes([0x11, 0x01, 0x00, adr, data])
        lib.FT_Write(self._handle, self.bytes_ss_low)
        lib.FT_Write(self._handle, buf)
        lib.FT_Write(self._handle, self.bytes_ss_high)

    def write_multi(self, item_list):
        buf_list = []
        for i in range(len(item_list)):
            buf = bytes([0x11, 0x01, 0x00, item_list[i][0], item_list[i][1]])
            buf_list.append(buf)
        for i in range(len(buf_list)):
            lib.FT_Write(self._handle, self.bytes_ss_low)
            lib.FT_Write(self._handle, buf_list[i])
            lib.FT_Write(self._handle, self.bytes_ss_high)

    def read_single(self, adr):
        buf_write = bytes([0x11, 0x00, 0x00, 0x80|adr]) # MOSI only, LowToHighEdge, MSB fast
        buf_read = bytes([0x21, 0x00, 0x00])            # MISO only, LowToHighEdge, MSB fast
        lib.FT_Write(self._handle, self.bytes_ss_low)
        lib.FT_Write(self._handle, buf_write)
        lib.FT_Write(self._handle, buf_read)
        lib.FT_Write(self._handle, self.bytes_ss_high)
        ret = lib.FT_Read(self._handle, 1)
        return ret

    def read_multi(self, adr_list):
        buf_write_list = []
        buf_read_list = []
        for i in range(len(adr_list)):
            buf_write = bytes([0x11, 0x00, 0x00, 0x80|adr_list[i]])
            buf_read = bytes([0x21, 0x00, 0x00])
            buf_write_list.append(buf_write)
            buf_read_list.append(buf_read)
        ret_list = []
        for i in range(len(buf_write)):
            lib.FT_Write(self._handle, self.bytes_ss_low)
            lib.FT_Write(self._handle, buf_write_list[i])
            lib.FT_Write(self._handle, buf_read_list[i])
            lib.FT_Write(self._handle, self.bytes_ss_high)
            ret = lib.FT_Read(self._handle, 1)
            ret_list.append(ret[0])
        return ret_list

    def unique(self, cmd):
        if cmd.unique_type != UniqueType.DEVICE:
            return
        if cmd.cmd == FT232H.UniqueCommandType.YMF825_RESET_SIGNAL:
            self.YMF825_reset_signal()
