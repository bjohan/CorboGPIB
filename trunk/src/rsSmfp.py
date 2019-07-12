import time
import gpib

class RsSmfp(gpib.GpibDevice):
    def __init__(self, gpibDevice, addr):
        gpib.GpibDevice.__init__(self, gpibDevice, addr)
        self.modulationTypes = {"AM_INT": "AA",
                                "FM_INT": "AB",
                                "PM_INT": "AC",
                                "AM_EXT": "BK",
                                "FM_EXT": "BI",
                                "PM_EXT": "BJ"}

        self.sigGenLevelUnits = { "uV": "AI",
                                "mV": "AJ",
                                "dBm": "AK",
                                "dBuV": "AL"}
    def writeline(self, data):
        self.write(data+'\n')


    def identify(self):
        #print "Scanning for RsSmfp"
        self.writeline("AW")
        time.sleep(1)
        result = self.read()
        #print "Stage 1", len(result), result
        if result[0:2] == "AW":
            self.writeline("BL")
            time.sleep(1)
            result = self.read()
            #print "Stage 2", result
            if result[0:2] == "BL":
                return True
        #    else:
        #        print "Second stage failed"
        #else:
        #        print "First stage failed"
        return False

    def receiverMode(self):
        self.writeline("AR");

    def transmitterMode(self):
        self.writeline("AT");

    def modulation(self, modType):
        self.writeline(self.modulationTypes[modType])

    def onOff(self, on, onCmd, offCmd):
        if on == True:
            self.writeline(onCmd);
        else:
            self.writeline(offCmd);

    def rfOn(self, on):
        self.onOff(on, "D@", "E@");

    def ccitOn(self, on):
        self.onOff(on, "EC", "DC");

    def store(self, num):
        if num not in range(6):
            raise ValueError("num must be in range 0..5");
        self.writeline("DS"+str(num))

    def recall(self, num):
        if num not in range(6):
            raise ValueError("num must be in range 0..5");
        self.writeline("DR"+str(num))

    def refFunction(self, fcn):
        self.writeline("BO"+str(int(fcn)))

    def reset(self):
        self.refFunction(99)
        time.sleep(3)

    def sigGenFrequency(self, frequency):
        self.writeline("AG"+str(frequency))

    def sigGenLevel(self, level, unit="dBm"):
        self.writeline(self.sigGenLevelUnits[unit]+str(float(level)))

    def incSigGenLevel(self):
        self.writeline("EK")

    def decSigGenLevel(self):
        self.writeline("DK")

    def modInt(self, value = None, off = False):
        #value is %, KHZ or RAD depending on modulation type
        if not off:
            if value is not None:
                self.writeline("AM"+str(int(value)))
            else:
                self.writeline("AM")
        else:
            self.writeline("EM")

    def modExt(self, on):
        #value is %, KHZ or RAD depending on modulation type
        if not off:
            if value is not None:
                self.writeline("AZ"+str(int(value)))
            else:
                self.writeline("AZ")
        else:
            self.writeline("EZ")

    def modGenFreq(self, freq):
        #Freq in khz
        self.writeline("AO"+str(float(freq)))

    def modGenLevel(self, level):
        #level in mv
        self.writeline("AQ"+str(float(level)))

    def incDeltaF(self, incr = None):
        #incr delta f in khz
        if incr is not None:
            self.writeline("AE"+str(float(incr)))
        else:
            self.writeline("AE")
            
    def decDeltaF(self, decr = None):
        #incr delta f in khz
        if decr is not None:
            self.writeline("AD"+str(float(decr)))
        else:
            self.writeline("AD")
           

    #Store and recall not implemented


