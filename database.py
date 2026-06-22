import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
from datetime import datetime
import os
import json
import streamlit as st

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
    sh = get_spreadsheet()
    return sh.worksheet(name)

def init_db():
    pass

@st.cache_data(ttl=60)
def get_users_df():
    try:
        ws = get_worksheet('users')
        data = ws.get_all_values()
        if not data: return pd.DataFrame(columns=['username', 'total_score', 'pin'])
        return pd.DataFrame(data[1:], columns=data[0])
    except Exception as e:
        print(f"Error fetching users: {e}")
        return pd.DataFrame(columns=['username', 'total_score', 'pin'])

@st.cache_data(ttl=60)
def get_matches():
    try:
        ws = get_worksheet('matches')
        data = ws.get_all_values()
        if not data: return pd.DataFrame(columns=['id', 'home_team', 'away_team', 'match_time', 'home_score', 'away_score', 'status', 'scorers'])
        return pd.DataFrame(data[1:], columns=data[0])
    except Exception as e:
        print(f"Error fetching matches: {e}")
        return pd.DataFrame(columns=['id', 'home_team', 'away_team', 'match_time', 'home_score', 'away_score', 'status', 'scorers'])

@st.cache_data(ttl=60)
def get_predictions_df():
    try:
        ws = get_worksheet('predictions')
        data = ws.get_all_values()
        if not data: return pd.DataFrame(columns=['username', 'match_id', 'pred_home', 'pred_away', 'points_earned'])
        df = pd.DataFrame(data[1:], columns=data[0])
        # ป้องกันและกรองรายการทำนายที่ซ้ำซ้อนในคู่เดียวกันของผู้ใช้แต่ละคน (ห้ามเปิ้ลคะแนนในคู่เดียว)
        df = df.drop_duplicates(subset=['username', 'match_id'], keep='first')
        return df
    except Exception as e:
        print(f"Error fetching predictions: {e}")
        return pd.DataFrame(columns=['username', 'match_id', 'pred_home', 'pred_away', 'points_earned'])

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
    st.cache_data.clear()

def verify_user(username, pin):
    name = normalize_name(username)
    df = get_users_df()
    if df.empty: return False
    user_row = df[df['username'] == name]
    return not user_row.empty and str(user_row.iloc[0]['pin']) == str(pin)

def save_prediction(username, match_id, pred_home, pred_away):
    name = normalize_name(username)
    ws = get_worksheet('predictions')
    df = get_predictions_df()
    
    mask = (df['username'] == name) & (df['match_id'].astype(str) == str(match_id))
    if mask.any():
        idx = df.index[mask][0] + 2
        # ใช้ update แบบระบุ range เพื่อความปลอดภัยใน gspread 6.x
        ws.update(f'C{idx}:D{idx}', [[int(pred_home), int(pred_away)]])
    else:
        ws.append_row([name, match_id, int(pred_home), int(pred_away), 0])
    st.cache_data.clear()

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
            preds[m_id] = (p_h, p_a)
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
            df_p.at[idx, 'points_earned'] = str(points)
            
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
    st.cache_data.clear()
    st.cache_resource.clear()

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


