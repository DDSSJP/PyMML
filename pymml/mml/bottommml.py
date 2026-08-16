from ..command import get_command_instance
from .mml_base import MMLBase
from .builder import MMLBuilder
from ..define import MML_Type

class BottomMML(MMLBase):
    MML_TYPE = MML_Type.BOTTOM

    @staticmethod
    def compile(builder:MMLBuilder, filename:str, encode:str):
        with open(filename,"r",encoding=encode) as f:
            data = f.read()

        # コメント部分を削除
        data = MMLBase.comment_range(data, 0, "/*", "*/")
        data = MMLBase.comment_line(data, ";")
        data = MMLBase.comment_line(data, "//")
        data = MMLBase.trim_space(data)

        # コマンド文字で分ける
        data_list = data.split('@')
        data_list.remove("")

        # コマンドのインスタンスにする
        cmd_list = []
        for i in range(len(data_list)):
            if len(data_list[i]) > 0:
                cmd_list.append(get_command_instance(data_list[i]))

        return cmd_list

        
