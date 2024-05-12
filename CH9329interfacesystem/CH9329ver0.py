import sys,time,serial

class CH9329():
    L_BTN=0x01; R_BTN=0x02; M_BTN=0x04
    BTN={L_BTN,R_BTN,M_BTN}

    ZENHAN=0x35; ENTER=0x28; SPACE=0x2C; BACKSPACE=0x2A; SHIFT=0xE1
    CTRL=0xE0; ALT=0xE2; TAB=0x2B; ESC=0x58; WINDOWS=0xE3

    SPK={ZENHAN, ENTER, SPACE, BACKSPACE, SHIFT, CTRL, ALT, TAB, ESC, WINDOWS}

    TBL={'!':[2,0x1E], '"':[2,0x1F], '#':[2,0x20], '$':[2,0x21], '%':[2,0x22],
         '&':[2,0x23], "'":[2,0x24], '=':[2,0x2D],
         '-':[0,0x2D], '~':[2,0x2E], '^':[0,0x2E], '|':[2,0x89], '\\':[0,0x89],
         '`':[2,0x2F], '@':[0,0x2F], '{':[2,0x30], '[':[0,0x30], '}':[2,0x31],
         ']':[0,0x31], '*':[2,0x34], ':':[0,0x34], '+':[2,0x33], ';':[0,0x33],
         '<':[2,0x36], ',':[0,0x36], '>':[2,0x36], '.':[0,0x36], '?':[2,0x38],
         '/':[0,0x38], '_':[2,0x87], '\\':[0,0x87] }

    TBL['0']=[0,0x27] #数字(0)
    for i in range(9):
        TBL[chr(i+1+48)]=[0,0x1E+i] #数字(1-9)
    for i in range(26):
        TBL[chr(i+65)]=[2,0x04+i] #大文字(A-Z)
        TBL[chr(i+97)]=[0,0x04+i] #小文字(a-z)

    EJECT=8; CDSTOP=9; PREVTRACK=10; NEXTTRACK=11;
    PLAYPAUSE=12; MUTE=13; VOLUMEM=14; VOLUMEP=15;
    MTBL={
        EJECT:    [0x02,0x80,0x00,0x00],
        CDSTOP:   [0x02,0x40,0x00,0x00],
        PREVTRACK:[0x02,0x20,0x00,0x00],
        NEXTTRACK:[0x02,0x10,0x00,0x00],
        PLAYPAUSE:[0x02,0x08,0x00,0x00],
        MUTE:     [0x02,0x04,0x00,0x00],
        VOLUMEM:  [0x02,0x02,0x00,0x00],
        VOLUMEP:  [0x02,0x01,0x00,0x00]
    }

    def __init__(self,port="COM5",baud=9600,xsize=2736,ysize=1824):
        #self.port=port #open COM port
        #self.baud=baud #Baudrate
        self.xsize=xsize #Screen X size
        self.ysize=ysize #Screen Y size
        #self.ser = serial.Serial( 'COM5', 9600, timeout = 1)
        #self.ser.port = self.port
        #self.ser.baudrate = self.baud
        #self.ser.timeout = 0

        #緒方先生と作成したコード（53~59行目）
        #コメントアウト（41, 42, 45~48行目）
        #生かしたコード（194, 195行目）
        self.ser = serial.Serial()
        self.ser.port = port
        self.ser.baudrate = 9600
        self.ser.parity = serial.PARITY_NONE
        self.ser.stopbits = serial.STOPBITS_ONE
        self.ser.bytesize = serial.EIGHTBITS
        self.ser.timeout = 5

        try:
            self.ser.open()

        except:
            print("can't open" + self.ser.port )
            sys.exit(0)

    def sendpacket(self,data):
        #print(hex(data))
        """
        print('[ ',end="")
        for i in data:
            print("{:02X}".format(i),end=" ")
        print(']')
        """
        self.ser.write(bytes(data))
        time.sleep(0.02)
        return self.ser.read(7)

    def push(self,k0,k1,k2=0,k3=0,k4=0,k5=0,k6=0):
        #print(self.port,": ",hex(k0),hex(k1))
        b=[0x57,0xAB,0x00,0x02,0x08,k0,0x00,k1,k2,k3,k4,k5,k6]
        b.append(sum(b) & 0xff)
        self.sendpacket(b)
        b=[0x57,0xAB,0x00,0x02,0x08,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x0c]
        self.sendpacket(b)

    def print(self,st):
        if len(st)<1:
            return
        for x in st:
            if(x in self.TBL):
                dat=self.TBL[x]
                self.push(dat[0],dat[1])

    def write(self,k):
        if(k in self.TBL): #通常キーの場合
            dat=self.TBL[k]
            self.push(dat[0],dat[1])
        if(k in self.SPK): #特殊(装飾)キーの場合
            if(k==self.SHIFT):
                self.push(0x02,0)
                return
            if(k==self.CTRL):
                self.push(0x01,0)
                return
            self.push(0x00,k)

    def media(self,mk):
        if(mk in self.MTBL):
            b=[0x57,0xAB,0x00,0x03,0x04]
            dat=self.MTBL[mk]
            b.append(dat[0])
            b.append(dat[1])
            b.append(dat[2])
            b.append(dat[3])
            s=sum(b) & 0xff
            b.append(s)
            self.sendpacket(b)
            b=[0x57,0xAB,0x00,0x03,0x04,0x02,0x00,0x00,0x00,0x0B]
            self.sendpacket(b)

    def moveabs(self,x,y):
        b=[0x57,0xAB,0x00,0x04,0x07,0x02]
        b.append(0x00)
        xabs=int(4096*x/self.xsize)
        b.append(xabs & 0xff)
        b.append(xabs >> 8)
        yabs=int(4096*y/self.ysize)
        b.append(yabs & 0xff)
        b.append(yabs >> 8)
        b.append(0x00)
        s=sum(b) & 0xff
        b.append(s)
        self.sendpacket(b)

    def moverel(self,x,y):
        if(x>127):
            x=127
        if(x<-128):
            x=-128
        if(y>127):
            y=127
        if(y<-128):
            y=-128
        b=[0x57,0xab,0x00,0x05,0x05,0x01]
        b.append(0x00)
        if(x<0): #左に移動する場合
            x=0x100+x
        if(y<0): #上に移動する場合
            y=0x100+y
        b.append(x)
        b.append(y)
        b.append(0x00)
        s=sum(b) & 0xff
        b.append(s)
        self.sendpacket(b)

    def click(self,btn):
        if(btn in self.BTN):
            b=[0x57,0xab,0x00,0x05,0x05,0x01]
            b.append(btn)
            b.append(0)
            b.append(0)
            b.append(0x00)
            s=sum(b) & 0xff
            b.append(s)
            self.sendpacket(b)
            b=[0x57,0xab,0x00,0x05,0x05,0x01,0x00,0x00,0x00,0x00,0x0D]
            self.sendpacket(b)

    def scroll(self,scr):
        if(scr>127):
            scr=127
        if(scr<-127):
            scr=-127
        if(scr<0): #下方向にスクロール
            scr=0x100+scr
        b=[0x57,0xab,0x00,0x05,0x05,0x01,0x00,0x00,0x00]
        b.append(scr)
        s=sum(b) & 0xff
        b.append(s)
        self.sendpacket(b)

    def close(self):
        pass
        self.ser.close()

drv=CH9329('COM5',9600,2736,1824)

#drv.print('#Abc')
#drv.write('#')
#drv.push(0x02,0x04)
drv.moveabs(100,100)
drv.moveabs(968,500)
#drv.moverel(-30,0)
#drv.moverel(0,50)
#drv.media(CH9329.MUTE)
#drv.media(CH9329.VOLUMEP)
#drv.click(CH9329.L_BTN)
#drv.click(CH9329.R_BTN)
#drv.scroll(1)
#drv.scroll(-10)
#drv.scroll(-10)
#drv.scroll(-1)

drv.close()
