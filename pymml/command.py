from .define import ControllerType, DeviceType, ChipType, ResetType, MuteType, UniqueType, MapperMode, DebugType, SignatureType, ModifyType

class CommandBase:
    BOTTOM_CMD = "NONE"
    
    def __len__(self):
        return len(vars(self)) + 1
    def __str__(self):
        return self.to_bottom()
    def to_dict(self):
        d = {"BOTTOM_CMD":self.BOTTOM_CMD}
        d |= vars(self)
        return d
    def to_list(self):
        return list(self.to_dict().values())
    def to_bottom(self):
        mml = "@" + self.BOTTOM_CMD
        for v in list(vars(self).values()):
            mml += ","
            mml += str(v)
        return mml
    def get_default(self):
        return vars(self.__class__())

class CommandSystem(CommandBase):
    BOTTOM_CMD = "SYSTEM"
    PORT_SPLIT_CHAR = '/'
    def __init__(self, id="", device_type=DeviceType.UNKNOWN, device_id="", info=""):
        self.id = id
        self.device_type = device_type
        self.device_id = device_id
        self.info = info

class CommandTarget(CommandBase):
    BOTTOM_CMD = "TARGET"
    def __init__(self, sys_id="", device_port=0, chip_no=0):
        self.sys_id = sys_id
        self.device_port = int(device_port)
        self.chip_no = int(chip_no)

class CommandDebug(CommandBase):
    BOTTOM_CMD = "DEBUG"
    def __init__(self, debug_type=DebugType.STATUS, data=""):
        self.debug_type = debug_type.upper()
        self.data = data

class CommandStopWatch(CommandBase):
    BOTTOM_CMD = "STOPWATCH"
    def __init__(self, id=""):
        self.id = id

class CommandPath(CommandBase):
    BOTTOM_CMD = "PATH"
    def __init__(self, path=""):
        self.path = path

class CommandInclude(CommandBase):
    BOTTOM_CMD = "INCLUDE"
    def __init__(self, filename=""):
        self.filename = filename

class CommandWait(CommandBase):
    BOTTOM_CMD = "WAIT"
    def __init__(self, value=0): # [msec]
        self.value = int(value)

class CommandTick(CommandBase):
    BOTTOM_CMD = "TICK"
    def __init__(self, value=0):
        self.value = int(value)

class CommandRegister(CommandBase):
    BOTTOM_CMD = "REGISTER"
    def __init__(self, address=0, data=0):
        self.address = int(address)
        self.data = data # int or intのlist

class CommandParameter(CommandBase):
    BOTTOM_CMD = "PARAMETER"
    def __init__(self, parameter="", value=0):
        self.parameter = parameter
        self.value = int(value)

class CommandReset(CommandBase):
    BOTTOM_CMD = "RESET"
    def __init__(self, reset_type=ResetType.CHIP, target="0"):
        self.reset_type = reset_type.upper()
        self.target = target

class CommandMute(CommandBase):
    BOTTOM_CMD = "MUTE"
    def __init__(self, mute_type=MuteType.CHANNEL, target="0", switch=0):
        self.mute_type = mute_type.upper()
        self.target = target
        self.switch = int(switch)

class CommandTitle(CommandBase):
    BOTTOM_CMD = "TITLE"
    def __init__(self, value=""):
        self.value = value

class CommandComposer(CommandBase):
    BOTTOM_CMD = "COMPOSER"
    def __init__(self, value=""):
        self.value = value

class CommandArranger(CommandBase):
    BOTTOM_CMD = "ARRANGER"
    def __init__(self, value=""):
        self.value = value

class CommandMessage(CommandBase):
    BOTTOM_CMD = "MESSAGE"
    def __init__(self, value=""):
        self.value = value

class CommandChannel(CommandBase):
    BOTTOM_CMD = "CHANNEL"
    def __init__(self, value=0):
        self.value = int(value)

class CommandTuning(CommandBase):
    BOTTOM_CMD = "TUNING"
    def __init__(self, value=440.0):
        self.value = float(value)

class CommandToneData(CommandBase):
    BOTTOM_CMD = "TONE_DATA"
    def __init__(self, chip_type=ChipType.UNKNOWN, id="", data=""):
        self.chip_type = chip_type.upper()
        self.id = id
        self.data = data

class CommandUnique(CommandBase):
    BOTTOM_CMD = "UNIQUE"
    def __init__(self, unique_type=UniqueType.DEVICE, cmd="", data=""):
        self.unique_type = unique_type.upper()
        self.cmd = cmd
        self.data = data

class CommandSequenceBegin(CommandBase):
    BOTTOM_CMD = "SEQUENCE_BEGIN"
    def __init__(self, id=""):
        self.id = id

class CommandSequenceEnd(CommandBase):
    BOTTOM_CMD = "SEQUENCE_END"

class CommandTrack(CommandBase):
    BOTTOM_CMD = "TRACK"
    def __init__(self, seq_id="", id=""):
        self.seq_id = seq_id
        self.id = id

class CommandPriority(CommandBase):
    BOTTOM_CMD = "PRIORITY"
    def __init__(self, value=0):
        self.value = int(value)

class CommandCall(CommandBase):
    BOTTOM_CMD = "CALL"
    def __init__(self, seq_id=""):
        self.seq_id = seq_id

class CommandJump(CommandBase):
    BOTTOM_CMD = "JUMP"
    def __init__(self, seq_id=""):
        self.seq_id = seq_id

class CommandLoopBegin(CommandBase):
    BOTTOM_CMD = "LOOP_BEGIN"
    def __init__(self, times=1):
        self.times = int(times)

class CommandLoopEnd(CommandBase):
    BOTTOM_CMD = "LOOP_END"

class CommandLoopBreak(CommandBase):
    BOTTOM_CMD = "LOOP_BREAK"

class CommandLoopInfinity(CommandBase):
    BOTTOM_CMD = "LOOP_INFINITY"

class CommandTempo(CommandBase):
    BOTTOM_CMD = "TEMPO"
    def __init__(self, value_type=ModifyType.CURRENT, value=0):
        self.value_type = value_type.upper()
        self.value = int(value)

class CommandBarTicks(CommandBase):
    BOTTOM_CMD = "BAR_TICKS"
    def __init__(self, tick=192):
        self.tick = int(tick)

class CommandTimeSignature(CommandBase):
    BOTTOM_CMD = "TIME_SIGNATURE"
    def __init__(self, numerator=4, denominator=4):
        self.numerator = numerator
        self.denominator = denominator

class CommandWholeNoteTicks(CommandBase):
    BOTTOM_CMD = "WHOLE_NOTE_TICKS"
    def __init__(self, tick=192):
        self.tick = int(tick)

class CommandRest(CommandBase):
    BOTTOM_CMD = "REST"
    def __init__(self, omission=0, length=4, dot=0, tick=0):
        self.omission  = int(omission) # フラグ 0=省略じゃない 1=である
        self.length    = int(length)   # 音符の分母 整数1以上
        self.dot       = int(dot)      # 付点の数 0以上
        self.tick      = int(tick)     # 0=tickじゃない 1以上=tick数 lengthより優先

class CommandTadpole(CommandBase):
    BOTTOM_CMD = "TADPOLE"
    def __init__(self, note=0, signature=SignatureType.NONE, omission=0, length=4, dot=0, tick=0, key_on=1, key_off=1):
        self.note      = int(note)         # 0～11=c～b  マイナス=CommandNote発行しない
        self.signature = signature.upper() # 臨時記号
        self.omission  = int(omission)     # フラグ 0=省略じゃない 1=である
        self.length    = int(length)       # 音符の分母 整数1以上
        self.dot       = int(dot)          # 付点の数 0以上
        self.tick      = int(tick)         # 0=tickじゃない 1以上=tick数 lengthより優先
        self.key_on    = int(key_on)       # フラグ 0=キーオンしない 1=する
        self.key_off   = int(key_off)      # フラグ 0=キーオフしない 1=する

class CommandPortamento(CommandBase):
    BOTTOM_CMD = "PORTAMENTO"
    def __init__(self, note=0, signature=SignatureType.NONE, octave=0):
        self.note      = int(note)         # 0～11=c～b
        self.signature = signature.upper() # 臨時記号
        self.octave    = int(octave)       # 相対

class CommandLength(CommandBase):
    BOTTOM_CMD = "LENGTH"
    def __init__(self, length=4, dot=0, tick=0):
        self.length = int(length) # 音符の分母 整数1以上
        self.dot    = int(dot)    # 付点の数 0以上
        self.tick   = int(tick)   # 0=tickじゃない 1以上=tick数 lengthより優先

class CommandSlur(CommandBase):
    BOTTOM_CMD = "SLUR"

class CommandTie(CommandBase):
    BOTTOM_CMD = "TIE"

class CommandQuantize(CommandBase):
    BOTTOM_CMD = "QUANTIZE"
    def __init__(self, shave=0, leave=0, ratio=1.0):
        self.shave = int(shave)
        self.leave = int(leave)
        self.ratio = float(ratio)

class CommandSignature(CommandBase):
    BOTTOM_CMD = "SIGNATURE"
    def __init__(self, c=SignatureType.NONE, d=SignatureType.NONE, e=SignatureType.NONE, f=SignatureType.NONE, g=SignatureType.NONE, a=SignatureType.NONE, b=SignatureType.NONE):
        self.c = c.upper()
        self.d = d.upper()
        self.e = e.upper()
        self.f = f.upper()
        self.g = g.upper()
        self.a = a.upper()
        self.b = b.upper()

class CommandKeyOn(CommandBase):
    BOTTOM_CMD = "KEY_ON"

class CommandKeyOff(CommandBase):
    BOTTOM_CMD = "KEY_OFF"

class CommandTone(CommandBase):
    BOTTOM_CMD = "TONE"
    def __init__(self, tone_id=""):
        self.tone_id = tone_id

class CommandNote(CommandBase):
    BOTTOM_CMD = "NOTE"
    def __init__(self, value_type=ModifyType.CURRENT, value=0):
        self.value_type = value_type.upper()
        self.value = int(value)

class CommandVolume(CommandBase):
    BOTTOM_CMD = "VOLUME"
    def __init__(self, value_type=ModifyType.CURRENT, value=0):
        self.value_type = value_type.upper()
        self.value = value

class CommandMasterVolume(CommandBase):
    BOTTOM_CMD = "MASTER_VOLUME"
    def __init__(self, value_type=ModifyType.CURRENT, value=0):
        self.value_type = value_type.upper()
        self.value = value

class CommandPan(CommandBase):
    BOTTOM_CMD = "PAN"
    def __init__(self, value_type=ModifyType.CURRENT, value=0):
        self.value_type = value_type.upper()
        self.value = value

class CommandDetune(CommandBase):
    BOTTOM_CMD = "DETUNE"
    def __init__(self, value_type=ModifyType.CURRENT, value=0):
        self.value_type = value_type.upper()
        self.value = value

class CommandOctave(CommandBase):
    BOTTOM_CMD = "OCTAVE"
    def __init__(self, value_type=ModifyType.CURRENT, value=4):
        self.value_type = value_type.upper()
        self.value = int(value)

class CommandOperator(CommandBase):
    BOTTOM_CMD = "OPERATOR"
    def __init__(self, op1=1, op2=1, op3=1, op4=1, op5=1, op6=1):
        self.op1 = int(op1)
        self.op2 = int(op2)
        self.op3 = int(op3)
        self.op4 = int(op4)
        self.op5 = int(op5)
        self.op6 = int(op6)

class CommandControllerData(CommandBase):
    BOTTOM_CMD = "CONTROLLER_DATA"
    def __init__(self, id="", controller_type=ControllerType.MODULATION, data=""):
        self.id = id
        self.controller_type = controller_type.upper()
        self.data = data

class CommandController(CommandBase):
    BOTTOM_CMD = "CONTROLLER"
    def __init__(self, ctrl_id="", value_type="", value=""):
        self.ctrl_id = ctrl_id
        self.value_type = value_type.upper()
        self.value = value

class CommandMapperData(CommandBase):
    BOTTOM_CMD = "MAPPER_DATA"
    def __init__(self, id="", mode=MapperMode.MAPPER, data=""):
        self.id = id
        self.mode = mode
        self.data = data

class CommandMapper(CommandBase):
    BOTTOM_CMD = "MAPPER"
    def __init__(self, map_id="", enable=0):
        self.map_id = map_id
        self.enable = int(enable)

# コマンドクラスのリスト作成
gdic = {}
gdic |= globals()
btm_cls_dic = {}
for item in gdic.items():
    if item[0].startswith("Command") and type(item[1]) == type:
        btm_cls_dic[item[1].BOTTOM_CMD] = item[1]
del gdic

#スペース削減しないコマンドのリスト
keep_space_list = [
    CommandInclude,
    CommandPath,
    CommandTitle,
    CommandComposer,
    CommandArranger,
    CommandMessage,
]

def get_command_instance(data:str, replace_tn=True):
    # タブ改行変換
    if replace_tn:
        data = data.replace("\t"," ").replace("\n"," ")

    # 分割
    cmd = data.split(",")

    # 種類を取得(大文字)
    btm = cmd[0].upper().strip()

    # クラスを取得
    if btm not in btm_cls_dic.keys():
        raise Exception("unknown command ->", btm)
    cls = btm_cls_dic[btm]

    # スペース削減
    if replace_tn and cls not in keep_space_list:
        for i in range(len(cmd)):
            cmd[i] = cmd[i].strip()
            l = 0
            while l != len(cmd[i]):
                l = len(cmd[i])
                cmd[i] = cmd[i].replace("  ", " ")

    # 長さを確認
    if len(cmd) != len(cls()):
        raise Exception("invalid length ->", data)

    # インスタンスを作成
    return cls(*cmd[1:])
