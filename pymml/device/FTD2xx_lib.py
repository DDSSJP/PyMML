#---------------------------------------------------
# DESCRIPTION:
#   This is ftd2xx.dll wrapper.
#
#   Driver installation required.
#   https://ftdichip.com/drivers/d2xx-drivers/
#
#   Check the Programmer's Guide for details.
#   https://ftdichip.com/wp-content/uploads/2020/08/D2XX_Programmers_GuideFT_000071.pdf
#   
# CAUTION:
#   - Only Windows is supported. Linux and MAC are not supported.
#   - Not implemented EEPROM-Functions and Win32-Functions.
#
# USAGE: 
#   import FTD2xx_lib
#     FTD2xx_lib.load_dll()
#       ...your process...
#     FTD2xx_lib.unload_dll()
#---------------------------------------------------

from ctypes import *

#---------------------------------------------------
# DLL
#---------------------------------------------------
dll = None

def load_dll():
    global dll
    unload_dll()
    dll = windll.ftd2xx

def unload_dll():
    global dll
    if dll is not None:
        del dll
        dll = None

#---------------------------------------------------
# typedef
#---------------------------------------------------
FT_STATUS = c_ulong
FT_HANDLE = c_void_p
FT_DEVICE = c_ulong
PVOID = c_void_p
INT = c_int64
USHORT = c_uint16
UCHAR = c_ubyte
WORD = c_uint16
DWORD = c_ulong
ULONG = c_ulong
LONG = c_long
BUF_16 = (c_ubyte * 16)
BUF_64 = (c_ubyte * 64)
BUF_128 = (c_ubyte * 128)
BUF_256 = (c_ubyte * 256)
CHAR_16 = (c_char * 16)
CHAR_64 = (c_char * 64)
CHAR_128 = (c_char * 128)
CHAR_256 = (c_char * 256)

#---------------------------------------------------
# Device status
#---------------------------------------------------
FT_OK                          = 0
FT_INVALID_HANDLE              = 1
FT_DEVICE_NOT_FOUND            = 2
FT_DEVICE_NOT_OPENED           = 3
FT_IO_ERROR                    = 4
FT_INSUFFICIENT_RESOURCES      = 5
FT_INVALID_PARAMETER           = 6
FT_INVALID_BAUD_RATE           = 7
FT_DEVICE_NOT_OPENED_FOR_ERASE = 8
FT_DEVICE_NOT_OPENED_FOR_WRITE = 9
FT_FAILED_TO_WRITE_DEVICE      = 10
FT_EEPROM_READ_FAILED          = 11
FT_EEPROM_WRITE_FAILED         = 12
FT_EEPROM_ERASE_FAILED         = 13
FT_EEPROM_NOT_PRESENT          = 14
FT_EEPROM_NOT_PROGRAMMED       = 15
FT_INVALID_ARGS                = 16
FT_NOT_SUPPORTED               = 17
FT_OTHER_ERROR                 = 18
FT_DEVICE_LIST_NOT_READY       = 19

def FT_SUCCESS(status):
    return (status) == FT_OK

_device_status_str = [
    "FT_OK",
    "FT_INVALID_HANDLE",
    "FT_DEVICE_NOT_FOUND",
    "FT_DEVICE_NOT_OPENED",
    "FT_IO_ERROR",
    "FT_INSUFFICIENT_RESOURCES",
    "FT_INVALID_PARAMETER",
    "FT_INVALID_BAUD_RATE",
    "FT_DEVICE_NOT_OPENED_FOR_ERASE",
    "FT_DEVICE_NOT_OPENED_FOR_WRITE",
    "FT_FAILED_TO_WRITE_DEVICE",
    "FT_EEPROM_READ_FAILED",
    "FT_EEPROM_WRITE_FAILED",
    "FT_EEPROM_ERASE_FAILED",
    "FT_EEPROM_NOT_PRESENT",
    "FT_EEPROM_NOT_PROGRAMMED",
    "FT_INVALID_ARGS",
    "FT_NOT_SUPPORTED",
    "FT_OTHER_ERROR",
    "FT_DEVICE_LIST_NOT_READY",
]

def get_device_status_str(status):
    if status >= len(_device_status_str):
        return "unknown"
    return _device_status_str[status]

#---------------------------------------------------
# FT_OpenEx Flags
#---------------------------------------------------
FT_OPEN_BY_SERIAL_NUMBER = 1
FT_OPEN_BY_DESCRIPTION   = 2
FT_OPEN_BY_LOCATION      = 4
FT_OPEN_MASK = FT_OPEN_BY_SERIAL_NUMBER | FT_OPEN_BY_DESCRIPTION | FT_OPEN_BY_LOCATION

#---------------------------------------------------
# FT_ListDevices Flags (used in conjunction with FT_OpenEx Flags)
#---------------------------------------------------
FT_LIST_NUMBER_ONLY = 0x80000000
FT_LIST_BY_INDEX    = 0x40000000
FT_LIST_ALL         = 0x20000000
FT_LIST_MASK = FT_LIST_NUMBER_ONLY | FT_LIST_BY_INDEX | FT_LIST_ALL

#---------------------------------------------------
# UART
#---------------------------------------------------
# Baud Rates
FT_BAUD_300    = 300
FT_BAUD_600    = 600
FT_BAUD_1200   = 1200
FT_BAUD_2400   = 2400
FT_BAUD_4800   = 4800
FT_BAUD_9600   = 9600
FT_BAUD_14400  = 14400
FT_BAUD_19200  = 19200
FT_BAUD_38400  = 38400
FT_BAUD_57600  = 57600
FT_BAUD_115200 = 115200
FT_BAUD_230400 = 230400
FT_BAUD_46080  = 460800
FT_BAUD_921600 = 921600

# Word Lengths
FT_BITS_8 = 8
FT_BITS_7 = 7

# Stop Bits
FT_STOP_BITS_1 = 0
FT_STOP_BITS_2 = 2

# Parity
FT_PARITY_NONE  = 0
FT_PARITY_ODD   = 1
FT_PARITY_EVEN  = 2
FT_PARITY_MARK  = 3
FT_PARITY_SPACE = 4

# Flow Control
FT_FLOW_NONE     = 0x0000
FT_FLOW_RTS_CTS  = 0x0100
FT_FLOW_DTR_DSR  = 0x0200
FT_FLOW_XON_XOFF = 0x0400

# Purge rx and tx buffers
FT_PURGE_RX = 1
FT_PURGE_TX = 2

# Events
PFT_EVENT_HANDLER = CFUNCTYPE(None, DWORD, DWORD)
FT_EVENT_RXCHAR       = 1
FT_EVENT_MODEM_STATUS = 2
FT_EVENT_LINE_STATUS  = 4

# Timeouts
FT_DEFAULT_RX_TIMEOUT = 300
FT_DEFAULT_TX_TIMEOUT = 300

#---------------------------------------------------
# Device types
#---------------------------------------------------
FT_DEVICE = c_ulong
FT_DEVICE_BM        = 0
FT_DEVICE_AM        = 1
FT_DEVICE_100AX     = 2
FT_DEVICE_UNKNOWN   = 3
FT_DEVICE_2232C     = 4
FT_DEVICE_232R      = 5
FT_DEVICE_2232H     = 6
FT_DEVICE_4232H     = 7
FT_DEVICE_232H      = 8
FT_DEVICE_X_SERIES  = 9
FT_DEVICE_4222H_0   = 10
FT_DEVICE_4222H_1_2 = 11
FT_DEVICE_4222H_3   = 12
FT_DEVICE_4222_PROG = 13
FT_DEVICE_900       = 14
FT_DEVICE_930       = 15
FT_DEVICE_UMFTPD3A  = 16
FT_DEVICE_2233HP    = 17
FT_DEVICE_4233HP    = 18
FT_DEVICE_2232HP    = 19
FT_DEVICE_4232HP    = 20
FT_DEVICE_233HP     = 21
FT_DEVICE_232HP     = 22
FT_DEVICE_2232HA    = 23
FT_DEVICE_4232HA    = 24
FT_DEVICE_232RN     = 25

_device_type_str = [
    "FT_DEVICE_BM",
    "FT_DEVICE_AM",
    "FT_DEVICE_100AX",
    "FT_DEVICE_UNKNOWN",
    "FT_DEVICE_2232C",
    "FT_DEVICE_232R",
    "FT_DEVICE_2232H",
    "FT_DEVICE_4232H",
    "FT_DEVICE_232H",
    "FT_DEVICE_X_SERIES",
    "FT_DEVICE_4222H_0",
    "FT_DEVICE_4222H_1_2",
    "FT_DEVICE_4222H_3",
    "FT_DEVICE_4222_PROG",
    "FT_DEVICE_900",
    "FT_DEVICE_930",
    "FT_DEVICE_UMFTPD3A",
    "FT_DEVICE_2233HP",
    "FT_DEVICE_4233HP",
    "FT_DEVICE_2232HP",
    "FT_DEVICE_4232HP",
    "FT_DEVICE_233HP",
    "FT_DEVICE_232HP",
    "FT_DEVICE_2232HA",
    "FT_DEVICE_4232HA",
    "FT_DEVICE_232RN",
]

def get_device_type_str(device_type):
    if device_type >= len(_device_status_str) or device_type < 0:
        return "unknown"
    return _device_type_str[device_type]

#---------------------------------------------------
# Bit Modes
#---------------------------------------------------
FT_BITMODE_RESET         = 0x00
FT_BITMODE_ASYNC_BITBANG = 0x01
FT_BITMODE_MPSSE         = 0x02
FT_BITMODE_SYNC_BITBANG  = 0x04
FT_BITMODE_MCU_HOST      = 0x08
FT_BITMODE_FAST_SERIAL   = 0x10
FT_BITMODE_CBUS_BITBANG  = 0x20
FT_BITMODE_SYNC_FIFO     = 0x40

#---------------------------------------------------
# Driver types
#---------------------------------------------------
FT_DRIVER_TYPE_D2XX = 0
FT_DRIVER_TYPE_VCP = 1

#---------------------------------------------------
# status
#---------------------------------------------------
last_status = FT_OK

def get_last_status():
    global last_status
    return last_status

def check_status(status):
    global last_status
    last_status = status
    if status != FT_OK:
        raise Exception(f"check status error. -> code:{get_device_status_str(status)}")

#---------------------------------------------------
# Functions
#---------------------------------------------------
def FT_Open(deviceNumber):
    dev_num = INT(deviceNumber)
    handle = FT_HANDLE()
    status = dll.FT_Open(dev_num, byref(handle))
    check_status(status)
    return handle.value

def FT_OpenEx(open_type, param):
    if open_type == FT_OPEN_BY_SERIAL_NUMBER:
        serial = (c_char * (len(param)))()
        serial.value = bytes(param,"utf-8")
        flags = DWORD(FT_OPEN_BY_SERIAL_NUMBER)
        handle = FT_HANDLE()
        status = dll.FT_OpenEx(serial, flags, byref(handle))
        check_status(status)
        return handle.value

    if open_type == FT_OPEN_BY_DESCRIPTION:
        desc = (c_char * (len(param)))()
        desc.value = bytes(param,"utf-8")
        flags = DWORD(FT_OPEN_BY_DESCRIPTION)
        handle = FT_HANDLE()
        status = dll.FT_OpenEx(byref(desc), flags, byref(handle))
        check_status(status)
        return handle.value

    if open_type == FT_OPEN_BY_LOCATION:
        loc = DWORD(param)
        flags = DWORD(FT_OPEN_BY_LOCATION)
        handle = FT_HANDLE()
        status = dll.FT_OpenEx(loc, flags, byref(handle))
        check_status(status)
        return handle.value

def FT_ListDevices(list_type, open_type, param):
    if list_type==FT_LIST_NUMBER_ONLY:
        num = DWORD()
        flags = DWORD(FT_LIST_NUMBER_ONLY)
        status = dll.FT_ListDevices(byref(num), None, flags)
        check_status(status)
        return num.value

    if list_type==FT_LIST_BY_INDEX:
        if open_type == FT_OPEN_BY_SERIAL_NUMBER:
            idx = PVOID(param)
            buf = BUF_16()
            flags = DWORD(FT_LIST_BY_INDEX | FT_OPEN_BY_SERIAL_NUMBER)
            status = dll.FT_ListDevices(idx, buf, flags)
            check_status(status)
            return buf.value.decode()

        if open_type == FT_OPEN_BY_DESCRIPTION:
            idx = PVOID(param)
            buf = BUF_64()
            flags = DWORD(FT_LIST_BY_INDEX | FT_OPEN_BY_DESCRIPTION)
            status = dll.FT_ListDevices(idx, buf, flags)
            check_status(status)
            return buf.value.decode()

        if open_type == FT_OPEN_BY_LOCATION:
            idx = PVOID(param)
            loc = DWORD()
            flags = DWORD(FT_LIST_BY_INDEX | FT_OPEN_BY_LOCATION)
            status = dll.FT_ListDevices(idx, byref(loc), flags)
            check_status(status)
            return loc.value

    # unfair!
    if list_type == FT_LIST_ALL:
        num = FT_ListDevices(FT_LIST_NUMBER_ONLY, None, None)
        data = []
        for i in range(num):
            data.append(FT_ListDevices(FT_LIST_BY_INDEX, open_type, i))
        return tuple(data)

def FT_Close(handle):
    hdl = FT_HANDLE(handle)
    status = dll.FT_Close(hdl)
    check_status(status)
    return None

def FT_Read(handle, size):
    hdl = FT_HANDLE(handle)
    buf = (c_char * size)()
    bytes_to_read = DWORD(size)
    bytes_returned = DWORD()
    status = dll.FT_Read(hdl, byref(buf), bytes_to_read, byref(bytes_returned))
    check_status(status)
    if bytes_returned.value == 0:
        # print("read:", size, 0) # debug
        return bytes()
    # print("read:", [f"0x{int(i):02x}" for i in buf[0:bytes_returned.value]]) # debug
    return bytes(buf[0:bytes_returned.value])

def FT_Write(handle, data:bytes):
    hdl = FT_HANDLE(handle)
    buf = c_char_p(data)
    bytes_to_write = DWORD(len(data))
    bytes_written = DWORD()
    status = dll.FT_Write(hdl, buf, bytes_to_write, byref(bytes_written))
    # print("write:", [f"0x{int(i):02x}" for i in data]) # debug
    check_status(status)
    return bytes_written.value

class OVERLAPPED_DUMMYSTRUCTNAME(Structure):
    _fields_ = [
        ("Offset", DWORD),
        ("OffsetHigh", DWORD)
    ]
class OVERLAPPED_DUMMYUNIONNAME(Union):
    _fields_= [
        ("NoName", OVERLAPPED_DUMMYSTRUCTNAME),
        ("Pointer", c_void_p)
    ]
class OVERLAPPED(Structure):
    _fields_ = [
        ("Internal", c_void_p),
        ("InternalHigh", c_void_p),
        ("NoName", OVERLAPPED_DUMMYUNIONNAME),
        ("hEvent", c_void_p)
    ]
def FT_IoCtl(handle, io_control_code, in_buf_size, out_data:bytes, event_handler):
    hdl = FT_HANDLE(handle)
    code = DWORD(io_control_code)
    in_buf = (c_char * in_buf_size)()
    in_size = DWORD(in_buf_size)
    out_buf = (c_char * len(out_data))
    out_size = DWORD(len(out_data))
    bytes_returned = DWORD()
    overlapped = OVERLAPPED(hEvent=event_handler)
    status = dll.FT_IoCtl(hdl, code, in_buf, in_size, out_buf, out_size, byref(bytes_returned), byref(overlapped))
    check_status(status)
    if bytes_returned.value == 0:
        return bytes()
    return bytes(out_buf.value[0:bytes_returned.value])

def FT_SetBaudRate(handle, baud_rate):
    hdl = FT_HANDLE(handle)
    rate = DWORD(baud_rate)
    status = dll.FT_SetBaudRate(hdl, rate)
    check_status(status)
    return None

def FT_SetDivisor(handle, divisor):
    hdl = FT_HANDLE(handle)
    div = USHORT(divisor)
    status = dll.FT_SetDivisor(hdl, div)
    check_status(status)
    return None

def FT_SetDataCharacteristics(handle, word_length, stop_bits, parity):
    hdl = FT_HANDLE(handle)
    leng = UCHAR(word_length)
    stop = UCHAR(stop_bits)
    prty = UCHAR(parity)
    status = dll.FT_SetDataCharacteristics(hdl, leng, stop, prty)
    check_status(status)
    return None

def FT_SetFlowControl(handle, flow_control, xon_char, xoff_char):
    hdl = FT_HANDLE(handle)
    flow = USHORT(flow_control)
    xon = UCHAR(xon_char)
    xoff = UCHAR(xoff_char)
    status = dll.FT_SetFlowControl(hdl, flow, xon, xoff)
    check_status(status)
    return None

def FT_ResetDevice(handle):
    hdl = FT_HANDLE(handle)
    status = dll.FT_ResetDevice(hdl)
    check_status(status)
    return None

def FT_SetDtr(handle):
    hdl = FT_HANDLE(handle)
    status = dll.FT_SetDtr(hdl)
    check_status(status)
    return None

def FT_ClrDtr(handle):
    hdl = FT_HANDLE(handle)
    status = dll.FT_ClrDtr(hdl)
    check_status(status)
    return None

def FT_SetRts(handle):
    hdl = FT_HANDLE(handle)
    status = dll.FT_SetRts(hdl)
    check_status(status)
    return None

def FT_ClrRts(handle):
    hdl = FT_HANDLE(handle)
    status = dll.FT_ClrRts(hdl)
    check_status(status)
    return None

def FT_GetModemStatus(handle):
    hdl = FT_HANDLE(handle)
    modem_status = ULONG()
    status = dll.FT_GetModemStatus(hdl, byref(modem_status))
    check_status(status)
    return modem_status.value

def FT_SetChars(handle, event_char, event_char_enable, error_char, error_char_enable):
    hdl = FT_HANDLE(handle)
    evnt = UCHAR(event_char)
    evnt_e = UCHAR(event_char_enable)
    err = UCHAR(error_char)
    err_e = UCHAR(error_char_enable)
    status = dll.FT_SetChars(hdl, evnt, evnt_e, err, err_e)
    check_status(status)
    return None

def FT_Purge(handle, mask):
    hdl = FT_HANDLE(handle)
    m = ULONG(mask)
    status = dll.FT_Purge(hdl, m)
    check_status(status)
    return None

def FT_SetTimeouts(handle, read_timeout, write_timeout):
    hdl = FT_HANDLE(handle)
    rt = ULONG(read_timeout)
    wt = ULONG(write_timeout)
    status = dll.FT_SetTimeouts(hdl, rt, wt)
    check_status(status)
    return None

def FT_GetQueueStatus(handle):
    hdl = FT_HANDLE(handle)
    rx_bytes = DWORD()
    status = dll.FT_GetQueueStatus(hdl, byref(rx_bytes))
    check_status(status)
    return rx_bytes.value

def FT_SetEventNotification(handle, mask, event_handler):
    hdl = FT_HANDLE(handle)
    m = DWORD(mask)
    eh = PVOID(event_handler)
    status = dll.FT_SetEventNotification(hdl, m, eh)
    check_status(status)
    return None

def FT_GetStatus(handle):
    hdl = FT_HANDLE(handle)
    rx_bytes = DWORD()
    tx_bytes = DWORD()
    event_dword = DWORD()
    status = dll.FT_GetStatus(hdl, byref(rx_bytes), byref(tx_bytes), byref(event_dword))
    check_status(status)
    return (rx_bytes.value, tx_bytes.value, event_dword.value)

def FT_SetBreakOn(handle, mask):
    hdl = FT_HANDLE(handle)
    status = dll.FT_SetBreakOn(hdl)
    check_status(status)
    return None

def FT_SetBreakOff(handle, mask):
    hdl = FT_HANDLE(handle)
    status = dll.FT_SetBreakOff(hdl)
    check_status(status)
    return None

def FT_SetWaitMask(handle, mask):
    hdl = FT_HANDLE(handle)
    m = DWORD(mask)
    status = dll.FT_SetWaitMask(hdl, m)
    check_status(status)
    return None

def FT_WaitOnMask(handle):
    hdl = FT_HANDLE(handle)
    mask = DWORD()
    status = dll.FT_WaitOnMask(hdl, byref(mask))
    check_status(status)
    return mask.value

def FT_GetEventStatus(handle):
    hdl = FT_HANDLE(handle)
    event_dword = DWORD()
    status = dll.FT_GetEventStatus(hdl, byref(event_dword))
    check_status(status)
    return event_dword.value

def FT_SetLatencyTimer(handle, latency):
    hdl = FT_HANDLE(handle)
    l = UCHAR(latency)
    status = dll.FT_SetLatencyTimer(hdl, l)
    check_status(status)
    return None

def FT_GetLatencyTimer(handle):
    hdl = FT_HANDLE(handle)
    latency = UCHAR()
    status = dll.FT_GetLatencyTimer(hdl, byref(latency))
    check_status(status)
    return latency.value

def FT_SetBitMode(handle, mask, enable):
    hdl = FT_HANDLE(handle)
    m = UCHAR(mask)
    e = UCHAR(enable)
    status = dll.FT_SetBitMode(hdl, m, e)
    check_status(status)
    return None

def FT_GetBitMode(handle):
    hdl = FT_HANDLE(handle)
    mode = UCHAR()
    status = dll.FT_GetBitMode(hdl, byref(mode))
    check_status(status)
    return mode.value

def FT_SetUSBParameters(handle, in_transfer_size, out_transfer_size):
    hdl = FT_HANDLE(handle)
    in_size = ULONG(in_transfer_size)
    out_size = ULONG(out_transfer_size)
    status = dll.FT_SetUSBParameters(hdl, in_size, out_size)
    check_status(status)
    return None

def FT_SetDeadmanTimeout(handle, deadman_timeout):
    hdl = FT_HANDLE(handle)
    deadman = ULONG(deadman_timeout)
    status = dll.FT_SetDeadmanTimeout(hdl, deadman)
    check_status(status)
    return None

def FT_SetVIDPID(handle, VID, PID):
    hdl = FT_HANDLE(handle)
    v = DWORD(VID)
    p = DWORD(PID)
    status = dll.FT_SetVIDPID(hdl, v, p)
    check_status(status)
    return None

def FT_GetVIDPID(handle):
    hdl = FT_HANDLE(handle)
    vid = DWORD()
    pid = DWORD()
    status = dll.FT_SetVIDPID(hdl, byref(vid), byref(pid))
    check_status(status)
    return (vid.value, pid.value)

def FT_GetDeviceLocId(handle):
    hdl = FT_HANDLE(handle)
    loc_id = DWORD(loc_id)
    status = dll.FT_GetDeviceLocId(hdl, byref(loc_id))
    check_status(status)
    return loc_id.value

def FT_GetDeviceInfo(handle):
    hdl = FT_HANDLE(handle)
    device = FT_DEVICE()
    id = DWORD()
    serial_number = CHAR_16()
    description = CHAR_64()
    dummy = PVOID()
    status = dll.FT_GetDeviceInfo(hdl, byref(device), byref(id), byref(serial_number), byref(description), dummy)
    check_status(status)
    return (device.value, id.value, serial_number.value.decode(), description.value.decode())

def FT_StopInTask(handle):
    hdl = FT_HANDLE(handle)
    status = dll.FT_StopInTask(hdl)
    check_status(status)
    return None

def FT_RestartInTask(handle):
    hdl = FT_HANDLE(handle)
    status = dll.FT_RestartInTask(hdl)
    check_status(status)
    return None

def FT_SetResetPipeRetryCount(handle, count):
    hdl = FT_HANDLE(handle)
    c = ULONG(count)
    status = dll.FT_SetResetPipeRetryCount(hdl, c)
    check_status(status)
    return None

def FT_ResetPort(handle):
    hdl = FT_HANDLE(handle)
    status = dll.FT_ResetPort(hdl)
    check_status(status)
    return None

def FT_CyclePort(handle):
    hdl = FT_HANDLE(handle)
    status = dll.FT_CyclePort(hdl)
    check_status(status)
    return None

class FT_DEVICE_LIST_INFO_NODE(Structure):
    _fields_ = [
        ("Flags", ULONG),
        ("Type", ULONG),
        ("ID", ULONG),
        ("LocId", DWORD),
        ("SerialNumber", CHAR_16),
        ("Description", CHAR_64),
        ("ftHandle",FT_HANDLE)
    ]

# Device information flags
FT_FLAGS_OPENED = 1
FT_FLAGS_HISPEED = 2

def get_device_information_flags_str(flags):
    s = "unknown"
    opend = (flags & FT_FLAGS_OPENED) != 0
    hispeed = (flags & FT_FLAGS_HISPEED) != 0
    if opend and not hispeed:
        s = "FT_FLAGS_OPENED"
    if not opend and hispeed:
        s = "FT_FLAGS_HISPEED"
    if opend and hispeed:
        s = "FT_FLAGS_OPENED | FT_FLAGS_HISPEED"
    return s

def FT_CreateDeviceInfoList():
    num = DWORD()
    status = dll.FT_CreateDeviceInfoList(byref(num))
    check_status(status)
    return num.value

def FT_GetDeviceInfoList(number_devs):
    num = DWORD(number_devs)
    dest = (FT_DEVICE_LIST_INFO_NODE * number_devs)()
    status = dll.FT_GetDeviceInfoList(dest, byref(num))
    check_status(status)
    ret = []
    for i in range(number_devs):
        ret.append((dest[i].Flags, dest[i].Type, dest[i].ID, dest[i].LocId, dest[i].SerialNumber.decode(), dest[i].Description.decode(), dest[i].ftHandle))
    return tuple(ret)

def FT_GetDeviceInfoDetail(index):
    idx = DWORD(index)
    flg = DWORD()
    typ = DWORD()
    id  = DWORD()
    loc = DWORD()
    srl = CHAR_16()
    dsc = CHAR_64()
    hdl = FT_HANDLE()
    status = dll.FT_GetDeviceInfoDetail(idx, byref(flg), byref(typ), byref(id), byref(loc), byref(srl), dsc, hdl)
    check_status(status)
    return (flg.value, typ.value, id.value, loc.value, srl.value.decode(), dsc.value.decode(), hdl.value)

def FT_GetDriverVersion(handle):
    hdl = FT_HANDLE(handle)
    version = DWORD()
    status = dll.FT_GetDriverVersion(hdl, byref(version))
    check_status(status)
    return version.value

def FT_GetLibraryVersion():
    version = DWORD()
    status = dll.FT_GetLibraryVersion(byref(version))
    check_status(status)
    return version.value

def FT_Rescan():
    status = dll.FT_Rescan()
    check_status(status)
    return None

def FT_Reload(vid, pid):
    v = WORD(vid)
    p = WORD(pid)
    status = dll.FT_Reload(v, p)
    check_status(status)
    return None

def FT_GetComPortNumber(handle):
    hdl = FT_HANDLE(handle)
    com_port_number = LONG()
    status = dll.FT_GetComPortNumber(hdl, byref(com_port_number))
    check_status(status)
    return com_port_number.value
