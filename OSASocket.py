# Connect to AQ6370C

import socket

class OSA:
    """
    class for operating the optical spectrum analyzer
    """
    def __init__ (self, ip, port,
                    username = 'anonymous', password = ' ',
                    timeout = 10,
                    addrFamily = socket.AF_INET,
                    socType = socket.SOCK_STREAM,
                    protocol=0):
        """
        IP: IP of the instrument
        port: port number of the instrument
        username: username of the instrument, "anonymous" (default)
        password: password of the instrument, " " (default)
        timeout: timeout on blocking connection, 10 seconds (default)
        addrFamily: address family, AF_INET(default) | AF_INET6 | AF_UNIX
        socType: socket type, SOCK_STREAM(default) | SOCK_DGRAM
        protocal: 0 (default)
        """

        self.__osa = socket.socket(addrFamily, socType, protocol)
        self.__osa.settimeout(timeout)
        try:
            self.__osa.connect((ip, port))
            print ('Successfully connected to the optical spectrum analyser')
        except TimeoutError:
            print ('ERROR: Cannot connect to the optical spectrum analyser')
            exitWin()
        except:
            print('Unexpected Error! Check the IP and port and the connection')
            exitWin()
        
        self.send('open "' + username + '"')
        print(self.recv())
        self.send(password)
        recStr = self.recv()
        if (recStr[:5] == 'ready'):
            print ('User authenticated.')
        else:
            print ('User authentication error')
            exitWin()
    
    def recv (self, bufsize = 1024):
        return self.__osa.recv(bufsize).decode()

    def send (self, sendStr):
        strLen = self.__osa.send(sendStr.encode())
        if strLen == len(sendStr):
            print('Command "' + sendStr + '" sent successfully')
        else:
            print('Command sent uncompletely')
    
    def reset(self):
        self.send('*RST')
    
    def sweep(self, sweepMode = 'REPEAT'):
        """
        SWEEP soft key
        sweepMode can be one of the following modes:
        AUTO (3)
        REPEAT (2) default
        SINGLE (1)
        and sweepMode is case-insensitive
        """
        if sweepMode.upper() in ['AUTO', 'REPEAT', 'SINGLE' '3', '2', '1']:
            self.__osa.send(':INITIATE:SMODE ' + sweepMode)
            self.__osa.send(':INITIATE')
        else:
            print('unsuitable sweep mode')
    
    def span(self, start, stop):
        """
        SPAN SOFT KEY
        start: start wavelength in nanometer, e.g. 1550(integer) -> 1550 nm
        stop: stop wavelength in nanometer
        """
        self.__osa.send(':SENSE:WAVELENGTH:START ' + str(start) + 'NM')
        self.__osa.send(':SENSE:WAVELENGTH:STOP ' + str(stop) + 'NM')
    
    def level(self, refLevel = -10.0, logScale = 10.0, autoRefLevel = False,
              subLog = 5.0, offsetLevel = 0, autoSubScale = True):
        """
        refLevel: reference level in dBm, -10.0 dBm (default)
        logScale: log scale in dB/D, 10 dB/D (default)
        autoRefLevel: Auto Reference Level
        subLog: sub log
        offsetLevel: offset level
        autoSubScale: auto sub scale ON(True) (default) | OFF(False)
        """
        self.__osa.send(':DISPLAY:WINDOW:TRACE:Y1:SCALE:PDIVISION '+double2expStr(logScale)) # without unit (DB)
        if autoRefLevel:
            self.__osa.send('CALCULATE:MARKER:MAXIMUM:SRLEVEL:AUTO')
        else:
            self.__osa.send(':DISPLAY:WINDOW:Y1:SCALE:RELVEL ' + double2expStr(logScale)) # without unit (DBM)
        self.__osa.send(':DISPLAY:WINDOW:TRACE:Y2:SCALE:PDIVISION '+double2expStr(subLog)) # without unit (DB)
        if autoSubScale:
            self.__osa.send(':DISPLAY:WINDOW:TRACE:Y2:SCALE:AUTO ON')
        else:
            self.__osa.send(':DISPLAY:WINDOW:TRACE:Y2:SCALE:AUTO OFF')
            self.__osa.send(':DISPLAY:WINDOW:TRACE:Y2:SCALE:OLEVEL '+double2expStr(offsetLevel)) # without unit (DB)
    
    def setup(self):
        """
        """
    
    def trace(self, channel, write=True, disp = True, calcC = 0):
        """
        channel: trace channel
        write: write data? True (write) | False (fix)
        disp: display the data of the selected channel, True (display) | False (blank)
        calcC: calculate C channel? >0 (calculate) | 0 (do not calculate)
        calcC = 1: C = A - B (LOG)
        calcC = 2: C = B - A (LOG)
        calcC = 3: C = A + B (LOG)
        """
        channel = channel.upper()
        if channel not in ['A', 'B', 'C', 'D', 'E', 'F', 'G']:
            print('Unsuitable channel')
        self.__osa.send(':TRACE:ACTIVE TR'+channel) # get selected channel active
        switch = 'ON' if disp else 'OFF'
        self.__osa.send(':TRACE:STATE:TR'+channel+' '+switch)
        if calcC:
            calcMode = {1:'A-B (LOG)', 2:'B-A (LOG)', 3:'A+B (LOG)'}
            self.__osa.send(':CALCULATE:MATH:TRC '+calcMode[calc])
    
    def saveFile(self, filename, form = 'CSV', channel = 'C', memory = 'EXT'):
        """
        filename: filename
        form: format, CSV | BIN
        channel: A, B, C
        memory: INTernal | EXTernal
        """
        channel = channel.upper()
        if channel not in ['A', 'B', 'C']:
            print('Unsuitable channel')
        # self.__osa.send(':MMEMORY:CDRIVE '+memory)
        # self.__osa.send(':MMEMORY:CDIRECTORY <DIRECTORY NAME>')
        self.__osa.send(':MMEMORY:STORE:TRACE TR'+channel+','+form+'"'+filename+'",'+memory)
        #self.__osa.send(':MMEMORY:STORE:DATA "'+filename+'",'+memory)



# custom functions
def exitWin():
    input('Enter any key to exit...\n')
    exit()   

def double2expStr(digit):
    flag = '-' if digit < 0 else ''
    digit = abs(digit)
    if digit < 10:
        return str(digit)
    e = 1
    digit /= 10
    while digit > 10:
        e += 1
        digit /= 10
    return flag+str(digit)+'E'+str(e)
