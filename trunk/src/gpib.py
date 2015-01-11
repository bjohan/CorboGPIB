import serial
import sys
import time

class GpibInterface:
    def __init__(self, iface):
        self.iface = iface
        self.debugEnable = False
        self.currentAddress = None
        self.setAddress(1)

    def printHex(self, string):
        w = 10
        currChar = 0
        for char in string:
           print "%02x"%ord(char),
           if (currChar % w) == w -1:
               print
           currChar += 1
        print 

    def sendControllerCommand(self, cmd):
        self.write("++%s\n"%(cmd))

    def sendCommand(self, cmd):
        self.write("%s\n"%(cmd))
    
    def read(self):
        self.sendControllerCommand('read')
        return self.readData()
    
    def readLoop(self, terminators = ['\n','\r']):
        data = ''
        while True:
            d = self.iface.read()
            if d:
                data+=d
                for t in terminators:
                    if t in d:
                        if self.debugEnable:
                            print "Hit terminator"
                        return (data, d)
            else:
                return(data,d) 
        
    def readData(self, terminators = ['\n','\r']):
        (data, d) = self.readLoop(terminators)
        if self.debugEnable:
            print "Time", time.time() 
            if len(d):   
                print "Got string:", data, "lastChar was 0x%02x"%(ord(d))
                print "Hex representation"
                self.printHex(data)
            elif len(data):
                print "Got string:", data
                print "Hex representation"
                self.printHex(data)
            else:
                print "Got no data"
            print 30*'='
        return data


    def write(self, data):
        if self.debugEnable:
            print "Time", time.time()
            print "Sending", data
            print "Hex representation:"
            self.printHex(data)
            print 30*'='
        self.iface.write(data)

    def setAddress(self, addr):
        if addr != self.currentAddress:
            self.write('++addr %d\n'%(addr))
            self.currentAddress = addr

class GpibDevice:
    def __init__(self, gpibDevice, addr):
        self.gpib = gpibDevice
        self.addr = addr

    def sendCommand(self, cmd):
        self.gpib.setAddress(self.addr)
        self.gpib.sendCommand(cmd)
    
    def write(self, data):
        self.gpib.setAddress(self.addr)
        self.gpib.write(data)

    def read(self):
        self.gpib.setAddress(self.addr)
        return self.gpib.read()

    def readIterative(self, maxTime= 5, minLen = 1):
        t0 = time.time();
        while time.time() < t0+maxTime:
            time.sleep(0.05)
            data = self.read()
            if len(data) > minLen:
                return data
