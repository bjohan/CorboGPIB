import time
import gpib

def range125(start, stop):
    r = []
    while start < stop:
        r.append(start)
        r.append(start*2)
        r.append(start*5)
        start*=10
    return r

class Tektronix2430A(gpib.GpibDevice):
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
        gpib.GpibDevice.__init__(self, gpibDevice, addr)
    
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
    
    def getChannelInfo(self):
        self.sendCommand('CH1?')
        return self.readIterative()

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
        
    def getTrace(self):
        self.sendCommand('WAV?')
        return self.readIterative()

