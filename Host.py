# Object for a host. Does a scan with easysnmp on all network interfaces,
# returns a tuple of interface and mac address pairs

from easysnmp import Session
import easysnmp.exceptions
from ipaddress import IPv4Address, AddressValueError
from Config import config
from binascii import hexlify
from datetime import datetime

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
        timestamp = datetime.now()
        responses = self.walk(mib)
        # We're going to make a dict out of the values, because that has to happen
        # before a database insert one way or another. 
        arpTable = []
        for response in responses:
            values = {}
            values['mac'] = self.decodeMac(response.value)
            values['ip'] = self.decodeIP(response.oid_index)
            values['timestamp'] = timestamp
            arpTable.append(values)
        return arpTable

if __name__ == '__main__':
    a = Host('10.11.0.1')
    b = a.getArpTable('ipNetToMediaPhysAddress')
    for arp in b:
        print('MAC ' + arp['mac'] + ' is assigned to IP ' + arp['ip'])
