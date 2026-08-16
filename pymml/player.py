from .controller.controller_base import ControllerBase
from .controller.controller_util import controller_type_to_cls
from .controller.sweep import Sweep
from .controller.portamento import Portamento
from .chip.chip_utils import chip_type_to_cls
from .device.device_util import device_type_to_cls
from .command import *
from .define import ORIGIN_SEQUENCE_ID, OP_NUM, ModifyValue, ModifyType
import time
import copy

def print_grid_right(lines):
    width = [0] * len(lines[0].split(','))
    for line in lines:
        cells = line.split(',')
        for i in range(len(cells)):
            width[i] = max(width[i], len(cells[i]))

    for line in lines:
        cells = line.split(',')
        s = ""
        for i in range(len(cells)):
            s += " " * (width[i] - len(cells[i]))
            s += cells[i]
            s += "  "
        print(s)

class MasterWork:
    def __init__(self):
        self.master_volume = VariableValue(0,127)
        self.reset()

    def reset(self):
        self.master_volume.reset()
    
    def tick_reset(self):
        self.master_volume.tick_reset()

    def print_debug(self):
        print("MasterWork")
        lines = ["," + VariableValue.get_status_head()]
        lines.append("master_volume," + self.master_volume.get_status())
        print_grid_right(lines)

class ChannelWork:
    def __init__(self, no=0):
        self.no = no
        self.tone_id = ""
        self.note   = VariableValue()
        self.volume = VariableValue()
        self.pan    = VariableValue()
        self.detune = VariableValue()
        self.octave = VariableValue()
        self.mute   = VariableValue(0,1,0)
        self.controller = {}
        self.signature = [SignatureType.NONE] * 12
        self.mapper = {} # key=id  value=enable
        self.reset()
        self.tick_count = 0 # debug

    def print_debug(self):
        print("ChannelWork")
        print(f"no: {self.no}")
        print(f"tone_id: {self.tone_id}")
        print(f"signature: {self.signature}")
        print(f"key_sw: {self.key_sw}")
        print(f"flg_key_on: {self.flg_key_on}")
        print(f"flg_key_off: {self.flg_key_off}")
        print(f"flg_tone: {self.flg_tone}")
        print(f"contoller: {[*self.controller.keys()]}")
        print(f"mapper: {[*self.mapper.keys()]}")
        lines = ["," + VariableValue.get_status_head()]
        lines.append("octave," + self.octave.get_status())
        lines.append("note," + self.note.get_status())
        lines.append("volume," + self.volume.get_status())
        lines.append("detune," + self.detune.get_status())
        lines.append("pan," + self.pan.get_status())
        lines.append("mute," + self.mute.get_status())
        print_grid_right(lines)

    def reset(self):
        self.key_sw = [False] * OP_NUM # True=on  False=off
        self.flg_key_on = [False] * OP_NUM
        self.flg_key_off = [False] * OP_NUM
        self.flg_tone = False
        self.note.reset()
        self.volume.reset()
        self.pan.reset()
        self.detune.reset()
        self.octave.reset()
        self.mute.reset()
        for ctrl in self.controller.values():
            ctrl.reset()
        for i in range(len(self.signature)):
            self.signature[i] = SignatureType.NONE

    def tick_reset(self):
        for i in range(OP_NUM):
            self.flg_key_on[i] = False
            self.flg_key_off[i] = False
        self.flg_tone = False
        self.note.tick_reset()
        self.volume.tick_reset()
        self.pan.tick_reset()
        self.detune.tick_reset()
        self.octave.tick_reset()
        self.mute.tick_reset()

    def set_key_on(self, op_list=[True]*OP_NUM):
        for i in range(len(op_list)):
            if op_list[i]:
                self.key_sw[i] = True
                self.flg_key_on[i] = True

    def set_key_off(self, op_list=[True]*OP_NUM):
        for i in range(len(op_list)):
            if op_list[i]:
                self.key_sw[i] = False
                self.flg_key_off[i] = True

    def get_key_on(self, op_list=[True]*OP_NUM):
        flg = False
        for i in range(len(op_list)):
            if op_list[i]:
                flg |= self.key_sw[i]
        return flg

    def get_key_off(self, op_list=[True]*OP_NUM):
        flg = False
        for i in range(len(op_list)):
            if op_list[i]:
                flg |= not self.key_sw[i]
        return flg

    def get_key_on_edge(self, op_list=[True]*OP_NUM):
        flg = False
        for i in range(len(op_list)):
            if op_list[i]:
                flg |= self.key_sw[i] and self.flg_key_on[i]
        return flg

    def get_key_off_edge(self, op_list=[True]*OP_NUM):
        flg = False
        for i in range(len(op_list)):
            if op_list[i]:
                flg |= not self.key_sw[i] and self.flg_key_off[i]
        return flg

    def set_tone_id(self, tone_id):
        self.flg_tone = self.tone_id != tone_id
        self.tone_id = tone_id

    def get_note(self):
        note = self.note.get_value() + self.octave.get_value() * 12
        return self.get_map_note2(note)

    def get_oct_key(self):
        note = self.get_note()
        oct = note // 12
        key = note % 12
        return oct, key

    def proc_controller(self):
        for ctrl in self.controller.values():
            if ctrl.enable == False:
                continue

            ctrl.tick(self)
            value = ctrl.get_output_value()

            if ctrl.modify_value == ModifyValue.NOTE:
                if type(ctrl) == Portamento:
                    vv = self.detune
                else:
                    vv = self.note
            elif ctrl.modify_value == ModifyValue.VOLUME:
                vv = self.volume
            elif ctrl.modify_value == ModifyValue.PAN:
                vv = self.pan
            elif ctrl.modify_value == ModifyValue.PITCH:
                vv = self.detune

            if ctrl.modify_type == ModifyType.CURRENT:
                vv.set_value(VariableValue.CURRENT, value)
            elif ctrl.modify_type == ModifyType.RELATIVE:
                vv.set_value(VariableValue.RELATIVE3, vv.relative3 + value)
            elif ctrl.modify_type == ModifyType.MULTIPLE:
                vv.set_value(VariableValue.MULTIPLE3, vv.multiple3 * value)

    def get_map_note2(self, note1):
        for map in self.mapper.values():
            if map.enable == True:
                if map.mode == MapperMode.DRUM:
                    note2 = map.note2(note1)
                    if note2 is not None:
                        return note2
        return note1
    
    def get_map_seq_id(self):
        for map in self.mapper.values():
            if map.enable == True:
                note1 = self.note.get_value() + self.octave.get_value() * 12
                seq_id = map.seq_id(note1)
                if seq_id is not None:
                    return seq_id
        return None
                
class VariableValue:
    RESET     = "RESET"
    CURRENT   = "CURRENT"
    RELATIVE0 = "RELATIVE0" # 累積  current指定で0
    RELATIVE1 = "RELATIVE1" # 相対1 弱相対
    RELATIVE2 = "RELATIVE2" # 相対2 強相対
    RELATIVE3 = "RELATIVE3" # コントローラー
    MULTIPLE1 = "MULTIPLE1" # 倍率1 弱倍率
    MULTIPLE2 = "MULTIPLE2" # 倍率2 強倍率
    MULTIPLE3 = "MULTIPLE3" # コントローラー
    GAMMA     = "GAMMA"

    def __init__(self, current=0, max=1, min=0):
        self.init(current, max, min)

    def init(self, current, max, min):
        self.current = current
        self.max = max
        self.min = min
        self.reset()
        self.back_value = current

    def reset(self):
        self.back_value = 0
        self.relative0 = 0
        self.relative1 = 0
        self.relative2 = 0
        self.relative3 = 0
        self.multiple1 = 1.0
        self.multiple2 = 1.0
        self.multiple3 = 1.0
        self.gamma = 1.0

    @staticmethod
    def get_status_head():
        s = "value,"
        s += "back_value,"
        s += "max,"
        s += "min,"
        s += "current,"
        s += "relative0,"
        s += "relative1,"
        s += "relative2,"
        s += "relative3,"
        s += "multiple1,"
        s += "multiple2,"
        s += "multiple3,"
        s += "gamma"
        return s

    def get_status(self):
        s = f"{self.get_value()},"
        s += f"{self.back_value},"
        s += f"{self.max},"
        s += f"{self.min},"
        s += f"{self.current},"
        s += f"{self.relative0},"
        s += f"{self.relative1},"
        s += f"{self.relative2},"
        s += f"{self.relative3},"
        s += f"{self.multiple1},"
        s += f"{self.multiple2},"
        s += f"{self.multiple3},"
        s += f"{self.gamma}"
        return s

    def tick_reset(self):
        self.back_value = self.get_value()
        self.relative3 = 0
        self.multiple3 = 1.0

    def is_change(self):
        return self.back_value != self.get_value()

    def get_value(self):
        v = self.current + self.relative0 + self.relative1 + self.relative3
        v *= self.multiple1
        v *= self.multiple3
        if self.gamma != 1.0:
            v *= ((v - self.min) / (self.max - self.min)) ** self.gamma
        v += self.relative2
        v *= self.multiple2
        v = int(v)
        v = max(self.min, v)
        v = min(self.max, v)
        return v

    def set_value(self, value_type, value):
        value_type = value_type.strip().upper()
        if value_type == VariableValue.RESET:
            self.reset()
        elif value_type == VariableValue.CURRENT:
            self.current = int(value)
            self.current = max(self.current, self.min)
            self.current = min(self.current, self.max)
            self.relative0 = 0
            self.relative1 = 0
            self.multiple1 = 1.0
        elif value_type == VariableValue.RELATIVE0:
            iv = int(value)
            if iv == 0:
                self.relative0 = 0
            else:
                self.relative0 += iv
                self.relative0 = max(self.relative0, -self.max)
                self.relative0 = min(self.relative0, self.max)
        elif value_type == VariableValue.RELATIVE1:
            self.relative1 = int(value)
            self.relative1 = max(self.relative1, -self.max)
            self.relative1 = min(self.relative1, self.max)
        elif value_type == VariableValue.RELATIVE2:
            self.relative2 = int(value)
            self.relative2 = max(self.relative2, -self.max)
            self.relative2 = min(self.relative2, self.max)
        elif value_type == VariableValue.RELATIVE3:
            self.relative3 = int(value)
            self.relative3 = max(self.relative3, -self.max)
            self.relative3 = min(self.relative3, self.max)
        elif value_type == VariableValue.MULTIPLE1:
            self.multiple1 = max(float(value), 0.0)
        elif value_type == VariableValue.MULTIPLE2:
            self.multiple2 = max(float(value), 0.0)
        elif value_type == VariableValue.MULTIPLE3:
            self.multiple3 = max(float(value), 0.0)
        elif value_type == VariableValue.GAMMA:
            self.gamma = min(float(value), 0.0)

class Quontize:
    def __init__(self):
        self.shave = 0
        self.leave = 1
        self.ratio = 1.0

    def get_note_rest_tick(self, tick):
        rest = tick * (1.0 - self.ratio) + self.shave
        note = tick - rest
        if note < self.leave:
            note = self.leave
            rest = tick - note
        return int(note), int(rest)

    def __str__(self):
        return f"{self.shave},{self.leave},{self.ratio}"

class SequenceData:
    def __init__(self, id, data):
        self.id = id
        self.data = data
        self.mute = False

    def __str__(self):
        return f"{self.id},{self.mute},{len(self.data)}"

class CallStackData:
    def __init__(self, seq_id="", seq_index=-1):
        self.seq_id = seq_id
        self.seq_index = seq_index

    def __str__(self):
        return f"{self.seq_id},{self.seq_index}"

class LoopStackData:
    def __init__(self, begin=-1, end=-1, left=0):
        self.begin = begin
        self.end = end
        self.left = left

    def __str__(self):
        return f"{self.begin},{self.end},{self.left}"

class TrackingData:
    serial_number_counter = 0
    def __init__(self, id=""):
        self.terminated = False
        self.mute = False

        self.system_id = None
        self.device_port = 0
        self.chip_no = 0
        self.ch_no = -1
        self.priority = 0
        self.serial_number = TrackingData.serial_number_counter
        TrackingData.serial_number_counter += 1
        # if TrackingData.serial_number_source >= 999999:
        #     TrackingData.serial_number_source = 0

        self.seq_id = ""
        self.seq_index = 0 # seq内index
        self.tick_count = 0 # 残りtick
        self.quantize = Quontize()
        self.omi_length = 4
        self.omi_dot    = 0
        self.omi_tick   = 0
        self.p_note = -1
        self.p_sig = SignatureType.NONE
        self.p_oct = 0
        self.operator = [1] * OP_NUM # index0~n-1=op1～n 1=use  0=notuse

        self.loop_stack = [] # LoopStackData
        self.call_stack = [] # CallStackData
        self.loop_inf_flg = False
        self.loop_inf_seq_id = ""
        self.loop_inf_seq_index = 0

        self.id = id
        self.tick_begin = 0
        self.tick_end = 0 # loop_infinityまで
        self.tick_loop_inf = -1
        self.stopwatch = {}

    @staticmethod
    def copy_from(other):
        trk = TrackingData()
        trk.mute = other.mute
        trk.system_id = other.system_id
        trk.device_port = other.device_port
        trk.chip_no = other.chip_no
        trk.ch_no = other.ch_no
        trk.priority = other.priority
        trk.quantize.shave = other.quantize.shave
        trk.quantize.leave = other.quantize.leave
        trk.quantize.ratio = other.quantize.ratio
        trk.omi_length = other.omi_length
        trk.omi_dot    = other.omi_dot
        trk.omi_tick   = other.omi_tick
        trk.p_note = other.p_note
        trk.p_sig  = other.p_sig
        trk.p_oct  = other.p_oct
        return trk

    def __lt__(self, other):
        if self.system_id != other.system_id:
            return self.system_id < other.system_id
        elif self.device_port != other.device_port:
            return self.device_port < other.device_port
        elif self.chip_no != other.chip_no:
            return self.chip_no < other.chip_no
        elif self.ch_no != other.ch_no:
            return self.ch_no < other.ch_no
        elif self.priority != other.priority:
            return self.priority > other.priority
        else:
            return self.serial_number < other.serial_number

    def __str__(self):
        return f"{self.terminated},{self.system_id},{self.device_port},{self.chip_no},{self.ch_no},{self.seq_id},{self.seq_index},{self.priority},{self.serial_number},{self.tick_count},{self.quantize},{self.omi_length},{self.omi_dot},{self.omi_tick},{self.loop_inf_flg},{self.loop_inf_seq_id},{self.loop_inf_seq_index}"

class PlayerStatus:
    PLAY = "PLAY"
    STOP = "STOP"
    PAUSE = "PAUSE"

    def __init__(self):
        self.whole_note_ticks = 192
        self.bar_ticks = 192
        self.tempo = VariableValue(120,480,1)
        self.status = PlayerStatus.STOP
        self.tick_total = 0
        self.tick = 0
        self.bar = 0
        self.info = {}

    def get_tick_time(self):
        # 60 / tempo / (whole_note_ticks / 4) = 240 / tempo / whole_note_ticks
        return 240 / self.tempo.get_value() / self.whole_note_ticks # [sec]

    def set_status(self, status):
        self.status = status

    def reset_bar(self):
        self.tick = 0
        self.bar = 0

    def increment(self, add_tick=1):
        if self.status == PlayerStatus.PLAY:
            key = (self.tempo.get_value(), self.whole_note_ticks)
            if key not in self.info.keys():
                self.info[key] = 0
            self.info[key] += add_tick
            self.tick_total += add_tick
            self.tick += add_tick
            if self.tick >= self.bar_ticks:
                self.bar += self.tick // self.bar_ticks
                self.tick = self.tick % self.bar_ticks

    def get_playing_time(self):
        sec = 0
        for key,val in self.info.items():
            sec += 240 / key[0] / key[1] * val
        return sec

    def print_debug(self):
        print("status,tempo,bar_ticks,tick_total,bar,tick,playing_time")
        print(f"{self.status},{self.tempo.get_value()},{self.bar_ticks},{self.tick_total},{self.bar},{self.tick},{self.get_playing_time():.3f}")

class ControllerManager:
    DEFAULT_PORTAMENT_ID = "DEFAULT_PORTAMENT_ID"

    def __init__(self):
        self.obj_dic = {}
        self.add(CommandControllerData(self.DEFAULT_PORTAMENT_ID, ControllerType.SWEEP, "PITCH RELATIVE 0 1 0"))

    def add(self, cmd):
        obj = controller_type_to_cls(cmd.controller_type)()
        obj.set_value_list(cmd.data)
        self.obj_dic[cmd.id] = obj

    def get(self, ctrl_id):
        if ctrl_id not in self.obj_dic.keys():
            raise Exception(f"Controller ID is not defined. -> {ctrl_id}")
        return copy.copy(self.obj_dic[ctrl_id])

class MapperManager:
    class Data:
        def __init__(self, mode, map_id, enable, seq_id_list, note2_list):
            self.mode = mode
            self.map_id = map_id
            self.enable = enable
            self.seq_id_list = seq_id_list
            self.note2_list = note2_list

        def seq_id(self, note1):
            if 0 <= note1 and note1 <= 127:
                return self.seq_id_list[note1]
            return None

        def note2(self, note1):
            if 0 <= note1 and note1 <= 127:
                return self.note2_list[note1]
            return None

    def __init__(self):
        self.data_dic = {}

    def add(self, cmd:CommandMapperData):
        seq_id_list = [None] * 128
        ntoe2_list = [None] * 128
        items = cmd.data.split(' ')
        for i in range(0,len(items),3):
            note1 = int(items[i])
            note2 = int(items[i + 1])
            seq_id = items[i + 2]
            if cmd.mode == MapperMode.MAPPER:
                for note in range(note1, note2 + 1):
                    if 0 <= note and note <= 127:
                        seq_id_list[note] = seq_id
                ntoe2_list[note1] = int(note2)
            if cmd.mode == MapperMode.DRUM:
                if 0 <= note1 and note1 <= 127:
                    if 0 <= note2 and note2 <= 127:
                        seq_id_list[note1] = seq_id
                        ntoe2_list[note1] = int(note2)
        self.data_dic[cmd.id] = MapperManager.Data(cmd.mode, cmd.id, False, seq_id_list, ntoe2_list)

    def get(self, map_id):
        if map_id not in self.data_dic.keys():
            raise Exception(f"not define map_id. -> {map_id}")
        return copy.copy(self.data_dic[map_id])

class SystemManager:
    class Info:
        def __init__(self, device_type, device_id, chip_type_list):
            self.device_type = device_type
            self.device_id = device_id
            self.chip_type_list = chip_type_list # ネストしたリスト
        def chip_num(self, device_port):
            return len(self.chip_type_list[device_port])
        def chip_type(self, device_port, chip_no):
            return self.chip_type_list[device_port][chip_no]
    
    class Data:
        def __init__(self, sys_id, device_port, chip_no, chip_obj, device_obj):
            self.sys_id = sys_id
            self.device_port = device_port
            self.chip_no = chip_no
            self.device_obj = device_obj
            self.chip_obj = chip_obj
            self.master_work = MasterWork()
            self.channel_work = [ChannelWork(ch_no) for ch_no in range(self.chip_obj.CHANNEL_NUMBER)]
            self.reg_buf = []
            self.prm_buf = []
            self.send_buf = []

    def __init__(self, tick_count_mode):
        self.info = {}    # sys_id
        self.devobj_dic = {} # devobj_id  device_type/device_id
        self.data = {}    # data_id device_type/device_id/device_port/chip_no
        self.tick_count_mode = tick_count_mode

    def add(self, sys_id, device_type, device_id, chip_type_list):
        if sys_id not in self.info.keys():
            device_cls = device_type_to_cls(device_type)
            if len(chip_type_list) != device_cls.PORT_NUM:
                raise Exception(f"not match port_num ->  sys_id:{sys_id}  device_type:{device_type}")
            self.info[sys_id] = SystemManager.Info(device_type, device_id, chip_type_list)

    def _get_device_obj_id(self, sys_id):
        return f"{self.info[sys_id].device_type}/{self.info[sys_id].device_id}"

    def _get_data_id(self, sys_id, device_port, chip_no):
        return f"{self.info[sys_id].device_type}/{self.info[sys_id].device_id}/{device_port}/{chip_no}"

    def open(self, sys_id, device_port, chip_no):
        if sys_id not in self.info.keys():
            raise Exception(f"unknown system id -> {sys_id}")
        info = self.info[sys_id]

        devobj_id = self._get_device_obj_id(sys_id)
        if devobj_id not in self.devobj_dic.keys():
            dev_obj = device_type_to_cls(info.device_type)()
            if not self.tick_count_mode:
                dev_obj.open(info.device_id)
                if dev_obj.opend == False:
                    raise Exception(f"failed open device -> sys_id:{sys_id}  device_type:{info.device_type}  device_id:{info.device_id}")
            else:
                dev_obj.device_id = info.device_id # 表示用にidだけ代入
            self.devobj_dic[devobj_id] = dev_obj
        else:
            dev_obj = self.devobj_dic[devobj_id]
        
        data_id = self._get_data_id(sys_id, device_port, chip_no)
        if data_id not in self.data.keys():
            chip_obj = chip_type_to_cls(info.chip_type(device_port, chip_no))()
            dat = SystemManager.Data(sys_id, device_port, chip_no, chip_obj, dev_obj)
            if not self.tick_count_mode:
                dat.chip_obj.send_init(dev_obj)
            dat.chip_obj.setup_master_work(dat.master_work)
            dat.master_work.reset()
            for cw in dat.channel_work:
                dat.chip_obj.setup_channel_work(cw)
            self.data[data_id] = dat

    def close_all(self):
        for dat in self.data.values():
            if dat.device_obj.is_open():
                dat.chip_obj.send_init(dat.device_obj)
                dat.device_obj.close()
        self.data.clear()

    def _data_id(self, trk):
        data_id = self._get_data_id(trk.system_id, trk.device_port, trk.chip_no)
        if data_id not in self.data.keys():
            raise Exception(f"Not registered data_id -> {data_id}")
        return data_id

    def device_obj(self, trk):
        data_id = self._data_id(trk)
        return self.data[data_id].device_obj

    def chip_obj(self, trk):
        data_id = self._data_id(trk)
        return self.data[data_id].chip_obj

    def master_work(self, trk):
        data_id = self._data_id(trk)
        return self.data[data_id].master_work

    def channel_work(self, trk, ch_no=None):
        if ch_no is None:
            ch_no = trk.ch_no
        if trk.ch_no < 0:
            raise Exception(f"Not assigned channel number -> trk:{trk.id}  seq:{trk.seq_id}")
        data_id = self._data_id(trk)
        return self.data[data_id].channel_work[ch_no]

    def add_reg(self, trk, address, data):
        data_id = self._data_id(trk)
        self.data[data_id].reg_buf.append((address, data))
    
    def add_prm(self, trk, parameter, value):
        data_id = self._data_id(trk)
        self.data[data_id].prm_buf.append((parameter, value))

    def prepare_send(self):
        for sd in self.data.values():
            # controller process
            for cw in sd.channel_work:
                cw.proc_controller()

            # work to parameter
            prm_list = sd.chip_obj.master_work_to_prm(sd.master_work)
            for cw in sd.channel_work:
                prm_list.extend(sd.chip_obj.channel_work_to_prm(cw))
                prm_list.extend(sd.prm_buf)

            # parameter to register
            for prm in prm_list:
                sd.chip_obj.write_parameter(prm[0], prm[1])

            # get register list
            sd.send_buf = sd.chip_obj.get_reg_list()
            sd.send_buf.extend(sd.reg_buf)
            for reg in sd.send_buf:
                sd.chip_obj.write_register(reg[0], reg[1])

    def send_register(self):
        for sd in self.data.values():
            sd.chip_obj.send_register(sd.device_obj, sd.send_buf)

    def tick_reset(self):
        for sd in self.data.values():
            sd.chip_obj.tick_reset()
            sd.master_work.tick_reset()
            for cw in sd.channel_work:
                cw.tick_reset()
            sd.reg_buf.clear()
            sd.prm_buf.clear()
            sd.send_buf.clear()

class Player:
    def __init__(self):
        self.tick_count_mode = False

    def tick_count(self, song):
        self.tick_count_mode = True
        self.play(song)
        self.tick_count_mode = False

    def stop(self):
        if hasattr(self, "sysmng") and hasattr(self, "status"):
            self.status.set_status(PlayerStatus.STOP)
            self.sysmng.close_all()

    def play(self, song):
        self.sysmng = SystemManager(self.tick_count_mode)
        self.ctlrmng = ControllerManager()
        self.mapmng = MapperManager()
        self.status = PlayerStatus()

        self.seq_dic = {}
        for seq_id,seq_data in song.seq_dic.items():
            self.seq_dic[seq_id] = SequenceData(seq_id, seq_data)

        trk = TrackingData("ORIGIN")
        trk.seq_id = ORIGIN_SEQUENCE_ID
        self.trk_list = [trk]
        self.report_trk_list = []
        self.report_trk_list.append(trk)

        self.status.set_status(PlayerStatus.PLAY)
        self.wait_time = 0.0

        # time_wait_back = time.perf_counter() # debug
        back_time = time.perf_counter()

        while len(self.trk_list) > 0:
            # time_start = time.perf_counter() # debug

            if self.status.status == PlayerStatus.PAUSE:
                time.sleep(16)
                continue
            if self.status.status != PlayerStatus.PLAY:
                break

            self.wait_time = 0.0

            # tracking process
            self.trk_list.sort()
            trk_idx = 0
            trk_size = 0
            while trk_size != len(self.trk_list):
                trk_size = len(self.trk_list)
                for trk in self.trk_list[trk_idx:]:
                    trk_idx += 1
                    self.proc_command(trk)
            
            # delete terminated track
            for trk in reversed(self.trk_list):
                if trk.terminated:
                    self.trk_list.remove(trk)

            if self.tick_count_mode:
                self.status.increment()
                continue

            self.sysmng.prepare_send()

            # time_track = time.perf_counter() # debug

            # wait
            next = back_time + self.status.get_tick_time() + self.wait_time
            while time.perf_counter() <= next:
                pass
            over = (time.perf_counter() - next) * 1000
            if over < 0.33:
                back_time = next
            else:
                # print(f"over {over:0.9f}") # debug
                back_time = time.perf_counter()

            # time_wait = time.perf_counter() # debug

            self.sysmng.send_register()

            # reset every tick
            self.sysmng.tick_reset()

            # status
            self.status.increment()

            # print(f"trak {(time_track-time_start)*1000:0.9f}") # debug
            # print(f"wait {(time_wait-time_track)*1000:0.9f}") # debug
            # print(f"fram {(time_wait-time_wait_back)*1000:0.9f}") # debug
            # print() # debug
            # time_wait_back = time_wait # debug
            # print("-----------------------------------------") # debug

        if self.tick_count_mode:
            self.print_report_trk()
        self.stop()

    def decode_tadpole_tick(self, cmd, trk):
        if cmd.omission > 0:
            length = trk.omi_length
            dot    = trk.omi_dot + cmd.dot
            tick   = trk.omi_tick
        else:
            length = cmd.length
            dot    = cmd.dot
            tick   = cmd.tick
        if tick == 0:
            if self.status.whole_note_ticks % length != 0:
                ht = self.status.whole_note_ticks
                print(f"The length of the note is not divisible.\nwhole_note_ticks/tadpole = {ht}/{cmd.length} = {ht/cmd.length}")
                self.status.print_bar()
            tick = int(self.status.whole_note_ticks / length)
            tick_dot = tick
            while dot > 0:
                if tick % 2 != 0:
                    ht = self.status.whole_note_ticks
                    print(f"The length of the dotnote is not divisible.\ntick/2 = {tick}/2 = {tick/2}")
                    self.status.print_bar()
                tick_dot = int(tick_dot / 2)
                tick += tick_dot
                dot -= 1
        return tick

    def decode_tadpole(self, cmd, trk):
        def note_add_sig(note, sig):
            if sig == SignatureType.NONE:
                sig2 = self.sysmng.channel_work(trk).signature[cmd.note % 12]
                if sig2 != SignatureType.NONE:
                    note = note_add_sig(note, sig2)
            elif sig == SignatureType.SHARP:
                note += 1
            elif sig == SignatureType.DOUBLE_SHARP:
                note += 2
            elif sig == SignatureType.FLAT:
                note -= 1
            elif sig == SignatureType.NATURAL:
                pass
            return note

        tick = self.decode_tadpole_tick(cmd, trk)
        if cmd.note < 0:
            note = -1
        else:
            note = note_add_sig(cmd.note, cmd.signature)

        cmd_list = []
        if cmd.key_on==1 and cmd.key_off==1:
            tick_on, tick_off = trk.quantize.get_note_rest_tick(tick)
            if note >= 0:
                cmd_list.append(CommandNote(VariableValue.CURRENT, note))
            cmd_list.append(CommandKeyOn())
            cmd_list.append(CommandTick(tick_on))
            cmd_list.append(CommandKeyOff())
            if tick_off > 0:
                cmd_list.append(CommandTick(tick_off))

        elif cmd.key_on==0 and cmd.key_off==1:
            tick_on, tick_off = trk.quantize.get_note_rest_tick(tick)
            if note >= 0:
                cmd_list.append(CommandNote(VariableValue.CURRENT, note))
            cmd_list.append(CommandTick(tick_on))
            cmd_list.append(CommandKeyOff())
            if tick_off > 0:
                cmd_list.append(CommandTick(tick_off))
        
        elif cmd.key_on==1 and cmd.key_off==0:
            if note >= 0:
                cmd_list.append(CommandNote(VariableValue.CURRENT, note))
            cmd_list.append(CommandKeyOn())
            cmd_list.append(CommandTick(tick))

        elif cmd.key_on==0 and cmd.key_off==0:
            if note >= 0:
                cmd_list.append(CommandNote(VariableValue.CURRENT, note))
            cmd_list.append(CommandTick(tick))

        if trk.p_note >= 0:
            now_oct = self.sysmng.channel_work(trk).octave.get_value()
            from_note = note_add_sig(trk.p_note, trk.p_sig) + (now_oct - trk.p_oct) * 12
            to_note = note + now_oct * 12
            cent = (to_note - from_note) * 100
            if abs(cent) > tick:
                volume_ini = cent - cent % tick
                volume = cent // tick
                step = 1
            else:
                volume_ini = cent
                volume = 1 if cent > 0 else -1
                step = tick // abs(cent)
            cmd_list.insert(1, CommandController(ControllerManager.DEFAULT_PORTAMENT_ID, Sweep.Parameter.ENABLE, "1"))
            cmd_list.insert(2, CommandController(ControllerManager.DEFAULT_PORTAMENT_ID, Sweep.Parameter.VOLUME_INI, str(-volume_ini)))
            cmd_list.insert(3, CommandController(ControllerManager.DEFAULT_PORTAMENT_ID, Sweep.Parameter.STEP, str(step)))
            cmd_list.insert(4, CommandController(ControllerManager.DEFAULT_PORTAMENT_ID, Sweep.Parameter.VOLUME, str(volume)))
            cmd_list.insert(5, CommandController(ControllerManager.DEFAULT_PORTAMENT_ID, Sweep.Parameter.RESET, ""))
            cmd_list.append(   CommandController(ControllerManager.DEFAULT_PORTAMENT_ID, Sweep.Parameter.ENABLE, "0"))
            trk.p_note = -1

        return cmd_list

    def proc_command(self, trk):
        if trk.tick_count > 0:
            trk.tick_count -= 1
            return

        while True:
            seq = self.seq_dic[trk.seq_id]
            cmd = seq.data[trk.seq_index]
            cls = type(cmd)

            #---------------------------------------------------------
            if cls == CommandRegister:
                self.sysmng.add_reg(trk, cmd.address, cmd.data)

            elif cls == CommandParameter:
                self.sysmng.add_prm(trk, cmd.parameter, cmd.value)

            #---------------------------------------------------------
            elif cls == CommandTick:
                trk.tick_count = cmd.value - 1
                if trk.tick_count >= 0:
                    trk.seq_index += 1
                    break
    
            elif cls == CommandRest:
                tick = self.decode_tadpole_tick(cmd, trk)
                seq.data[trk.seq_index] = CommandTick(tick)
                continue

            elif cls == CommandWait:
                start = time.perf_counter()
                time.sleep(cmd.value / 1000)
                self.wait_time += time.perf_counter() - start

            #---------------------------------------------------------

            elif cls == CommandSequenceEnd:
                if trk.loop_inf_flg and trk.seq_id == trk.loop_inf_seq_id:
                    if not self.tick_count_mode:
                        trk.seq_index = trk.loop_inf_seq_index
                        continue

                elif len(trk.call_stack) > 0:
                    cs = trk.call_stack.pop()
                    trk.seq_id = cs.seq_id
                    trk.seq_index = cs.seq_index + 1
                    continue

                elif trk.loop_inf_flg:
                    if not self.tick_count_mode:
                        trk.seq_id = trk.loop_inf_seq_id
                        trk.seq_index = trk.loop_inf_seq_index
                        continue

                trk.tick_end = self.status.tick_total
                trk.terminated = True
                break

            elif cls == CommandTrack:
                new_trk = TrackingData.copy_from(trk)
                if len(cmd.id) == 0:
                    new_trk.id = "(none)"
                else:
                    new_trk.id = cmd.id
                new_trk.seq_id = cmd.seq_id
                new_trk.seq_index = 0
                new_trk.tick_begin = self.status.tick_total
                self.trk_list.append(new_trk)
                self.report_trk_list.append(new_trk)

            elif cls == CommandCall:
                trk.call_stack.append(CallStackData(trk.seq_id, trk.seq_index))
                trk.seq_id = cmd.seq_id
                trk.seq_index = 0
                continue

            elif cls == CommandJump:
                trk.seq_id = cmd.seq_id
                trk.seq_index = 0
                continue

            elif cls == CommandLoopBegin:
                trk.loop_stack.append(LoopStackData(trk.seq_index + 1, -1, cmd.times))

            elif cls == CommandLoopEnd:
                if len(trk.loop_stack) > 0:
                    trk.loop_stack[-1].end = trk.seq_index
                    trk.loop_stack[-1].left -= 1
                    if trk.loop_stack[-1].left <= 0:
                        trk.loop_stack.pop()
                    else:
                        trk.seq_index = trk.loop_stack[-1].begin
                        continue

            elif cls == CommandLoopBreak:
                if len(trk.loop_stack) > 0 and trk.loop_stack[-1].left == 1:
                    trk.seq_index = trk.loop_stack[-1].end + 1
                    trk.loop_stack.pop()
                    continue

            elif cls == CommandLoopInfinity:
                trk.loop_inf_flg = True
                trk.loop_inf_seq_id = trk.seq_id
                trk.loop_inf_seq_index = trk.seq_index + 1
                trk.tick_loop_inf = self.status.tick_total

            #---------------------------------------------------------
            elif cls == CommandSystem:
                chip_type_list = []
                for p in cmd.info.split(CommandSystem.PORT_SPLIT_CHAR):
                    chip_type_list.append([])
                    if len(p) > 0:
                        for ct in p.split(' '):
                            if len(ct) > 0:
                                chip_type_list[-1].append(ct)
                self.sysmng.add(cmd.id, cmd.device_type, cmd.device_id, chip_type_list)

            elif cls == CommandTarget:
                self.sysmng.open(cmd.sys_id, cmd.device_port, cmd.chip_no)
                trk.system_id = cmd.sys_id
                trk.device_port = cmd.device_port
                trk.chip_no = cmd.chip_no

            #---------------------------------------------------------
            elif cls == CommandReset:
                if cmd.reset_type == ResetType.PLAYBACK_STATUS:
                    self.status.reset_bar()
                elif cmd.reset_type == ResetType.MASTERWORK:
                    self.sysmng.master_work(trk).reset()
                elif cmd.reset_type == ResetType.CHANNELWORK:
                    self.sysmng.channel_work(trk).reset()
                elif cmd.reset_type == ResetType.CHIP:
                    chip_obj = self.sysmng.chip_obj(trk)
                    chip_obj.send_init()
                    self.sysmng.master_work(trk).reset()
                    for ch_no in range(chip_obj.CHANNEL_NUMBER):
                        self.sysmng.channel_work(trk, ch_no).reset()
                elif cmd.reset_type == ResetType.DEVICE:
                    self.sysmng.device_obj(trk).reset()

            elif cls == CommandMute:
                if cmd.mute_type == MuteType.CHIP:
                    chip_obj = self.sysmng.chip_obj(trk)
                    for ch_no in range(chip_obj.CHANNEL_NUMBER):
                        cw = self.sysmng.channel_work(trk, ch_no)
                        cw.mute.set_value(VariableValue.CURRENT, cmd.switch)
                elif cmd.mute_type == MuteType.CHANNEL:
                    if len(cmd.target) == 0:
                        ch_no = trk.ch_no
                    else:
                        ch_no = int(cmd.target)
                    chip_obj = self.sysmng.chip_obj(trk)
                    if 0 <= ch_no and ch_no < chip_obj.CHANNEL_NUMBER:
                        cw = self.sysmng.channel_work(trk, ch_no)
                        cw.mute.set_value(VariableValue.CURRENT, cmd.switch)
                elif cmd.mute_type == MuteType.TRACK:
                    if len(cmd.target) == 0:
                        trk.mute = cmd.switch
                    else:
                        for i in range(len(self.trk_list)):
                            if self.trk_list[i].id == cmd.target:
                                self.trk_list[i].mute = cmd.switch
                elif cmd.mute_type == MuteType.SEQUENCE:
                    if len(cmd.target) == 0:
                        self.seq_dic[trk.seq_id].mute = cmd.switch
                    else:
                        if cmd.target in self.seq_dic.keys():
                            self.seq_dic[cmd.target].mute = cmd.switch
                elif cmd.mute_type == MuteType.CONTROL:
                    if len(cmd.target) == 0:
                        cw = self.sysmng.channel_work(trk)
                        for ctrl in cw.controller:
                            ctrl.set_value(ControllerBase.MUTE, cmd.switch)
                    else:
                        target = cmd.target.split(" ")
                        ch_no = -1
                        id = ""
                        if len(target) >= 1:
                            ch_no = int(target[0])
                            if len(target) >= 2:
                                id = target[1]
                        if ch_no == -1:
                            cw = self.sysmng.channel_work(trk)
                        else:
                            cw = self.sysmng.channel_work(trk, ch_no)
                        if len(id) == 0:
                            for id in cw.controller.keys():
                                cw.controller[id].set_value(ControllerBase.MUTE, cmd.switch)
                        else:
                            if id in cw.controller.keys():
                                cw.controller[id].set_value(ControllerBase.MUTE, cmd.switch)

            elif cls == CommandUnique:
                if cmd.unique_type.upper() == UniqueType.CHIP:
                    chip_obj = self.sysmng.chip_obj(trk)
                    chip_obj.unique(cmd, trk.ch_no)
                elif cmd.unique_type.upper() == UniqueType.DEVICE:
                    device_obj = self.sysmng.device_obj(trk)
                    device_obj.unique(cmd)

            #---------------------------------------------------------
            elif cls == CommandChannel:
                trk.ch_no = cmd.value

            elif cls == CommandLength:
                trk.omi_length = cmd.length
                trk.omi_dot    = cmd.dot
                trk.omi_tick   = cmd.tick

            elif cls == CommandQuantize:
                trk.quantize.shave = cmd.shave
                trk.quantize.leave = cmd.leave
                trk.quantize.ratio = cmd.ratio

            elif cls == CommandPortamento:
                trk.p_note = cmd.note
                trk.p_sig  = cmd.signature
                trk.p_oct  = cmd.octave

            elif cls == CommandSignature:
                if trk.ch_no >= 0:
                    cw = self.sysmng.channel_work(trk)
                    cw.signature[ 0] = cmd.c
                    cw.signature[ 2] = cmd.d
                    cw.signature[ 4] = cmd.e
                    cw.signature[ 5] = cmd.f
                    cw.signature[ 7] = cmd.g
                    cw.signature[ 9] = cmd.a
                    cw.signature[11] = cmd.b

            elif cls == CommandOperator:
                if trk.ch_no >= 0:
                    trk.operator[0] = cmd.op1 == 1 if 1 else 0
                    trk.operator[1] = cmd.op2 == 1 if 1 else 0
                    trk.operator[2] = cmd.op3 == 1 if 1 else 0
                    trk.operator[3] = cmd.op4 == 1 if 1 else 0
                    trk.operator[4] = cmd.op5 == 1 if 1 else 0
                    trk.operator[5] = cmd.op6 == 1 if 1 else 0

            elif cls == CommandPriority:
                trk.priority = cmd.priority

            #---------------------------------------------------------
            elif cls == CommandTadpole:
                cl = self.decode_tadpole(cmd, trk)
                seq.data[trk.seq_index:trk.seq_index+1] = cl
                continue

            elif cls == CommandKeyOn:
                if trk.ch_no >= 0:
                    cw = self.sysmng.channel_work(trk)
                    if trk.mute == False and self.seq_dic[trk.seq_id].mute == False:
                        cw.set_key_on(trk.operator)
                    map_seq_id = cw.get_map_seq_id()
                    if map_seq_id is not None:
                        # CommandCallと同じことする
                        trk.call_stack.append(CallStackData(trk.seq_id, trk.seq_index))
                        trk.seq_id = map_seq_id
                        trk.seq_index = 0
                        continue

            elif cls == CommandKeyOff:
                if trk.ch_no >= 0:
                    self.sysmng.channel_work(trk).set_key_off(trk.operator)

            elif cls == CommandTone:
                if trk.ch_no >= 0:
                    self.sysmng.channel_work(trk).set_tone_id(cmd.tone_id)

            elif cls == CommandNote:
                if trk.ch_no >= 0:
                    cw = self.sysmng.channel_work(trk).note.set_value(cmd.value_type, cmd.value)

            elif cls == CommandVolume:
                if trk.ch_no >= 0:
                    self.sysmng.channel_work(trk).volume.set_value(cmd.value_type, cmd.value)

            elif cls == CommandPan:
                if trk.ch_no >= 0:
                    self.sysmng.channel_work(trk).pan.set_value(cmd.value_type, cmd.value)

            elif cls == CommandDetune:
                if trk.ch_no >= 0:
                    self.sysmng.channel_work(trk).detune.set_value(cmd.value_type, cmd.value)

            elif cls == CommandOctave:
                if trk.ch_no >= 0:
                    self.sysmng.channel_work(trk).octave.set_value(cmd.value_type, cmd.value)

            elif cls == CommandController:
                if trk.ch_no >= 0:
                    cw = self.sysmng.channel_work(trk)
                    if cmd.ctrl_id not in cw.controller.keys():
                        cw.controller[cmd.ctrl_id] = self.ctlrmng.get(cmd.ctrl_id)
                    cw.controller[cmd.ctrl_id].set_value(cmd.value_type, cmd.value)

            elif cls == CommandMapper:
                if trk.ch_no >= 0:
                    cw = self.sysmng.channel_work(trk)
                    if cmd.map_id not in cw.mapper.keys():
                        cw.mapper[cmd.map_id] = self.mapmng.get(cmd.map_id)
                    cw.mapper[cmd.map_id].enable = cmd.enable

            elif cls == CommandMasterVolume:
                self.sysmng.master_work(trk).master_volume.set_value(cmd.value_type, cmd.value)

            #---------------------------------------------------------
            elif cls == CommandTempo:
                self.status.tempo.set_value(cmd.value_type, cmd.value)

            elif cls == CommandWholeNoteTicks:
                self.status.whole_note_ticks = cmd.tick

            elif cls == CommandBarTicks:
                self.status.bar_ticks = cmd.tick

            elif cls == CommandTuning:
                chip_obj = self.sysmng.chip_obj(trk)
                chip_obj.tuning(cmd.value)

            elif cls == CommandToneData:
                chip_cls = chip_type_to_cls(cmd.chip_type)
                chip_cls.tone_data_dic[cmd.id] = [int(v) for v in cmd.data.split(" ")]

            elif cls == CommandControllerData:
                self.ctlrmng.add(cmd)

            elif cls == CommandMapperData:
                self.mapmng.add(cmd)

            #---------------------------------------------------------
            elif cls == CommandStopWatch:
                if cmd.id in trk.stopwatch.keys():
                    print(f"StopWatch {cmd.id} {self.status.tick_total} {self.status.tick_total - trk.stopwatch[cmd.id]}")
                else:
                    print(f"StopWatch {cmd.id} {self.status.tick_total} -")
                trk.stopwatch[cmd.id] = self.status.tick_total

            elif cls == CommandDebug:
                if cmd.debug_type == DebugType.PRINT:
                    print(cmd.data)
                elif cmd.debug_type == DebugType.PAUSE:
                    input("*** Paused for debugging. please hit any key. ***")
                elif cmd.debug_type == DebugType.EXIT:
                    exit(cmd.data)
                elif cmd.debug_type == DebugType.REPORT:
                    self.print_report_trk()
                elif cmd.debug_type == DebugType.STATUS:
                    self.status.print_debug()
                elif cmd.debug_type == DebugType.MASTERWORK:
                    self.sysmng.master_work(trk).print_debug()
                elif cmd.debug_type == DebugType.CHANNELWORK:
                    self.sysmng.channel_work(trk).print_debug()

            if trk.terminated:
                break
            trk.seq_index += 1

    def print_report_trk(self, flg_save_csv=False):
        rep_trk = ["device,id,chip,ch,begin-p,loop-p,end-p,total-l,loop-l,trk_id"]
        for i in range(len(self.report_trk_list)):
            if len(self.report_trk_list[i].id) == 0:
                continue
            line = ""
            trk = self.report_trk_list[i]
            if trk.system_id is not None:
                d = self.sysmng.device_obj(trk)
                c = self.sysmng.chip_obj(trk)
                line += f"{d.device_type},"
                line += f"{d.device_id},"
                line += f"{c.chip_type},"
            else:
                line += "-,-,-,"
            total_l = trk.tick_end - trk.tick_begin
            loop_l = trk.tick_end - trk.tick_loop_inf
            line += f"{trk.ch_no}," if trk.ch_no >= 0 else "-,"
            line += f"{trk.tick_begin},"
            line += f"{trk.tick_loop_inf}," if trk.tick_loop_inf >= 0 else "-,"
            line += f"{trk.tick_end},"
            line += f"{total_l}," if total_l >= 0 else "-,"
            line += f"{loop_l}," if trk.tick_loop_inf >= 0 else "-,"
            line += f"{trk.id}"
            rep_trk.append(line)

        if flg_save_csv:
            with open("report_trk.csv","w") as f:
                for line in rep_trk:
                    f.write(line)
                    f.write("\n")
                f.write("\n")
        
        print_grid_right(rep_trk)

    def print_report_seq(self, flg_save_csv=False):
        rep_seq = ["seq_id,cmd_num"]
        for seq in self.seq_dic.values():
            line = f"{seq.id},"
            line += f"{len(seq.data)},"
            rep_seq.append(line)
        if flg_save_csv:
            with open("report_seq.csv","w") as f:
                for line in rep_seq:
                    f.write(line)
                    f.write("\n")
        print_grid_right(rep_seq)


        
