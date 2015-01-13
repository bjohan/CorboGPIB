import time
import gpib

def format(string, fmt):
    if fmt == 'i':
        return int(string)
    if fmt == 'f':
        return float(string)
    if fmt == 's':
        return str(string)

def parse(string, flist):
    string = string.strip()
    datas = string.split(',')
    result = {}
    for d,f in zip(datas, flist):
        w = d.split(':')
        result[w[0]] = format(w[1],f)
    return result

def range125(start, stop):
    r = []
    while start < stop:
        r.append(start)
        r.append(start*2)
        r.append(start*5)
        start*=10
    return r

class Tektronix2430A(gpib.GpibDevice):

    aTrigger = {
        "MODE": ('s', ("AUTOLEVEL", "AUTO", "NORMAL", "SGLSEQ")),
        "SOURCE": ('s', ("CH1", "CH2", "VERTICAL", "EXT1", "EXT2")),
        "LOGSRC": ('s', ("WORD", "A.B", "OFF")),
        "COUPLING": ('s',("AC", "DC", "LFREJ", "HFREJ", "NOISEREJ", "TV")),
        "LEVEL": ('f', None),
        "SLOPE": ('s', ("PLUS", "MINUS")),
        "POSITION": ('i',('set', range(31)[1:])),
        "HOLDOFF": ('f',('range', 0.0, 100.0)),
        "ABSELECT":('s', ("A", "B")),
    }

    bTrigger = {
        "MODE": ('s', ("RUNSAFT", "TRIGAFT")),
        "EXTCLK": ('s', ("ON", "OFF")),
        "SOURCE": ('s', ("CH1", "CH2", "WORD", "VERTICAL", "EXT1", "EXT2")),
        "COUPLING": ('s', ("AC", "DC", "LFREJ", "HFREJ", "NOISEREJ")),
        "LEVEL": ('f', None),
        "SLOPE": ('s', ("PLUS", "MINUS")),
        "POSITION": ('i',('set', range(31)[1:])),
    } 
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

    verticalModeCh1 = ['ON', 'OFF']
    verticalModeCh2 = ['ON', 'OFF']
    verticalModeAdd = ['ON', 'OFF']
    verticalModeMult = ['ON', 'OFF']
    verticalModeDisplay = ['XY', 'YT']
    validVerticalModeParameters = [verticalModeCh1, verticalModeCh2,
                                    verticalModeAdd, verticalModeMult,
                                    verticalModeDisplay] 

    def __init__(self, gpibDevice, addr):
        gpib.GpibDevice.__init__(self, gpibDevice, addr)

    def identify(self):
        idString = self.getIdentification()
        if idString:
            return "TEK/2430A" in idString
        return False
    
    def verifyParameters(self, toValidate, validParams):
        valid = True
        for (tv, valid) in zip(toValidate, validParams):
            if tv not in valid:
                print tv, "is not a valid. The valid values are:", valid
                valid = False;
        return valid

    def getIdentification(self):
        self.sendCommand('ID?')
        return self.readIterative()
    
    def getChannelInfo(self, channel):
        self.verifyParameters([channel], [Tektronix2430A.channelVals])
        self.sendCommand('CH%d?'%(channel))
        channelInfo = self.readIterative()
        channelInfo = channelInfo.split(' ')[1]
        return parse(channelInfo, 'fffsss')

    def setChannel(self, ch, voltsPerDiv, varVoltsPerDiv, pos, coupling, fiftyOhm, invert):
        if not self.verifyParameters([ch, voltsPerDiv, varVoltsPerDiv, pos, coupling, fiftyOhm, invert], Tektronix2430A.validChannelParameters):
            print "Invalid parameter(s) channel is not configured"
        else:
            self.sendCommand("CH%d VOLTS:%f,VARIABLE:%d,POSITION:%d,COUPLING:%s,FIFTY:%s,INVERT:%s"%(ch, voltsPerDiv, varVoltsPerDiv, pos, coupling, fiftyOhm, invert))
            return self.readIterative()

    def getBandwidthLimit(self):
        self.sendCommand('BWL?')
        return self.readIterative()

    def setBandwidthLimit(self, lim):
        if not self.verifyParameters([lim], [Tektronix2430A.bandwidthVals]):
            print "Invalid parameter bandwidth limit is not configured"
        else:
            self.sendCommand('BWL %s'%(lim))
            return self.readIterative()

    def getProbes(self):
        self.sendCommand('PROB?')
        probes = self.readIterative() 
        parsed = parse(probes, 'iiii')
        return parsed

    def getVerticalMode(self):
        self.sendCommand('VMO?')
        vmode = self.readIterative() 
        parsed = parse(vmode, 'sssss')
        return parsed

    def setVerticalMode(self, ch1, ch2, add, mult, display): 
        self.verifyParameters([ch1, ch2, add, mult, display], 
                            Tektronix2430A.validVerticalModeParameters)
        self.sendCommand('VMODE CH1:%s,CH2:%s,ADD:%s,MULT:%s,DISPLAY:%s'%
                    (ch1, ch2, add, mult, display))
        return self.readIterative()

    def validateString(self, value, ref):
            if ref:
                return value in ref
            return True

    def validateFloat(self, value, ref):
        if ref:
            if(ref[0] == 'set'):
                return value in ref[1]
            if(ref[0] == 'range'):
                return value <= ref[2] and value >= ref[1]
            return False
        return True
    
    def validateValue(self, value, ref):
        if(ref[0] == 's'):
            return self.validateString(value, ref[1])
        if(ref[0] == 'f'):
            return self.validateFloat(value, ref[1]) #works for all numbers
        if(ref[0] == 'i'):
            return self.validateFloat(value, ref[1]) #works for all numbers
        
    def validateDictionary(self, dinput, dref):
        success = True
        for key in dinput:
            if not self.validateValue(dinput[key], dref[key]):
                print dinput[key], "is not in", dref[key]
                success = False;
        return success       
            
    def getATrigger(self):
        self.sendCommand('ATR?')
        atr = self.readIterative().split(' ')[1]
        return parse(atr, 'ssssfsifs')

    def buildCommand(self, d):
        cmd = ''
        for key in d:
            cmd+="%s:%s,"%(key, str(d[key]))
        return cmd[:-1]

    def setATriggerD(self, d):
        if self.validateDictionary(d, Tektronix2430A.aTrigger):
            print "sending", self.buildCommand(d)
            self.sendCommand("ATR "+self.buildCommand(d))
            return self.readIterative()

    def getBTrigger(self):
        self.sendCommand('BTR?')
        btr = self.readIterative().split(' ')[1]
        return parse(btr, 'ssssfsi')

    def setBTriggerD(self, d):
        self.sendCommand('BTR '+self.buildCommand(d))
        return self.readIterative()

    def getTrace(self):
        self.sendCommand('WAV?')
        return self.readIterative()

