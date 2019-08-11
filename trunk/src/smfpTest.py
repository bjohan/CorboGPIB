import sys
import serial
import gpib
import gpibmanager
import matplotlib.pyplot as plt
import rsSmfp
import time
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
print "Resetting",
smfp.reset()
print "Done"
smfp.sigGenFrequency(123.4567)
time.sleep(0.5)
smfp.sigGenLevel(40, "dBuV")
time.sleep(0.5)
smfp.incSigGenLevel()
time.sleep(0.5)
smfp.decSigGenLevel()
time.sleep(0.5)
smfp.modulation("AM_INT")
time.sleep(0.5)
smfp.modInt(50)
time.sleep(0.5)
smfp.modGenFreq(3.4)
time.sleep(0.5)
smfp.modGenLevel(992)
time.sleep(0.5)
smfp.incDeltaF(12.5)
time.sleep(0.5)
for a in range(5):
    time.sleep(0.5)
    smfp.incDeltaF()

time.sleep(0.5)
smfp.decDeltaF(12.5)
for a in range(5):
    time.sleep(0.5)
    smfp.decDeltaF()

exit()
print "Measure frequency", 
time.sleep(0.5)
print smfp.measureFrequency()
print "Rf freq",
time.sleep(0.5)
print smfp.rfFreq()

print "Power, w",
time.sleep(0.5)
print smfp.power()

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
