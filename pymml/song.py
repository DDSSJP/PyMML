from .command import CommandTitle, CommandComposer, CommandArranger, CommandMessage
from .mml.builder import MMLBuilder

class SongData:
    def __init__(self, filename):

        builder = MMLBuilder()
        builder.build(filename)

        self.seq_dic = builder.seq_dic
        self.filename = filename
        self.title = ""
        self.composer = ""
        self.arranger = ""
        self.message = ""

        del builder

        for seq in self.seq_dic.values():
            for cmd in seq:
                cls = type(cmd)
                if cls == CommandTitle:
                    self.title = cmd.value
                elif cls == CommandComposer:
                    self.composer = cmd.value
                elif cls == CommandArranger:
                    self.arranger = cmd.value
                elif cls == CommandMessage:
                    self.message = cmd.value

    def print_text(self):
        print(" Filename:", self.filename)
        print("    Title:", self.title)
        print(" Composer:", self.composer)
        print(" Arranger:", self.arranger)
        print("  Message:", self.message)
        print()
