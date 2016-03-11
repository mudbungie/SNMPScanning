# Database adapter for import SNMP logs

import sqlalchemy as sqla
from datetime import datetime

class Database:
    def __init__(self, databaseConfig):
        # Open the database with the info in the config
        self.dbname = databaseConfig['dbname']
        self.host = databaseConfig['host']
        self.user = databaseConfig['user']
        self.password = databaseConfig['password']
        self.connect()

    def connect(self):
        # Take all that and make a single string
        connectionString = ''.join([    'postgresql+psycopg2://',
                                        self.user, ':',
                                        self.password, '@',
                                        self.host, '/',
                                        self.dbname,
                                        ])
        # Open the connection
        self.connection = sqla.create_engine(connectionString)
        # Retrieve the precious olives within
        self.metadata = sqla.MetaData(self.connection)
        # Get data from the DB
        self.metadata.reflect()
        print(self.metadata.tables.keys())
    def insertArpData(self, ):#arps):
        # Find out if those MACs are in the arp table already. If not, 
        # insert them. If they are, make sure that the IP/MAC relationship
        # is unchanged, otherwise expire them and insert a new record.

        #FIXME This is sample data, delete it for production
        arps = [{'mac':'00:25:90:cb:5c:4a', 'ip':'172.31.0.45', 'observed':datetime.now()}]

        # Connect to the table
        tableName = 'arp'
        arpRecords = self.metadata.tables[tableName]

        for arp in arps:
            # Find a matching MAC address that hasn't been expired
            historicArpSelect = arpRecords.select(#[arpRecords.c.arp_id,
                                                  #  arpRecords.c.mac, 
                                                  #  arpRecords.c.ip]
                                                    ).where(
                                                        (arpRecords.c.expired == None) &
                                                        (arpRecords.c.mac == arp['mac']))
            historicArp = self.connection.execute(historicArpSelect)
            # If there is no matching entry, then insert it, this is a new device!
            if historicArp.rowcount == 0:
                print('New device found!')
                arpInsert = arpRecords.insert().values(**arp)
                self.connection.execute(arpInsert)
            # If there is a matching entry, we have to see if it's consistent.
            elif historicArp.rowcount == 1:
                print('Matching record found!')
                matchingArp = historicArp.fetchone()
                if matchingArp.ip == arp['ip']:
                    print('The ARP data is consistent.')
                else:
                    print('The ARP data has updated!')
                    # Expire the old record
                    arpUpdate = arpRecords.update().\
                                        where(arpRecords.c.arp_id == matchingArp.arp_id).\
                                        values(expired = datetime.now())
                    self.connection.execute(arpUpdate)
                    # Insert the new record
                    arpInsert = arpRecords.insert().values(**arp)
                    self.connection.execute(arpInsert)
            # If there is more than one matching records, then something is wrong.
            else:
                raise Exception('Multiple unexpired matches for MAC ' + arp['mac'])
        '''
        for arp in arps:
            print('we\'re at least parsing the data')
            # Pull non-expired matches for the IP
            arpRecords = table.query.filter_by(
                            table.c.expired == None)#,
                           # sqla.and_(table.c.ip == arp['ip']))
            if len(arpRecords) > 1:
                print('Duplicate records, something is wrong')
            else:
                for arpRecord in arpRecords:
                    pass
            # The keys in arpTable are ip, mac, and timestamp, same as the columns
            insert = table.insert().values(**arp)
            self.connection.execute(insert)
            '''

