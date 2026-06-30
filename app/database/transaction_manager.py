import sqlite3


class TransactionManager:
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn
        self._committed = False

    def __enter__(self):
        self.conn.execute("BEGIN")
        return self

    def commit(self):
        self.conn.commit()
        self._committed = True

    def rollback(self):
        self.conn.rollback()
        self._committed = True

    def __exit__(self, exc_type, exc_val, exc_tb):
        if not self._committed:
            self.conn.rollback()
        self.conn.close()
