class StringStream:
    @staticmethod
    def from_file(filename, encode):
        with open(filename, "r", encoding=encode) as f:
            data = f.read()
        ss = StringStream(data, filename, encode)
        ss.flg_open = True
        return ss
    
    @staticmethod
    def from_lines(lines, filename="", encode=""):
        data = ""
        for line in lines:
            data += line
        ss = StringStream(data, filename, encode)
        return ss

    def __init__(self, data, filename="", encode=""):
        self.data = data
        self.index = 0
        self.size = len(self.data)
        self.filename = filename
        self.encode = encode
        self.block_stack = [] # ({のindex,}のindex)
        self.flg_eof = False # seekでfile後ろの範囲外になった
        self.flg_eob = False # seekでblock後ろの範囲外になった
        self.flg_open = False # ファイルから開いたか
    
    def get_col_row(self):
        col = 0
        row = 0
        for i in range(self.index):
            if self.data[i] == '\n':
                row += 1
                col = 0
            else:
                col += 1
        return col, row

    def find(self, substr, offset=0):
        return self.data.find(substr, self.index + offset)

    def bol(self):
        return self.index == 0 or self.data[self.index - 1] == '\n'
    
    def eol(self):
        return self.index >= len(self.data) - 1 or self.data[self.index + 1] == '\n'

    def eof(self):
        return self.index >= len(self.data) - 1 and self.flg_eof
    
    def eob(self):
        if len(self.block_stack) == 0:
            return False
        return self.index >= self.block_stack[-1][1] and self.flg_eob
    
    def bob(self):
        if len(self.block_stack) == 0:
            return False
        return self.index == self.block_stack[-1][0]

    def is_block_stack(self):
        if len(self.block_stack) == 0:
            return False
        return True

    def block_pop(self):
        if len(self.block_stack) == 0:
            return None
        return self.block_stack.pop()

    def block_reset(self):
        self.flg_eob = False
        self.block_stack.clear()
    
    def seek_to_eob(self):
        if len(self.block_stack) == 0:
            return
        while not self.eob():
            self.seek(1)

    def is_block_begin(self, begin="{"):
        return self.is_c(begin)

    def is_block_end(self, end="}"):
        return self.is_c(end)

    def is_c(self, c):
        return self.data[self.index] == c

    def is_LF(self):
        return self.data[self.index] == '\n'

    def is_space(self):
        return self.data[self.index] in [' ', '\t', '\n']

    def is_number(self):
        c = self.data[self.index]
        return '0' <= c and c <= '9'
    
    def is_alphabet_upper(self):
        c = self.data[self.index]
        return 'A' <= c and c <= 'Z'

    def is_alphabet_lower(self):
        c = self.data[self.index]
        return 'a' <= c and c <= 'z'

    def is_alphabet(self):
        return self.is_alphabet_upper() or self.is_alphabet_lower()

    def seek_reset(self):
        self.flg_eof = False
        self.index = 0
        self.size = len(self.data)
        self.block_reset()

    def seek(self, n):
        self.index += n
        # print("seek", self.data[self.index])
        if self.is_block_stack():
            if self.index < self.block_stack[-1][0]:
                self.index = self.block_stack[-1][0]
            self.flg_eob = False
            if self.index >= self.block_stack[-1][1]:
                self.index = self.block_stack[-1][1]
                self.flg_eob = True
        else:
            if self.index < 0:
                self.index = 0
            self.flg_eof = False
            if self.index >= self.size:
                self.index = self.size - 1
                self.flg_eof = True

    def seek_to_c(self, c, inline=False):
        while True:
            if self.eof():
                break
            if self.eob():
                break
            if inline and self.is_LF():
                break
            if self.is_c(c):
                break
            self.seek(1)

    def seek_to_space(self):
        while True:
            if self.eof():
                break
            if self.eob():
                break
            if self.is_space():
                break
            self.seek(1)

    def seek_to_not_space(self, inline=False):
        while True:
            if self.eof():
                break
            if self.eob():
                break
            if inline and self.is_LF():
                break
            if not self.is_space():
                break
            self.seek(1)

    def show(self, n):
        if self.eof():
            return ""
        ret = self.data[self.index:self.index+n]
        return ret

    def show_line(self):
        idx = self.data.find('\n', self.index)
        if idx >= 0:
            ret = self.data[self.index:idx]
        else:
            ret = self.data[self.index:]
        return ret

    def seek_to_bob(self):
        if self.is_block_stack():
            self.index = self.block_stack[-1][0]
            self.flg_eob = False
            self.flg_eof = False

    def show_block(self, begin:str='{', end:str='}', push_block=False, back=False):
        if back:
            self.seek_to_bob()
        idx_begin = -1
        idx_end = -1
        if self.data[self.index] == begin:
            idx_begin = self.index
            count = 1
            idx = self.index + 1
            while idx < self.size:
                c = self.data[idx]
                if c == begin:
                    count += 1
                if c == end:
                    count -= 1
                    if count == 0:
                        idx_end = idx
                        break
                idx += 1
        if idx_begin < 0 or idx_end < 0:
            return ""
        ret = self.data[idx_begin+1:idx_end] # {}は含まない
        if push_block:
            self.block_stack.append((idx_begin,idx_end))
        return ret

    def show_to_c(self, c, inline=True):
        index = self.index
        eof = self.flg_eof
        eob = self.flg_eob
        ret = self.read_to_c(c, inline)
        self.index = index
        self.flg_eof = eof
        self.flg_eob = eob
        return ret

    def show_to_space(self, inline=True, add_char=""):
        index = self.index
        eof = self.flg_eof
        eob = self.flg_eob
        ret = self.read_to_space(inline, add_char)
        self.index = index
        self.flg_eof = eof
        self.flg_eob = eob
        return ret

    def read(self, n):
        ret = self.show(n)
        self.seek(n)
        return ret

    def read_line(self):
        ret = self.show_line()
        self.seek(len(ret))
        return ret

    def read_block(self, begin:str='{', end:str='}', push_block=False, back=False):
        ret = self.show_block(begin, end, push_block, back)
        if len(ret) == 0:
            return ""
        self.seek(len(ret) + 2) # +2は{}のぶん
        return ret

    def read_to_c(self, c, inline=True):
        ret = ""
        while True:
            if self.eof():
                break
            if self.eob():
                break
            r = self.show(1)
            if r == c:
                break
            if inline and r == '\n':
                break
            self.seek(1)
            ret += r
        return ret

    def read_to_space(self, inline=True, add_char=""):
        ret = ""
        while True:
            if self.eof():
                break
            if self.eob():
                break
            if self.is_space():
                break
            r = self.show(1)
            if len(add_char) > 0 and r in add_char:
                break
            if inline and r == '\n':
                break
            self.seek(1)
            ret += r
        return ret

    def print_location(self, length=1, msg=""):
        if self.flg_open:
            with open(self.filename,"r",encoding=self.encode) as f:
                data = f.read()
        else:
            data = self.data

        lines = data.splitlines()
        col, row = self.get_col_row()
        begin = max(0, row - 3)
        end = min(len(lines), row + 4)

        print()
        if len(self.filename) > 0:
            print(self.filename)
        for i in range(begin,end):
            print(f"{i+1: 4d}: {lines[i]}")
            if i == row:
                for _ in range(col + 6): # 行番号表示のため+6
                    print(" ",end="")
                for _ in range(length):
                    print("^",end="")
                print("", msg)

    def print_index(self):
        row, col = self.get_col_row()
        msg = f"{self.index} ({row},{col})"
        self.print_location(1, msg)
