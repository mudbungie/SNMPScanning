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
        connectionString = ''.join([    'postgresql+psycopg2://'.
                                        self.user, ':',
                                        self.password, '@',
                                        self.host, '/',
                                        self.dbname,
                                    [)
        # Open the connection
        self.connection = sqla.create_engine(connectionString)
        # Retrieve the precious olives within
        self.metadata = sqla.MetaData(self.connection)


    def insertArpData(self, table, arpTable):
        # Connect to the table
        table = sqla.Table(tableName, self.metadata, autoload=True)
        for arp in arpTable:
            mac = arp[0]
            ip = arp[1]
            timestamp = arp[2]
            
            insert = table.insert(table, )
