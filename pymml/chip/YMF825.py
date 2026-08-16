import time
from ..define import TypeList, ChipType, DeviceType, UniqueType
from .chip_base import ChipBase, RegisterBase, ParameterBase, ToneDataBase
from .. import error as Error

class YMF825Register(RegisterBase):
    NOT_READ = [7, 12, 13, 14, 15, 16, 17, 18, 19, 20, 30, 31, 32, 33, 34]
    NOT_WRITE = [4, 22, 30, 31]
    NOT_WRITE.extend([35 + i for i in range(15*3)])
    NOT_DIFF = [0, 1, 2, 4, 7, 11, 12, 13, 14, 15, 16, 17, 18, 19, 21, 22, 29, 30, 31, 32, 33, 34, 80]
    NOT_DIFF.extend([35 + i for i in range(15*3)])

    def __init__(self):
        self._reg = [0] * 81
        self._ctrl = [0] * 128
        self._fifo = [0] * 512
        self._fifo_write_point = 0
        self._eq_temp = [[0] * 15] * 3
        self._eq_write_point = [0] * 3
        self.hardware_reset()

    def write(self, adr, data):
        if adr in YMF825Register.NOT_WRITE:
            raise Exception(f"not write address. -> {adr}")

        # Out of the reset state
        self._reg[1] = 0b0000_0000

        # ALRST
        if adr == 1 and (data & 0b1000_0000) != 0:
            self.all_reset()

        # Contents Data Write Port
        if adr == 7:
            self._fifo[self._fifo_write_point] = data
            self._fifo_write_point += 1
            if self._fifo_write_point >= len(self._fifo):
                self._fifo_write_point = 0

        if adr == 8:
            # AllKeyOff
            if data & 0b1000_0000 != 0:
                for i in range(16):
                    self._ctrl[i*8 + 3] &= 0b1011_1111 # KeyOn=0
                data &= 0b0111_1111 # After setting the register bit to "1", wait for more than 6us and then return it to "0".
            # AllMute
            if data & 0b0100_0000 != 0:
                for i in range(16):
                    self._ctrl[i*8 + 3] &= 0b1101_1111 # Mute=0
                data &= 0b1011_1111 # After setting the register bit to "1", wait for more than 6us and then return it to "0".
            # AllEGRst
            if data & 0b0010_0000 != 0:
                for i in range(16):
                    self._ctrl[i*8 + 3] &= 0b1110_1111 # EG_RST=0
                data &= 0b1101_1111 # After setting the register bit to "1", wait for more than 6us and then return it to "0".
            # R_FIFO
            if data & 0b0000_0010 != 0:
                for i in range(len(self._fifo)):
                    self._fifo[i] = 0x00
                self._fifo_write_point = 0

        # Control Register
        if 12 <= adr and adr <= 19:
            vno = self._reg[11] & 0b0000_1111 # CRGD_VNO
            self._ctrl[vno*8 + adr-12] = data

        # EQ
        if 32 <= adr and adr <= 34:
            band = adr - 32
            self._eq_temp[band][self._eq_write_point[band]] = data
            self._eq_write_point[band] += 1
            if self._eq_write_point[band] >= 15:
                self._eq_write_point[band] = 0
                for i in range(15):
                    self._reg[35 + band*15 + i] = self._eq_temp[band][i]

        self._reg[adr] = data

    def read(self, adr):
        if adr in YMF825Register.NOT_READ:
            raise Exception(f"not read address. -> {adr}")

        # Control Register Read Port
        if adr == 22:
            rdadr = self.read(21) # RDADR_CRG
            self._reg[22] = self._ctrl[rdadr]

        return self._reg[adr]

    def diff(self, other):
        reg = []
        for adr in range(len(self._reg)):
            if adr in YMF825Register.NOT_DIFF:
                continue
            if adr in YMF825Register.NOT_WRITE:
                continue
            if self._reg[adr] != other._reg[adr]:
                reg.append((adr, self._reg[adr]))
        return reg

    def diff_ctrl(self, other):
        ctrl = set()
        for adr in range(len(self._ctrl)):
            if (self._ctrl[adr] != other._ctrl[adr]):
                ofs = adr%8
                # セットで書き込むやつ
                if ofs==1 or ofs==6:
                    ctrl.add((adr, self._ctrl[adr]))
                    ctrl.add((adr+1, self._ctrl[adr+1]))
                elif ofs==2 or ofs==7:
                    ctrl.add((adr-1, self._ctrl[adr-1]))
                    ctrl.add((adr, self._ctrl[adr]))
                else:
                    ctrl.add((adr, self._ctrl[adr]))
        ctrl = sorted(list(ctrl))

        # if len(ctrl) > 0:
        #     for i in range(8):
        #         print(f"{other._ctrl[i]:02x}"," ", end="")
        #     print()
        #     for i in range(8):
        #         print(f"{self._ctrl[i]:02x}"," ", end="")
        #     print()

        return ctrl
    
    def diff_fifo(self, other):
        fifo = []
        size = (self._reg[9] & 0b0000_0001) * 256 + self._reg[10] + 1
        p = 0
        for adr in range(size):
            if self._fifo[adr] != other._fifo[adr]:
                p = adr+1
        for adr in range(p):
            fifo.append((adr, self._fifo[adr]))
        return fifo

    def copy(self, other):
        for i in range(len(self._reg)):
            self._reg[i] = other._reg[i]
        for i in range(len(self._ctrl)):
            self._ctrl[i] = other._ctrl[i]
        for i in range(len(self._fifo)):
            self._fifo[i] = other._fifo[i]
        self._fifo_write_point = other._fifo_write_point
        for band in range(3):
            for i in range(15):
                self._eq_temp[band][i] = other._eq_temp[band][i]
            self._eq_write_point[band] = other._eq_write_point[band]

    def hardware_reset(self):
        for i in range(len(self._reg)):
            self._reg[i] = 0x00
        self._reg[ 1] = 0x80
        self._reg[ 2] = 0x0f
        self._reg[ 3] = 0x01
        self._reg[ 4] = 0x01
        self._reg[35] = 0x10
        self._reg[50] = 0x10
        self._reg[65] = 0x10
        for i in range(len(self._ctrl)):
            self._ctrl[i] = 0x00
        for i in range(16):
            self._ctrl[i*8 + 4] = 0x60
            self._ctrl[i*8 + 6] = 0x08
        for i in range(len(self._fifo)):
            self._fifo[i] = 0x00

    def all_reset(self):
        back_00 = self._reg[ 0]
        back_01 = self._reg[ 1]
        back_02 = self._reg[ 2]
        back_29 = self._reg[29]
        back_80 = self._reg[80]
        self.hardware_reset()
        self._reg[ 0] = back_00
        self._reg[ 1] = back_01
        self._reg[ 2] = back_02
        self._reg[29] = back_29
        self._reg[80] = back_80

class YMF825Parameter(ParameterBase):
    # Clock Enable
    CLKE = "CLKE" # 0,1/Disable,Enable
    # Reset
    ALRST = "ALRST" # 0,1/OFF,ON
    # AnalogBlockPowerDown
    AP3 = "AP3" # 0,1/OFF,ON  DAC
    AP2 = "AP2" # 0,1/OFF,ON  SPAMP, SPOUT2
    AP1 = "AP1" # 0,1/OFF,ON  SPAMP, SPOUT1
    AP0 = "AP0" # 0,1/OFF,ON  VREF, IREF
    # SpeakerAmplifireGain
    GAIN = "GAIN" # 0-3
    # HardwareID
    HardwareID = "HardwareID"
    # Interrupt
    EMP_DW = "EMP_DW" # 0,1/clear,set         empty data write ?
    FIFO = "FIFO" # 0,1/clear,set             FIFO ...?
    SQ_STP = "SQ_STP" # 0,1/clear,set         Sequencer stopping ?
    EIRQ = "EIRQ" # 0,1/Disable,Enable        Enable IRQ
    EEMP_DW = "EEMP_DW" # 0,1/Disable,Enable  Enable EMP Interrupt
    EFIFO = "EFIFO" # 0,1/Disable,Enable      Enable FIFO Interrupt
    ESQ_STP = "ESQ_STP" # 0,1/Disable,Enable  Enable Sequencer Stopping Interrupt
    # ContentsDataWrite
    ContentsDataWrite = "ContentsDataWrite" # burst write to FIFO
    # Sequencer
    AllKeyOff = "AllKeyOff" # 0,1/OFF,ON
    AllMute = "AllMute" # 0,1/OFF,ON
    AllEGRst = "AllEGRst" # 0,1/OFF,ON
    R_FIFOR = "R_FIFOR" # 0,1/OFF,ON  Reset FIFO Read point ?
    REP_SQ = "REP_SQ" # 0,1/OFF,ON    Repeat Sequencer ?
    R_SEQ = "R_SEQ" # 0,1/OFF,ON      Reset Sequencer ?
    R_FIFO = "R_FIFO" # 0,1/OFF,ON    Reset FIFO ?
    START = "START" # 0,1/OFF,ON      Sequencer Start ?
    SEQ_Vol = "SEQ_Vol" # 0-31
    DIR_SV = "DIR_SV" # 0,1/Enable,Disable Sequence Volume Interpolation
    SIZE = "SIZE" # 0-511/1-512 Sequence data size
    MS_S = "MS_S" # 0-16383/1-16384 Sequencer Time unit Setting
    # Synthesizer
    CRGD_VNO = "CRGD_VNO" # 0-15 Control Register Voice NO
    VoVol = "VoVol" # 0-31 Voice Volume
    BLOCK = "BLOCK" # 0-7 Octave
    FNUM = "FNUM" # 0-1023 Frequency
    KeyOn = "KeyOn" # 0,1/OFF,ON
    Mute = "Mute" # 0,1/OFF,ON
    EG_RST = "EG_RST" # 0,1/OFF,ON  Envelop Generator Reset
    ToneNum = "ToneNum" # 0-15 Tone Number
    ChVol = "ChVol" # 0-31 Channel Volume
    DIR_CV = "DIR_CV" # 0,1/Enable,Disable Channel Volume Interpolation
    XVB = "XVB" # 0,1,2,4,6/OFF,DVB,2x(DVB+1),4x(DVB+2),8x(DVB+3) Vibrato Extension
    INT = "INT" # 0-3 Audio frequency multiplier Integer part
    FRAC = "FRAC" # 0-511 Audio frequency multiplier Fraction part
    DIR_MT = "DIR_MT" # 0,1/Enable,Disable Master Volume Interpolation
    # ControlRegister
    RDADR_CRG = "RDADR_CRG" # 0-255 Read Address Control Register 0-127?
    RDDATA_CRG = "RDDATA_CRG" # 0-127 Read Data Control Register
    # MasterVolume
    MASTER_VOL = "MASTER_VOL" # 0-63 Master Volume
    # SoftReset
    SFTRST = "SFTRST" # 0-255
    # VolumeInterpolation
    DADJT = "DADJT" # 0,1/OFF,ON  Sequencer Delay Adjust ?
    MUTE_ITIME = "MUTE_ITIME" # 0-3    Mute Interpolation Time
    CHVOL_ITIME = "CHVOL_ITIME" # 0-3  Channel Volume Interpolation Time
    MVOL_ITIME = "MVOL_ITIME" # 0-3    Master Volumne Interpolation Time
    # LFOReset
    LFO_RST = "LFO_RST" # 0,1/off,on
    # PowerRailSelection
    DRV_SEL = "DRV_SEL" # 0,1
    # Equalizer
    W_CEQ0 = "W_CEQ0" # 0-255
    W_CEQ1 = "W_CEQ1" # 0-255
    W_CEQ2 = "W_CEQ2" # 0-255
    CEQ00 = "CEQ00" # 0-16777215
    CEQ01 = "CEQ01" # 0-16777215
    CEQ02 = "CEQ02" # 0-16777215
    CEQ03 = "CEQ03" # 0-16777215
    CEQ04 = "CEQ04" # 0-16777215
    CEQ10 = "CEQ10" # 0-16777215
    CEQ11 = "CEQ11" # 0-16777215
    CEQ12 = "CEQ12" # 0-16777215
    CEQ13 = "CEQ13" # 0-16777215
    CEQ14 = "CEQ14" # 0-16777215
    CEQ20 = "CEQ20" # 0-16777215
    CEQ21 = "CEQ21" # 0-16777215
    CEQ22 = "CEQ22" # 0-16777215
    CEQ23 = "CEQ23" # 0-16777215
    CEQ24 = "CEQ24" # 0-16777215
    # SoftwareCommunicationCheck
    COMM = "COMM" # 0-255

    @staticmethod
    def write(reg:YMF825Register, prm, value):
        if prm == YMF825Parameter.CLKE:
            reg.write(0, value & 0b0000_0001)
        elif prm == YMF825Parameter.ALRST:
            reg.write(1, (value & 0b0000_0001) << 7)
        elif prm == YMF825Parameter.AP3:
            reg.write(2, (reg.read(2) & 0b1111_0111) | (value & 0b0000_0001) << 3)
        elif prm == YMF825Parameter.AP2:
            reg.write(2, (reg.read(2) & 0b1111_1011) | (value & 0b0000_0001) << 2)
        elif prm == YMF825Parameter.AP1:
            reg.write(2, (reg.read(2) & 0b1111_1101) | (value & 0b0000_0001) << 1)
        elif prm == YMF825Parameter.AP0:
            reg.write(2, (reg.read(2) & 0b1111_1110) | (value & 0b0000_0001))
        elif prm == YMF825Parameter.GAIN:
            reg.write(3, value & 0b0000_0011)
        elif prm == YMF825Parameter.EMP_DW:
            reg.write(5, (reg.read(5) & 0b1110_1111) | (value & 0b0000_0001) << 4)
        elif prm == YMF825Parameter.FIFO:
            reg.write(5, (reg.read(5) & 0b1111_1011) | (value & 0b0000_0001) << 2)
        elif prm == YMF825Parameter.SQ_STP:
            reg.write(5, (reg.read(5) & 0b1111_1110) | (value & 0b0000_0001))
        elif prm == YMF825Parameter.EIRQ:
            reg.write(6, (reg.read(6) & 0b1011_1111) | (value & 0b0000_0001) << 6)
        elif prm == YMF825Parameter.EEMP_DW:
            reg.write(6, (reg.read(6) & 0b1110_1111) | (value & 0b0000_0001) << 4)
        elif prm == YMF825Parameter.EFIFO:
            reg.write(6, (reg.read(6) & 0b1111_1011) | (value & 0b0000_0001) << 2)
        elif prm == YMF825Parameter.ESQ_STP:
            reg.write(6, (reg.read(6) & 0b1111_1110) | (value & 0b0000_0001))
        elif prm == YMF825Parameter.ContentsDataWrite:
            reg.write(7, value & 0b1111_1111)
        elif prm == YMF825Parameter.AllKeyOff:
            reg.write(8, (reg.read(8) & 0b0111_1111) | (value & 0b0000_0001) << 7)
        elif prm == YMF825Parameter.AllMute:
            reg.write(8, (reg.read(8) & 0b1011_1111) | (value & 0b0000_0001) << 6)
        elif prm == YMF825Parameter.AllEGRst:
            reg.write(8, (reg.read(8) & 0b1101_1111) | (value & 0b0000_0001) << 5)
        elif prm == YMF825Parameter.R_FIFOR:
            reg.write(8, (reg.read(8) & 0b1110_1111) | (value & 0b0000_0001) << 4)
        elif prm == YMF825Parameter.REP_SQ:
            reg.write(8, (reg.read(8) & 0b1111_0111) | (value & 0b0000_0001) << 3)
        elif prm == YMF825Parameter.R_SEQ:
            reg.write(8, (reg.read(8) & 0b1111_1011) | (value & 0b0000_0001) << 2)
        elif prm == YMF825Parameter.R_FIFO:
            reg.write(8, (reg.read(8) & 0b1111_1101) | (value & 0b0000_0001) << 1)
        elif prm == YMF825Parameter.START:
            reg.write(8, (reg.read(8) & 0b1111_1110) | (value & 0b0000_0001))
        elif prm == YMF825Parameter.SEQ_Vol:
            reg.write(9, (reg.read(9) & 0b0000_0111) | (value & 0b0001_1111) << 3)
        elif prm == YMF825Parameter.DIR_SV:
            reg.write(9, (reg.read(9) & 0b1111_1011) | (value & 0b0000_0001) << 2)
        elif prm == YMF825Parameter.SIZE:
            vh = (value & 0b0000_0001_0000_0000) >> 8
            vl =  value & 0b0000_0000_1111_1111
            reg.write(9, (reg.read(9) & 0b1111_1110) | vh )
            reg.write(10, vl )
        elif prm == YMF825Parameter.CRGD_VNO:
            reg.write(11, value & 0b0000_1111)
        elif prm == YMF825Parameter.VoVol:
            vno = reg.read(11) & 0b0000_1111
            reg.write(21, vno*8)
            reg.write(12, (reg.read(22) & 0b0000_0000) | (value & 0b0001_1111) << 2)
        elif prm == YMF825Parameter.BLOCK:
            vno = reg.read(11) & 0b0000_1111
            reg.write(21, vno*8 + 1)
            reg.write(13, (reg.read(22) & 0b0011_1000) | (value & 0b0000_0111))
        elif prm == YMF825Parameter.FNUM:
            vh = (value & 0b0000_0011_1000_0000) >> 7
            vl =  value & 0b0000_0000_0111_1111
            vno = reg.read(11) & 0b0000_1111
            reg.write(21, vno*8 + 1)
            reg.write(13, (reg.read(22) & 0b0000_0111) | vh << 3)
            reg.write(14, vl)
        elif prm == YMF825Parameter.KeyOn:
            vno = reg.read(11) & 0b0000_1111
            reg.write(21, vno*8 + 3)
            reg.write(15, (reg.read(22) & 0b0011_1111) | (value & 0b0000_0001) << 6)
        elif prm == YMF825Parameter.Mute:
            vno = reg.read(11) & 0b0000_1111
            reg.write(21, vno*8 + 3)
            reg.write(15, (reg.read(22) & 0b0101_1111) | (value & 0b0000_0001) << 5)
        elif prm == YMF825Parameter.EG_RST:
            vno = reg.read(11) & 0b0000_1111
            reg.write(21, vno*8 + 3)
            reg.write(15, (reg.read(22) & 0b0110_1111) | (value & 0b0000_0001) << 4)
        elif prm == YMF825Parameter.ToneNum:
            vno = reg.read(11) & 0b0000_1111
            reg.write(21, vno*8 + 3)
            reg.write(15, (reg.read(22) & 0b1111_0000) | (value & 0b0000_1111))
        elif prm == YMF825Parameter.ChVol:
            vno = reg.read(11) & 0b0000_1111
            reg.write(21, vno*8 + 4)
            reg.write(16, (reg.read(22) & 0b0000_0001) | (value & 0b0001_1111) << 2)
        elif prm == YMF825Parameter.DIR_CV:
            vno = reg.read(11) & 0b0000_1111
            reg.write(21, vno*8 + 4)
            reg.write(16, (reg.read(22) & 0b0111_1100) | (value & 0b0000_0001))
        elif prm == YMF825Parameter.XVB:
            reg.write(17, value & 0b0000_0111)
        elif prm == YMF825Parameter.INT:
            vno = reg.read(11) & 0b0000_1111
            reg.write(21, vno*8 + 6)
            reg.write(18, (reg.read(22) & 0b1110_0111) | (value & 0b0000_0011) << 3)
        elif prm == YMF825Parameter.FRAC:
            vh = (value & 0b0000_0001_1100_0000) >> 6
            vl = (value & 0b0000_0000_0011_1111)
            vno = reg.read(11) & 0b0000_1111
            reg.write(21, vno*8 + 6)
            reg.write(18, (reg.read(22) & 0b1111_1000) | vh)
            reg.write(19, vl << 1)
        elif prm == YMF825Parameter.DIR_MT:
            reg.write(20, value & 0b0000_0001)
        elif prm == YMF825Parameter.RDADR_CRG:
            reg.write(21, value & 0b1111_1111)
        elif prm == YMF825Parameter.MS_S:
            vh = (value & 0b0011_1111_1000_0000) >> 7
            vl =  value & 0b0000_0000_0111_1111
            reg.write(23, vh)
            reg.write(24, vl)
        elif prm == YMF825Parameter.MASTER_VOL:
            reg.write(25, (value & 0b0011_1111) << 2)
        elif prm == YMF825Parameter.SFTRST:
            reg.write(26, value & 0b1111_1111)
        elif prm == YMF825Parameter.DADJT:
            reg.write(27, (reg.read(27) & 0b1011_1111) | (value & 0b0000_0001) << 6)
        elif prm == YMF825Parameter.MUTE_ITIME:
            reg.write(27, (reg.read(27) & 0b1100_1111) | (value & 0b0000_0011) << 4)
        elif prm == YMF825Parameter.CHVOL_ITIME:
            reg.write(27, (reg.read(27) & 0b1111_0011) | (value & 0b0000_0011) << 2)
        elif prm == YMF825Parameter.MVOL_ITIME:
            reg.write(27, (reg.read(27) & 0b1111_1100) | (value & 0b0000_0011))
        elif prm == YMF825Parameter.LFO_RST:
            reg.write(28, value & 0b0000_0001)
        elif prm == YMF825Parameter.DRV_SEL:
            reg.write(29, value & 0b0000_0001)
        else:
            raise Exception(f"Invalid write parameter. -> {prm}")

    @staticmethod
    def read(reg, prm, ch=0):
        if prm == YMF825Parameter.CLKE:
            value = (reg.read(1) & 0b1000_0000) >> 7
        elif prm == YMF825Parameter.AP3:
            value = (reg.read(2) & 0b0000_1000) >> 3
        elif prm == YMF825Parameter.AP2:
            value = (reg.read(2) & 0b0000_0100) >> 2
        elif prm == YMF825Parameter.AP1:
            value = (reg.read(2) & 0b0000_0010) >> 1
        elif prm == YMF825Parameter.AP0:
            value = reg.read(2) & 0b0000_0001
        elif prm == YMF825Parameter.GAIN:
            value = reg.read(3) & 0b0000_0011
        elif prm == YMF825Parameter.HardwareID:
            value = reg.read(4)
        elif prm == YMF825Parameter.EMP_DW:
            value = (reg.read(5) & 0b0001_0000) >> 4
        elif prm == YMF825Parameter.FIFO:
            value = (reg.read(5) & 0b0000_0100) >> 2
        elif prm == YMF825Parameter.SQ_STP:
            value = reg.read(5) & 0b0000_0001
        elif prm == YMF825Parameter.EIRQ:
            value = (reg.read(6) & 0b0100_0000) >> 6
        elif prm == YMF825Parameter.EEMP_DW:
            value = (reg.read(6) & 0b0001_0000) >> 4
        elif prm == YMF825Parameter.EFIFO:
            value = (reg.read(6) & 0b0000_0100) >> 2
        elif prm == YMF825Parameter.ESQ_STP:
            value = reg.read(6) & 0b0000_0001
        elif prm == YMF825Parameter.AllKeyOff:
            value = (reg.read(8) & 0b1000_0000) >> 7
        elif prm == YMF825Parameter.AllMute:
            value = (reg.read(8) & 0b0100_0000) >> 6
        elif prm == YMF825Parameter.AllEGRst:
            value = (reg.read(8) & 0b0010_0000) >> 5
        elif prm == YMF825Parameter.R_FIFOR:
            value = (reg.read(8) & 0b0001_0000) >> 4
        elif prm == YMF825Parameter.REP_SQ:
            value = (reg.read(8) & 0b0000_1000) >> 3
        elif prm == YMF825Parameter.R_SEQ:
            value = (reg.read(8) & 0b0000_0100) >> 2
        elif prm == YMF825Parameter.R_FIFO:
            value = (reg.read(8) & 0b0000_0010) >> 1
        elif prm == YMF825Parameter.START:
            value = reg.read(8) & 0b0000_0001
        elif prm == YMF825Parameter.SEQ_Vol:
            value = (reg.read(9) & 0b1111_1000) >> 3
        elif prm == YMF825Parameter.DIR_SV:
            value = (reg.read(9) & 0b0000_0100) >> 2
        elif prm == YMF825Parameter.SIZE:
            value = (reg.read(9) & 0b0000_0001) * 256 +  reg.read(10)
        elif prm == YMF825Parameter.MS_S:
            value = (reg.read(23) & 0b0111_1111) * 128 + (reg.read(24) & 0b0111_1111)
        elif prm == YMF825Parameter.CRGD_VNO:
            value = reg.read(11) & 0b0000_1111
        elif prm == YMF825Parameter.VoVol:
            reg.write(21, ch*8)
            value = (reg.read(22) & 0b0111_1100) >> 2
        elif prm == YMF825Parameter.BLOCK:
            reg.write(21, ch*8 + 1)
            value = reg.read(22) & 0b0000_0111
        elif prm == YMF825Parameter.FNUM:
            reg.write(21, ch*8 + 1)
            vh = (reg.read(22) & 0b0011_1000) >> 3
            reg.write(21, ch*8 + 2)
            value = vh * 128 + (reg.read(22) & 0b0111_1111)
        elif prm == YMF825Parameter.KeyOn:
            reg.write(21, ch*8+3)
            value = (reg.read(22) & 0b0100_0000) >> 6
        elif prm == YMF825Parameter.Mute:
            reg.write(21, ch*8+3)
            value = (reg.read(22) & 0b0010_0000) >> 5
        elif prm == YMF825Parameter.EG_RST:
            reg.write(21, ch*8+3)
            value = (reg.read(22) & 0b0001_0000) >> 4
        elif prm == YMF825Parameter.ToneNum:
            reg.write(21, ch*8+3)
            value = reg.read(22) & 0b0000_1111
        elif prm == YMF825Parameter.ChVol:
            reg.write(21, ch*8+4)
            value = (reg.read(22) & 0b0111_1100) >> 2
        elif prm == YMF825Parameter.DIR_CV:
            reg.write(21, ch*8+4)
            value = reg.read(22) & 0b0000_0001
        elif prm == YMF825Parameter.XVB:
            reg.write(21, ch*8+5)
            value = reg.read(22) & 0b0000_0111
        elif prm == YMF825Parameter.INT:
            reg.write(21, ch*8+6)
            value = (reg.read(22) & 0b0001_1000) >> 3
        elif prm == YMF825Parameter.FRAC:
            reg.write(21, ch*8+6)
            hv = reg.read(22) & 0b0000_0111
            reg.write(21, ch*8+7)
            value = hv * 128 + ((reg.read(22) & 0b0111_1110) >> 1)
        elif prm == YMF825Parameter.DIR_MT:
            reg.write(21, ch*8+8)
            value = reg.read(22) & 0b0000_0001
        elif prm == YMF825Parameter.RDADR_CRG:
            value = reg.read(21) & 0b1111_1111
        elif prm == YMF825Parameter.RDDATA_CRG:
            value = reg.read(22) & 0b0111_1111
        elif prm == YMF825Parameter.MASTER_VOL:
            value = (reg.read(25) & 0b1111_1100) >> 2
        elif prm == YMF825Parameter.SFTRST:
            value = reg.read(26) & 0b1111_1111
        elif prm == YMF825Parameter.DADJT:
            value = (reg.read(27) & 0b0100_0000) >> 6
        elif prm == YMF825Parameter.MUTE_ITIME:
            value = (reg.read(27) & 0b0011_0000) >> 4
        elif prm == YMF825Parameter.CHVOL_ITIME:
            value = (reg.read(27) & 0b0000_1100) >> 2
        elif prm == YMF825Parameter.MVOL_ITIME:
            value = reg.read(27) & 0b0000_0011
        elif prm == YMF825Parameter.LFO_RST:
            value = reg.read(28) & 0b0000_0001
        elif prm == YMF825Parameter.DRV_SEL:
            value = reg.read(29) & 0b0000_0001
        elif prm == YMF825Parameter.CEQ00:
            value = YMF825Parameter.read_eq(reg, 0, 0)
        elif prm == YMF825Parameter.CEQ01:
            value = YMF825Parameter.read_eq(reg, 0, 1)
        elif prm == YMF825Parameter.CEQ02:
            value = YMF825Parameter.read_eq(reg, 0, 2)
        elif prm == YMF825Parameter.CEQ03:
            value = YMF825Parameter.read_eq(reg, 0, 3)
        elif prm == YMF825Parameter.CEQ04:
            value = YMF825Parameter.read_eq(reg, 0, 4)
        elif prm == YMF825Parameter.CEQ10:
            value = YMF825Parameter.read_eq(reg, 1, 0)
        elif prm == YMF825Parameter.CEQ11:
            value = YMF825Parameter.read_eq(reg, 1, 1)
        elif prm == YMF825Parameter.CEQ12:
            value = YMF825Parameter.read_eq(reg, 1, 2)
        elif prm == YMF825Parameter.CEQ13:
            value = YMF825Parameter.read_eq(reg, 1, 3)
        elif prm == YMF825Parameter.CEQ14:
            value = YMF825Parameter.read_eq(reg, 1, 4)
        elif prm == YMF825Parameter.CEQ20:
            value = YMF825Parameter.read_eq(reg, 2, 0)
        elif prm == YMF825Parameter.CEQ21:
            value = YMF825Parameter.read_eq(reg, 2, 1)
        elif prm == YMF825Parameter.CEQ22:
            value = YMF825Parameter.read_eq(reg, 2, 2)
        elif prm == YMF825Parameter.CEQ23:
            value = YMF825Parameter.read_eq(reg, 2, 3)
        elif prm == YMF825Parameter.CEQ24:
            value = YMF825Parameter.read_eq(reg, 2, 4)
        elif prm == YMF825Parameter.COMM:
            value = reg.read(80) & 0b0000_0001
        else:
            raise Exception(f"Invalid read parameter. -> {prm}")
        return value

    @staticmethod
    def read_eq(reg, band, coefficients):
        adr = 35 + band * 15 + coefficients * 3
        vh = reg.read(adr  ) & 0b1111_1111
        vm = reg.read(adr+1) & 0b1111_1111
        vl = reg.read(adr+2) & 0b1111_1111
        return vh * 256 * 256 + vm * 256 + vl

    @staticmethod
    def write_eq(reg, band, coefficients):
        if len(coefficients) == 5:
            adr = 32 + band
            for coef in coefficients:
                if coef > 0:
                    sign = 0
                else:
                    sign = 1
                    coef = abs(coef)
                inte = int(coef) & 0b0000_0111
                frac = int((coef - inte) * (2**20))
                reg.write(adr, (sign<<7) | (inte<<4) | (frac>>16) & 0b0000_1111)
                reg.write(adr, (frac>>8)&0b1111_1111)
                reg.write(adr, (frac)&0b1111_1111)

class YMF825UniqueType:
    SET_TONE_TABLE = "SET_TONE_TABLE" # [0]no, [1:]data
    WRITE_TONE_TABLE = "WRITE_TONE_TABLE"
    WRITE_CONTROL_REGISTER = "WRITE_CONTROL_REGISTER"
    WRITE_EQ = "WRITE_EQ"

class YMF825ToneData(ToneDataBase):
    TONE_PRM_NUM = 3 + (17 * 4)
    class Parameter(TypeList):
        ALG = 2**3 - 1
        BO  = 2**2 - 1
        LFO = 2**2 - 1
        WS  = 2**5 - 1
        FB  = 2**3 - 1
        AR  = 2**4 - 1
        TL  = 2**6 - 1
        DR  = 2**4 - 1
        SL  = 2**4 - 1
        SR  = 2**4 - 1
        RR  = 2**4 - 1
        MUL = 2**4 - 1
        DT  = 2**3 - 1
        EAM = 2**1 - 1
        DAM = 2**2 - 1
        EVB = 2**1 - 1
        DVB = 2**2 - 1
        KSR = 2**1 - 1
        KSL = 2**2 - 1
        XOF = 2**1 - 1

    class Operator:
        OP_PRM_NUM = 17
        def __init__(self, op:list=[0] * OP_PRM_NUM):
            self.set_operator(op)
        
        def set_operator(self, op):
            self.WS  = op[0]
            self.FB  = op[1]
            self.AR  = op[2]
            self.TL  = op[3]
            self.DR  = op[4]
            self.SL  = op[5]
            self.SR  = op[6]
            self.RR  = op[7]
            self.MUL = op[8]
            self.DT  = op[9]
            self.EAM = op[10]
            self.DAM = op[11]
            self.EVB = op[12]
            self.DVB = op[13]
            self.KSR = op[14]
            self.KSL = op[15]
            self.XOF = op[16]

        def to_reg(self):
            reg = [0] * 7
            reg[0] = ((self.SR &0b0000_1111)<<4) | ((self.XOF&0b0000_0001)<<3) |  (self.KSR&0b0000_0001)
            reg[1] = ((self.RR &0b0000_1111)<<4) |  (self.DR &0b0000_1111)
            reg[2] = ((self.AR &0b0000_1111)<<4) |  (self.SL &0b0000_1111)
            reg[3] = ((self.TL &0b0011_1111)<<2) |  (self.KSL&0b0000_0011)
            reg[4] = ((self.DAM&0b0000_0011)<<5) | ((self.EAM&0b0000_0001)<<4) | ((self.DVB&0b0000_0011)<<1) | (self.EVB&0b0000_0001)
            reg[5] = ((self.MUL&0b0000_1111)<<4) |  (self.DT &0b0000_0111)
            reg[6] = ((self.WS &0b0001_1111)<<3) |  (self.FB &0b0000_0111)
            return reg
    
    def __init__(self, name="(none)", data:list=[0] * TONE_PRM_NUM):
        self.set_tone(name, data)
    
    def set_tone(self, name, data):
        self.name = name
        self.ALG = data[0]
        self.BO  = data[1]
        self.LFO = data[2]
        self.OP = []
        for i in range(4):
            begin = 3 + i * YMF825ToneData.Operator.OP_PRM_NUM
            end   = begin + YMF825ToneData.Operator.OP_PRM_NUM
            self.OP.append(YMF825ToneData.Operator(data[begin:end]))

    def to_reg(self):
        reg = []
        reg.append(self.BO&0b0000_0011)
        reg.append((self.LFO&0b0000_0011)<<6 | (self.ALG&0b0000_0111))
        reg.extend(self.OP[0].to_reg())
        reg.extend(self.OP[1].to_reg())
        reg.extend(self.OP[2].to_reg())
        reg.extend(self.OP[3].to_reg())
        reg[15] &= 0b1111_1000 # op2 FB to 0
        reg[29] &= 0b1111_1000 # op4 FB to 0
        return reg

    @staticmethod
    def check(prm_index, value):
        # print(prm_index, end=None)
        if prm_index > (3 + YMF825ToneData.Operator.OP_PRM_NUM) - 1:
            prm_index = (prm_index - 3) % YMF825ToneData.Operator.OP_PRM_NUM + 3
        # print(" ",prm_index)
        prm_type = YMF825ToneData.Parameter.get_list()[prm_index]
        prm_max  = YMF825ToneData.Parameter.value(prm_type)
        msg = Error.check(prm_type, value, int, 0, prm_max)
        return len(msg) > 0, msg

class YMF825(ChipBase):
    CHANNEL_NUMBER = 16
    BASE_CLOCK = 12288000
    FNUM_COUNTER = 2**24
    TONE_PRM_NUM = YMF825ToneData.TONE_PRM_NUM
    tone_prm_check = YMF825ToneData.check

    def __init__(self):
        self.chip_type = ChipType.YMF825
        self.reg_crnt = YMF825Register()
        self.reg_prev = YMF825Register()
        self.flg_key_off = [False] * YMF825.CHANNEL_NUMBER
        self.flg_mute = [False] * YMF825.CHANNEL_NUMBER
        self.tone_table = [None] * YMF825.CHANNEL_NUMBER # indexがCRGD_VNO
        self.tone_table_num = False
        self.flg_write_tone_table = False
        self.flg_write_eq = False
        self.eq_coef = []
        self.ctrl_prm = [[] for _ in range(YMF825.CHANNEL_NUMBER)]
        self.fnum_table = [0] * 12
        self.tuning(440)

    def tuning(self, a_hz):
        for n in range(12):
            self.fnum_table[n] = int(a_hz*(2**((n-9)/12)) * self.FNUM_COUNTER / self.BASE_CLOCK + 0.5)

    def setup_master_work(self, master_work):
        master_work.master_volume.init(0, 63, 0) # MASTER_VOL

    def setup_channel_work(self, channel_work):
        channel_work.volume.init(24, 31, 0) # ChVol
        channel_work.note.init(0, 127, -127) # BLOCK FNUM
        channel_work.detune.init(0, 8*1200-1, -8*1200+1) # BLOCK INT FRAC
        channel_work.octave.init(0, 9, 0) # BLOCK FNUM
        channel_work.pan.init(0, 0, 0) # ...
        channel_work.mute.init(0, 1, 0) # Mute

    def send_init(self, device):
        if device.device_type == DeviceType.MOCK:
            device.write_single(80,0xA5)
            device.write_single(4,0b0000_0001)

        # 1. Supply the power to the device.
        # 2. Wait for 100us after supply voltages rise
        # 3. Set the RST_N pin to "H".
        if "YMF825_reset_signal" in dir(device):
            if callable(device.YMF825_reset_signal):
                device.YMF825_reset_signal()

        # Software Communication Check
        device.write_single(80, 0xA5)
        ret = device.read_single(80)
        if ret[0] != 0xA5:
            raise Exception(f"failed to software communication check. -> read_data:{ret[0]}")
        self.reg_crnt.write(80, 0xA5)

        # check HardwareID
        ret = device.read_single(4)
        if ret[0] != 0b0000_0001:
            raise Exception(f"not target hardware. -> read_data:{ret[0]}")

        # 4. Set DRV_SEL to "0" when this device is used in single 5-V power supply configuration. Set DRV_SEL to "1" when this device is used in dual power supply configuration.
        device.write_single(29, 0b0000_0000) # output power: used in single 5-V power
        self.reg_crnt.write(29, 0b0000_0000)

        # 5. Set the AP0 to "0". The VREF is powered.
        device.write_single( 2, 0b0000_1110) # analog powered: AP3,AP2,AP1,AP0 (DAC,SP2,SP1,VREF)
        self.reg_crnt.write( 2, 0b0000_1110)

        # 6. Wait until the clock becomes stable.
        time.sleep(1/1000) # Oops, but not implemented!

        # 7. Set the CLKE to "1".
        device.write_single( 0, 0b0000_0001) # clock enable
        self.reg_crnt.write( 0, 0b0000_0001)

        # 8. Set the ALRST to "0".
        device.write_single( 1, 0b0000_0000) # all reset Out of the reset state.
        self.reg_crnt.write( 1, 0b0000_0000)

        # 9. Set the SFTRST to "A3H".
        device.write_single(26, 0b1010_0011) # soft reset
        self.reg_crnt.write(26, 0b1010_0011)

        # 10. Set the SFTRST to "00H".
        device.write_single(26, 0b0000_0000) # soft reset
        self.reg_crnt.write(26, 0b0000_0000)

        # 11. Wait for 30ms after the step 10.
        time.sleep(30/1000)

        # 12. Set the AP1 and the AP3 to "0".
        device.write_single( 2, 0b0000_0100) # analog powered: AP3,AP2,AP1,AP0 (DAC,SP2,SP1,VREF)
        self.reg_crnt.write( 2, 0b0000_0100)

        # 13. Wait for 10us.
        time.sleep(10/1000/1000)

        # 14. Set the AP2 to "0".
        device.write_single( 2, 0b0000_0000) # analog powered: AP3,AP2,AP1,AP0 (DAC,SP2,SP1,VREF)
        self.reg_crnt.write( 2, 0b0000_0000)

    def master_work_to_prm(self, master_work):
        prm_list = []
        if master_work.master_volume.is_change():
            prm_list.append((YMF825Parameter.MASTER_VOL,master_work.master_volume.get_value()))
        return prm_list

    def channel_work_to_prm(self, channel_work):
        prm_list = []

        # 音色
        if channel_work.flg_tone:
            if channel_work.tone_id in self.tone_table:
                vno = self.tone_table.index(channel_work.tone_id)
                prm_list.append((YMF825Parameter.ToneNum,vno))

        # 音階
        if channel_work.octave.is_change() or channel_work.note.is_change():
            oct, key = channel_work.get_oct_key()
            prm_list.append((YMF825Parameter.BLOCK,oct))
            prm_list.append((YMF825Parameter.FNUM,self.fnum_table[key]))
            # print(f"oct:{oct} key:{key}") # debug

        # デチューン
        if channel_work.detune.is_change():
            dt = channel_work.detune.get_value()
            if dt < 0:
                doct = ((dt // 2400) + 1) * 2
                dt = dt % 2400 - 2400
            else:
                doct = (dt // 2400) * 2
                dt %= 2400
            oct, _ = channel_work.get_oct_key()
            oct += doct
            if oct < 0 or (oct == 0 and dt <= (-1200 + 1)):
                oct = 0
                dt = -1200 + 1
            if oct > 7 or (oct == 7 and dt >= (1200 - 1)):
                oct = 7
                dt = 1200 - 1
            crnt_oct = YMF825Parameter.read(self.reg_crnt, YMF825Parameter.BLOCK, channel_work.no)
            if crnt_oct != oct:
                prm_list.append((YMF825Parameter.BLOCK, oct))
            # print(f"   det: {dt}") # debug
            dt = 2**(dt/1200)
            prm_list.append((YMF825Parameter.INT,int(dt)))
            prm_list.append((YMF825Parameter.FRAC,int((dt-int(dt))*512)))

        # 音量
        if channel_work.volume.is_change():
            prm_list.append((YMF825Parameter.ChVol,channel_work.volume.get_value()))

        # key on
        if channel_work.flg_key_off[0] or channel_work.flg_key_on[0]:
            prm_list.append((YMF825Parameter.KeyOn, 1 if channel_work.key_sw[0] else 0))
        self.flg_key_off[channel_work.no] = channel_work.flg_key_off[0]

        # mute
        if channel_work.mute.is_change():
            prm_list.append((YMF825Parameter.Mute, channel_work.mute.get_value()))

        # control register parameter
        prm_list.extend(self.ctrl_prm[channel_work.no])

        # チャンネル番号
        if len(prm_list) > 0:
            prm_list.insert(0, (YMF825Parameter.CRGD_VNO,channel_work.no))

        return prm_list

    def write_parameter(self, prm, value):
        YMF825Parameter.write(self.reg_crnt, prm, value)

    def get_reg_list(self):
        # Registerの差分
        reg_list = self.reg_crnt.diff(self.reg_prev)

        # 音色データ
        if self.flg_write_tone_table:
            data = [0x80+self.tone_table_num]
            for i in range(self.tone_table_num):
                name = self.tone_table[i]
                if name in self.tone_data_dic.keys():
                    td = YMF825ToneData(name, self.tone_data_dic[name])
                else:
                    td = YMF825ToneData()
                data.extend(td.to_reg())
            data.extend([0x80,0x03,0x81,0x80])
            sqset = self.reg_crnt.read(8)
            reg_list.append((8, [sqset & 0b1111_1101, sqset | 0b0000_0010, sqset & 0b1111_1101]))
            reg_list.append((7, data))
        
        # EQ
        if self.flg_write_eq:
            for i in len(self.eq_coef):
                band = self.eq_coef[i][0]
                coef = self.eq_coef[i][1]
                YMF825Parameter.write_eq(self.reg_crnt, band, coef)
                wadr = 32 + band
                radr = 35 + band * 5
                reg_list.append((wadr, [self.reg_crnt.read(radr+n) for n in range(5)]))

        # ControlRegisterの差分
        diff_ctrl = self.reg_crnt.diff_ctrl(self.reg_prev)

        # チャンネルに振り分ける
        ctrl_reg = [[(11,ch)] for ch in range(YMF825.CHANNEL_NUMBER)]
        for ctrl in diff_ctrl:
            adr = ctrl[0]
            val = ctrl[1]
            ch = adr // 8
            idx = adr % 8
            ctrl_reg[ch].append((12+idx, val))
        
        # KeyOn/KeyOff処理
        for ch in range(YMF825.CHANNEL_NUMBER):
            # 0tickのKeyOff検出
            pre = YMF825Parameter.read(self.reg_prev, YMF825Parameter.KeyOn, ch)
            cnt = YMF825Parameter.read(self.reg_crnt, YMF825Parameter.KeyOn, ch)
            if pre == 1 and cnt == 1 and self.flg_key_off[ch]:
                YMF825Parameter.write(self.reg_crnt, YMF825Parameter.CRGD_VNO, ch)
                YMF825Parameter.write(self.reg_crnt, YMF825Parameter.KeyOn, 0)
                ctrl_reg[ch].append((15, self.reg_crnt.read(22)))
                YMF825Parameter.write(self.reg_crnt, YMF825Parameter.KeyOn, 1)
                ctrl_reg[ch].append((15, self.reg_crnt.read(22)))
            # KeyOn/KeyOffを移動
            if len(ctrl_reg[ch]) >= 3:
                for i in range(len(ctrl_reg[ch])):
                    adr = ctrl_reg[ch][i][0]
                    val = ctrl_reg[ch][i][1]
                    if adr == 15:
                        if (val & 0b0100_0000) == 0:
                            ctrl_reg[ch].insert(1, ctrl_reg[ch].pop(i)) # KeyOffは最初に移動
                        else:
                            ctrl_reg[ch].append(ctrl_reg[ch].pop(i)) # KeyOnは最後に移動
            # リストに追加
            if len(ctrl_reg[ch]) > 1:
                reg_list.extend(ctrl_reg[ch])

        return reg_list

    def tick_reset(self):
        # 現在レジスタを過去レジスタにコピー
        self.reg_crnt.write(28, 0) # LFO_RST to 0
        self.reg_prev.copy(self.reg_crnt)

        # KeyOn/KeyOffフラグクリア
        for i in range(len(self.flg_key_off)):
            self.flg_key_off[i] = False
        
        # コントロールレジスタパラメータクリア
        for i in range(len(self.ctrl_prm)):
            self.ctrl_prm[i].clear()

        # 音色書き込み情報クリア
        self.flg_write_tone_table = False
        self.tone_table_num = 0

        # EQ書き込み情報クリア
        self.flg_write_eq
        self.eq_coef.clear()

    def write_register(self, address, value):
        if type(value) == list:
            for v in value:
                self.reg_crnt.write(address, v)
        else:
            self.reg_crnt.write(address, value)

    def send_register(self, device, reg_list):
        for i in range(len(reg_list)):
            if type(reg_list[i][1]) == list:
                device.write_burst(reg_list[i][0], reg_list[i][1])
            else:
                device.write_single(reg_list[i][0], reg_list[i][1])
        # flg = False
        # burst = []
        # multi = []
        # for i in range(len(reg_list)):
        #     # アドレスが同じならburst(ただし最後ではないこと)
        #     if (i < len(reg_list) - 1) and (reg_list[i][0] == reg_list[i+1][0]):
        #         # burstの最初ならmultiを送信
        #         if (flg == False) and (len(multi) > 0):
        #             device.write_multi(multi)
        #             multi.clear()
        #         flg = True # burst判定
        #         burst.append(reg_list[i][1]) # burst蓄積
        #     # アドレスが違うならmulti
        #     else:
        #         # burstの最後なのでburstを送信
        #         if flg:
        #             flg = False
        #             burst.append(reg_list[i][1]) # 最後のburst
        #             device.write_burst(reg_list[i][0], burst)
        #             burst.clear()
        #         else:
        #             # multi蓄積
        #             multi.append(reg_list[i])
        # if len(multi) > 0:
        #     device.write_multi(multi)

    def unique(self, cmd, ch):
        if cmd.unique_type != UniqueType.CHIP:
            return

        if cmd.cmd == YMF825UniqueType.WRITE_CONTROL_REGISTER:
            data = cmd.data.split(" ") 
            self.ctrl_prm[ch].append((data[0].strip(),int(data[1].strip())))

        elif cmd.cmd == YMF825UniqueType.SET_TONE_TABLE:
            data = cmd.data.split(" ") 
            if len(data) == 2: # no id
                no = int(data[0])
                id = data[1].strip()
                if 0 <= no and no <= 15:
                    if id in self.tone_data_dic.keys():
                        self.tone_table[no] = id
                    else:
                        raise Exception(f"tone_id dose not exist in tone_data. -> {id}")

        elif cmd.cmd == YMF825UniqueType.WRITE_TONE_TABLE:
            self.flg_write_tone_table = True
            self.tone_table_num = int(cmd.data)
        
        elif cmd.cmd == YMF825UniqueType.WRITE_EQ:
            self.flg_write_eq = True
            data = cmd.data.split(" ")
            if len(data) == 6:
                coef = (int(data[0]), [float(v) for v in data[1:]])
                self.eq_coef.append(coef)

    #--------------------------------------------------------
    # 便利関数
    @staticmethod
    def write_eq(device, band, data):
        if len(data) == 15:
            adr = band + 32
            device.write_burst(adr, data)

    @staticmethod
    def write_tone(device, tone_list):
        num = len(tone_list)
        data = [0x80 + num]
        for i in range(len(tone_list)):
            data.extend(tone_list[i])
        data.extend([0x80,0x03,0x81,0x80])
        device.write_burst(7, data)

    @staticmethod
    def print_control_register(device):
        ctrl = []
        for i in range(128):
            device.write_single(21, i)
            ctrl.append(device.read_single(22))
        for i in range(16):
            print(f"{i*8:02x}:",end="")
            for k in range(8):
                print(f"{ctrl[i*8+k][0]:02x} ",end="")
            print()

    @staticmethod
    def print_register(device):
        reg = []
        for i in range(80):
            if i in YMF825Register.NOT_READ:
                reg.append(0)
            else:
                reg.append(int(device.read_single(i)[0]))
        for i in range(8):
            for k in range(10):
                print(f"{reg[i*10+k]:02x} ",end="")
            print()
