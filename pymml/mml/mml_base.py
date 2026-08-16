from ..command import CommandBase
from .builder import MMLBuilder
from ..define import MML_Type

class MMLBase:
    MML_TYPE = MML_Type.UNKNOWN
    PROC_SLUR_TIE = True

    def __init__(self):
        raise NotImplementedError()
    
    @staticmethod
    def compile(builder:MMLBuilder, filename:str, encode:str) -> list[CommandBase]:
        return []

    @staticmethod
    def delete_end(data:str, key:str) -> str:
        lines = data.splitlines()
        i = 0
        while i < len(lines):
            if lines[i].endswith(key):
                lines[i+1] = lines[i][:-len(key)] + lines[i+1]
                lines[i] = ""
            else:
                i += 1
        ret = ""
        for line in lines:
            ret += line
            ret += '\n'
        return ret

    @staticmethod
    def comment_line(data:str, key:str):
        lines = data.splitlines()
        for i in range(len(lines)):
            idx = lines[i].find(key)
            if idx >= 0:
                lines[i] = lines[i][:idx]
        return "\n".join(lines)

    @staticmethod
    def delete_ranges(data:str, ranges):
        ret = ""
        end2 = 0
        for begin, end in ranges:
            ret += data[end2:begin]
            for i in range(begin,end):
                if data[i] == '\n':
                    ret += '\n'
                else:
                    ret += ' '
            end2 = end
        ret += data[end2:]
        return ret

    @staticmethod
    def comment_toggle(data:str, start:int, key:str):
        flg = True
        idx = start
        keysize = len(key)
        begin = 0
        ranges = []
        while True:
            idx = data.find(key, idx)
            if idx < 0:
                break
            if flg:
                begin = idx
                idx += keysize
            else:
                idx += keysize
                end = idx
                ranges.append((begin, end))
            flg = not flg
        return MMLBase.delete_ranges(data, ranges)

    @staticmethod
    def comment_range(data, start, begin, end):
        ranges = []
        bi = 0
        ei = start
        while True:
            bi = data.find(begin, ei)
            if bi >= 0:
                ei = data.find(end, bi + len(begin))
                if ei >= 0:
                    ei += + len(end)
                    ranges.append((bi,ei))
                    continue
            break
        return MMLBase.delete_ranges(data, ranges)

    @staticmethod
    def trim_space(value:str):
            for c in ['\t', '\n', '\r', '\f', '\v']:
                value = value.replace(c, ' ')
            l = 0
            while l != len(value):
                l = len(value)
                value = value.replace("  ", " ")
            return value.strip()
