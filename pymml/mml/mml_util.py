from ..define import MML_Type
from ..command import *

def mml_type_to_cls(type):
    cls = None
    if type == MML_Type.BOTTOM:
        from .bottommml import BottomMML
        cls = BottomMML
    elif type == MML_Type.STANDARD:
        from .standardmml import StandardMML
        cls = StandardMML
    else:
        raise Exception(f"Unknown mml type. -> {type}")
    return cls

def mml_cls_to_type(cls):
    type = None
    if hasattr(cls, "MML_TYPE"):
        type = cls.MML_TYPE
    else:
        type = MML_Type.UNKNOWN
    return type

def cmdlist_to_seqdic(cmd_list):
    dic = {}
    crnt_id = ""
    pre_id = []
    for cmd in cmd_list:
        if type(cmd) == CommandSequenceBegin:
            if cmd.id not in dic.keys():
                dic[cmd.id] = [cmd]
            pre_id.append(crnt_id)
            crnt_id = cmd.id
        elif type(cmd) == CommandSequenceEnd:
            dic[crnt_id].append(cmd)
            crnt_id = pre_id.pop()
        else:
            if len(crnt_id) > 0:
                dic[crnt_id].append(cmd)
    return dic

def get_mml_type(filename):
    data = bytes()
    with open(filename, "rb") as f:
        while len(data) < 256:
            b = f.read(1)
            if len(b) == 0 or not b.isascii():
                break
            data = data + b

    mmltype = MML_Type.UNKNOWN
    version = "0"
    encode = "utf_8"

    if len(data) > 16:
        data = data.decode("ascii")
        lines = data.splitlines()
        for line in lines:
            idx = line.strip().find("@MML_TYPE")
            if idx >= 0:
                items = line[idx:].split(',')
                if len(items) >= 4:
                    mmltype = items[1].strip().upper()
                    version = items[2].strip()
                    encode = items[3].strip()
                    break

    return (mmltype, version, encode)

RESET_CMD_LIST = [
        CommandChannel,
        CommandReset,
        CommandCall,
        CommandJump,
        CommandSequenceBegin,
        CommandSequenceEnd,
        CommandLoopBegin,
        CommandLoopEnd,
        CommandLoopInfinity,
        CommandRest,
    ]
def proc_slur_tie(seq):
    flg_tie = False
    idx = -1
    for i in range(len(seq)):
        cmd = seq[i]
        typ = type(cmd)
        if typ == CommandSlur or typ == CommandTie:
            flg_tie = typ == CommandTie
            if idx > 0:
                seq[idx].key_off = 0
                idx = -1
        elif typ == CommandTadpole:
            if flg_tie:
                seq[i].key_on = 0
            flg_tie = False
            idx = i
        elif typ in RESET_CMD_LIST:
            flg_tie = False
            idx = -1
