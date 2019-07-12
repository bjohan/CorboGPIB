import sys
import serial
import gpib
import gpibmanager
import matplotlib.pyplot as plt
import rsSmfp
print "opeinging", sys.argv[1]
p = serial.Serial(sys.argv[1], 115200, timeout = 1)
print "Creating gpib interface"
gpib = gpib.GpibInterface(p)
print "Creating gpib manager"
manager = gpibmanager.GpibManager(gpib)
print "Registering drivers"
manager.registerDriver(rsSmfp.RsSmfp)
manager.useConfig('test.cfg')

smfp = rsSmfp.RsSmfp(gpib, 2)
smfp.sigGenFrequency(123.4567)
smfp.sigGenLevel(40, "dBuV")
#smfp.reset()
#manager.scanBus()
#manager.verifyDrivers()
#manager.saveConfiguration('test.cfg')
#gpib.debugEnable = True
#meter = hp3438a.Hp3438A(gpib, 2)
#meter = manager.getInstrumentsByDriverName('Hp3438A')[0]
#scope = tektronix2430a.Tektronix2430A(gpib,1)
#scope = manager.getInstrumentsByDriverName('Tektronix2430A')[0]
#print "Reading from multimeter:", meter.readValue()
#print "Getting identification"
#print scope.getIdentification()
#print scope.getTrace()
#plt.plot( scope.getTraceF())
#plt.show()
#print "Setting ext gain", scope.setExtGain(eg)
