#!/usr/bin/python3

# User-executable frontend
# Currently just does single hosts. IP network scanning will be patched in later.

from Config import config
from sys import argv
from Host import Host
from Database import Database


def scan(target):
    host = Host(target)
    arps = host.getArpTable()
    db = Database(config['databases']['arp'])
    db.insertArpData(arps)

if __name__ == '__main__':
    target = argv[1]
    scan(target)
