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
#print "Creating gpib manager"
#manager = gpibmanager.GpibManager(gpib)
#print "Registering drivers"
#manager.registerDriver(rsSmfp.RsSmfp)
#manager.useConfig('test.cfg')

print "Opening instrument"
smfp = rsSmfp.RsSmfp(gpib, 2)
print "Resetting"
smfp.reset()
smfp.sigGenFrequency(123.4567)
smfp.sigGenLevel(40, "dBuV")
smfp.incSigGenLevel()
smfp.decSigGenLevel()
smfp.modulation("AM_INT")
smfp.modInt(50)
smfp.modGenFreq(3.4)
smfp.modGenLevel(992)
smfp.incDeltaF(12.5)
for a in range(5):
    smfp.incDeltaF()
smfp.decDeltaF(12.5)
for a in range(5):
    smfp.decDeltaF()
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
