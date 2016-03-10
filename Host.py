# Object for a host. Does a scan with easysnmp on all network interfaces,
# returns a tuple of interface and mac address pairs

from easysnmp import Session
import easysnmp.exceptions
from ipaddress import IPv4Address, AddressValueError
from Config import config
from binascii import hexlify

class Host:
    def __init__(self, ip):
        # Verification; if it's not an address, it will error
        IPv4Address(ip)
        self.ip = ip
        # Set up the SNMP variables that we'll use
        self.session = Session(hostname=self.ip, community=config['community'], version=1)

    def decodeMac(self, value):
        # The raw data has some quirks to it. Have to clean it up
        s = str(hexlify(value.encode('utf-16')))
        mac = ':'.join([s[6:8], s[10:12], s[14:16], s[18:20], s[22:24], s[26:28]])
        # Verify data
        if not len(mac) == 17:
            raise AssertionError(mac + ' IS NOT A VALID MAC ADDRESS')
        return mac

    def decodeIP(self, value):
        # oid_index on arp table returns includes the interface number, 
        # which should be stripped. Also, verify the data.
        try:
            # Strip the leading interface number and .
            ip = '.'.join(value.split('.')[1:])
            IPv4Address(ip)
            return ip
        except AddressValueError:
            print('NOT AN IP:' + ip)
            

    def walk(self, mib):
       # Just executes a walk, returns all of the values 
        try:
            responses = self.session.walk(mib)
            return responses
        except easysnmp.exceptions.EasySNMPNoSuchNameError:
            print('NO MATCH FOR ' + mib)

    def getArpTable(self, mib):
        # Scan the target's ARP table, return a list of IP, MAC tuples
            responses = self.walk(mib)
            arpTable = []
            for response in responses:
                # They come back all munged together, so I have to do some string hacking
                mac = self.decodeMac(response.value)
                ip = self.decodeIP(response.oid_index)
                arp = (mac, ip)
                arpTable.append(arp)
            return arpTable

if __name__ == '__main__':
    a = Host('10.11.0.1')
    b = a.getArpTable('ipNetToMediaPhysAddress')
    for arp in b:
        print('MAC ' + arp[0] + ' is assigned to IP ' + arp[1])
