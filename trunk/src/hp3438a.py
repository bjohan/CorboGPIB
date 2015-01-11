import time
import gpib

class Hp3438A(gpib.GpibDevice):
    def __init__(self, gpibDevice, addr):
        gpib.GpibDevice.__init__(self, gpibDevice, addr)

    def identify(self):
        (value, unit) = self.readValue()
        return (value != None) and (unit != None)

    def readValue(self, maxTries = 10):
        while True:
            data = self.read()
            time.sleep(0.01)
            if len(data) > 2:
                break
            if maxTries > 0:
                maxTries -= 1
            else:
                return (None, None)
        try:
            (value, unit) = data.strip().split(',')
            numVal = float(value)
            strUnit = ['V DC', 'V AC', 'A DC', 'A AC', 'Ohm'][int(unit)-1]
        except:
            print "Unable to parse:", data
            return (None, None)
        return (numVal, strUnit)
