#!/usr/bin/env python3
import sqlite3
import os

DB_PATH = '/root/singbox-eps-node/data/singbox.db'
conn = sqlite3.connect(DB_PATH)
c = conn.cursor()
c.execute("SELECT * FROM cdn_settings")
rows = c.fetchall()
for row in rows:
    print(f'{row[0]}: {row[1]}')
conn.close()
