import sys,time,serial

import cv2
from cv2 import aruco
import numpy as np

##################################################################################################################

### --- class CH9329 : emulator functions --- ###
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

    ##includes mapping between frame_size(480, 640) & device's screen size(2736, 1824)
    def moveabs(self,x,y):

    ## 0 < X < self.xsize, 0 < Y < self.ysize
        if(x>=self.xsize):
            x=self.xsize - 1
        if(x<=0):
            x=1
        if(y>=self.ysize):
            y=self.ysize - 1
        if(y<=0):
            y=1

        xm = (640 - x) * (self.xsize / 640)  ## xm = x coordinate in the frame * (screen xsize / frame xsize)
        ym = y * (self.ysize / 480)  ## ym = y coordinate in the frame * (screen ysize / frame ysize)

        b=[0x57,0xAB,0x00,0x04,0x07,0x02]
        b.append(0x00)
        xabs=int(4096*xm/self.xsize)
        b.append(xabs & 0xff)
        b.append(xabs >> 8)
        yabs=int(4096*ym/self.ysize)
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

    def dblclick(self,btn):
        if(btn in self.BTN):
            for _ in range (2):
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

    def drag(self,x,y):
        #b=[0x57,0xab,0x00,0x05,0x05,0x01,0x01,0x00,0x00,0x00,0x0E] #マウスの左ボタンクリックのパケット
        #self.sendpacket(b)
        
        #while keyboard.is_pressed('d'):
            if(x>=self.xsize):
                x=self.xsize - 1
            if(x<=0):
                x=1
            if(y>=self.ysize):
                y=self.ysize - 1
            if(y<=0):
                y=1

            xm = (640 - x) * (self.xsize / 640)  ## xm = x coordinate in the frame * (screen xsize / frame xsize)
            ym = y * (self.ysize / 480)  ## ym = y coordinate in the frame * (screen ysize / frame ysize)

            b=[0x57,0xAB,0x00,0x04,0x07,0x02,0x01] ##最後に0x01追加(マウスの左ボタンを押したまま)
            xabs=int(4096*xm/self.xsize)
            b.append(xabs & 0xff)
            b.append(xabs >> 8)
            yabs=int(4096*ym/self.ysize)
            b.append(yabs & 0xff)
            b.append(yabs >> 8)
            b.append(0x00)
            s=sum(b) & 0xff
            b.append(s)
            self.sendpacket(b)
        
        #b=[0x57,0xab,0x00,0x05,0x05,0x01,0x00,0x00,0x00,0x00,0x0D] #何も推してない状態
        #self.sendpacket(b)

    def close(self):
        pass
        self.ser.close()

##################################################################################################################

### --- class MarkSearch : search markers and extract the coordinates --- ###
class MarkSearch :

    ### --- aruco設定 --- ###
    dict_aruco = aruco.Dictionary_get(aruco.DICT_4X4_50)
    parameters = aruco.DetectorParameters_create()

    def __init__(self, cameraID):
        self.cap = cv2.VideoCapture(cameraID) ##cameraID

    def get_mark_coordinate(self, num_id):
        ##################################
        marker_length = 0.056 # [m]
        dictionary = aruco.getPredefinedDictionary(aruco.DICT_ARUCO_ORIGINAL)
        # for the videocapture adjustment, read the files in the same directory which are made by calib.py
        camera_matrix = np.load("mtx.npy")
        distortion_coeff = np.load("dist.npy")
        ###################################

        ret, frame = self.cap.read()
        gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY) # convert the image to gray scale
        corners, ids, rejectedImgPoints = aruco.detectMarkers(gray, dict_aruco, parameters=parameters)

        ### num_id のマーカーが検出された場合 ###
        if num_id in np.ravel(ids) :
            ### while a marker is detected, calculate the pose
            for i, corner in enumerate(corners):
                # rvec -> rotation vector, tvec -> translation vector
                rvec, tvec, _ = aruco.estimatePoseSingleMarkers(corner, marker_length, camera_matrix, distortion_coeff)

                # < rodoriguesからeuluerへの変換 >

                # 不要なaxisを除去
                tvec = np.squeeze(tvec)
                rvec = np.squeeze(rvec)
                # 回転ベクトルからrodoriguesへ変換
                rvec_matrix = cv2.Rodrigues(rvec)
                rvec_matrix = rvec_matrix[0] # rodoriguesから抜き出し
                # 並進ベクトルの転置
                transpose_tvec = tvec[np.newaxis, :].T
                # 合成
                proj_matrix = np.hstack((rvec_matrix, transpose_tvec))
                # オイラー角への変換
                euler_angle = cv2.decomposeProjectionMatrix(proj_matrix)[6] # [deg]

                global mc ## to share the variable mc between threads
                ## scopes below are measured by experiments, and modifiable according to a user
                if -90 < int(euler_angle[2]) < -30:
                    #print("rolling right")
                    mc = 1
                elif 30 < int(euler_angle[2]) < 90:
                    #print("rolling left")
                    mc = 2

                if -165 < int(euler_angle[0]) < -90: ## because default front value is wether -180~-170 or 170~180
                    #print("pitching down")
                    mc = 3
                elif 90 < int(euler_angle[0]) < 140:
                    #print("pitching up")
                    mc = 4

                if (40 < int(euler_angle[1]) < 90) or (-90 < int(euler_angle[1]) < -40): ## or include yawing left, make the drag function to be used widely
                    #print("yawing right")
                    mc = 5
                #elif -90 < int(euler_angle[1]) < -40:
                    #print("yawing left")
                    #mc = 5
            
            ### And, extract its coordinates
            index = np.where(ids == num_id)[0][0] #num_id が格納されているindexを抽出
            cornerUL = corners[index][0][0]
            cornerUR = corners[index][0][1]
            cornerBR = corners[index][0][2]
            cornerBL = corners[index][0][3]

            centerx = (cornerUL[0]+cornerBR[0])/2
            centery = (cornerUL[1]+cornerBR[1])/2

            #center = [ (cornerUL[0]+cornerBR[0])/2 , (cornerUL[1]+cornerBR[1])/2 ]

            return centerx, centery

        return None

##################################################################################################################

### --- Establish threads --- ###

import threading
import time
##import keyboard ## no need from ver6

# Global variable to signal threads to exit
exit_signal = threading.Event() # Event制御

# Function to extract coordinates
def extract_cdnt():
    global mc ## to share the variable mc between threads
    while not exit_signal.is_set():
        print(' ----- get_mark_coordinate ----- ')
        print(cam0_mark_search.get_mark_coordinate(markID)) #属性（オブジェクトの変数）取得
        if (cam0_mark_search.get_mark_coordinate(markID) != None) and (mc != 1 or mc != 2) : # to prevent drag
            xi, yi = cam0_mark_search.get_mark_coordinate(markID)
            drv.moveabs(xi, yi)
            while mc == 5 :
                xi, yi = cam0_mark_search.get_mark_coordinate(markID) #return値を二つ格納
                print("dragging...")
                drv.drag(xi, yi)  # No matter time.sleep exits, time lag occurs & the following packet is not sent immediately
                #time.sleep(0.01)
            b=[0x57,0xab,0x00,0x05,0x05,0x01,0x00,0x00,0x00,0x00,0x0D] #何も推してない状態
            drv.sendpacket(b)
        time.sleep(0.1)  # Simulating the extraction process

# Function to execute different tasks based on gestures(ar marker's pose)
def mouse_controller():
    global mc ## to share the variale mc between threads
    while not exit_signal.is_set():
        try:
            if mc == 1 :
                print("Function 'Right click' executed")
                drv.click(CH9329.R_BTN)
            elif mc == 2 :
                print("Function 'Left click' executed")
                drv.click(CH9329.L_BTN)
            elif mc == 3 :
                print("Function 'scroll up' executed")
                drv.scroll(1)
            elif mc == 4:
                print("Function 'scroll down' executed")
                drv.scroll(-1)
            mc = 0 ## to prevent endless function execution
            time.sleep(0.1) ## 3 times bigger than the def extract_cdnt(class MarkSearch), to prevent overreaction  
        except KeyboardInterrupt:
            exit_signal.set()

##################################################################################################################
            
### --- main program --- ###

def main():
    # Create threads for coordinate extraction and keyboard input handling
    extract_thread = threading.Thread(target=extract_cdnt)
    controll_thread = threading.Thread(target=mouse_controller)

    # Start the keyboard_listener thread first to simulate HIGHER PRIORITY (foreground task)
    controll_thread.start()
    extract_thread.start()

    try:
        while not exit_signal.is_set():
            time.sleep(0.1)  # Main thread waits for exit signal
    except KeyboardInterrupt:
        print("\nKeyboardInterrupt detected. Finishing the program...")
        cam0_mark_search.cap.release()

    # Set exit signal for threads to finish gracefully
    exit_signal.set()

    # Wait for threads to finish
    extract_thread.join()
    controll_thread.join()

    print("Program finished.")

##################################################################################################################
    
### --- Execute the program --- ###

if __name__ == "__main__":
    ### --- aruco設定 --- ###
    dict_aruco = aruco.Dictionary_get(aruco.DICT_4X4_50)
    parameters = aruco.DetectorParameters_create()

    ### --- parameter --- ###
    cameraID = 0
    cam0_mark_search = MarkSearch(cameraID) #MarkSearch のオブジェクト作成

    markID = 1

    drv = CH9329('COM5',9600,2736,1824) #CH9329 のオブジェクト作成

    mc = 0 ## a flag which is used between threads;
    main()


drv.close() #解説書によると、この行は無くても可能