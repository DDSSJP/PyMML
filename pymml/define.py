# 最初のsequence_id
ORIGIN_SEQUENCE_ID = "ORIGIN_SEQUENCE_ID"

# FM音源が1チャンネルにもつオペレータの最大数
OP_NUM = 6

class TypeList:
    _key = None
    @classmethod
    def _setup(cls):
        cls._key = []
        for key in vars(cls).keys():
            if key.startswith('_') == False:
                cls._key.append(key)
        cls._key = tuple(cls._key)

    @classmethod
    def get_list(cls):
        if cls._key is None:
            cls._setup()
        return cls._key

    @classmethod
    def value(cls, key):
        if cls._key is None:
            cls._setup()
        return getattr(cls, key)

    @classmethod
    def contein(cls, key):
        if cls._key is None:
            cls._setup()
        return key in cls._key
    

class MML_Type(TypeList):
    UNKNOWN = "UNKNOWN"
    BOTTOM = "BOTTOM"
    STANDARD = "STANDARD"

class ChipType(TypeList):
    UNKNOWN = "UNKNOWN"
    YMF825 = "YMF825"
    YM2203 = "YM2203"
    YM2608 = "YM2608"

class ControllerType(TypeList):
    ENVELOPE = "ENVELOPE"
    MODULATION = "MODULATION"
    PORTAMENTO = "PORTAMENTO"
    RAW = "RAW"
    SWEEP = "SWEEP"

class ModifyType(TypeList):
    CURRENT = "CURRENT"
    RELATIVE = "RELATIVE"
    MULTIPLE = "MULTIPLE"

class ModifyValue(TypeList):
    NOTE = "NOTE"
    VOLUME = "VOLUME"
    PAN = "PAN"
    PITCH = "PITCH"
    # TEMPO = "TEMPO"

class WaveForm(TypeList):
    SIN = "SIN"
    SAW = "SAW"
    TRIANGLE = "TRIANGLE"
    SQUARE = "SQUARE"
    RANDOM = "RANDOM"

class DeviceType(TypeList):
    UNKNOWN = "UNKNOWN"
    MOCK = "MOCK"
    MOCK4 = "MOCK4"
    FT232H = "FT232H"

class ResetType(TypeList):
    PLAYBACK_STATUS = "PLAYBACK_STATUS"
    DEVICE = "DEVICE"
    CHIP = "CHIP"
    MASTERWORK = "MASTERWORK"
    CHANNELWORK = "CHANNELWORK"

class MuteType(TypeList):
    CHIP = "CHIP"
    CHANNEL = "CHANNEL"
    TRACK = "TRACK"
    SEQUENCE = "SEQUENCE"
    CONTROL = "CONTROL"

class UniqueType(TypeList):
    DEVICE = "DEVICE"
    CHIP = "CHIP"

class MapperMode(TypeList):
    MAPPER = "MAPPER"
    DRUM = "DRUM"

class DebugType(TypeList):
    REPORT = "REPORT"
    STATUS = "STATUS"
    PRINT = "PRINT"
    PAUSE = "PAUSE"
    EXIT = "EXIT"
    TRACK = "TRACK"
    MASTERWORK = "MASTERWORK"
    CHANNELWORK = "CHANNELWORK"

class SignatureType(TypeList):
    NONE = "NONE"
    SHARP = "SHARP"
    FLAT = "FLAT"
    NATURAL = "NATURAL"
    DOUBLE_SHARP = "DOUBLE_SHARP"
    DOUBLE_FLAT = "DOUBLE_FLAT"

class DefNameMode(TypeList):
    STRING = "STRING"
    NUMBER = "NUMBER"
