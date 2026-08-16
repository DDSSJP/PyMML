from ..define import MML_Type, ORIGIN_SEQUENCE_ID, ControllerType, ModifyValue, ModifyType, WaveForm, TypeList, DefNameMode
from .mml_base import MMLBase
from .builder import MMLBuilder
from ..command import *
from ..controller.controller_util import controller_type_to_cls
from ..controller.controller_base import ControllerBase
from ..controller.modulation import Modulation
from ..controller.controller_raw import ControllerRaw
from ..controller.envelope import Envelope
from ..controller.portamento import Portamento
from ..controller.sweep import Sweep
from ..chip.chip_utils import chip_type_to_cls
from ..device.device_util import device_type_to_cls
from ..string_stream import StringStream
from ..player import VariableValue
from ..chip.YMF825 import YMF825UniqueType
from .. import error as Error
import copy

C_TADPOLE_A = 'a'
C_TADPOLE_B = 'b'
C_TADPOLE_C = 'c'
C_TADPOLE_D = 'd'
C_TADPOLE_E = 'e'
C_TADPOLE_F = 'f'
C_TADPOLE_G = 'g'
# C_ = 'h'
# C_ = 'i'
# C_ = 'j'
C_KEYONOFF = 'k'
C_LENGTH_DEF = 'l'
C_MUTE = 'm'
C_NOTE = 'n'
C_OCTAVE = 'o'
C_PAN = 'p'
C_QUONTIZE = 'q'
C_REST = 'r'
C_TARGET = 's'
C_TEMPO = 't'
C_UNIQUE = 'u'
C_VOLUME = 'v'
# C_ = 'w'
C_TADPOLE_X = 'x'
C_REGISTER = 'y'
# C_ = 'z'
C_TUNING = 'A'
C_BAR_TICKS = 'B'
C_CHANNEL = 'C'
C_DETUNE = 'D'
C_CTRL_ENV = 'E'
C_FM_OPERATOR = 'F'
# C_ = 'G'
# C_ = 'H'
# C_ = 'I'
# C_ = 'J'
C_SIGNATURE = 'K'
C_LOOP_INF = 'L'
C_CTRL_MODULATION = 'M'
# C_ = 'N'
# C_ = 'O'
C_CTRL_PORTAMENTO = 'P'
# C_ = 'Q'
C_CTRL_RAW = 'R'
C_CTRL_SWEEP = 'S'
# C_ = 'T'
# C_ = 'U'
C_MASTER_VOLUME = 'V'
C_WAIT = 'W'
# C_ = 'X'
# C_ = 'Y'
C_PRIORITY = 'Z'
C_MACRO = '!'
C_DEFINE = '#'
C_TRACKER = '$'
C_TICK = '%'
C_TAI_SLAR = '&'
C_PARAMETER = "'"
C_VOLUME_DOWN = '('
C_VOLUME_UP = ')'
C_CONTROLLER = '*'
C_SHARP = '+'
C_DELIMITER = ','
C_FLAT = '-'
C_DOTNOTE = '.'
C_PART = '/'
C_LOOP_EXIT = ':'
C_COMMENT = ';'
C_OCTAVE_DOWN = '<'
C_OCTAVE_UP = '>'
C_NATURAL = '='
C_DEBUG = '?'
C_TONE = '@'
C_LOOP_BEIGN = '['
C_LOOP_END = ']'
C_CR_CANCEL = '\\'
C_LENGTH_ADD = '^'
C_PART_ORIGIN = '_'
C_MAPPER = '`'
C_SWEEP_BEIGN = '{'
C_SWEEP_END = '}'
# C_ = '~'
C_NO_FUNC = '|'
KEY_TO_NOTE_DIC = {
    C_TADPOLE_C: 0,
    C_TADPOLE_D: 2,
    C_TADPOLE_E: 4,
    C_TADPOLE_F: 5,
    C_TADPOLE_G: 7,
    C_TADPOLE_A: 9,
    C_TADPOLE_B: 11,
    C_TADPOLE_C + C_NATURAL: 0,
    C_TADPOLE_D + C_NATURAL: 2,
    C_TADPOLE_E + C_NATURAL: 4,
    C_TADPOLE_F + C_NATURAL: 5,
    C_TADPOLE_G + C_NATURAL: 7,
    C_TADPOLE_A + C_NATURAL: 9,
    C_TADPOLE_B + C_NATURAL: 11,
    C_TADPOLE_C + C_SHARP: 0+1,
    C_TADPOLE_D + C_SHARP: 2+1,
    C_TADPOLE_E + C_SHARP: 4+1,
    C_TADPOLE_F + C_SHARP: 5+1,
    C_TADPOLE_G + C_SHARP: 7+1,
    C_TADPOLE_A + C_SHARP: 9+1,
    C_TADPOLE_B + C_SHARP: 11+1,
    C_TADPOLE_C + C_SHARP + C_SHARP: 0+2,
    C_TADPOLE_D + C_SHARP + C_SHARP: 2+2,
    C_TADPOLE_E + C_SHARP + C_SHARP: 4+2,
    C_TADPOLE_F + C_SHARP + C_SHARP: 5+2,
    C_TADPOLE_G + C_SHARP + C_SHARP: 7+2,
    C_TADPOLE_A + C_SHARP + C_SHARP: 9+2,
    C_TADPOLE_B + C_SHARP + C_SHARP: 11+2,
    C_TADPOLE_C + C_FLAT: 0-1,
    C_TADPOLE_D + C_FLAT: 2-1,
    C_TADPOLE_E + C_FLAT: 4-1,
    C_TADPOLE_F + C_FLAT: 5-1,
    C_TADPOLE_G + C_FLAT: 7-1,
    C_TADPOLE_A + C_FLAT: 9-1,
    C_TADPOLE_B + C_FLAT: 11-1,
    C_TADPOLE_C + C_FLAT + C_FLAT: 0-2,
    C_TADPOLE_D + C_FLAT + C_FLAT: 2-2,
    C_TADPOLE_E + C_FLAT + C_FLAT: 4-2,
    C_TADPOLE_F + C_FLAT + C_FLAT: 5-2,
    C_TADPOLE_G + C_FLAT + C_FLAT: 7-2,
    C_TADPOLE_A + C_FLAT + C_FLAT: 9-2,
    C_TADPOLE_B + C_FLAT + C_FLAT: 11-2,
    }
KEY_LIST = [
    C_TADPOLE_C,
    C_TADPOLE_D,
    C_TADPOLE_E,
    C_TADPOLE_F,
    C_TADPOLE_G,
    C_TADPOLE_A,
    C_TADPOLE_B
    ]
DOT_LIST = [
    1.0,
    1.0 + 0.5,
    1.0 + 0.5 + 0.25,
    1.0 + 0.5 + 0.25 + 0.125,
    1.0 + 0.5 + 0.25 + 0.125 + 0.0625,
    1.0 + 0.5 + 0.25 + 0.125 + 0.0625 + 0.03125,
    1.0 + 0.5 + 0.25 + 0.125 + 0.0625 + 0.03125 + 0.015625,
    1.0 + 0.5 + 0.25 + 0.125 + 0.0625 + 0.03125 + 0.015625 + 0.0078125,
    1.0 + 0.5 + 0.25 + 0.125 + 0.0625 + 0.03125 + 0.015625 + 0.0078125 + 0.00390625,
    ]
SIG_DIC = {
    None: SignatureType.NONE,
    C_SHARP: SignatureType.SHARP,
    C_FLAT: SignatureType.FLAT,
    C_NATURAL: SignatureType.NATURAL,
    C_SHARP + C_SHARP: SignatureType.DOUBLE_SHARP,
    C_FLAT + C_FLAT: SignatureType.DOUBLE_FLAT,
    }
MAP_ACCEPT_LIST = [
    C_PAN,
    C_QUONTIZE,
    C_DETUNE,
    C_VOLUME,
    C_REGISTER,
    C_PARAMETER,
    C_FM_OPERATOR,
    C_UNIQUE,
    C_TONE,
    C_CONTROLLER,
    C_CTRL_MODULATION,
    C_CTRL_ENV,
    C_CTRL_RAW,
    C_CTRL_SWEEP,
    C_CTRL_PORTAMENTO,
    C_NO_FUNC,
    ]
# entry = [full, short]
E_SYSTEM           = [CommandSystem.BOTTOM_CMD, "SYS"]
E_PATH             = [CommandPath.BOTTOM_CMD]
E_INCLUDE          = [CommandInclude.BOTTOM_CMD, "INC"]
E_TITLE            = [CommandTitle.BOTTOM_CMD, "TIT"]
E_COMPOSER         = [CommandComposer.BOTTOM_CMD, "COM"]
E_ARRANGER         = [CommandArranger.BOTTOM_CMD, "ARR"]
E_MESSAGE          = [CommandMessage.BOTTOM_CMD, "MSG"]
E_WHOLENOTE        = ["WHOLENOTETICKS", "ZEN"]
E_OCTAVE_UP_DOWN   = ["OCTAVEUPDOWN", "OCT"]
E_VOLUME_UP_DOWN   = ["VOLUMEUPDOWN", "VOL"]
E_DEFNAMEMODE      = ["DEFNAMEMODE", "DNMODE"]
E_ENABLE_PART      = ["ENABLEPART", "PART"]
E_CONTROLLER       = ["CONTROLLERDATA", "CTRL"]
E_TONE             = ["TONEDATA", "TONE"]
E_MAP              = ["MAPPERDATA", "MAP"]
E_SEQUENCE         = ["SEQUENCE", "SEQ"]
E_MACRO            = ["MACRO", "MAC"]
E_YMF825_TONETABLE = ["YMF825_TONETABLE"]
ENTRY_ALL_LIST = []
ENTRY_ALL_LIST += E_SYSTEM
ENTRY_ALL_LIST += E_PATH
ENTRY_ALL_LIST += E_INCLUDE
ENTRY_ALL_LIST += E_TITLE
ENTRY_ALL_LIST += E_COMPOSER
ENTRY_ALL_LIST += E_ARRANGER
ENTRY_ALL_LIST += E_MESSAGE
ENTRY_ALL_LIST += E_WHOLENOTE
ENTRY_ALL_LIST += E_OCTAVE_UP_DOWN
ENTRY_ALL_LIST += E_VOLUME_UP_DOWN
ENTRY_ALL_LIST += E_DEFNAMEMODE
ENTRY_ALL_LIST += E_ENABLE_PART
ENTRY_ALL_LIST += E_CONTROLLER
ENTRY_ALL_LIST += E_TONE
ENTRY_ALL_LIST += E_MAP
ENTRY_ALL_LIST += E_SEQUENCE
ENTRY_ALL_LIST += E_MACRO
ENTRY_ALL_LIST += E_YMF825_TONETABLE
CHARS_ID  = "_0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
CHARS_HEX = "_0123456789abcdefABCDEF"
CHARS_DEC = "_0123456789"
CHARS_BIN = "_01"
DEFN_MODE = DefNameMode.STRING
CTRL_ID_M = "STANDARD_CONTROLLER_MODULATION"
CTRL_ID_E = "STANDARD_CONTROLLER_ENVELOPE"
CTRL_ID_R = "STANDARD_CONTROLLER_RAW"
CTRL_ID_S = "STANDARD_CONTROLLER_SWEEP"
CTRL_ID_P = "STANDARD_CONTROLLER_PORTAMENTO"
PREFIX_HEX = 'H'
PREFIX_BIN = 'I'

WHOLE_NOTE_TICKS = 192
DEF_PART_LIST = []
CTRL_ID_CLS_DIC = {}
MACRO_DIC = {}
CTRL_MODIFYVALUE_DIC = [ModifyValue.PITCH, ModifyValue.VOLUME, ModifyValue.PAN, ModifyValue.NOTE]
CTRL_WAVEFORM_DIC = [WaveForm.SIN, WaveForm.SAW, WaveForm.TRIANGLE, WaveForm.SQUARE, WaveForm.RANDOM]

def printx(ss, length=1, msg="", offset=0):
    ss.block_reset()
    ss.seek(offset)
    ss.print_location(length, msg)
    exit()

def checkx(ss, name, value, typ, minv=None, maxv=None, offset=0):
    msg = Error.check(name, value, typ, minv, maxv)
    if len(msg) > 0:
        if type(value) == str:
            length = len(value)
            if length == 0:
                length = 1
        else:
            length = 1
        if ss is not None:
            ss.seek(-length)
            printx(ss, length, msg, offset)
        else:
            print(msg)
            exit()

class Macro:
    class Parameter:
        class Type(TypeList):
            ID = "ID"
            INT = "INT"
            REAL = "REAL"
            FLAG = "FLAG"
        def __init__(self, key, type, value):
            self.key   = key
            self.type  = str(type).upper()
            self.value = value
    def __init__(self):
        self.id = None
        self.prm = []
        self.mml = None
    def add_parameter(self, key, type, value):
        self.prm.append(Macro.Parameter(key, type, value))
    def set_mml(self, mml):
        self.mml = mml
    def get_prm(self, index):
        return self.prm[index]
    def get_replace(self, values):
        ret = self.mml
        for i in range(len(self.prm)):
            if len(values) > i and len(values[i]) > 0:
                ret = ret.replace(self.prm[i].key, values[i])
            else:
                ret = ret.replace(self.prm[i].key, self.prm[i].value)
        return ret

def get_define(ss:StringStream, builder:MMLBuilder):
    global DEFN_MODE
    ss.block_reset() # リセットしておく
    ss.seek(1) # 最初の#の次にする

    # エントリ確認
    entry = ss.read_to_space(add_char="{").upper()
    if entry not in ENTRY_ALL_LIST:
        printx(ss, -len(entry), "Unknown entry.", -1)

    # 定義があるか？
    line = ss.show_line().strip()
    if len(line) == 0:
        printx(ss, 1, "Not found define data.")

    # 定義はブロックか
    ss.seek_to_not_space()
    if ss.is_block_begin():
        ret = ss.show_block(push_block=True)
        if len(ret) == 0:
            printx(ss, 1, "Failed to read block.")

    # 入れ物用意
    cmd_list = []

    #------------------------------------------------------------
    if entry in E_TITLE:
        text = get_define_text(ss)
        cmd_list.append(CommandTitle(text))
    
    elif entry in E_COMPOSER:
        text = get_define_text(ss)
        cmd_list.append(CommandComposer(text))
    
    elif entry in E_ARRANGER:
        text = get_define_text(ss)
        cmd_list.append(CommandArranger(text))
    
    elif entry in E_MESSAGE:
        text = get_define_text(ss)
        cmd_list.append(CommandMessage(text))
    
    elif entry in E_INCLUDE:
        text = get_define_text(ss)
        builder.proc_include(text.strip())

    elif entry in E_PATH:
        text = get_define_text(ss)
        builder.add_path(text.strip())

    if ss.is_block_stack():
        ss.seek(1)
        ss.seek_to_not_space()

    #------------------------------------------------------------
    if entry in E_SEQUENCE:
        cl = []
        id = get_define_item(ss, mode=DEFN_MODE)
        if ss.is_block_stack():
            while not ss.eob():
                if ss.show(1) == C_PART:
                    printx(ss, 1, "Can't use \"{C_PART}\" in sequence define.")
                cl.extend(get_seq(ss))
                ss.seek_to_not_space()
        else:
            end_index = ss.index + len(ss.show_line()) - 1
            while ss.index < end_index:
                if ss.show(1) == C_PART:
                    printx(ss, 1, "Can't use \"{C_PART}\" in sequence define.")
                cl.extend(get_seq(ss))
        builder.add_seq_data(id, cl)

    #------------------------------------------------------------
    elif entry in E_OCTAVE_UP_DOWN:
        global C_OCTAVE_UP, C_OCTAVE_DOWN
        up, down = get_define_item_up_down(ss, C_OCTAVE_UP, C_OCTAVE_DOWN)
        C_OCTAVE_UP = up
        C_OCTAVE_DOWN = down

    #------------------------------------------------------------
    elif entry in E_VOLUME_UP_DOWN:
        global C_VOLUME_UP, C_VOLUME_DOWN
        up, down = get_define_item_up_down(ss, C_VOLUME_UP, C_VOLUME_DOWN)
        C_VOLUME_UP = up
        C_VOLUME_DOWN = down

    #------------------------------------------------------------
    elif entry in E_ENABLE_PART:
        if not ss.is_block_stack():
            end_index = ss.index + len(ss.show_line())
        global DEF_PART_LIST
        part_set = set(DEF_PART_LIST)
        a = None
        n = None
        while True:
            if ss.is_block_stack():
                ss.seek_to_not_space()
                if ss.eob():
                    break
            else:
                ss.seek_to_not_space(inline=True)
                if ss.index >= end_index:
                    break
            n = None
            if ss.is_alphabet_upper():
                a = ss.read(1)
            elif ss.is_number() and a is not None:
                n = ss.read(1)
            else:
                printx(ss, 1, "Please, use capital letter.")
            if n is None:    
                if ss.is_space() or ss.is_alphabet_upper():
                    n = "0"
                elif ss.is_number():
                    n = ss.read(1)
                else:
                    printx(ss, 1, "Please, use a number.")
            part_set.add(a + n)
        DEF_PART_LIST = sorted(list(part_set))

    #------------------------------------------------------------
    elif entry in E_DEFNAMEMODE:
        mode = get_define_item(ss).upper()
        checkx(ss, "DefNameMode", mode, DefNameMode.get_list())
        DEFN_MODE = mode

    #------------------------------------------------------------
    elif entry in E_SYSTEM:
        id = get_define_item(ss, mode=DEFN_MODE)
        device_type = get_define_item(ss)
        checkx(ss, "DeviceType", device_type, DeviceType.get_list())
        device_id = get_define_item(ss)
        dev = device_type_to_cls(device_type)
        info = ""
        while True:
            item = get_define_item(ss, err=False)
            if item is None:
                break
            info += item + " "
        if info.count(CommandSystem.PORT_SPLIT_CHAR) != dev.PORT_NUM:
            printx(ss, 1, f"not match the port counts. (device port num: {dev.PORT_NUM})")
        if info.startswith(CommandSystem.PORT_SPLIT_CHAR):
            info = info[1:]
        cmd_list.append(CommandSystem(id, device_type, device_id, info.strip()))

    #------------------------------------------------------------
    elif entry in E_WHOLENOTE:
        n = get_define_item(ss)
        checkx(ss, "WholeNoteTicks", n, int, 1)
        global WHOLE_NOTE_TICKS
        WHOLE_NOTE_TICKS = int(n)
        cmd_list.append(CommandWholeNoteTicks(n))

    #------------------------------------------------------------
    elif entry in E_CONTROLLER:
        def get_item_def_x(data:list, ss, name, typ, minv=None, maxv=None):
            item = get_define_item(ss)
            checkx(ss, name, item, typ, minv, maxv)
            data.append(item)
        data = []
        id = get_define_item(ss, mode=DEFN_MODE)
        ctrl_type = get_define_item(ss).upper()
        checkx(ss, "ControllerType", ctrl_type, ControllerType.get_list())
        global CTRL_ID_CLS_DIC
        CTRL_ID_CLS_DIC[id] = controller_type_to_cls(ctrl_type)
        get_item_def_x(data, ss, ControllerBase.Parameter.MODIFY_VALUE, ModifyValue.get_list())
        get_item_def_x(data, ss, ControllerBase.Parameter.MODIFY_TYPE, ModifyType.get_list())
        if ctrl_type == ControllerType.MODULATION:
            get_item_def_x(data, ss, Modulation.Parameter.WAVE, WaveForm.get_list())
            get_item_def_x(data, ss, Modulation.Parameter.DELAY, int, 0)
            get_item_def_x(data, ss, Modulation.Parameter.AMPLIFY, float)
            get_item_def_x(data, ss, Modulation.Parameter.PERIOD, int, 1)
        elif ctrl_type == ControllerType.ENVELOPE:
            get_item_def_x(data, ss, Envelope.Parameter.INI_VALUE, float, 0)
            get_item_def_x(data, ss, Envelope.Parameter.ATTACK_TICK, int, 0)
            get_item_def_x(data, ss, Envelope.Parameter.ATTACK_VALUE, float, 0)
            get_item_def_x(data, ss, Envelope.Parameter.DECAY_TICK, int, 0)
            get_item_def_x(data, ss, Envelope.Parameter.DECAY_VALUE, float, 0)
            get_item_def_x(data, ss, Envelope.Parameter.SUSTAIN_TICK, int, 0)
            get_item_def_x(data, ss, Envelope.Parameter.SUSTAIN_VALUE, float, 0)
            get_item_def_x(data, ss, Envelope.Parameter.RELEASE_RATE, float, 0)
        elif ctrl_type == ControllerType.PORTAMENTO:
            get_item_def_x(data, ss, Portamento.Parameter.TIME, int, 1)
            get_item_def_x(data, ss, Portamento.Parameter.CONTROL, int, -1)
        elif ctrl_type == ControllerType.SWEEP:
            get_item_def_x(data, ss, Sweep.Parameter.VOLUME_INI, int, 0)
            get_item_def_x(data, ss, Sweep.Parameter.STEP, int, 1)
            get_item_def_x(data, ss, Sweep.Parameter.VOLUME, int)
        elif ctrl_type == ControllerType.RAW:
            while True:
                item = get_define_item(ss, False)
                if item is None:
                    break
                item = item.upper()
                for c in item:
                    checkx(ss, "ControllerRaw item", c, [*"0123456789RL*"])
                data.append(item)
            line = ' '.join(data)
            line.replace("R"," R ")
            line.replace("L"," L ")
            length = len(line)
            while length != len(line):
                length = len(line)
                line.replace(" *","*")
                line.replace("* ","*")
                line.replace("  ", " ")
            data = [line]
        cmd_list.append(CommandControllerData(id, ctrl_type, ' '.join(data)))

    #------------------------------------------------------------
    elif entry in E_TONE:
        data = []
        chip_type = get_define_item(ss)
        chip_cls = chip_type_to_cls(chip_type)
        id = get_define_item(ss, mode=DEFN_MODE)
        for i in range(chip_cls.TONE_PRM_NUM):
            item = get_define_item(ss)
            data.append(item)
            err, msg = chip_cls.tone_prm_check(i, item)
            if err:
                printx(ss, -len(item), msg)
        cmd_list.append(CommandToneData(chip_type, id, ' '.join(data)))

    #------------------------------------------------------------
    elif entry in E_MAP:
        data = []
        map_id = get_define_item(ss, mode=DEFN_MODE)
        mode = get_define_item(ss).upper()
        checkx(ss, "MapperMode", mode, MapperMode.get_list())
        seq_id_list = []
        while True:
            oct1 = get_define_item(ss, False)
            if oct1 is None:
                break
            checkx(ss, "Note1(octave)", oct1, int, 0, 9)
            key1 = get_define_item(ss)
            checkx(ss, "Note1(key)", key1, list(KEY_TO_NOTE_DIC.keys()))
            oct2 = get_define_item(ss)
            checkx(ss, "Note2(octave)", oct2, int, 0, 9)
            key2 = get_define_item(ss)
            checkx(ss, "Note2(key)", key2, list(KEY_TO_NOTE_DIC.keys()))

            note1 = int(oct1) * 12 + KEY_TO_NOTE_DIC[key1]
            note2 = int(oct2) * 12 + KEY_TO_NOTE_DIC[key2]
            if mode == MapperMode.MAPPER:
                if note1 > note2:
                    printx(ss, 8, "please, Note1 <= Note2", -8)

            seq_id = f"map_{map_id}_{note1}_{note2}"
            if seq_id in seq_id_list:
                printx(ss, 8, f"found same id. -> {seq_id}", -8)
            seq_id_list.append(seq_id)
            data.append(str(note1))
            data.append(str(note2))
            data.append(seq_id)

            cl = [CommandSequenceBegin(seq_id)]
            ss.seek_to_not_space()
            ret = ss.show_block(push_block=True)
            if len(ret) == 0:
                printx(ss, 1, "failed to read block")
            ss.seek(1)
            ss.seek_to_not_space()
            while not ss.eob():
                if ss.show(1) not in MAP_ACCEPT_LIST:
                    printx(ss, 1, "This command is not available in the map definition.")
                cl.extend(get_seq(ss))
                ss.seek_to_not_space()
            ss.block_pop()
            ss.seek(1)
            ss.seek_to_not_space()
            cl.append(CommandSequenceEnd())
            builder.add_seq_data(seq_id, cl)
        cmd_list.append(CommandMapperData(map_id, mode, ' '.join(data).strip()))

    #------------------------------------------------------------
    elif entry in E_MACRO:
        id = get_define_item(ss, mode=DEFN_MODE)
        checkx(ss, "ID", id, CHARS_ID)

        # ss.seek_to_not_space()
        # if ss.is_block_begin():
        #     ret = ss.show_block(push_block=True)
        #     if len(ret) == 0:
        #         printx(ss, 1, "failed to read block")
        #     ss.seek(1)

        m = Macro()
        m.id = id
        while True:
            ss.seek_to_not_space()
            if ss.is_block_begin():
                break
            key = get_define_item(ss)
            checkx(ss, "Macro parameter key", key, CHARS_ID)
            typ = get_define_item(ss).upper()
            checkx(ss, "Macro parameter type", typ, Macro.Parameter.Type.get_list())
            val = get_define_item(ss)
            if typ == Macro.Parameter.Type.FLAG:
                check_type = bool
            if typ == Macro.Parameter.Type.ID:
                check_type = CHARS_ID
            if typ == Macro.Parameter.Type.INT:
                check_type = int
            if typ == Macro.Parameter.Type.REAL:
                check_type = float            
            checkx(ss, "Macro parameter value", val, check_type)
            m.add_parameter(key, typ, val)
        mml = get_define_item_block(ss)
        m.set_mml(mml)
        MACRO_DIC[m.id] = m

    #------------------------------------------------------------
    elif entry in E_YMF825_TONETABLE:
        no = 0
        while True:
            name = get_define_item(ss, False, mode=DEFN_MODE)
            if name is None:
                break
            if 15 < no:
                printx(ss, 1, "a lot of tone name.")
            cmd_list.append(CommandUnique(UniqueType.CHIP, YMF825UniqueType.SET_TONE_TABLE,f"{no} {name}"))
            no += 1
        num = len(cmd_list)
        if  num < 1:
            printx(ss, 1, "not found tone name.")
        cmd_list.append(CommandUnique(UniqueType.CHIP, YMF825UniqueType.WRITE_TONE_TABLE,str(num)))        

    #------------------------------------------------------------
    if ss.is_block_stack():
        ss.seek_to_not_space()
        ss.block_reset()
        ss.seek(1) # ブロック終わりの}の次に移動
    return cmd_list

def get_define_text(ss:StringStream):
    if ss.is_block_stack():
        text = ss.read_block()
    else:
        text = ss.read_line()
    return text

def get_define_item(ss, err=True, mode=DefNameMode.STRING):
    if ss.is_block_stack():
        ss.seek_to_not_space()
        if ss.eob():
            if err:
                printx(ss, 1, "failed to read item.")
            else:
                return None
    else:
        ss.seek_to_not_space(inline=True)
        if ss.is_LF():
            if err:
                printx(ss, 1, "failed to read item.")
            else:
                return None
    value = ss.read_to_space().strip() 
    if mode == DefNameMode.NUMBER:
        checkx(ss, "DefineValue", value, int, 0)
        value = str(int(value))
    return value

def get_define_item_block(ss):
    ss.seek_to_not_space()
    if ss.is_block_begin() == False:
        printx(ss, 1, "not found begin of block.")
    ret = ss.read_block().strip()
    if len(ret) == 0:
        printx(ss, 1, "failed to read block", -1)
    ss.seek(1) # ブロック終わりの}の次にする
    return MMLBase.trim_space(ret).strip()

def get_define_item_up_down(ss, def_up, def_down):
    up = None
    down = None
    if ss.is_block_stack():
        while not ss.eob():
            ss.seek_to_not_space()
            if up is None:
                up = ss.read(1)
            elif down is None:
                down = ss.read(1)
                break
    else:
        end_index = ss.index + len(ss.show_line())
        while ss.index < end_index:
            ss.seek_to_not_space(inline=True)
            if up is None:
                up = ss.read(1)
            elif down is None:
                down = ss.read(1)
                break
    if up is None or down is None:
        printx(ss, -3, "failed to read up-char and down-char.", -1)
    if sorted([up,down]) != sorted([def_up,def_down]):
        printx(ss, -3, f"Please use default characters. {def_up} and {def_down}", -1)
    return up, down

class ValueAdapt:
    INTEGER = "INTEGER"
    REAL = "REAL"
    RELATIVE0 = "RELATIVE0"
    RELATIVE1 = "RELATIVE1"
    RELATIVE2 = "RELATIVE2"
    MULTIPLE1 = "MULTIPLE1"
    MULTIPLE2 = "MULTIPLE2"
    TICK = "TICK"
    DECIMAL = "DECIMAL"
    HEX = "HEX"
    BINARY = "BINARY"
    OMISSION = "OMISSION"

class ValueAdaptPackage:
    INT_DEC  = [ValueAdapt.DECIMAL, ValueAdapt.INTEGER]
    INT  = [ValueAdapt.DECIMAL, ValueAdapt.HEX, ValueAdapt.BINARY, ValueAdapt.INTEGER]
    REAL = [ValueAdapt.DECIMAL, ValueAdapt.REAL]
    VV   = [ValueAdapt.DECIMAL, ValueAdapt.HEX, ValueAdapt.BINARY, ValueAdapt.INTEGER, ValueAdapt.REAL, ValueAdapt.RELATIVE0, ValueAdapt.RELATIVE1, ValueAdapt.RELATIVE2, ValueAdapt.MULTIPLE1, ValueAdapt.MULTIPLE2]
    TICK_R = [ValueAdapt.DECIMAL, ValueAdapt.HEX, ValueAdapt.BINARY, ValueAdapt.INTEGER, ValueAdapt.RELATIVE1, ValueAdapt.TICK]
    TICK = [ValueAdapt.DECIMAL, ValueAdapt.HEX, ValueAdapt.BINARY, ValueAdapt.INTEGER, ValueAdapt.TICK]
    TADPOLE_LENGTH = [ValueAdapt.DECIMAL, ValueAdapt.INTEGER, ValueAdapt.TICK]

    @classmethod
    def add_omi(cls, pack):
        ex = [ValueAdapt.OMISSION]
        ex.extend(pack)
        return ex

def get_item_num(ss:StringStream, accept=[], omission=False, default="", flg_seek_to_not_space=True):
    if flg_seek_to_not_space:
        ss.seek_to_not_space(inline=True)
    if omission:
        accept = ValueAdaptPackage.add_omi(accept)
    flgs = []
    chars = ""

    # 相対値
    if ValueAdapt.RELATIVE2 in accept:
        if ss.show(2) == "~~":
            ss.seek(2)
            flgs.append(ValueAdapt.RELATIVE2)
    if ValueAdapt.RELATIVE1 in accept:
        if ss.show(1) == "~":
            ss.seek(1)
            flgs.append(ValueAdapt.RELATIVE1)
    
    # 倍率
    if ValueAdapt.MULTIPLE2 in accept:
        if ss.show(2) == "**":
            ss.seek(2)
            flgs.append(ValueAdapt.MULTIPLE2)
    if ValueAdapt.MULTIPLE1 in accept:
        if ss.show(1) == "*":
            ss.seek(1)
            flgs.append(ValueAdapt.MULTIPLE1)

    # Tick指定
    if ValueAdapt.TICK in accept:
        if ss.show(1) == C_TICK:
            ss.read(1)
            flgs.append(ValueAdapt.TICK)

    # 符号
    sign = ""
    if ss.show(1) in "+-":
        sign = ss.read(1)

    # 進数
    c = ss.show(1)
    if ValueAdapt.HEX in accept and c == PREFIX_HEX:
        ss.read(1)
        chars = CHARS_HEX
        flgs.append(ValueAdapt.HEX)
    elif ValueAdapt.BINARY in accept and c == PREFIX_BIN:
        ss.read(1)
        chars = CHARS_BIN
        flgs.append(ValueAdapt.BINARY)
    else:
        chars = CHARS_DEC
        flgs.append(ValueAdapt.DECIMAL)

    # 10進数のみ実数用の小数点を追加(実数or整数は未確定)
    if ValueAdapt.REAL in accept and ValueAdapt.DECIMAL in flgs:
        chars += "."

    # 数字を読み込む
    vstr = ""
    while ss.show(1) in chars and not ss.eof() and not ss.eob():
        c = ss.read(1)
        if len(c) == 0:
            break
        if c == '_':
            continue
        vstr += c
        if ValueAdapt.REAL in flgs:
            if vstr.count('.') > 1:
                printx(ss, 1, "multiple decimal points.", -1)
    if len(vstr) == 0:
        if ValueAdapt.OMISSION in accept:
            flgs.append(ValueAdapt.OMISSION)
            return default, flgs
        printx(ss, 1, "failed to read value.")

    # Pythonに進数から値へ変換してもらおう!
    if ValueAdapt.BINARY in flgs:
        vstr = str(eval("0b" + vstr))
    elif ValueAdapt.HEX in flgs:
        vstr = str(eval("0x" + vstr))

    # 小数点があれば実数、なければ整数とする
    if ValueAdapt.REAL in accept and vstr.count('.') > 0:
        flgs.append(ValueAdapt.REAL)
    else:
        flgs.append(ValueAdapt.INTEGER)

    # 数字文字列最適化
    if ValueAdapt.REAL in flgs:
        vstr = str(float(sign + vstr))
    else:
        vstr = str(int(sign + vstr))

    return vstr, flgs

def get_item_id(ss:StringStream, omission=False, default="", mode=DefNameMode.STRING):
    ss.seek_to_not_space(inline=True)
    id = ""
    if mode == DefNameMode.STRING:
        while True:
            if ss.show(1) not in CHARS_ID:
                break
            if ss.eof():
                break
            if ss.eob():
                break
            id += ss.read(1)
    else:
        value, flgs = get_item_num(ss, ValueAdaptPackage.INT_DEC)
        id = str(int(value))
    if len(id) == 0:
        if omission == False:
            printx(ss, 1, "failed read id character string.")
        else:
            id = default
    return id

def get_item_flag(ss:StringStream, omission=False, default=0, no_error=False):
    ss.seek_to_not_space(inline=True)
    value = ss.show(1)
    if value in "01":
        ss.seek(1)
        return int(value)
    # printx(ss, 1, "failed to read flag value. (0 or 1)")
    value = ss.show_line().upper()
    if value.startswith("FALSE"):
        ss.seek(5)
        return 0
    if value.startswith("TRUE"):
        ss.seek(4)
        return 1
    if not no_error:
        printx(ss, 1, "failed to read flag value. (0, false, 1, true)")
    return None

def make_vv_cmd(cls, value, flgs):
    if ValueAdapt.RELATIVE0 in flgs:
        typ = VariableValue.RELATIVE0
    elif ValueAdapt.RELATIVE1 in flgs:
        typ = VariableValue.RELATIVE1
    elif ValueAdapt.RELATIVE2 in flgs:
        typ = VariableValue.RELATIVE2
    elif ValueAdapt.MULTIPLE1 in flgs:
        typ = VariableValue.MULTIPLE1
    elif ValueAdapt.MULTIPLE2 in flgs:
        typ = VariableValue.MULTIPLE2
    else:
        typ = VariableValue.CURRENT
    return cls(typ, value)

def decode_tadpole_tick(ss, length, dot, tick):
    if tick == 0:
        if WHOLE_NOTE_TICKS % length != 0:
            printx(ss, 1, f"note length is not divisible. whole_note_ticks/tadpole = {WHOLE_NOTE_TICKS}/{length} = {WHOLE_NOTE_TICKS/length}")
        tick = int(WHOLE_NOTE_TICKS / length)
        if dot > 0:
            sumtick = 0
            divtick = tick
            for _ in range(dot):
                if divtick % 2 != 0:
                    printx(ss, 1, f"note length is not divisible. whole_note_ticks/tadpole = {WHOLE_NOTE_TICKS}/{length}*{DOT_LIST[dot]} = {WHOLE_NOTE_TICKS/length*DOT_LIST[dot]}")
                divtick /= 2
                sumtick += divtick
            tick = sumtick
    return tick

def get_tadpole_length(ss:StringStream, omission=False):
    value, flgs = get_item_num(ss, ValueAdaptPackage.TADPOLE_LENGTH, omission)
    omi = 0
    tick = 0
    length = 0
    dot = 0
    if ValueAdapt.OMISSION in flgs:
        omi = 1
    elif ValueAdapt.TICK in flgs:
        tick = int(value)
    else:
        length = int(value)
    # 付点
    while ss.show(1) == C_DOTNOTE:
        dot += 1
        checkx(ss, "dot", dot, int, 1, 8)
        if omi == 0 and length > 0:
            decode_tadpole_tick(ss, length, dot, 0) # エラーチェックのため
        ss.seek(1)
    # 長さ増減がある場合
    if length > 0 or tick > 0:
        if ss.show(1) in "+-":
            s = ss.read(1)
            _, length2, dot2, tick2 = get_tadpole_length(ss, False)
            # tickに変換
            tick = decode_tadpole_tick(ss, length, dot, tick)
            tick2 = decode_tadpole_tick(ss, length2, dot2, tick2)
            if s == "+":
                tick += tick2
            if s == "-":
                 tick -= tick2            
            checkx(ss, "tadpole_length", tick, int, 1)
            length = 0
            dot = 0
    return omi, length, dot, tick

def need_next_item(ss, name="item"):
    ss.seek_to_not_space(inline=True)
    if ss.show(1) != C_DELIMITER:
        printx(ss, 1, f"failed to read {name}.")
    ss.seek(1)

def is_next_item(ss:StringStream):
    ss.seek_to_not_space(inline=True)
    if ss.show(1) == C_DELIMITER:
        ss.seek(1)
        return True
    return False

def get_item_CommandController(ss):
    id = get_item_id(ss, mode=DEFN_MODE)
    checkx(ss, "ContollerID", id, list(CTRL_ID_CLS_DIC.keys()))

    need_next_item(ss, "ControllerParameterType/Enable")
    typ = get_item_id(ss).upper()

    # Enableだけ
    if typ in ["0","1"]:
        return CommandController(id, ControllerBase.Parameter.ENABLE, typ)

    cls = CTRL_ID_CLS_DIC[id]

    prm_list = []
    prm_list.extend(ControllerBase.Parameter.get_list())
    if cls is not None:
        prm_list.extend(cls.Parameter.get_list())
    checkx(ss, "ControllerParameterType", typ, prm_list)

    need_next_item(ss)
    dat = ""
    if typ == ControllerBase.Parameter.RESET:
        pass
    elif typ == ControllerBase.Parameter.ENABLE:
        dat = get_item_flag(ss)
    elif typ == ControllerBase.Parameter.MUTE:
        dat = get_item_flag(ss)
    elif typ == ControllerBase.Parameter.MODIFY_VALUE:
        dat = get_item_id(ss)
        checkx(ss, typ, dat, ModifyValue.get_list())
    elif typ == ControllerBase.Parameter.MODIFY_TYPE:
        dat = get_item_id(ss)
        checkx(ss, typ, dat, ModifyType.get_list())
    elif cls == Modulation:
        if typ == Modulation.Parameter.WAVE:
            dat = get_item_id(ss)
            checkx(ss, typ, dat, WaveForm.get_list)
        elif typ == Modulation.Parameter.DELAY_TICK:
            dat, flgs = get_item_num(ss, ValueAdaptPackage.INT)
            checkx(ss, typ, dat, int, 0)
        elif typ == Modulation.Parameter.ATTACK_TICK:
            dat, flgs = get_item_num(ss, ValueAdaptPackage.INT)
            checkx(ss, typ, dat, int, 1)
        elif typ == Modulation.Parameter.INI_VALUE:
            dat, flgs = get_item_num(ss, ValueAdaptPackage.REAL)
            checkx(ss, typ, dat, float, 0)
        elif typ == Modulation.Parameter.PERIOD_TICK:
            dat, flgs = get_item_num(ss, ValueAdaptPackage.INT)
            checkx(ss, typ, dat, int, 1)
        elif typ == Modulation.Parameter.AMPLIFY:
            dat, flgs = get_item_num(ss, ValueAdaptPackage.REAL)
            # checkx(ss, "AMPLIFY", dat, float, 0.0, 1.0)
        elif typ == Modulation.Parameter.DUTY:
            dat, flgs = get_item_num(ss, ValueAdaptPackage.REAL)
            checkx(ss, typ, dat, float, 0.0, 1.0)
    elif cls == Envelope:
        if typ == Envelope.Parameter.INI_VALUE:
            dat, flgs = get_item_num(ss, ValueAdaptPackage.REAL)
            checkx(ss, typ, dat, float, 0.0)
        elif typ == Envelope.Parameter.ATTACK_TICK:
            dat, flgs = get_item_num(ss, ValueAdaptPackage.INT)
            checkx(ss, typ, dat, int, 0)
        elif typ == Envelope.Parameter.ATTACK_VALUE:
            dat, flgs = get_item_num(ss, ValueAdaptPackage.REAL)
            checkx(ss, typ, dat, float, 0)
        elif typ == Envelope.Parameter.DECAY_TICK:
            dat, flgs = get_item_num(ss, ValueAdaptPackage.INT)
            checkx(ss, typ, dat, int, 0)
        elif typ == Envelope.Parameter.DECAY_VALUE:
            dat, flgs = get_item_num(ss, ValueAdaptPackage.REAL)
            checkx(ss, typ, dat, float, 0)
        elif typ == Envelope.Parameter.SUSTAIN_TICK:
            dat, flgs = get_item_num(ss, ValueAdaptPackage.INT)
            checkx(ss, typ, dat, int, 0)
        elif typ == Envelope.Parameter.SUSTAIN_VALUE:
            dat, flgs = get_item_num(ss, ValueAdaptPackage.REAL)
            checkx(ss, typ, dat, float, 0)
        elif typ == Envelope.Parameter.RELEASE_RATE:
            dat, flgs = get_item_num(ss, ValueAdaptPackage.REAL)
            checkx(ss, typ, dat, float, 0)
    elif cls == ControllerRaw:
        while True:
            value, flgs = get_item_num(ss, ValueAdaptPackage.INT, flg_seek_to_not_space=True)
            if ss.show(1) == '*':
                ss.seek(1)
                v, flgs = get_item_num(ss, ValueAdaptPackage.INT, flg_seek_to_not_space=False)
                value += "*" + v
            if not is_next_item(ss):
                break
            dat += " " + value
        dat.strip()
    elif cls == Portamento:
        if typ == Portamento.Parameter.TIME:
            dat, flgs = get_item_num(ss, ValueAdaptPackage.INT)
            checkx(ss, typ, dat, int, 0)
        elif typ == Portamento.Parameter.CONTROL:
            dat, flgs = get_item_num(ss, ValueAdaptPackage.INT)
            checkx(ss, typ, dat, int, -1)
    elif cls == Sweep:
        if typ == Sweep.Parameter.VOLUME_INI:
            dat, flgs = get_item_num(ss, ValueAdaptPackage.INT)
            checkx(ss, typ, dat, int)
        elif typ == Sweep.Parameter.STEP:
            dat, flgs = get_item_num(ss, ValueAdaptPackage.INT)
            checkx(ss, typ, dat, int, 1)
        elif typ == Sweep.Parameter.VOLUME:
            dat, flgs = get_item_num(ss, ValueAdaptPackage.INT)
            checkx(ss, typ, dat, int)
    if len(dat) == 0:
        printx(ss, len(typ), "Unknown parameter type.")

    return CommandController(id, typ, dat)

def get_sig(ss:StringStream):
    sig = SignatureType.NONE
    s = ss.show(2)
    if len(s) == 2:
        if s == (C_SHARP + C_SHARP):
            sig = SignatureType.DOUBLE_SHARP
            ss.seek(2)
        if s == (C_FLAT + C_FLAT):
            sig = SignatureType.DOUBLE_FLAT
            ss.seek(2)
    if sig == SignatureType.NONE and len(s) >= 1:
        if s[0] == C_SHARP:
            sig = SignatureType.SHARP
            ss.seek(1)
        elif s[0] == C_FLAT:
            sig = SignatureType.FLAT
            ss.seek(1)
        elif s[0] == C_NATURAL:
            sig = SignatureType.NATURAL
            ss.seek(1)
    return sig

class ctrl_prm_item:
    def __init__(self, name, char, min, max, prm):
        self.name  = name
        self.char  = char
        self.min   = min
        self.max   = max
        self.prm   = prm

def get_controller_idx_value_list(ss:StringStream, ctrl_id, item_list):
    idx_value_list = []
    c = ss.show(1)
    for i in range(len(item_list)):
        if c == item_list[i].char:
            ss.seek(1)
            val, flgs = get_item_num(ss, ValueAdaptPackage.INT)
            checkx(ss, f"{ctrl_id} {item_list[i].name}", val, int, item_list[i].min, item_list[i].max)
            idx_value_list.append([i, int(val)])
            break
    if len(idx_value_list) == 0:
        for i in range(len(item_list)):
            val, flgs = get_item_num(ss, ValueAdaptPackage.INT, True)
            if ValueAdapt.OMISSION not in flgs:
                checkx(ss, f"{ctrl_id} {item_list[i].name}", val, int, item_list[i].min, item_list[i].max)
                idx_value_list.append([i, int(val)])
            if not is_next_item(ss):
                break
    for i in range(len(idx_value_list)):
        idx = idx_value_list[i][0]
        if item_list[idx].prm == ControllerBase.Parameter.MODIFY_VALUE:
            idx_value_list[i][1] = CTRL_MODIFYVALUE_DIC[idx_value_list[i][1]]
        if item_list[idx].prm == Modulation.Parameter.WAVE:
            idx_value_list[i][1] = CTRL_WAVEFORM_DIC[idx_value_list[i][1]]
    return idx_value_list

def get_seq(ss:StringStream):
    cmd_list = []
    ss.seek_to_not_space()
    c = ss.read(1)

    if c in KEY_LIST:
        note = KEY_TO_NOTE_DIC[c]
        sig = get_sig(ss)
        omi, length, dot, tick = get_tadpole_length(ss, omission=True)
        cmd_list.append(CommandTadpole(note, sig, omi, length, dot, tick))

    elif c == C_KEYONOFF:
        if get_item_flag(ss, False) == 0:
            cmd_list.append(CommandKeyOff())
        else:
            cmd_list.append(CommandKeyOn())

    elif c == C_LENGTH_DEF:
        omi, length, dot, tick = get_tadpole_length(ss, omission=False)
        cmd_list.append(CommandLength(length, dot, tick))

    elif c == C_MUTE:
        sw = get_item_flag(ss)
        typ = MuteType.CHANNEL
        tgt = ""
        if is_next_item(ss):
            typ = get_item_id(ss).upper()
            checkx(ss, "MuteType", typ, MuteType.get_list())
            if typ == MuteType.CHIP:
                pass
            elif typ == MuteType.CHANNEL:
                if is_next_item(ss):
                    tgt, flgs = get_item_num(ss, ValueAdaptPackage.INT)
            elif typ == MuteType.TRACK:
                if is_next_item(ss):
                    tgt = get_item_id(ss)
            elif typ == MuteType.SEQUENCE:
                if is_next_item(ss):
                    tgt = get_item_id(ss)
            elif typ == MuteType.CONTROL:
                if is_next_item(ss):
                    id = get_item_id(ss)
                    tgt = ch + " " + id
                    if is_next_item(ss):
                        ch, flgs = get_item_num(ss, ValueAdaptPackage.INT)
                        checkx(ss, "ChannelNo", ch, int, 0)
            else:
                printx(ss, 1, "Unknown MuteType")
        cmd_list.append(CommandMute(typ, tgt, sw))

    elif c == C_NOTE:
        value, flgs = get_item_num(ss, ValueAdaptPackage.VV)
        cmd_list.append(make_vv_cmd(CommandNote, value, flgs))

    elif c == C_OCTAVE:
        value, flgs = get_item_num(ss, ValueAdaptPackage.VV)
        cmd_list.append(make_vv_cmd(CommandOctave, value, flgs))

    elif c == C_PAN:
        value, flgs = get_item_num(ss, ValueAdaptPackage.VV)
        cmd_list.append(make_vv_cmd(CommandPan, value, flgs))

    elif c == C_QUONTIZE:
        shv, flgs = get_item_num(ss, ValueAdaptPackage.INT, True, 0)
        checkx(ss, "Shave", shv, int, 0)
        lve = 1
        rto = 1.0
        if is_next_item(ss):
            lve, flgs = get_item_num(ss, ValueAdaptPackage.INT, True, 1)
            checkx(ss, "Leave", lve, int, 1)
            if is_next_item(ss):
                rto, flgs = get_item_num(ss, ValueAdaptPackage.REAL, True, 1.0)
                checkx(ss, "Ratio", rto, float, 0, 1.0)
        cmd_list.append(CommandQuantize(shv, lve, rto))

    elif c == C_REST:
        omi, length, dot, tick = get_tadpole_length(ss, omission=True)
        cmd_list.append(CommandRest(omi, length, dot, tick))

    elif c == C_TARGET:
        id = get_item_id(ss, mode=DEFN_MODE)
        need_next_item(ss, "DevicePort")
        dp, flgs = get_item_num(ss, ValueAdaptPackage.INT)
        checkx(ss, "DevicePort", dp, int, 0)
        need_next_item(ss, "ChipNo")
        cn, flgs = get_item_num(ss, ValueAdaptPackage.INT)
        checkx(ss, "ChipNo", cn, int, 0)
        cmd_list.append(CommandTarget(id, dp, cn))

    elif c == C_TEMPO:
        value, flgs = get_item_num(ss, ValueAdaptPackage.VV)
        cmd_list.append(make_vv_cmd(CommandTempo, value, flgs))

    elif c == C_UNIQUE:
        typ = get_item_id(ss)
        checkx(ss, "UniqueType", typ, UniqueType.get_list())
        need_next_item(ss, "command")
        cmd = get_item_id(ss)
        data = []
        while True:
            if is_next_item(ss):
                data.append(get_item_id(ss))
                continue
            break
        cmd_list.append(CommandUnique(typ, cmd, " ".join(data)))

    elif c == C_VOLUME:
        value, flgs = get_item_num(ss, ValueAdaptPackage.VV)
        cmd_list.append(make_vv_cmd(CommandVolume, value, flgs))

    elif c == C_TADPOLE_X:
        omi, length, dot, tick = get_tadpole_length(ss, omission=True)
        cmd_list.append(CommandTadpole(-1, SignatureType.NONE, omi, length, dot, tick))

    elif c == C_REGISTER:
        adr, flgs = get_item_num(ss, ValueAdaptPackage.INT)
        checkx(ss, "Address", adr, int, 0)
        need_next_item(ss, "Data")
        dat, flgs = get_item_num(ss, ValueAdaptPackage.INT)
        checkx(ss, "Data", dat, int, 0)
        if is_next_item(ss):
            ss.seek(-1)
            dat_list = [int(dat)]
            while is_next_item(ss):
                dat, flgs = get_item_num(ss, ValueAdaptPackage.INT)
                checkx(ss, "Data", dat, int, 0)
                dat_list.append(int(dat))
            cmd_list.append(CommandRegister(adr, dat_list))
        else:
            cmd_list.append(CommandRegister(adr, int(dat)))

    elif c == C_TUNING:
        o4a, flgs = get_item_num(ss, ValueAdaptPackage.REAL)
        checkx(ss, "o4aFrequency", o4a, float, 1.0)
        cmd_list.append(CommandTuning(o4a))

    elif c == C_BAR_TICKS:
        bt, flgs = get_item_num(ss, ValueAdaptPackage.INT)
        checkx(ss, "BarTicks", bt, int, 1)
        cmd_list.append(CommandBarTicks(bt))

    elif c == C_CHANNEL:
        ch, flgs = get_item_num(ss, ValueAdaptPackage.INT)
        checkx(ss, "ChannelNo", ch, int, 0)
        cmd_list.append(CommandChannel(ch))

    elif c == C_DETUNE:
        value, flgs = get_item_num(ss, ValueAdaptPackage.VV)
        cmd_list.append(make_vv_cmd(CommandDetune, value, flgs))

    elif c == C_CTRL_ENV:
        prm_list = [ctrl_prm_item("FirstLevel",   "F", 0,  100, Envelope.Parameter.INI_VALUE),
                    ctrl_prm_item("AttackTick",   "A", 0, None, Envelope.Parameter.ATTACK_TICK),
                    ctrl_prm_item("DecayTick",    "D", 0, None, Envelope.Parameter.DECAY_TICK),
                    ctrl_prm_item("DecayLevel",   "C", 0,  100, Envelope.Parameter.DECAY_VALUE),
                    ctrl_prm_item("SustainTick",  "S", 0, None, Envelope.Parameter.SUSTAIN_TICK),
                    ctrl_prm_item("SustainLevel", "U", 0,  100, Envelope.Parameter.SUSTAIN_VALUE),
                    ctrl_prm_item("ReleaseRate",  "R", 0, 1000, Envelope.Parameter.RELEASE_RATE),
                    ctrl_prm_item("Enable",       "E", 0,    1, Envelope.Parameter.ENABLE)]
        idx_value_list = get_controller_idx_value_list(ss, CTRL_ID_E, prm_list)
        for (idx, value) in idx_value_list:
            if idx in [0, 3, 5, 6]:
                value /= prm_list[idx].max
            cmd_list.append(CommandController(CTRL_ID_E, prm_list[idx].prm, value))

    elif c == C_FM_OPERATOR:
        op = [1, 1, 1, 1, 1, 1]
        for i in range(len(op)):
            if not is_next_item(ss):
                break
            op[i] = get_item_flag(ss, True, 1)
        cmd_list.append(CommandOperator(*op))

    elif c == C_SIGNATURE:
        ret = ss.show_block(push_block=True)
        if len(ret) == 0:
            printx(ss, 1, "Failed to read sigunature block.")
        ss.seek(1)

        ss.seek_to_not_space()
        c = ss.read(1)
        checkx(ss, "Signature", c, list(SIG_DIC.keys())[1:4])
        sig = SIG_DIC[c]

        sl = [SignatureType.NONE] * 7
        while not ss.eob():
            ss.seek_to_not_space()
            n = ss.read(1)
            checkx(ss, "note", n, KEY_LIST)
            idx = KEY_LIST.index(n)
            sl[idx] = sig
        cmd_list.append(CommandSignature(*sl))
        ss.block_reset()
        ss.seek(1)

    elif c == C_LOOP_INF:
        cmd_list.append(CommandLoopInfinity())

    elif c == C_CTRL_MODULATION:
        prm_list = [ctrl_prm_item("Delay",   "D", 0, None, Modulation.Parameter.DELAY),
                    ctrl_prm_item("Amplify", "A", 0, None, Modulation.Parameter.AMPLIFY),
                    ctrl_prm_item("Period",  "P", 1, None, Modulation.Parameter.PERIOD),
                    ctrl_prm_item("Wave",    "W", 0,    4, Modulation.Parameter.WAVE),
                    ctrl_prm_item("Value",   "V", 0,    3, Modulation.Parameter.MODIFY_VALUE),
                    ctrl_prm_item("Enable",  "E", 0,    1, Modulation.Parameter.ENABLE)]
        idx_value_list = get_controller_idx_value_list(ss, CTRL_ID_M, prm_list)
        for (idx, value) in idx_value_list:
            cmd_list.append(CommandController(CTRL_ID_M, prm_list[idx].prm, value))

    elif c == C_CTRL_PORTAMENTO:
        prm_list = [ctrl_prm_item("Time",    "T",  0, None, Portamento.Parameter.TIME),
                    ctrl_prm_item("Control", "C", -1,  127, Portamento.Parameter.CONTROL),
                    ctrl_prm_item("Enable",  "E",  0,    1, Portamento.Parameter.ENABLE)]
        idx_value_list = get_controller_idx_value_list(ss, CTRL_ID_P, prm_list)
        for (idx, value) in idx_value_list:
            cmd_list.append(CommandController(CTRL_ID_P, prm_list[idx].prm, value))

    elif c == C_CTRL_RAW:
        c = ss.show(1)
        if c in "VE":
            prm_list = [ctrl_prm_item("Value",  "V", 0, 3, ControllerRaw.Parameter.MODIFY_VALUE),
                        ctrl_prm_item("Enable", "E", 0, 1, ControllerRaw.Parameter.ENABLE)]
            idx_value_list = get_controller_idx_value_list(ss, CTRL_ID_R, prm_list)
            for (idx, value) in idx_value_list:
                cmd_list.append(CommandController(CTRL_ID_R, prm_list[idx].prm, value))
        else:
            if c == "D":
                ss.seek(1)
            if ss.is_block_begin() == False:
                printx(ss, 1, "Please use block formatting. -> {1 2 L 3 4 R 5 6}")
            value = ss.read_block()
            cmd_list.append(CommandController(CTRL_ID_R, ControllerRaw.Parameter.DATA, value))

    elif c == C_CTRL_SWEEP:
        prm_list = [ctrl_prm_item("Amount", "A", None, None, Sweep.Parameter.VOLUME),
                    ctrl_prm_item("Step",   "S",    1, None, Sweep.Parameter.STEP),
                    ctrl_prm_item("Value",  "V",    0,    3, Sweep.Parameter.MODIFY_VALUE),
                    ctrl_prm_item("Enable", "E",    0,    1, Sweep.Parameter.ENABLE)]
        idx_value_list = get_controller_idx_value_list(ss, CTRL_ID_S, prm_list)
        for (idx, value) in idx_value_list:
            cmd_list.append(CommandController(CTRL_ID_S, prm_list[idx].prm, value))

    elif c == C_MASTER_VOLUME:
        value, flgs = get_item_num(ss, ValueAdaptPackage.VV)
        cmd_list.append(make_vv_cmd(CommandMasterVolume, value, flgs))

    elif c == C_WAIT:
        ms, flgs = get_item_num(ss, ValueAdaptPackage.REAL, True, 1)
        checkx(ss, "msec", ms, float, 0)
        cmd_list.append(CommandWait(ms))

    elif c == C_PRIORITY:
        pri, flgs = get_item_num(ss, ValueAdaptPackage.INT)
        checkx(ss, "Proprity", pri, int, 0)
        cmd_list.append(CommandPriority(pri))

    elif c == C_MACRO:
        id = get_item_id(ss, mode=DEFN_MODE)
        if id not in MACRO_DIC.keys():
            printx(ss, -len(id), f"not define macro id. -> {id}", -1)
        values = []
        index = 0
        m = MACRO_DIC[id]
        while is_next_item(ss):
            prm = m.get_prm(index)
            val = ""
            if prm.type == Macro.Parameter.Type.ID:
                val = get_item_id(ss)
            elif prm.type == Macro.Parameter.Type.INT:
                val, flgs = get_item_num(ss, ValueAdaptPackage.INT, True, prm.value)
            elif prm.type == Macro.Parameter.Type.REAL:
                val, flgs = get_item_num(ss, ValueAdaptPackage.REAL, True, prm.value)
            elif prm.type == Macro.Parameter.Type.FLAG:
                val = str(get_item_flag(ss, True, prm.value))
            values.append(val)
            index += 1
        mml = MACRO_DIC[id].get_replace(values)
        mss = StringStream(mml, f"Macro({id})", "utf-8")
        while mss.eof() == False:
            mss.seek_to_not_space()
            c = mss.show(1)
            if c == C_PART:
                printx(mss, 1, "Can't use \"{C_PART}\" in macro define.")
            cl = get_seq(mss)
            cmd_list.extend(cl)

    elif c == C_TRACKER:
        seq_id = get_item_id(ss, mode=DEFN_MODE)
        type = 0 # 0=call 1=jump 2=kick
        if is_next_item(ss):
            val, flgs = get_item_num(ss, ValueAdaptPackage.INT, False)
            type = int(val)
            checkx(ss, "TrackerType", type, int, 0, 2)
        if type == 0: # call
            cmd_list.append(CommandCall(seq_id))
        elif type == 1: # jump
            cmd_list.append(CommandJump(seq_id))
        elif type == 2: # kick
            if is_next_item(ss):
                trk_id = get_item_id(ss, mode=DEFN_MODE)
            else:
                trk_id = ""
            cmd_list.append(CommandTrack(seq_id, trk_id))

    elif c == C_TAI_SLAR:
        if ss.show(1) == C_TAI_SLAR:
            ss.seek(1)
            cmd_list.append(CommandSlur())
        else:
            cmd_list.append(CommandTie())

    elif c == C_PARAMETER:
        prm = get_item_id(ss)
        need_next_item(ss, "ParameterData")
        dat, flags = get_item_num(ss, ValueAdaptPackage.INT)
        checkx(ss, "ParameterData", int, 0)
        cmd_list.append(CommandParameter(prm, dat))

    elif c == C_VOLUME_UP:
        val, flags = get_item_num(ss, ValueAdaptPackage.INT, True, "1", False)
        cmd_list.append(CommandVolume(VariableValue.RELATIVE0, int(val)))

    elif c == C_VOLUME_DOWN:
        val, flags = get_item_num(ss, ValueAdaptPackage.INT, True, "1", False)
        cmd_list.append(CommandVolume(VariableValue.RELATIVE0, -int(val)))

    elif c == C_CONTROLLER:
        cmd = get_item_CommandController(ss)
        if cmd is not None:
            cmd_list.append(cmd)

    elif c == C_LOOP_EXIT:
        cmd_list.append(CommandLoopBreak())

    elif c == C_OCTAVE_DOWN:
        val, flgs = get_item_num(ss, ValueAdaptPackage.INT, True, "1", False)
        cmd_list.append(CommandOctave(VariableValue.RELATIVE0, -int(val)))

    elif c == C_OCTAVE_UP:
        val, flgs = get_item_num(ss, ValueAdaptPackage.INT, True, "1", False)
        cmd_list.append(CommandOctave(VariableValue.RELATIVE0, int(val)))

    elif c == C_DEBUG:
        typ = get_item_id(ss)
        if typ in DebugType.get_list():
            checkx(ss, "DebugType", typ, DebugType.get_list())
            dat = ""
            if is_next_item(ss):
                dat = get_item_id(ss)
            cmd_list.append(CommandDebug(typ, dat))
        if typ == CommandStopWatch.BOTTOM_CMD:
            need_next_item(ss, "StopwatchID")
            id = get_item_id(ss)
            cmd_list.append(CommandStopWatch(id))
        if typ == CommandReset.BOTTOM_CMD:
            rtp = ResetType.PLAYBACK_STATUS
            tgt = "0"
            if is_next_item(ss):
                rtp = get_item_id(ss)
                checkx(ss, "ResetType", rtp, ResetType.get_list())
                if is_next_item(ss):
                    tgt = get_item_id(ss)
            cmd_list.append(CommandReset(rtp, tgt))

    elif c == C_TONE:
        id = get_item_id(ss, mode=DEFN_MODE)
        cmd_list.append(CommandTone(id))

    elif c == C_LOOP_BEIGN:
        times, flgs = get_item_num(ss, ValueAdaptPackage.INT, True, "2", False)
        checkx(ss, "LoopTimes", times, int, 1)
        cmd_list.append(CommandLoopBegin(times))

    elif c == C_LOOP_END:
        cmd_list.append(CommandLoopEnd())

    elif c == C_LENGTH_ADD:
        omi, length, dot, tick = get_tadpole_length(ss, omission=True)
        cmd_list.append(CommandTie())
        cmd_list.append(CommandTadpole(-1, SignatureType.NONE, omi, length, dot, tick))

    elif c == C_MAPPER:
        id = get_item_id(ss, mode=DEFN_MODE)
        need_next_item(ss)
        enable = get_item_flag(ss)
        cmd_list.append(CommandMapper(id, enable))

    elif c == C_SWEEP_BEIGN:
        # from_note
        ss.seek_to_not_space()
        c = ss.read(1)
        checkx(ss, "StartNote", c, KEY_LIST)
        from_note = KEY_TO_NOTE_DIC[c]
        from_sig = get_sig(ss)
        # octave
        oct = 0
        while True:
            ss.seek_to_not_space()
            c = ss.show(1)
            if c == C_OCTAVE_UP:
                ss.seek(1)
                oct += 1
            elif c == C_OCTAVE_DOWN:
                ss.seek(1)
                oct -= 1
            else:
                break
        # to_note
        ss.seek_to_not_space()
        c = ss.read(1)
        checkx(ss, "TargetNote", c, KEY_LIST)
        to_note = KEY_TO_NOTE_DIC[c]
        to_sig = get_sig(ss)
        # end
        ss.seek_to_not_space()
        c = ss.show(1)
        if c != C_SWEEP_END:
            printx(ss, 1, "failed to read end of blcok.")
        ss.seek(1)
        # length
        omi, length, dot, tick = get_tadpole_length(ss, omission=True)
        # command
        cmd_list.append(CommandPortamento(from_note, from_sig, oct))
        if oct != 0:
            cmd_list.append(CommandOctave(VariableValue.RELATIVE0, oct))
        cmd_list.append(CommandTadpole(to_note, to_sig, omi, length, dot, tick))

    elif c == C_NO_FUNC:
        pass

    elif c in [' ','\n','\t']:
        pass

    else:
        printx(ss, 1, "Unkown command. -> " + c, -1)

    return cmd_list

def get_part_list(ss:StringStream, part_list_base):
    part_list = []
    ss.seek(1)
    length = len(ss.show_to_space(inline=True))
    end_index = ss.index + length
    a = None
    while ss.index < end_index:
        if ss.show(1) == C_PART_ORIGIN:
            part_list.append(C_PART_ORIGIN)
            ss.seek(1)
            continue
        n = None
        if ss.is_alphabet_upper():
            a = ss.read(1)
        elif ss.is_number() and a is not None:
            n = ss.read(1)
        else:
            printx(ss, 1, "Please, use capital letter.")
        if n is None:
            if ss.is_space() or ss.is_alphabet_upper() or ss.is_c(C_PART_ORIGIN):
                n = "0"
            elif ss.is_number():
                n = ss.read(1)
            else:
                printx(ss, 1, "Please, use a number.")
        part = a + n
        if part not in part_list_base:
            printx(ss, 1, "Can't use this part.")
        if part in part_list:
            printx(ss, 1, "it is same part.")
        part_list.append(part)
    return part_list

class StandardMML(MMLBase):
    MML_TYPE = MML_Type.STANDARD

    @staticmethod
    def compile(builder:MMLBuilder, filename:str, encode:str):
        with open(filename,"r",encoding=encode) as f:
            data = f.read()
        
        data = MMLBase.comment_toggle(data, 0, C_COMMENT * 4)
        data = MMLBase.comment_range(data, 0, C_COMMENT * 2 + "<", C_COMMENT * 2 + ">")
        data = MMLBase.comment_line(data, C_COMMENT)
        data = MMLBase.comment_toggle(data, 0, '"')
        data = MMLBase.delete_end(data, C_CR_CANCEL)
        ss = StringStream(data, filename, encode)

        # seq_idのlist
        part_list = [ORIGIN_SEQUENCE_ID] # 現在の出力先
        part_list_base = [ORIGIN_SEQUENCE_ID] # 行頭で更新

        # controller定義
        builder.add_seq_data(ORIGIN_SEQUENCE_ID, [
            CommandControllerData(CTRL_ID_M, ControllerType.MODULATION, "PITCH RELATIVE SIN 0 30 24"),
            CommandControllerData(CTRL_ID_E, ControllerType.ENVELOPE, "VOLUME MULTIPLE 0.5 24 1.0 24 0.5 96 0.2 0.010"),
            CommandControllerData(CTRL_ID_R, ControllerType.RAW, "VOLUME CURRENT 15 L 15 R 0"),
            CommandControllerData(CTRL_ID_S, ControllerType.SWEEP, "PITCH RELATIVE 0 1 -10"),
            CommandControllerData(CTRL_ID_P, ControllerType.PORTAMENTO, "NOTE RELATIVE 12 -1"),
        ])

        ss.seek_to_not_space()
        while ss.eof() == False:
            c = ss.show(1)

            if ss.bol() and c == C_DEFINE:
                cmd_list = get_define(ss, builder)
                if len(cmd_list) > 0:
                    builder.add_seq_data(ORIGIN_SEQUENCE_ID, cmd_list)

            elif ss.bol() and c == C_PART:
                part_list_base = get_part_list(ss, DEF_PART_LIST)
                if len(part_list_base) == 0:
                    printx(ss, 1, "Please, define the part.")
                if C_PART_ORIGIN in part_list_base:
                    if len(part_list_base) == 1:
                        part_list_base = [ORIGIN_SEQUENCE_ID]
                    else:
                        printx(ss, 1, "Please specify only the ORIGIN part in base part.", -1)
                part_list = copy.copy(part_list_base)

            elif c == C_PART:
                    temp = get_part_list(ss, part_list_base)
                    if C_PART_ORIGIN in temp:
                        printx(ss, 1, "Can't use the origin part in sliced part.", -1)
                    if len(temp) == 0:
                        part_list = copy.copy(part_list_base)
                    else:
                        part_list = temp
            else:
                cmd_list = get_seq(ss)
                if len(cmd_list) > 0:
                    for part in part_list:
                        builder.add_seq_data(part, cmd_list)

            ss.seek_to_not_space()
