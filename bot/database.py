import sqlite3
import datetime
import os

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'trips.db')


class TaxiDB:
    def __init__(self):
        self.conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        self._create_table()

    def _create_table(self):
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS trips (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                amount INTEGER,
                timestamp TIMESTAMP
            )
        ''')
        self.conn.commit()

    def start_trip(self, amount, user_id):
        cursor = self.conn.execute(
            'INSERT INTO trips (user_id, amount, timestamp) VALUES (?, ?, ?)',
            (user_id, amount, datetime.datetime.now())
        )
        self.conn.commit()
        return cursor.lastrowid

    def get_shift_stats(self, user_id):
        cursor = self.conn.execute('''
            SELECT
                COUNT(*) as trips_count,
                SUM(amount) as total,
                MIN(timestamp) as first,
                MAX(timestamp) as last
            FROM trips
            WHERE user_id = ? AND
                  timestamp > datetime('now', '-24 hours')
        ''', (user_id,))
        return cursor.fetchone()
