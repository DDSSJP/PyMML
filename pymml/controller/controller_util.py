from ..define import ControllerType
from .envelope import Envelope
from .modulation import Modulation
from .portamento import Portamento
from .controller_raw import ControllerRaw
from .sweep import Sweep

_ctrl_cls_type_dic = {
    Envelope: ControllerType.ENVELOPE,
    Modulation: ControllerType.MODULATION,
    Portamento: ControllerType.PORTAMENTO,
    ControllerRaw: ControllerType.RAW,
    Sweep: ControllerType.SWEEP,
    }

_ctrl_type_cls_dic = {
    ControllerType.ENVELOPE: Envelope,
    ControllerType.MODULATION: Modulation,
    ControllerType.PORTAMENTO: Portamento,
    ControllerType.RAW: ControllerRaw,
    ControllerType.SWEEP: Sweep,
    }

def controller_cls_to_type(cls):
    if cls in _ctrl_cls_type_dic.keys():
        return _ctrl_cls_type_dic[cls]
    raise Exception(f"unknown controller class. -> {cls}")

def controller_type_to_cls(type):
    if type in _ctrl_type_cls_dic.keys():
        return _ctrl_type_cls_dic[type]
    raise Exception(f"unknown controller type. -> {type}")

