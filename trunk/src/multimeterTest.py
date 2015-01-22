import sys

import serial
import gpib
import gpibmanager
import hp3438a

sys.path.append("./Corbomite/trunk/src/py")
from common.tcpCommunication import TcpServer
from device.corbomiteDevice import CorbomiteDevice, AnalogIn


class MultimeterTest(CorbomiteDevice):
    def __init__(self, iface):
        CorbomiteDevice.__init__(self, iface)
        self.vdcIn = AnalogIn(self, "vdc", "VDC", -200.0, 200.0, -200000000, 200000000)
        self.addWidget(self.vdcIn)
        self.vacIn = AnalogIn(self, "vac", "VAC", -200.0, 200.0, -200000000, 200000000)
        self.addWidget(self.vacIn)
        self.idcIn = AnalogIn(self, "idc", "ADC", -200.0, 200.0, -200000000, 200000000)
        self.addWidget(self.idcIn)
        self.iacIn = AnalogIn(self, "iac", "AAC", -200.0, 200.0, -200000000, 200000000)
        self.addWidget(self.iacIn)
        self.ohmsIn = AnalogIn(self, "ohms", "Ohm", -200.0, 200.0, -200000000, 200000000)
        self.addWidget(self.ohmsIn)


print "Opening serial port", sys.argv[1]
p = serial.Serial(sys.argv[1], 115200, timeout=1)
gpib = gpib.GpibInterface(p)
manager = gpibmanager.GpibManager(gpib)
manager.registerDriver(hp3438a.Hp3438A)
manager.useConfig('multimetertest.cfg')

gpibmeter = manager.getInstrumentsByDriverName('Hp3438A')[0]

rw = TcpServer()
meter = MultimeterTest(rw)

def writeValue(value):
    if value[1] == 'V DC':
        meter.vdcIn.setValue(float(value[0]))
    elif value[1] == 'V AC':
        meter.vacIn.setValue(float(value[0]))
    elif value[1] == 'A DC':
        meter.idcIn.setValue(float(value[0]))
    elif value[1] == 'A AC':
        meter.iacIn.setValue(float(value[0]))
    elif value[1] == 'Ohm':
        meter.ohmsIn.setValue(float(value[0]))

lastUnit = 'V DC'

while True:
    value = gpibmeter.readValue()
    print "Meter value", value
    writeValue(value)
    if lastUnit != value[1]:
        writeValue((0.0, lastUnit))
    lastUnit = value[1]
