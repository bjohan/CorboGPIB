import time
import gpib
#TODO try to come up with a more general parser/generator for various GPIB messages
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
    ch1 = {
        "VOLTS": ('f', ('set', range125(0.0001, 5000)[1:])), #skip 100uV
        "VARIABLE": ('f', ('range', 0.0, 100.0)),
        "POSITION": ('f', ('range', -10.0, 10.0)),
        "COUPLING": ('s', ("AC", "DC", "GND")),
        "FIFTY": ('s', ("ON", "OFF")),
        "INVERT": ('s', ("ON", "OFF")),
    }
    ch2 = ch1
    probe = ('s', ("CH1", "CH2", "EXT1", "EXT2"))
    bandwidthLimit = ('s', ("TWENTY", "FIFTY", "FULL"))
    verticalMode = {
        "CH1": ('s', ("ON", "OFF")),
        "CH2": ('s', ("ON", "OFF")),
        "ADD": ('s', ("ON", "OFF")),
        "MULT": ('s', ("ON", "OFF")),
        "DISPLAY": ('s', ("XY", "XT"))}

    bandwidthVals = ['TWEnty', 'FIFty', 'FULl']

    setTv = {
        "ICOUPLING": ('s', ("FLD1", "FLD2", "ALT", "TVLINE")),
        "NICOUPLING": ('s', ("FLD1", "TVLINE")),
        "INTERLACED": ('s', ("This command is query only, do not use")),
        "TVCLAMP": ('s', ("ON", "OFF")),
        "TVLINE": ('i', None),
        "LCNTRESET": ('s', ("F1ONLY", "BOTH")),
        "LCNTSTART": ('s', ("PREFID", "ATFID")),
        "SYNC": ('s', ("PLUS", "MINUS")),
    }

    setWord = {
        "RADIX": ('s', ("OCT", "HEX")),
        "CLOCK": ('s', ("ASYNC", "FALL", "RISE")),
        "WORD": ('s', None), #TODO make validation support this kind of value
                              #01Xx0110x01X etc.
        "PROBE": ('s', ("This command is query only, do not use")),
    }

    extGain = {
        "EXT1": ('s', ("DIV1", "DIV5")),
        "EXT2": ('s', ("DIV1", "DIV5")),
    }

    def __init__(self, gpibDevice, addr):
        gpib.GpibDevice.__init__(self, gpibDevice, addr)

    def identify(self):
        idString = self.getIdentification()
        if idString:
            return "TEK/2430A" in idString
        return False
    
    def getIdentification(self):
        self.sendCommand('ID?')
        return self.readIterative()
    
    def getBandwidthLimit(self):
        self.sendCommand('BWL?')
        return self.readIterative()

    def setBandwidthLimit(self, lim):
        if self.validateValue(lim, Tektronix2430A.bandwidthLimit):
            self.sendCommand('BWL %s'%(lim))
            return self.readIterative()

    def getProbes(self):
        self.sendCommand('PROB?')
        probes = self.readIterative() 
        parsed = parse(probes, 'iiii')
        return parsed

    def getVerticalMode(self):
        self.sendCommand('VMO?')
        vmode = self.readIterative().split(' ')[1] 
        parsed = parse(vmode, 'sssss')
        return parsed

    def validateAndSendCommand(self, cmd, din, dref):
        if self.validateDictionary(din, dref):
            self.sendCommand(cmd+' '+self.buildCommand(din))
            return self.readIterative()

    def setVerticalModeD(self, d):
        return self.validateAndSendCommand('VMODE', d, Tektronix2430A.verticalMode)

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

    def getTraceF(self):
            return self.toFloat(self.getTrace().split('CURVE')[1])

    def toFloat(self, data):
        f = []
        for d in data.split(','):
            f.append(float(d))
        return f

    def getChannel1(self):
        self.sendCommand('CH1?')
        ch1 = self.readIterative().split(' ')[1]
        return parse(ch1, 'fffsss')

    def setChannel1D(self,d):
        if self.validateDictionary(d, Tektronix2430A.ch1):
            self.sendCommand('CH1 '+self.buildCommand(d))
            return self.readIterative()

    def getChannel2(self):
        self.sendCommand('CH2?')
        ch2 = self.readIterative().split(' ')[1]
        return parse(ch2, 'fffsss')
    
    def setChannel2D(self,d):
        if self.validateDictionary(d, Tektronix2430A.ch2):
            self.sendCommand('CH2 '+self.buildCommand(d))
            return self.readIterative()

    def getSetTv(self):
        #Untested, i do not have tv trigger on my scope
        self.sendCommand('SETTV?')
        settv = self.readIterative()
        return parse(settv.split(' ')[1], 'ssssisss')

    def setSetTvD(self, d):
        #Untested, i do not have tv trigger on my scope
        return self.validateAndSendCommand('SETTV', d, Tektronix2430A.setTv)

    def getSetWord(self):
        self.sendCommand('SETWORD?')
        word = self.readIterative()
        return parse(word.split(' ')[1], 'ssss')
        
    def setSetWordD(self, d):
        #Untested, i do not have tv trigger on my scope
        return self.validateAndSendCommand('SETWORD', d, Tektronix2430A.setWord)

    def manTrig(self):
        self.sendCommand('MANTRIG');
        return self.readIterative()

    def getExtGain(self):
        #untested does not seem to be supported by my scope
        self.sendCommand('EXTGAIN?')
        eg = self.readIterative()
        return parse(eg.split(' ')[1], 'ss')
        
    def setSetExtGainD(self, d):
        #untested does not seem to be supported by my scope
        return self.validateAndSendCommand('EXTGAIN?', d, Tektronix2430A.extGain)
    
