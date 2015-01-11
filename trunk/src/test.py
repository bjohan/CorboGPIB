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
#scope = tektronix2430a.Tektronix2430A(gpib,1)
#print "Reading from multimeter:", meter.readValue()
#print "Getting identification"
#print scope.getIdentification()
#print scope.getTrace()
#print "Setting bwl"
#print scope.setBandwidthLimit('TWEnty')
#print "Getting bwl"
#print scope.getBandwidthLimit()
#print "Configuring channel 1"
#print scope.setChannel(1,0.1,0,0,'AC', 'OFF', 'OFF')
#print "reading channel 1"
#data = scope.getChannelInfo()
#print "Got", data
