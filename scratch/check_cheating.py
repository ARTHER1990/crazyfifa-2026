import subprocess
import sqlite3
import pandas as pd
import os
import shutil
from datetime import datetime, timezone, timedelta

# กำหนดพาธ
BASE_DIR = '/Users/art/Desktop/ART_JOB/ฟุตบอลโลก2026'
DB_RELATIVE_PATH = 'worldcup.db'
TEMP_DB_PATH = '/Users/art/Desktop/ART_JOB/ฟุตบอลโลก2026/temp_worldcup.db'

def get_git_commits():
    # ดึงรายการ commits ทั้งหมดที่แก้ไข worldcup.db พร้อมเวลาและข้อความ commit
    cmd = ['git', 'log', '--follow', '--pretty=format:%H|%ai|%s', '--', DB_RELATIVE_PATH]
    result = subprocess.run(cmd, cwd=BASE_DIR, capture_output=True, text=True, check=True)
    commits = []
    for line in result.stdout.strip().split('\n'):
        if line:
            parts = line.split('|', 2)
            if len(parts) == 3:
                commits.append({
                    'hash': parts[0],
                    'time': parts[1],
                    'message': parts[2]
                })
    return commits

def extract_db_from_commit(commit_hash):
    # สกัดไฟล์ worldcup.db จาก commit hash เฉพาะมาไว้ที่ TEMP_DB_PATH
    cmd = ['git', 'show', f'{commit_hash}:{DB_RELATIVE_PATH}']
    result = subprocess.run(cmd, cwd=BASE_DIR, capture_output=True)
    if result.returncode == 0:
        with open(TEMP_DB_PATH, 'wb') as f:
            f.write(result.stdout)
        return True
    return False

def analyze_cheating():
    print("🔍 กำลังเริ่มการสืบสวนประวัติฐานข้อมูล (Git History Analysis)...")
    commits = get_git_commits()
    print(f"📋 พบทีกิจกรรมการ Commit ฐานข้อมูลทั้งหมด {len(commits)} รายการในประวัติ Git")
    
    # ดึงแมตช์ทั้งหมดมาก่อนเพื่อรู้เวลาแข่งขันและชื่อทีม
    conn_real = sqlite3.connect(os.path.join(BASE_DIR, 'worldcup.db'))
    df_matches = pd.read_sql_query("SELECT id, home_team, away_team, match_time FROM matches", conn_real)
    conn_real.close()
    
    matches_dict = {}
    for _, row in df_matches.iterrows():
        matches_dict[int(row['id'])] = {
            'home': row['home_team'],
            'away': row['away_team'],
            'time': datetime.strptime(row['match_time'], '%Y-%m-%d %H:%M:%S')
        }
        
    all_predictions_history = []
    
    # วนลูปอ่านข้อมูลทีละ commit จากเก่าไปใหม่ (หรือใหม่ไปเก่าเพื่อความรวดเร็ว)
    # เราจะเรียงลำดับจากเก่าที่สุดไปใหม่สุด เพื่อดูประวัติการเปลี่ยนแปลงแบบต่อเนื่อง
    commits.reverse()
    
    for commit in commits:
        c_hash = commit['hash']
        c_time_str = commit['time']
        # เวลาของ commit (เช่น 2026-07-06 13:10:00 +0700)
        c_time = pd.to_datetime(c_time_str).replace(tzinfo=None)
        
        if not extract_db_from_commit(c_hash):
            continue
            
        try:
            conn_temp = sqlite3.connect(TEMP_DB_PATH)
            df_preds = pd.read_sql_query("SELECT username, match_id, pred_home, pred_away, pred_qualify FROM predictions", conn_temp)
            conn_temp.close()
            
            for _, row in df_preds.iterrows():
                try:
                    m_id = int(row['match_id'])
                    pred_home = int(row['pred_home'])
                    pred_away = int(row['pred_away'])
                    pred_qualify = str(row['pred_qualify']).strip()
                except:
                    continue
                    
                all_predictions_history.append({
                    'commit_hash': c_hash,
                    'commit_time': c_time,
                    'commit_msg': commit['message'],
                    'username': row['username'],
                    'match_id': m_id,
                    'pred_home': pred_home,
                    'pred_away': pred_away,
                    'pred_qualify': pred_qualify
                })
        except Exception as e:
            # บาง commit อาจยังไม่มีตาราง predictions หรือ sqlite พัง
            pass
            
    if os.path.exists(TEMP_DB_PATH):
        os.remove(TEMP_DB_PATH)
        
    df_hist = pd.DataFrame(all_predictions_history)
    if df_hist.empty:
        print("❌ ไม่พบข้อมูลประวัติคำทำนายในระบบ")
        return
        
    # ค้นหาการโกง: วิเคราะห์การแก้ไขคำทำนายหลังจากเลยเวลาล็อก (1 ชั่วโมงก่อนเริ่มเตะ)
    # คัดกรองข้อมูลประวัติการทายผล โดยเรียงตามผู้ใช้, แมตช์, และเวลา commit เพื่อสังเกตการแก้ไข
    print("\n🕵️‍♂️ กำลังตรวจสอบการเปลี่ยนแปลงข้อมูล...")
    
    cheating_reports = []
    
    # จัดกลุ่มตามผู้เล่น และแมตช์
    grouped = df_hist.groupby(['username', 'match_id'])
    for (username, m_id), group in grouped:
        if m_id not in matches_dict:
            continue
            
        m_info = matches_dict[m_id]
        m_time = m_info['time']
        lock_time = m_time - timedelta(hours=1) # ปิดทายผล 1 ชั่วโมงก่อนเริ่มเกม
        
        # ค้นหาว่ามี commit ไหนที่เปลี่ยนแปลงคำทำนาย และเกิดขึ้นหลัง lock_time
        # เราจะเปรียบเทียบค่าทำนายที่เปลี่ยนไป
        prev_pred = None
        
        # เรียงตามเวลา commit
        group_sorted = group.sort_values('commit_time')
        
        for idx, row in group_sorted.iterrows():
            current_pred = (row['pred_home'], row['pred_away'], row['pred_qualify'])
            commit_time = row['commit_time']
            
            if prev_pred is not None and prev_pred != current_pred:
                # เกิดการเปลี่ยนค่าทำนาย!
                # เช็คว่า commit นี้สร้างขึ้นหลังจากเลยเวลาล็อกคำทำนายแล้วหรือไม่
                if commit_time > lock_time:
                    cheating_reports.append({
                        'username': username,
                        'match_id': m_id,
                        'home_team': m_info['home'],
                        'away_team': m_info['away'],
                        'match_time': m_time,
                        'lock_time': lock_time,
                        'change_time': commit_time,
                        'prev_pred': prev_pred,
                        'new_pred': current_pred,
                        'commit_msg': row['commit_msg']
                    })
                    
            prev_pred = current_pred

    if cheating_reports:
        print(f"🚨 ตรวจพบพฤติกรรมน่าสงสัย (แก้ไขผลหลังจากเลยเวลาปิดรับทาย) ทั้งหมด {len(cheating_reports)} รายการ!")
        df_reports = pd.DataFrame(cheating_reports)
        # ปรับรูปแบบแสดงผลให้น่าอ่าน
        for r in cheating_reports:
            print(f"\n👤 ผู้เล่น: {r['username']}")
            print(f"🏟️ คู่แข่ง: {r['home_team']} vs {r['away_team']} (ID: {r['match_id']})")
            print(f"📅 เวลาแข่ง: {r['match_time']} | 🔒 ปิดรับทาย: {r['lock_time']}")
            print(f"🕒 มีการแก้ไขเมื่อ: {r['change_time']} ({r['change_time'] - r['match_time']} หลังเตะ)")
            print(f"🔄 คำทำนาย: จาก {r['prev_pred'][0]}-{r['prev_pred'][1]} ({r['prev_pred'][2]}) ➡️ เป็น {r['new_pred'][0]}-{r['new_pred'][1]} ({r['new_pred'][2]})")
            print(f"📝 Commit Message: {r['commit_msg']}")
    else:
        print("✅ ไม่พบพฤติกรรมการแก้ไขผลทำนายหลังหมดเขตส่งในประวัติ Git!")

if __name__ == '__main__':
    analyze_cheating()
