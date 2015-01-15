import sys
import serial
import gpib
import gpibmanager

import tektronix2430a
import hp3438a

print "opeinging", sys.argv[1]
p = serial.Serial(sys.argv[1], 115200, timeout = 1)
gpib = gpib.GpibInterface(p)
manager = gpibmanager.GpibManager(gpib)
manager.registerDriver(tektronix2430a.Tektronix2430A)
manager.registerDriver(hp3438a.Hp3438A)
manager.useConfig('test.cfg')
#manager.scanBus()
#manager.verifyDrivers()
#gpib.debugEnable = True
#meter = hp3438a.Hp3438A(gpib, 2)
meter = manager.getInstrumentsByDriverName('Hp3438A')[0]
#scope = tektronix2430a.Tektronix2430A(gpib,1)
scope = manager.getInstrumentsByDriverName('Tektronix2430A')[0]
print "Reading from multimeter:", meter.readValue()
print "Getting identification"
print scope.getIdentification()
#print scope.getTrace()
print "Setting bwl"
scope.setBandwidthLimit('TWEnty')
print "Getting bwl"
print scope.getBandwidthLimit()
print "Configuring channel 1"
print "Probes", scope.getProbes()
print "getting vertical mode"
vm = scope.getVerticalMode()
scope.setVerticalModeD(vm)
trg = scope.getATrigger()
print "Trigger setings", trg
trg['LEVEL'] = 0.0
print scope.setATriggerD(trg)

trg = scope.getBTrigger()
print "Trigger setings", trg
trg['LEVEL'] = 1.0
print scope.setBTriggerD(trg)
print "Getting channel1"
ch1 = scope.getChannel1()
print ch1
print "Getting channel2"
ch2 = scope.getChannel2()
print "Setting channel1", scope.setChannel1D(ch2)
print "Setting channel2", scope.setChannel2D(ch1)
print "Getting setword"
word = scope.getSetWord();
print word
print "Setting word", scope.setSetWordD(word)

print "man trig", scope.manTrig()
#print "Getting ext gain"
#eg = scope.getExtGain()
#print eg
#print "Setting ext gain", scope.setExtGain(eg)
