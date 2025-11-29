class BaseDAO:
    def __init__(self, connection):
        self.conn = connection
        self.cursor = connection.cursor()

    def commit(self):
        self.conn.commit()
    
    def rollback(self):
        self.conn.rollback()
    
    def close(self):
        self.conn.close()