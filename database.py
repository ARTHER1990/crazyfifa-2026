import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
from datetime import datetime
import os
import json
import streamlit as st

# ตั้งค่า Credentials
SCOPES = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
LOCAL_KEY_PATH = '.secrets/directed-graph-494807-i7-f79a56b5b375.json'
SHEET_URL = 'https://docs.google.com/spreadsheets/d/1MWZoajy6xNEQunVccEqNcb4iV4124qRxrDS5pHLf57c/edit'

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

def get_worksheet(name):
    client = get_gspread_client()
    sh = client.open_by_url(SHEET_URL)
    return sh.worksheet(name)

def init_db():
    pass

@st.cache_data(ttl=60)
def get_users_df():
    ws = get_worksheet('users')
    data = ws.get_all_values()
    return pd.DataFrame(data[1:], columns=data[0])

@st.cache_data(ttl=60)
def get_matches():
    ws = get_worksheet('matches')
    data = ws.get_all_values()
    return pd.DataFrame(data[1:], columns=data[0])

@st.cache_data(ttl=60)
def get_predictions_df():
    ws = get_worksheet('predictions')
    data = ws.get_all_values()
    return pd.DataFrame(data[1:], columns=data[0])

def sync_results_from_web():
    results = [
        {'home': 'Mexico', 'away': 'South Africa', 'h_score': 2, 'a_score': 0, 'status': 'Finished'},
        {'home': 'South Korea', 'away': 'Czech Republic', 'h_score': 2, 'a_score': 1, 'status': 'Finished'},
        {'home': 'Canada', 'away': 'Bosnia and Herzegovina', 'id': 3},
        {'home': 'USA', 'away': 'Paraguay', 'id': 4}
    ]
    
    ws = get_worksheet('matches')
    data = ws.get_all_values()
    df = pd.DataFrame(data[1:], columns=data[0])
    
    updated_count = 0
    for res in results:
        if res.get('status') == 'Finished':
            mask = (df['home_team'] == res['home']) & (df['away_team'] == res['away']) & (df['status'] == 'Upcoming')
            if mask.any():
                idx = df.index[mask][0]
                df.at[idx, 'home_score'] = res['h_score']
                df.at[idx, 'away_score'] = res['a_score']
                df.at[idx, 'status'] = 'Finished'
                updated_count += 1
        elif 'id' in res:
            mask = (df['id'].astype(str) == str(res['id'])) & (df['home_team'].str.startswith('TBD') | df['away_team'].str.startswith('TBD'))
            if mask.any():
                idx = df.index[mask][0]
                df.at[idx, 'home_team'] = res['home']
                df.at[idx, 'away_team'] = res['away']
                updated_count += 1
                
    if updated_count > 0:
        ws.update([df.columns.values.tolist()] + df.values.tolist())
        update_scores_logic()
    st.cache_data.clear() # ล้างแคชเพื่อให้ดึงข้อมูลใหม่
    return updated_count

def normalize_name(username):
    name = username.strip()
    return 'Art' if name.lower() == 'art' else name

def has_pin(username):
    name = normalize_name(username)
    df = get_users_df()
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
    user_row = df[df['username'] == name]
    return not user_row.empty and str(user_row.iloc[0]['pin']) == str(pin)

def save_prediction(username, match_id, pred_home, pred_away):
    name = normalize_name(username)
    ws = get_worksheet('predictions')
    df = get_predictions_df()
    
    mask = (df['username'] == name) & (df['match_id'].astype(str) == str(match_id))
    if mask.any():
        idx = df.index[mask][0] + 2
        ws.update(f'C{idx}:D{idx}', [[pred_home, pred_away]])
    else:
        ws.append_row([name, match_id, pred_home, pred_away, 0])
    st.cache_data.clear()

def get_user_predictions(username):
    name = normalize_name(username)
    df = get_predictions_df()
    user_preds = df[df['username'] == name]
    return {int(row['match_id']): (row['pred_home'], row['pred_away']) for _, row in user_preds.iterrows()}

def get_leaderboard():
    df_u = get_users_df()
    df_p = get_predictions_df()
    
    active_users = df_p['username'].unique()
    df_u = df_u[df_u['username'].isin(active_users)]
    df_u['total_score'] = pd.to_numeric(df_u['total_score'], errors='coerce').fillna(0)
    return df_u.sort_values('total_score', ascending=False)

def get_prediction_history():
    df_p = get_predictions_df()
    df_m = get_matches()
    
    merged = df_p.merge(df_m, left_on='match_id', right_on='id')
    
    res = []
    for _, row in merged.iterrows():
        real = f"{row['home_score']}-{row['away_score']}" if row['status'] == 'Finished' else ( "กำลังแข่งขัน" if row['status'] == 'Live' else "ยังไม่เริ่ม")
        res.append({
            'username': row['username'],
            'match': f"{row['home_team']} vs {row['away_team']}",
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
    
    # แปลง ID เป็น int เพื่อกรองอย่างปลอดภัย
    df_m['id_int'] = pd.to_numeric(df_m['id'], errors='coerce').fillna(0).astype(int)
    df_p['match_id_int'] = pd.to_numeric(df_p['match_id'], errors='coerce').fillna(0).astype(int)
    
    # คำนวณคะแนนเฉพาะแมตช์ ID >= 12 เป็นต้นไป (ล้างผลแมตช์ 1-11 เพื่อเริ่มเล่นใหม่พร้อมกันวันนี้)
    finished = df_m[(df_m['status'] == 'Finished') & (df_m['id_int'] >= 12)]
    
    # บังคับแต้มแมตช์ 1-11 ให้กลายเป็น 0 แต้มทั้งหมด
    mask_old = df_p['match_id_int'] < 12
    df_p.loc[mask_old, 'points_earned'] = '0'
    
    for _, m in finished.iterrows():
        m_id = str(m['id'])
        r_h, r_a = int(m['home_score']), int(m['away_score'])
        
        mask = df_p['match_id'].astype(str) == m_id
        for idx, p in df_p[mask].iterrows():
            p_h, p_a = int(p['pred_home']), int(p['pred_away'])
            points = 0
            if p_h == r_h and p_a == r_a:
                points = 3
            else:
                pred_win = (p_h > p_a) - (p_h < p_a)
                real_win = (r_h > r_a) - (r_h < r_a)
                if pred_win == real_win:
                    points = 1
            df_p.at[idx, 'points_earned'] = str(points)
            
    # ลบคอลัมน์ชั่วคราวก่อนอัปเดตลง Google Sheets
    df_p_save = df_p.drop(columns=['match_id_int'])
    ws_p.update([df_p_save.columns.values.tolist()] + df_p_save.astype(str).values.tolist())
    
    ws_u = get_worksheet('users')
    data_u = ws_u.get_all_values()
    df_u = pd.DataFrame(data_u[1:], columns=data_u[0])
    
    for idx, u in df_u.iterrows():
        user_points = df_p[df_p['username'] == u['username']]['points_earned'].astype(int).sum()
        df_u.at[idx, 'total_score'] = int(user_points)
        
    ws_u.update([df_u.columns.values.tolist()] + df_u.astype(str).values.tolist())
    st.cache_data.clear()
