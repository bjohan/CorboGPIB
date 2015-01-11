import sys
import time

class GpibManager:
    def __init__(self, interface):
        self.gpib = interface
        self.drivers = {}
        self.addressDriverMap = {}
        self.addressInstrumentMap = {}

    def numberOfDevices(self):
        return len(self.addressDriverMap)

    def registerDriver(self, driver):
        self.drivers[driver.__name__] = driver

    def scanBus(self):
        activeAddresses = []
        for addr in range(31)[1:]:
            print "Scanning address", addr,
            sys.stdout.flush()
            self.gpib.setAddress(addr)
            if(self.gpib.read()):
                print "found device!"
                self.scanDriver(addr)
            else:
                print "noting."
                
    def scanDriver(self, addr):
        print "\tScanning for driver:",
        sys.stdout.flush()
        for driver in self.drivers:
            print driver, 
            sys.stdout.flush()
            d = self.drivers[driver](self.gpib, addr)
            if d.identify():
                print "Match"
                self.addressDriverMap[addr] = driver
                break;
            print "...",
        else:
            print "no driver for device at", addr

    def createInstruments(self):
        for addr, driver in self.addressDriverMap.iteritems():
            self.addressInstrumentMap[addr] = self.drivers[driver](self.gpib, addr)

    def getInstrumentByAddress(self, address):
        if len(self.addressDriverMap) != len(self.addressInstrumentMap):
            self.createInstruments()
        return self.addressInstrumentMap[address]

    def saveConfiguration(self, fileName):
        of = open(fileName, 'w')
        for addr in self.addressDriverMap:
            of.write("%d %s\n"%(addr, self.addressDriverMap[addr]))
        of.close()

    def readConfiguration(self, fileName):
        try:
            a = open(fileName)
            for line in a.read().splitlines():
                words = line.split()
                addr = words[0]
                driver = words[1]
                self.addressDriverMap[int(addr)] = driver
        except:
            pass

    def verifyDrivers(self):
        failed = []
        for addr, driver in self.addressDriverMap.iteritems():
            print "Verifying that", addr, "is a", driver,
            sys.stdout.flush()
            d = self.drivers[driver](self.gpib, addr)
            if d.identify():
                print "OK"
            else:
                print "FAIL"
                failed.append(addr)
        return failed

    def useConfig(self, fileName):
        print "Loading config"
        self.readConfiguration(fileName)
        if self.numberOfDevices()  == 0:
            print "bad config or no devices listed in it, scanning..."
            self.scanBus()
        print "Verifying drivers"
        failed = self.verifyDrivers()
        for f in failed:
            del self.addressDriverMap[f]

        if len(failed) > 0:
            print len(failed), "drivers failed verification, scanning..."
            self.scanBus()
        self.saveConfiguration(fileName)
        
