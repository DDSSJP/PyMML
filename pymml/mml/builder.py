import os
from .mml_util import mml_type_to_cls, get_mml_type, cmdlist_to_seqdic, proc_slur_tie
from ..command import *

DEFINE_CMD_LIST = [
    CommandSystem,
    CommandSequenceBegin,
    CommandToneData,
    CommandControllerData,
    CommandMapperData,
    ]
REFERENCE_CMD_DIC = {
    CommandTarget:(CommandSystem,"sys_id"),
    CommandTrack:(CommandSequenceBegin,"seq_id"),
    CommandCall:(CommandSequenceBegin,"seq_id"),
    CommandJump:(CommandSequenceBegin,"seq_id"),
    CommandTone:(CommandToneData,"tone_id"),
    CommandController:(CommandControllerData,"ctrl_id"),
    CommandMapper:(CommandMapperData,"map_id"),
    }

class MMLBuilder:
    def __init__(self):
        self.include_stack = [] # フルパス ファイル名
        self.path_list = [""] # フルパス /で終わること
        self.seq_dic = {} # key=seq_id  value=seq_data
        self.id_dic = {} # key=def_cls  value=set(id)
        for def_cls in DEFINE_CMD_LIST:
            self.id_dic[def_cls] = set()
        self.reset()

    def build(self, filename):
        self.reset()
        self.proc_include(filename)
    
    def reset(self):
        self.include_stack.clear()
        self.seq_dic.clear()
        self.id_dic.clear()
        for def_cls in DEFINE_CMD_LIST:
            self.id_dic[def_cls] = set()
        self.path_list.clear()
        self.path_list.append("")
        env = os.getenv("PyMmlPath", "")
        if len(env) > 0:
            print("get env path.")
            items = env.split(';')
            for item in items:
                item = item.strip()
                if item.endswith('\\'):
                    item = item[:-1]
                if not item.endswith('/'):
                    item = item + "/"
                self.path_list.append(item.strip())

    def add_seq_data(self, seq_id, seq_data):
        if seq_id not in self.seq_dic.keys():
            self.seq_dic[seq_id] = [CommandSequenceBegin(seq_id), CommandSequenceEnd()]
        if type(seq_data) == list:
            for data in seq_data:
                if type(data) not in [CommandSequenceBegin, CommandSequenceEnd]:
                    self.seq_dic[seq_id].insert(len(self.seq_dic[seq_id]) - 1, data)
        else:
            self.seq_dic[seq_id].insert(-1, seq_data)

    def add_seq_from_cmdlist(self, cmd_list):
        if type(cmd_list) == list:
            seq_dic = cmdlist_to_seqdic(cmd_list)
            for seq_id, seq_data in seq_dic.items():
                self.add_seq_data(seq_id, seq_data)

    def add_def_cmd(self, def_cmd):
        def_cls = type(def_cmd)
        if def_cls not in DEFINE_CMD_LIST:
            return
        self.id_dic[def_cls].add(def_cmd.id)

    def exist_id(self, ref_cmd):
        ref_cls = type(ref_cmd)
        if ref_cls not in REFERENCE_CMD_DIC.keys():
            return True
        def_cls = REFERENCE_CMD_DIC[ref_cls][0]
        ref_id = getattr(ref_cmd, REFERENCE_CMD_DIC[ref_cls][1])
        return ref_id in self.id_dic[def_cls]

    def add_path(self, folder):
        self.path_list.append(folder)    

    def proc_include(self, filename):
        find = os.path.exists(filename)
        mml_path = os.path.dirname(filename)
        if len(mml_path) > 0:
            mml_path += "/"
            if mml_path not in self.path_list:
                self.path_list.insert(0, mml_path)
        if not find:
            for fld in self.path_list:
                if os.path.exists(fld + filename):
                    filename = fld + filename
                    find = True
                    break
        if not find:
            raise Exception(f"Not found include file. -> {filename}")

        if filename in self.include_stack:
            raise Exception(f"Circular references were detected in the include process.\n{self.include_stack}")
        self.include_stack.append(filename)

        mmltype, version, encode = get_mml_type(filename)
        mmlcls = mml_type_to_cls(mmltype)
        mmlcls.compile(self, filename, encode)
        if mmlcls.PROC_SLUR_TIE:
            for seq in self.seq_dic.values():
                proc_slur_tie(seq)

        self.include_stack.pop()
