import sqlite3
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
import numpy as np
import os

# ตั้งค่า
DB_PATH = 'ฟุตบอลโลก2026/worldcup.db'
SHEET_URL = 'https://docs.google.com/spreadsheets/d/1MWZoajy6xNEQunVccEqNcb4iV4124qRxrDS5pHLf57c/edit'
KEY_PATH = '.secrets/directed-graph-494807-i7-f79a56b5b375.json'
SCOPES = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']

def migrate():
    # 1. เชื่อมต่อ Google Sheets
    creds = Credentials.from_service_account_file(KEY_PATH, scopes=SCOPES)
    client = gspread.authorize(creds)
    sh = client.open_by_url(SHEET_URL)
    
    # 2. เชื่อมต่อ SQLite
    conn = sqlite3.connect(DB_PATH)
    
    tables = ['users', 'matches', 'predictions']
    
    for table in tables:
        print(f"Migrating table: {table}...")
        df = pd.read_sql_query(f"SELECT * FROM {table}", conn)
        
        # จัดการค่า NaN / None ให้เป็นค่าว่าง เพื่อป้องกัน Error ของ JSON
        df = df.replace({np.nan: None})
        
        # เตรียมแผ่นงาน
        try:
            ws = sh.worksheet(table)
        except gspread.exceptions.WorksheetNotFound:
            ws = sh.add_worksheet(title=table, rows="1000", cols="20")
            
        # ล้างข้อมูลเก่า
        ws.clear()
        
        # แปลงข้อมูลเป็น list of lists และจัดการค่า None เป็น string ว่าง
        data_to_write = [df.columns.values.tolist()]
        for row in df.values.tolist():
            clean_row = ["" if v is None else v for v in row]
            data_to_write.append(clean_row)
            
        # เขียนข้อมูล
        ws.update(data_to_write)
        print(f"Table {table} migrated successfully. ({len(df)} rows)")

    conn.close()
    print("Migration completed!")

if __name__ == "__main__":
    migrate()
