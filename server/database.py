import sqlite3
import json
from datetime import datetime

class Database:
    def __init__(self, db_file):
        self.conn = sqlite3.connect(db_file)
        self.create_tables()
        
    def create_tables(self):
        cursor = self.conn.cursor()
        
        # Clients table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS clients (
            session_id TEXT PRIMARY KEY,
            os TEXT,
            hostname TEXT,
            ip TEXT,
            first_seen TEXT,
            last_seen TEXT,
            raw_data TEXT
        )
        ''')
        
        # Commands table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS commands (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT,
            command TEXT,
            timestamp TEXT,
            FOREIGN KEY(session_id) REFERENCES clients(session_id)
        )
        ''')
        
        self.conn.commit()
    
    def insert_data(self, session_id, os, hostname, ip, raw_data):
        cursor = self.conn.cursor()
        now = datetime.now().isoformat()
        
        # Check if client exists
        cursor.execute('SELECT 1 FROM clients WHERE session_id = ?', (session_id,))
        exists = cursor.fetchone()
        
        if exists:
            cursor.execute('''
            UPDATE clients 
            SET last_seen = ?, raw_data = ?
            WHERE session_id = ?
            ''', (now, raw_data, session_id))
        else:
            cursor.execute('''
            INSERT INTO clients (session_id, os, hostname, ip, first_seen, last_seen, raw_data)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (session_id, os, hostname, ip, now, now, raw_data))
        
        self.conn.commit()
    
    def log_command(self, session_id, command):
        cursor = self.conn.cursor()
        cursor.execute('''
        INSERT INTO commands (session_id, command, timestamp)
        VALUES (?, ?, ?)
        ''', (session_id, command, datetime.now().isoformat()))
        self.conn.commit()
    
    def get_all_clients(self):
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM clients ORDER BY last_seen DESC')
        columns = [col[0] for col in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]
    
    def get_commands(self, session_id):
        cursor = self.conn.cursor()
        cursor.execute('''
        SELECT command, timestamp 
        FROM commands 
        WHERE session_id = ?
        ORDER BY timestamp DESC
        ''', (session_id,))
        return [{"command": row[0], "timestamp": row[1]} for row in cursor.fetchall()]
