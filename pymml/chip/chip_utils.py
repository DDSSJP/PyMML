from ..define import ChipType
from .YMF825 import YMF825
# from .YM2203 import YM2203
# from .YM2608 import YM2608

_chip_type_cls_dic = {
    ChipType.YMF825: YMF825,
    # ChipType.YM2203: YM2203,
    # ChipType.YM2608: YM2608,
    }

_chip_cls_type_dic = {
    YMF825: ChipType.YMF825,
    # YM2203: ChipType.YM2203,
    # YM2608: ChipType.YM2608,
    }

def chip_type_to_cls(type):
    if type in _chip_type_cls_dic.keys():
        return _chip_type_cls_dic[type]
    raise Exception(f"unknown chip type. -> {type}")

def chip_cls_to_type(cls):
    if cls in _chip_cls_type_dic.keys():
        return _chip_cls_type_dic[type]
    raise Exception(f"unknown chip class. -> {cls}")
