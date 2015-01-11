import serial
import sys
import time

def range125(start, stop):
    r = []
    while start < stop:
        r.append(start)
        r.append(start*2)
        r.append(start*5)
        start*=10
    return r

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

class Hp3438ADigitalMultimeter(GpibDevice):
    def __init__(self, gpibDevice, addr):
        GpibDevice.__init__(self, gpibDevice, addr)

    def readValue(self, maxTries = 10):
        while True:
            data = self.read()
            time.sleep(0.01)
            if len(data) > 2:
                break
            if maxTries > 0:
                maxTries -= 1
            else:
                print "Not getting any data, giving up"
                return (None, None)
        try:
            (value, unit) = data.strip().split(',')
            numVal = float(value)
            strUnit = ['V DC', 'V AC', 'A DC', 'A AC', 'Ohm'][int(unit)-1]
        except:
            print "Unable to parse:", data
            return (None, None)
        return (numVal, strUnit)

class Tektronix2430A(GpibDevice):

    channelVals = [1,2]
    bandwidthVals = ['TWEnty', 'FIFty', 'FULl']
    #Note that the scope divides this value with probe attenuation
    voltagePerDivisionVals = range125(0.0001, 5000)[1:] #skip 100uV
    voltagePerDivisionVariableVals = range(0,100)
    channelPositionVals = range(-10, 10)
    couplingVals = ['AC', 'DC', 'GND']
    fiftyOhmVals = ['ON', 'OFF']
    invertVals = ['ON', 'OFF']
    validChannelParameters = [channelVals, voltagePerDivisionVals, 
                                voltagePerDivisionVariableVals, 
                                channelPositionVals, couplingVals, fiftyOhmVals,
                                invertVals]
    def __init__(self, gpibDevice, addr):
        GpibDevice.__init__(self, gpibDevice, addr)

    
    def verifyParameters(self, toValidate, validParams):
        valid = True
        for (tv, valid) in zip(toValidate, validParams):
            if tv not in valid:
                print tv, "is not a valid. The valid values are:", valid
                valid = False;
        return valid

    def getIdentification(self):
        self.sendCommand('ID?')
        #time.sleep(0.2)
        return self.readIterative()
    
    def getChannelInfo(self):
        self.sendCommand('CH1?')
        #time.sleep(0.2)
        return self.readIterative()

    def setChannel(self, ch, voltsPerDiv, varVoltsPerDiv, pos, coupling, fiftyOhm, invert):
        #self.gpib.debugEnable = True
        if not self.verifyParameters([ch, voltsPerDiv, varVoltsPerDiv, pos, coupling, fiftyOhm, invert], Tektronix2430A.validChannelParameters):
            print "Invalid parameter(s) channel is not configured"
        else:
            self.sendCommand("CH%d VOLTS:%f,VARIABLE:%d,POSITION:%d,COUPLING:%s,FIFTY:%s,INVERT:%s"%(ch, voltsPerDiv, varVoltsPerDiv, pos, coupling, fiftyOhm, invert))
            #time.sleep(0.3)
            return self.readIterative()

    def getBandwidthLimit(self):
        self.sendCommand('BWL?')
        #time.sleep(0.2)
        return self.readIterative()

    def setBandwidthLimit(self, lim):
        if not self.verifyParameters([lim], [Tektronix2430A.bandwidthVals]):
            print "Invalid parameter bandwidth limit is not configured"
        else:
            self.sendCommand('BWL %s'%(lim))
            return self.readIterative()
        
    def getTrace(self):
        self.sendCommand('WAV?')
        #time.sleep(0.3)
        return self.readIterative()

print "opeinging", sys.argv[1]
p = serial.Serial(sys.argv[1], 115200, timeout = 1)
gpib = GpibInterface(p)
#gpib.debugEnable = True
meter = Hp3438ADigitalMultimeter(gpib, 2)
print "Reading from multimeter:", meter.readValue()

scope = Tektronix2430A(gpib,1)
print "Getting identification"
print scope.getIdentification()
print scope.getTrace()
print "Setting bwl"
print scope.setBandwidthLimit('TWEnty')
print "Getting bwl"
print scope.getBandwidthLimit()
print "Configuring channel 1"
print scope.setChannel(1,0.1,0,0,'AC', 'OFF', 'OFF')
print "reading channel 1"
data = scope.getChannelInfo()
print "Got", data
