import gspread
from google.oauth2.service_account import Credentials
import os

# ตั้งค่า Credentials
SCOPES = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
KEY_PATH = '.secrets/directed-graph-494807-i7-f79a56b5b375.json'

def create_gsheet():
    if not os.path.exists(KEY_PATH):
        print(f"Error: Credentials file not found at {KEY_PATH}")
        return

    creds = Credentials.from_service_account_file(KEY_PATH, scopes=SCOPES)
    client = gspread.authorize(creds)

    # 1. สร้าง Google Sheets ใหม่
    sheet_name = "CRAZYFIFA_2026_DB"
    try:
        sh = client.create(sheet_name)
        print(f"Successfully created spreadsheet: {sheet_name}")
        print(f"Spreadsheet URL: https://docs.google.com/spreadsheets/d/{sh.id}")
        
        # 2. สร้าง Tabs
        # gspread สร้างไฟล์มาพร้อมแผ่นงานแรกชื่อ 'Sheet1' เสมอ
        sh.get_worksheet(0).update_title("users")
        sh.add_worksheet(title="matches", rows="100", cols="20")
        sh.add_worksheet(title="predictions", rows="1000", cols="20")
        
        # 3. แชร์สิทธิ์ให้ 'Anyone with link' เป็น Editor
        sh.share(None, perm_type='anyone', role='writer')
        print("Set permission to 'Anyone with link' as Editor.")
        
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    create_gsheet()
