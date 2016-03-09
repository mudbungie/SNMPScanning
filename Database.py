# Database adapter for import SNMP logs

import sqlalchemy as sqla

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
        print(self.metadata.tables.keys())
    def insertArpData(self, arps):
        # Connect to the table
        tableName = 'arp'
        #table = sqla.Table(tableName, self.metadata, autoload=True)
        # Define the database arp table
        table = self.metadata.tables['arp']
        table.select()
        self.connection.execute()
        '''
        for arp in arps:
            # Find out if those MACs are in the arp table already. If not, 
            # insert them. If they are, make sure that the IP/MAC relationship
            # is unchanged, otherwise expire them and insert a new record.
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
