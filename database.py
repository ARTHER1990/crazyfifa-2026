import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
from datetime import datetime
import os
import json
import streamlit as st
import socket

# ตั้งค่า Network Timeout สูงสุดไม่เกิน 4.0 วินาที เพื่อป้องกันอาการหน้าเว็บค้างหมุนจาก Google API หรือ Wikipedia ล่ม
socket.setdefaulttimeout(4.0)

# ตั้งค่า Credentials
SCOPES = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
# ค้นหาไฟล์ .secrets จากตำแหน่งของไฟล์นี้ หรือโฟลเดอร์หลัก
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.dirname(BASE_DIR)
KEY_NAME = 'directed-graph-494807-i7-f79a56b5b375.json'

LOCAL_KEY_PATH = os.path.join(PARENT_DIR, '.secrets', KEY_NAME)
if not os.path.exists(LOCAL_KEY_PATH):
    LOCAL_KEY_PATH = os.path.join(BASE_DIR, '.secrets', KEY_NAME)
if not os.path.exists(LOCAL_KEY_PATH):
    LOCAL_KEY_PATH = os.path.join('.secrets', KEY_NAME) # Fallback to relative

SHEET_URL = 'https://docs.google.com/spreadsheets/d/1MWZoajy6xNEQunVccEqNcb4iV4124qRxrDS5pHLf57c/edit'

@st.cache_resource
def get_gspread_client():
    if os.path.exists(LOCAL_KEY_PATH):
        creds = Credentials.from_service_account_file(LOCAL_KEY_PATH, scopes=SCOPES)
    else:
        creds_info = st.secrets["gcp_service_account"]
        if isinstance(creds_info, str):
            creds_info = json.loads(creds_info)
        else:
            creds_info = dict(creds_info)
        if "private_key" in creds_info:
            creds_info["private_key"] = creds_info["private_key"].replace("\\n", "\n")
        creds = Credentials.from_service_account_info(creds_info, scopes=SCOPES)
    return gspread.authorize(creds)

@st.cache_resource
def get_spreadsheet():
    client = get_gspread_client()
    return client.open_by_url(SHEET_URL)

def get_worksheet(name):
    try:
        sh = get_spreadsheet()
        return sh.worksheet(name)
    except Exception as e:
        print(f"gspread connection issue in get_worksheet({name}), clearing resource cache and retrying: {e}")
        get_gspread_client.clear()
        get_spreadsheet.clear()
        sh = get_spreadsheet()
        return sh.worksheet(name)

def save_local_backup(name, df):
    try:
        backup_dir = os.path.join(BASE_DIR, '.backup_data')
        os.makedirs(backup_dir, exist_ok=True)
        path = os.path.join(backup_dir, f"{name}.json")
        df.to_json(path, orient='records', force_ascii=False, indent=2)
    except Exception as e:
        print(f"Error saving local backup for {name}: {e}")

def load_local_backup(name, columns):
    try:
        backup_dir = os.path.join(BASE_DIR, '.backup_data')
        path = os.path.join(backup_dir, f"{name}.json")
        if os.path.exists(path):
            df = pd.read_json(path)
            # รักษาคอลัมน์ดั้งเดิมให้สมบูรณ์แบบ
            for col in columns:
                if col not in df.columns:
                    df[col] = ""
            return df
    except Exception as e:
        print(f"Error loading local backup for {name}: {e}")
    return pd.DataFrame(columns=columns)

def init_db():
    try:
        import sqlite3
        conn = sqlite3.connect('worldcup.db')
        conn.execute('''
            CREATE TABLE IF NOT EXISTS champion_predictions (
                username TEXT PRIMARY KEY,
                predicted_team TEXT,
                timestamp TEXT
            )
        ''')
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Error in init_db SQLite initialization: {e}")


@st.cache_data(ttl=300)
def get_users_df():
    cols = ['username', 'total_score', 'pin']
    try:
        ws = get_worksheet('users')
        data = ws.get_all_values()
        if not data:
            df = pd.DataFrame(columns=cols)
        else:
            df = pd.DataFrame(data[1:], columns=data[0])
        save_local_backup('users', df)
        return df
    except Exception as e:
        print(f"Error fetching users, returning local backup: {e}")
        return load_local_backup('users', cols)

@st.cache_data(ttl=300)
def get_matches():
    cols = ['id', 'home_team', 'away_team', 'match_time', 'home_score', 'away_score', 'status', 'scorers', 'winner_qualify']
    try:
        ws = get_worksheet('matches')
        data = ws.get_all_values()
        if not data:
            df = pd.DataFrame(columns=cols)
        else:
            df = pd.DataFrame(data[1:], columns=data[0])
        save_local_backup('matches', df)
        return df
    except Exception as e:
        print(f"Error fetching matches, returning local backup: {e}")
        return load_local_backup('matches', cols)

@st.cache_data(ttl=300)
def get_predictions_df():
    cols = ['username', 'match_id', 'pred_home', 'pred_away', 'pred_qualify', 'points_earned']
    try:
        ws = get_worksheet('predictions')
        data = ws.get_all_values()
        if not data:
            df = pd.DataFrame(columns=cols)
        else:
            df = pd.DataFrame(data[1:], columns=data[0])
        df = df.drop_duplicates(subset=['username', 'match_id'], keep='first')
        save_local_backup('predictions', df)
        return df
    except Exception as e:
        print(f"Error fetching predictions, returning local backup: {e}")
        return load_local_backup('predictions', cols)

def sync_results_from_web():
    """ฟังก์ชันหลักสำหรับเรียกใช้การซิงค์ข้อมูลจากแหล่งภายนอก (Wikipedia)"""
    updated_count = auto_sync_scores()
    return updated_count

def normalize_name(username):
    # ... (เหมือนเดิม)
    name = username.strip()
    return 'Art' if name.lower() == 'art' else name

def has_pin(username):
    name = normalize_name(username)
    df = get_users_df()
    if df.empty: return False
    user_row = df[df['username'] == name]
    return not user_row.empty and user_row.iloc[0]['pin'] != ""

def get_or_create_user(username, pin=None):
    name = normalize_name(username)
    ws = get_worksheet('users')
    df = get_users_df()
    
    if name not in df['username'].values:
        new_row = [name, 0, pin if pin else ""]
        ws.append_row(new_row)
    elif pin:
        idx = df.index[df['username'] == name][0] + 2
        ws.update_cell(idx, 3, pin)
    get_users_df.clear()

def verify_user(username, pin):
    name = normalize_name(username)
    df = get_users_df()
    if df.empty: return False
    user_row = df[df['username'] == name]
    return not user_row.empty and str(user_row.iloc[0]['pin']) == str(pin)

def safe_int(val, default=0):
    try:
        if val is None:
            return default
        s_val = str(val).strip()
        if s_val == "":
            return default
        return int(float(s_val))
    except Exception:
        return default

def save_prediction(username, match_id, pred_home, pred_away, pred_qualify=""):
    name = normalize_name(username)
    ws = get_worksheet('predictions')
    df = get_predictions_df()
    
    val_home = safe_int(pred_home, 0)
    val_away = safe_int(pred_away, 0)
    
    mask = (df['username'] == name) & (df['match_id'].astype(str) == str(match_id))
    if mask.any():
        idx = df.index[mask][0] + 2
        # ใช้ update แบบระบุ range เพื่อความปลอดภัยใน gspread 6.x ครอบคลุมถึงคอลัมน์ E (pred_qualify)
        ws.update(f'C{idx}:E{idx}', [[val_home, val_away, str(pred_qualify)]])
    else:
        ws.append_row([name, match_id, val_home, val_away, str(pred_qualify), 0])
    get_predictions_df.clear()

def get_user_predictions(username):
    name = normalize_name(username)
    df = get_predictions_df()
    if df.empty: return {}
    user_preds = df[df['username'] == name]
    preds = {}
    for _, row in user_preds.iterrows():
        try:
            m_id = int(row['match_id'])
            p_h = int(row['pred_home']) if row['pred_home'] != "" else 0
            p_a = int(row['pred_away']) if row['pred_away'] != "" else 0
            p_q = str(row['pred_qualify']).strip() if 'pred_qualify' in row and str(row['pred_qualify']).strip() != "" else ""
            preds[m_id] = (p_h, p_a, p_q)
        except:
            continue
    return preds

def get_leaderboard():
    df_u = get_users_df()
    df_p = get_predictions_df()
    if df_u.empty: return pd.DataFrame(columns=['username', 'total_score', 'pin'])
    
    # คำนวณคะแนนจาก predictions ถ้ามี
    if not df_p.empty:
        df_p['points_earned_int'] = pd.to_numeric(df_p['points_earned'], errors='coerce').fillna(0).astype(int)
        user_scores = df_p.groupby('username')['points_earned_int'].sum().reset_index()
        user_scores.columns = ['username', 'calculated_score']
        
        # Merge คะแนนเข้ากับ users
        df_u = df_u.merge(user_scores, on='username', how='left')
        df_u['total_score'] = df_u['calculated_score'].fillna(0).astype(int)
        df_u = df_u.drop(columns=['calculated_score'])
    else:
        df_u['total_score'] = pd.to_numeric(df_u['total_score'], errors='coerce').fillna(0).astype(int)
    
    return df_u.sort_values('total_score', ascending=False)

def get_prediction_history():
    df_p = get_predictions_df()
    df_m = get_matches()
    if df_p.empty or df_m.empty: return pd.DataFrame()
    
    merged = df_p.merge(df_m, left_on='match_id', right_on='id')
    
    res = []
    for _, row in merged.iterrows():
        real = f"{row['home_score']}-{row['away_score']}" if row['status'] == 'Finished' else ( "Live" if row['status'] == 'Live' else "Upcoming")
        res.append({
            'username': row['username'],
            'home_team': row['home_team'],
            'away_team': row['away_team'],
            'prediction': f"{row['pred_home']}-{row['pred_away']}",
            'real_score': real,
            'points': row['points_earned'],
            'match_time': row['match_time']
        })
    return pd.DataFrame(res)

def update_scores_logic():
    ws_m = get_worksheet('matches')
    data_m = ws_m.get_all_values()
    df_m = pd.DataFrame(data_m[1:], columns=data_m[0])
    
    ws_p = get_worksheet('predictions')
    data_p = ws_p.get_all_values()
    df_p = pd.DataFrame(data_p[1:], columns=data_p[0])
    
    # ป้องกันและเคลียร์การทำนายซ้ำซ้อนในคู่เดียวกันของผู้ใช้แต่ละคน (ห้ามเปิ้ลคะแนนในคู่เดียว)
    df_p = df_p.drop_duplicates(subset=['username', 'match_id'], keep='first')
    
    df_m['id_int'] = pd.to_numeric(df_m['id'], errors='coerce').fillna(0).astype(int)
    df_p['match_id_int'] = pd.to_numeric(df_p['match_id'], errors='coerce').fillna(0).astype(int)
    
    finished = df_m[(df_m['status'] == 'Finished') & (df_m['id_int'] >= 12)]
    
    mask_old = df_p['match_id_int'] < 12
    df_p.loc[mask_old, 'points_earned'] = '0'
    
    for _, m in finished.iterrows():
        m_id = str(m['id'])
        r_h = int(m['home_score']) if str(m['home_score']).strip() != "" else 0
        r_a = int(m['away_score']) if str(m['away_score']).strip() != "" else 0
        
        mask = df_p['match_id'].astype(str) == m_id
        for idx, p in df_p[mask].iterrows():
            p_h = int(p['pred_home']) if str(p['pred_home']).strip() != "" else 0
            p_a = int(p['pred_away']) if str(p['pred_away']).strip() != "" else 0
            points = 0
            if p_h == r_h and p_a == r_a:
                points = 3
            else:
                pred_win = (p_h > p_a) - (p_h < p_a)
                real_win = (r_h > r_a) - (r_h < r_a)
                if pred_win == real_win:
                    points = 1
            
            # คำนวณคะแนนโบนัสพิเศษ (โกลเดนโบนัส: ทีมเข้ารอบถัดไป) เฉพาะนัดน็อกเอาต์ที่มีผลผู้เข้ารอบจริง
            bonus = 0
            w_qualify = str(m.get('winner_qualify', '')).strip()
            p_qualify = str(p.get('pred_qualify', '')).strip()
            if p_qualify == "":
                try:
                    if int(p_h) > int(p_a):
                        p_qualify = str(m.get('home_team', '')).strip()
                    elif int(p_a) > int(p_h):
                        p_qualify = str(m.get('away_team', '')).strip()
                except Exception:
                    pass
            
            if w_qualify != "" and w_qualify.lower() != "nan" and p_qualify != "":
                if p_qualify.lower() == w_qualify.lower():
                    bonus = 1
                    
            total_points = points + bonus
            df_p.at[idx, 'points_earned'] = str(total_points)
            
    df_p_save = df_p.drop(columns=['match_id_int'])
    # ล้างชีตก่อนอัปเดตเพื่อป้องกันข้อมูลเก่าค้าง
    ws_p.clear()
    ws_p.update([df_p_save.columns.values.tolist()] + df_p_save.values.tolist())
    
    ws_u = get_worksheet('users')
    data_u = ws_u.get_all_values()
    df_u = pd.DataFrame(data_u[1:], columns=data_u[0])
    
    # คำนวณคะแนนใหม่
    df_p['points_earned_int'] = pd.to_numeric(df_p['points_earned'], errors='coerce').fillna(0).astype(int)
    for idx, u in df_u.iterrows():
        user_points = df_p[df_p['username'] == u['username']]['points_earned_int'].sum()
        df_u.at[idx, 'total_score'] = str(int(user_points))
        
    ws_u.clear()
    ws_u.update([df_u.columns.values.tolist()] + df_u.values.tolist())
    get_predictions_df.clear()
    get_users_df.clear()
    get_matches.clear()

def auto_sync_scores():
    try:
        import requests
        from bs4 import BeautifulSoup
        import re
        
        ws = get_worksheet('matches')
        data = ws.get_all_values()
        df = pd.DataFrame(data[1:], columns=data[0])
        
        url = "https://en.wikipedia.org/wiki/2026_FIFA_World_Cup"
        headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
        
        r = requests.get(url, headers=headers, timeout=15)
        if r.status_code != 200:
            return 0
            
        soup = BeautifulSoup(r.text, 'html.parser')
        boxes = soup.find_all('table', class_='fevent')
        
        updated_count = 0
        
        # Mapping ชื่อทีมจาก Wikipedia เป็นชื่อทีมในระบบของเรา
        name_mapping = {
            'United States': 'USA',
            'Czechia': 'Czech Republic',
            'Ivory Coast': "Côte d'Ivoire",
            'DR Congo[D]': 'DR Congo',
            'Cabo Verde': 'Cape Verde',
            'IR Iran': 'Iran',
            'Korea Republic': 'South Korea',
            'Türkiye': 'Turkey'
        }
        
        for box in boxes:
            home_td = box.find('th', class_='fhome') or box.find('td', class_='fhome')
            away_td = box.find('th', class_='faway') or box.find('td', class_='faway')
            score_td = box.find('th', class_='fscore') or box.find('td', class_='fscore')
            
            if home_td and away_td and score_td:
                home = home_td.get_text(strip=True)
                away = away_td.get_text(strip=True)
                score = score_td.get_text(strip=True)
                
                # คลีนชื่อ (ลบตัวเลข [D], [C] หรือช่องว่างพิเศษ)
                home = re.sub(r'\[.*?\]', '', home)
                home = re.sub(r'[\d\W]+$', '', home).strip().replace('\xa0', ' ')
                
                away = re.sub(r'\[.*?\]', '', away)
                away = re.sub(r'^[\d\W]+', '', away).strip().replace('\xa0', ' ')
                
                if score and not score.startswith('Match') and ('–' in score or '-' in score):
                    score_parts = re.split(r'[–-]', score)
                    if len(score_parts) == 2:
                        try:
                            # สกัดตัวเลขสกอร์ (กรณีมีตัวอักษรอื่นปน)
                            h_score_val = re.search(r'\d+', score_parts[0].strip())
                            a_score_val = re.search(r'\d+', score_parts[1].strip())
                            
                            if not h_score_val or not a_score_val:
                                continue
                                
                            h_score = int(h_score_val.group())
                            a_score = int(a_score_val.group())
                        except:
                            continue
                            
                        # ดึงคนทำประตู
                        h_goal_td = box.find('td', class_='fhgoal')
                        a_goal_td = box.find('td', class_='fagoal')
                        
                        h_scorers = h_goal_td.get_text(strip=True) if h_goal_td else ""
                        a_scorers = a_goal_td.get_text(strip=True) if a_goal_td else ""
                        
                        scorers_combined = ""
                        h_clean = re.sub(r'\s+', ' ', h_scorers).strip()
                        a_clean = re.sub(r'\s+', ' ', a_scorers).strip()
                        if h_clean and a_clean:
                            scorers_combined = f"{h_clean} | {a_clean}"
                        elif h_clean:
                            scorers_combined = h_clean
                        else:
                            scorers_combined = a_clean
                            
                        home_mapped = name_mapping.get(home, home)
                        away_mapped = name_mapping.get(away, away)
                        
                        # อัปเดตแมตช์ที่ยังไม่เสร็จ (Upcoming) 
                        # หรือถ้าอยากให้มีการอัปเดตทับเพื่อแก้ไขคะแนนที่ผิดพลาด ก็เปลี่ยนเป็น status != 'Finished' ได้
                        mask = (df['home_team'] == home_mapped) & (df['away_team'] == away_mapped) & (df['status'] == 'Upcoming')
                        if mask.any():
                            idx = df.index[mask][0]
                            df.at[idx, 'home_score'] = str(h_score)
                            df.at[idx, 'away_score'] = str(a_score)
                            df.at[idx, 'status'] = 'Finished'
                            df.at[idx, 'scorers'] = scorers_combined
                            updated_count += 1
                            
        if updated_count > 0:
            ws.clear()
            ws.update([df.columns.values.tolist()] + df.values.tolist())
            update_scores_logic()
            return updated_count
    except Exception as e:
        print("Auto-sync error:", e)
    return 0


def get_world_cup_standings():
    try:
        import requests
        from bs4 import BeautifulSoup
        import re
        import pandas as pd
        
        url = "https://en.wikipedia.org/wiki/2026_FIFA_World_Cup"
        headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
        r = requests.get(url, headers=headers, timeout=15)
        if r.status_code != 200:
            return {}
        
        soup = BeautifulSoup(r.text, 'html.parser')
        wikitables = soup.find_all('table', class_='wikitable')
        
        standings = {}
        
        for table in wikitables:
            headers_raw = [th.get_text(strip=True) for th in table.find_all('th')]
            headers_cleaned = [h.replace('Teamvte', 'Team').strip() for h in headers_raw]
            
            if any('Pos' in h for h in headers_cleaned) and any('Pts' in h for h in headers_cleaned):
                sibling = table.find_previous(['h2', 'h3', 'h4'])
                sibling_text = sibling.get_text(strip=True) if sibling else ""
                
                label = None
                for g in ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L']:
                    if f"Group {g}" in sibling_text:
                        label = f"Group {g}"
                        break
                if not label and "third-placed" in sibling_text.lower():
                    label = "Third-placed"
                
                if label:
                    rows = table.find_all('tr')
                    table_data = []
                    is_third_placed = (label == "Third-placed")
                    desired_cols = ['Pos', 'Team', 'Pld', 'W', 'D', 'L', 'GF', 'GA', 'GD', 'Pts']
                    if is_third_placed:
                        desired_cols = ['Pos', 'Grp', 'Team', 'Pld', 'W', 'D', 'L', 'GF', 'GA', 'GD', 'Pts']
                    
                    col_indices = {}
                    for col in desired_cols:
                        for idx, h in enumerate(headers_cleaned):
                            if h == col or (col == 'Team' and 'Team' in h) or (col == 'Pos' and 'Pos' in h) or (col == 'Pts' and 'Pts' in h):
                                col_indices[col] = idx
                                break
                    
                    if 'Team' not in col_indices:
                        col_indices['Team'] = 1
                    
                    for row in rows:
                        cells = row.find_all(['td', 'th'])
                        if not cells:
                            continue
                        
                        row_vals = [c.get_text(strip=True) for c in cells]
                        
                        first_cell = row_vals[0] if len(row_vals) > 0 else ""
                        if not re.match(r'^\d+$', first_cell):
                            continue
                        
                        row_data = {}
                        for col in desired_cols:
                            idx = col_indices.get(col)
                            if idx is not None and idx < len(row_vals):
                                val = row_vals[idx]
                            else:
                                val = ""
                            val = re.sub(r'\[.*?\]', '', val)
                            val = re.sub(r'\(.*?\)', '', val)
                            row_data[col] = val.strip()
                        
                        table_data.append(row_data)
                    
                    df = pd.DataFrame(table_data)
                    standings[label] = df
        return standings
    except Exception as e:
        print("Scrape standings error:", e)
        return {}


@st.cache_data(ttl=300)
def get_champion_predictions_df():
    cols = ['username', 'predicted_team', 'timestamp']
    # 1. Try reading from SQLite first for speed and offline robustness
    try:
        import sqlite3
        conn = sqlite3.connect('worldcup.db')
        df_sql = pd.read_sql_query("SELECT * FROM champion_predictions", conn)
        conn.close()
        if not df_sql.empty:
            save_local_backup('champion_predictions', df_sql)
            return df_sql
    except Exception as e:
        print(f"SQLite reading error for champion_predictions: {e}")

    # 2. If SQLite is empty or errors, pull from Google Sheets
    try:
        ws = get_worksheet('champion_predictions')
        data = ws.get_all_values()
        if not data:
            df = pd.DataFrame(columns=cols)
        else:
            df = pd.DataFrame(data[1:], columns=data[0])
        
        # Save to SQLite immediately to sync both sides
        try:
            import sqlite3
            conn = sqlite3.connect('worldcup.db')
            df.to_sql('champion_predictions', conn, if_exists='replace', index=False)
            conn.close()
        except Exception as esql:
            print(f"Error syncing Google Sheet to SQLite: {esql}")
            
        save_local_backup('champion_predictions', df)
        return df
    except Exception as e:
        # If worksheet does not exist on Google Sheets, create it
        try:
            sh = get_spreadsheet()
            ws = sh.add_worksheet(title='champion_predictions', rows="100", cols="3")
            ws.append_row(cols)
            df = pd.DataFrame(columns=cols)
            save_local_backup('champion_predictions', df)
            return df
        except Exception as ex:
            print(f"Error creating champion_predictions worksheet: {ex}")
            return load_local_backup('champion_predictions', cols)

def save_champion_prediction(username, predicted_team):
    name = normalize_name(username)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # 1. Save to SQLite immediately
    try:
        import sqlite3
        conn = sqlite3.connect('worldcup.db')
        # Clear existing row first to avoid duplicate rows and ensure uniqueness in SQLite
        conn.execute("DELETE FROM champion_predictions WHERE username = ?", (name,))
        conn.execute("""
            INSERT INTO champion_predictions (username, predicted_team, timestamp)
            VALUES (?, ?, ?)
        """, (name, str(predicted_team), timestamp))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Error saving to SQLite champion_predictions: {e}")

    # 2. Save to Google Sheets
    try:
        ws = get_worksheet('champion_predictions')
        df = get_champion_predictions_df()
        
        mask = df['username'] == name
        if mask.any():
            idx = df.index[mask][0] + 2
            ws.update(f'B{idx}:C{idx}', [[str(predicted_team), timestamp]])
        else:
            ws.append_row([name, str(predicted_team), timestamp])
    except Exception as e:
        print(f"Error saving to Google Sheets champion_predictions: {e}")
        
    get_champion_predictions_df.clear()

def get_user_champion_prediction(username):
    name = normalize_name(username)
    
    # Query SQLite first for speed, ordering by timestamp DESC to get the absolute latest prediction
    try:
        import sqlite3
        conn = sqlite3.connect('worldcup.db')
        cursor = conn.cursor()
        cursor.execute("SELECT predicted_team FROM champion_predictions WHERE username = ? ORDER BY timestamp DESC LIMIT 1", (name,))
        row = cursor.fetchone()
        conn.close()
        if row:
            return str(row[0]).strip()
    except Exception as e:
        print(f"SQLite query error in get_user_champion_prediction: {e}")
        
    # Fallback to DataFrame if SQLite fails
    df = get_champion_predictions_df()
    if df.empty: return ""
    user_pred = df[df['username'] == name]
    if user_pred.empty:
        return ""
    return str(user_pred.iloc[0]['predicted_team']).strip()




