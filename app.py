import streamlit as st
import database as db
from datetime import datetime, timedelta, timezone
import pandas as pd
import base64
import os

# ฟังก์ชันแปลงรูปภาพในเครื่องเป็น Base64
def get_base64_image(image_path):
    if not os.path.exists(image_path):
        return ""
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

current_dir = os.path.dirname(os.path.abspath(__file__))
image_full_path = os.path.join(current_dir, "ต่างดาว_optimized.webp")
ufo_base64 = get_base64_image(image_full_path)

# โหลดภาพ Artwork Messi บน Sidebar
messi_path = os.path.join(current_dir, "messi_optimized.png")
messi_base64 = get_base64_image(messi_path)

# ฟังก์ชันสำหรับเพลง
def get_audio_html(audio_path):
    if not os.path.exists(audio_path):
        return ""
    with open(audio_path, "rb") as f:
        audio_base64 = base64.b64encode(f.read()).decode()
    return f"""
        <audio autoplay loop id="bg-music">
            <source src="data:audio/mp3;base64,{audio_base64}" type="audio/mp3">
        </audio>
        <script>
            var audio = document.getElementById("bg-music");
            audio.volume = 0.3; // ตั้งความดังที่ 30% เพื่อความพรีเมี่ยม
        </script>
    """

# --- ตั้งค่าหน้าเว็บ ---
st.set_page_config(page_title="🏆 CRAZYFIFA WORLD CUP 2026", layout="wide", page_icon="⚽")

# แผนผังธงชาติ
FLAG_MAP = {
    'Mexico': '🇲🇽', 'South Africa': '🇿🇦', 'South Korea': '🇰🇷', 'Czech Republic': '🇨🇿',
    'Canada': '🇨🇦', 'Bosnia and Herzegovina': '🇧🇦', 'USA': '🇺🇸', 'Paraguay': '🇵🇾',
    'Spain': '🇪🇸', 'Morocco': '🇲🇦', 'England': '🏴󠁧󠁢󠁥󠁮󠁧󠁿', 'Australia': '🇦🇺',
    'Qatar': '🇶🇦', 'Switzerland': '🇨🇭', 'Brazil': '🇧🇷', 'Haiti': '🇭🇹',
    'Scotland': '🏴󠁧󠁢󠁳󠁣󠁴󠁿', 'Turkey': '🇹🇷', 'Argentina': '🇦🇷', 'France': '🇫🇷',
    'Germany': '🇩🇪', 'Japan': '🇯🇵', 'Portugal': '🇵🇹', 'Netherlands': '🇳🇱'
}

def get_team_display(team_name):
    flag = FLAG_MAP.get(team_name, '🏳️')
    return f"{team_name} {flag}"

# เริ่มต้นฐานข้อมูล
db.init_db()

# --- CSS ส่วนหัวและแอนิเมชัน ---
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Kanit:wght@300;400;600&display=swap');
    
    html, body, [class*="css"] {{
        font-family: 'Kanit', sans-serif;
    }}
    
    /* ปรับแต่ง Sidebar ให้ดูพรีเมี่ยม โทนเขียวตุ่น พร้อมแสงเงาเลื่อนผ่าน */
    [data-testid="stSidebar"] {{
        background: linear-gradient(180deg, #2d3a31 0%, #1a241e 100%);
        background-size: 200% 200%;
        position: relative;
        overflow: hidden;
        border-right: none; /* ลบเส้นขอบเงินออกเพื่อความ Minimal */
        box-shadow: 2px 0 15px rgba(0,0,0,0.3); /* คงเงาไว้ให้ดูมีมิติ */
    }}
    
    /* สร้างเลเยอร์แสงเงาเลื่อนผ่าน - ปรับปรุงให้เป็นสีเหลืองออกเขียวตุ่นๆ (Muted Lime Glow) */
    [data-testid="stSidebar"]::before {{
        content: "";
        position: absolute;
        top: -100%;
        left: -150%;
        width: 400%;
        height: 300%;
        background: linear-gradient(
            135deg,
            rgba(188, 204, 110, 0) 0%,
            rgba(188, 204, 110, 0) 45%,
            rgba(188, 204, 110, 0.25) 50%,
            rgba(188, 204, 110, 0) 55%,
            rgba(188, 204, 110, 0) 100%
        );
        animation: shimmer-fade 12s infinite linear;
        pointer-events: none;
        z-index: -1; /* ปรับไปอยู่ข้างหลังสุดเพื่อไม่ให้บดบังการคลิกของ UI */
        filter: blur(45px); /* เพิ่มความฟุ้งให้เนียนที่สุด */
    }}

    @keyframes shimmer-fade {{
        0% {{ transform: translate(-30%, -30%); }}
        100% {{ transform: translate(30%, 30%); }}
    }}

    /* สร้างเลเยอร์ภาพ Artwork Messi (Custom Artwork Overlay) */
    [data-testid="stSidebar"]::after {{
        content: "";
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background-image: url("data:image/png;base64,{messi_base64}");
        background-repeat: no-repeat;
        background-size: cover;
        background-position: center;
        opacity: 0.18; /* ปรับระดับความจางให้ลงตัว */
        filter: grayscale(100%) contrast(110%) brightness(85%); /* แปลงเป็นขาวดำเพื่อย้อมให้กลืนไปกับพื้นหลังสีเขียวตุ่นได้อย่างแนบเนียน */
        pointer-events: none;
        z-index: -2; /* ปรับไปอยู่หลังสุด */
    }}

    /* ระบายสีข้อความเฉพาะจุดอย่างถูกต้องเพื่อไม่ให้ชนโครงสร้าง z-index */
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {{
        color: #e2e8f0 !important;
    }}
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3, [data-testid="stSidebar"] h4 {{
        color: #ffffff !important;
    }}
    
    /* ปรับแต่งปุ่มเมนู พร้อมขอบเงินโครเมี่ยม */
    div[role="radiogroup"] > label {{
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid #c0c0c066; /* ขอบเงินโครเมี่ยมจางๆ */
        padding: 10px 15px;
        border-radius: 12px;
        margin-bottom: 8px;
        transition: all 0.3s ease;
    }}
    div[role="radiogroup"] > label:hover {{
        background: rgba(255, 255, 255, 0.08);
        border: 1px solid #c0c0c0; /* ขัดขอบเงินให้ชัดขึ้นเมื่อ hover */
        transform: translateX(5px);
    }}
    div[role="radiogroup"] > label[data-selected="true"] {{
        background: linear-gradient(90deg, #5c7a67 0%, #3d5244 100%) !important;
        border: 1.5px solid #ffffff; /* ขอบสีขาวสว่างแบบโครเมี่ยมสะท้อนแสง */
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
    }}
    div[role="radiogroup"] > label[data-selected="true"] span {{
        color: #ffffff !important;
        font-weight: 600;
    }}

    .header-wrapper {{
    display: flex;
    justify-content: center;
    align-items: center;
    width: 100%;
    height: 180px;
    overflow: visible;
    position: relative;
    z-index: 10;
}}
.main-title {{
    color: #FFD700;
    font-size: 3.5rem;
    font-weight: bold;
    margin: 0;
    text-shadow: 3px 3px 6px rgba(0,0,0,0.4);
    letter-spacing: 2px;
}}
.trophy-wrapper {{
    position: relative;
    display: inline-flex;
    justify-content: center;
    align-items: center;
    font-size: 3rem;
    margin-left: 20px;
}}
.animated-ball {{
    position: absolute;
    font-size: 1.5rem;
    z-index: 15;
    animation: goal-physics 5s cubic-bezier(0.25, 0.1, 0.25, 1.0) infinite;
    will-change: transform;
}}
.firework-particle {{
    position: absolute;
    width: 5px;
    height: 5px;
    background: #FFD700;
    border-radius: 50%;
    opacity: 0;
    z-index: 5;
    pointer-events: none;
    top: 10px; 
}}
.white-p {{ background: #FFFFFF; width: 3px; height: 3px; }}

.p1 {{ animation: burst 5s infinite; --tx: -120px; --ty: -150px; }}
.p2 {{ animation: burst 5s infinite; --tx: 120px; --ty: -150px; animation-delay: 0.1s; }}
.p3 {{ animation: burst 5s infinite; --tx: -60px; --ty: -200px; animation-delay: 0.05s; }}
.p4 {{ animation: burst 5s infinite; --tx: 60px; --ty: -200px; animation-delay: 0.15s; }}
.p5 {{ animation: burst 5s infinite; --tx: 0px; --ty: -230px; }}
.p6 {{ animation: burst 5s infinite; --tx: -180px; --ty: -80px; animation-delay: 0.2s; }}
.p7 {{ animation: burst 5s infinite; --tx: 180px; --ty: -80px; animation-delay: 0.25s; }}

@keyframes burst {{
    0%, 82% {{ transform: translate3d(0, 0, 0) scale(1); opacity: 0; }}
    84% {{ opacity: 1; }}
    94% {{ transform: translate3d(var(--tx), var(--ty), 0) scale(0.1); opacity: 0; }}
    100% {{ opacity: 0; }}
}}

@keyframes goal-physics {{
    0% {{ transform: translate3d(-500px, -150px, 0) rotate(0deg) scale(0); opacity: 0; }}
    5% {{ transform: translate3d(-480px, -120px, 0) rotate(20deg) scale(1); opacity: 1; }}
    25% {{ transform: translate3d(-350px, 30px, 0) rotate(180deg); }}
    35% {{ transform: translate3d(-280px, -40px, 0) rotate(270deg); }}
    50% {{ transform: translate3d(-150px, 30px, 0) rotate(450deg); }}
    60% {{ transform: translate3d(-80px, -20px, 0) rotate(540deg); }}
    75% {{ transform: translate3d(0px, 30px, 0) rotate(720deg); }}
    82% {{ transform: translate3d(0px, -10px, 0) rotate(810deg) scale(1); opacity: 1; }}
    92% {{ transform: translate3d(0px, -10px, 0) rotate(810deg) scale(0.7); opacity: 1; }}
    100% {{ transform: translate3d(0px, -5px, 0) rotate(810deg) scale(0.2); opacity: 0; }}
}}

@keyframes bounce {{
    0%, 100% {{ transform: translateY(0); }}
    50% {{ transform: translateY(-8px); }}
}}
.bouncing-icon {{
    display: inline-block;
    animation: bounce 1.5s infinite ease-in-out;
    margin-right: 8px;
}}

/* แต่งปุ่มแบบ Primary (บันทึกแล้ว) ให้แสดงผลเป็นสีเขียวพรีเมี่ยมสวยสะดุดตา */
button[data-testid="baseButton-primary"] {{
    background: linear-gradient(90deg, #2e7d32 0%, #1b5e20 100%) !important;
    color: #ffffff !important;
    border: 1px solid #4caf50 !important;
    box-shadow: 0 4px 10px rgba(46, 125, 50, 0.4) !important;
    font-weight: bold !important;
}}
button[data-testid="baseButton-primary"]:hover {{
    background: linear-gradient(90deg, #388e3c 0%, #2e7d32 100%) !important;
    box-shadow: 0 4px 15px rgba(76, 175, 80, 0.6) !important;
}}

/* ระบบพื้นหลัง UFO เวอร์ชั่นย้อนกลับ (Step -3) - แก้ไขชิดขอบบนและขยายใหญ่ */
[data-testid="stAppViewContainer"] {{
    background-image: url('data:image/webp;base64,{ufo_base64}');
    background-repeat: no-repeat;
    background-position: center 0px; /* บังคับชิดขอบบนสุด */
    background-attachment: fixed;
    background-size: 160vw auto; /* ขยายให้ใหญ่ขึ้นอีกและคุมความกว้าง */
    position: relative;
}}
[data-testid="stAppViewContainer"]::before {{
    content: "";
    position: absolute;
    top: 0; left: 0; width: 100%; height: 100%;
    background-color: rgba(14, 20, 16, 0.9); /* ปรับเป็นสีเขียวดำทึบโปร่งแสง 90% ให้เข้ากับธีมหลัก */
    z-index: -1;
}}
[data-testid="stAppViewContainer"] > section:nth-child(2) {{
    background-color: transparent !important;
}}

/* ซ่อนแถบเครื่องมือพัฒนาของ Streamlit ทั้งหมดทางขวา (Share, Star, Edit, Deploy, Menu) */
[data-testid="stHeaderActionElements"] {{display:none !important;}}
.stAppDeployButton {{display:none !important;}}
[data-testid="stHeaderActionButton"] {{display:none !important;}}
#MainMenu {{display:none !important;}}
footer {{visibility: hidden;}}
[data-testid="stHeader"] {{
    background-color: transparent !important;
    box-shadow: none !important;
}}

/* รองรับการแสดงผลบนโทรศัพท์มือถือ (Mobile Responsive) */
@media (max-width: 768px) {{
    .main-title {{
        font-size: 2.0rem !important;
    }}
    .header-wrapper {{
        height: 120px !important;
    }}
    .trophy-wrapper {{
        font-size: 2.0rem !important;
        margin-left: 10px !important;
    }}
    [data-testid="stAppViewContainer"] {{
        background-size: cover !important;
        background-position: center top !important;
    }}
    /* ดันช่องกรอกข้อมูลและปุ่มให้ดูกระชับขึ้นบนหน้าจอมือถือ */
    .stNumberInput {{
        margin-bottom: 5px !important;
    }}
    /* ซ่อนช่องว่างดันปุ่มเมื่ออยู่ในจอมือถือ */
    .desktop-spacer {{
        display: none !important;
    }}
    /* ล็อก Sidebar หลักไม่ให้แสงเงาทะลุออกนอกขอบเขตด้านล่าง */
    [data-testid="stSidebar"] {{
        overflow: hidden !important;
    }}
    /* ปล่อยให้เฉพาะเนื้อหาภายใน Sidebar เลื่อนแนวตั้งได้ และจะหยุดทันทีเมื่อสุดเนื้อหา */
    [data-testid="stSidebarUserContent"] {{
        overflow-y: auto !important;
        max-height: 100vh !important;
    }}
    /* ย่อขนาดหัวข้อล็อกอินใน Sidebar */
    [data-testid="stSidebar"] h2 {{
        font-size: 1.1rem !important;
        margin-top: 5px !important;
        margin-bottom: 5px !important;
    }}
    /* ย่อขนาดและจัดกระชับปุ่มเลือกเมนูหลักใน Sidebar เพื่อให้เห็นครบทุกเมนูโดยไม่ต้องเลื่อน */
    div[role="radiogroup"] > label {{
        padding: 5px 10px !important;
        margin-bottom: 4px !important;
        border-radius: 6px !important;
    }}
    div[role="radiogroup"] > label span {{
        font-size: 0.8rem !important;
    }}
}}
</style>

<div class='header-wrapper'>
    <div class='main-title'>CRAZYFIFA 2026</div>
    <div class='trophy-wrapper'>
        🏆
        <span class='animated-ball'>⚽</span>
        <div class='firework-particle p1'></div>
        <div class='firework-particle p2'></div>
        <div class='firework-particle p3'></div>
        <div class='firework-particle p4'></div>
        <div class='firework-particle p5'></div>
        <div class='firework-particle p6 white-p'></div>
        <div class='firework-particle p7 white-p'></div>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("<h3 style='text-align: center; margin-top: -30px; color: #888;'>WORLD CUP PREDICTION CHALLENGE</h3>", unsafe_allow_html=True)

# 1. ระบบผู้ใช้งาน (Sidebar)
if 'username' not in st.session_state:
    st.session_state.username = ""
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

st.sidebar.header("👤 เข้าสู่ระบบ")
existing_users = db.get_leaderboard()['username'].tolist()
options = ["เลือกชื่อของคุณ..."] + existing_users + ["➕ เพิ่มผู้เล่นใหม่..."]

default_idx = 0
if st.session_state.username in existing_users:
    default_idx = existing_users.index(st.session_state.username) + 1

selected_user = st.sidebar.selectbox("ชื่อผู้เล่น:", options, index=default_idx)

if selected_user == "➕ เพิ่มผู้เล่นใหม่...":
    new_name = st.sidebar.text_input("ระบุชื่อเล่นใหม่ (ภาษาอังกฤษ):", placeholder="เช่น Jacky")
    new_pin = st.sidebar.text_input("ตั้งรหัสผ่าน (PIN 4 หลัก):", type="password", max_chars=4)
    if new_name and new_pin:
        formatted_name = db.normalize_name(new_name)
        if st.sidebar.button("ลงทะเบียนและเข้าสู่ระบบ"):
            db.get_or_create_user(formatted_name, new_pin)
            st.session_state.username = formatted_name
            st.session_state.authenticated = True
            st.rerun()
elif selected_user != "เลือกชื่อของคุณ...":
    if st.session_state.username != selected_user:
        st.session_state.authenticated = False
    if not st.session_state.authenticated:
        if not db.has_pin(selected_user):
            st.sidebar.warning(f"⚠️ ยังไม่ได้ตั้งรหัส PIN สำหรับ {selected_user}")
            set_pin = st.sidebar.text_input("ตั้งรหัส PIN (4 หลัก):", type="password", max_chars=4)
            if st.sidebar.button("ตั้งรหัสและเข้าสู่ระบบ"):
                if set_pin:
                    db.get_or_create_user(selected_user, set_pin)
                    st.session_state.username = selected_user
                    st.session_state.authenticated = True
                    st.rerun()
        else:
            pin_input = st.sidebar.text_input(f"ใส่รหัส PIN ({selected_user}):", type="password", max_chars=4)
            if st.sidebar.button("ยืนยันตัวตน"):
                if db.verify_user(selected_user, pin_input):
                    st.session_state.username = selected_user
                    st.session_state.authenticated = True
                    st.rerun()
                else:
                    st.sidebar.error("❌ PIN ไม่ถูกต้อง")
    else:
        st.session_state.username = selected_user
        st.sidebar.success(f"ยินดีต้อนรับคุณ **{st.session_state.username}**")
        if st.sidebar.button("ออกจากระบบ"):
            st.session_state.username = ""
            st.session_state.authenticated = False
            st.rerun()
else:
    st.info("👈 กรุณาเลือกชื่อเพื่อเริ่มเล่นครับ")
    st.stop()

if not st.session_state.authenticated:
    st.stop()

username = st.session_state.username

# --- ระบบเพลงประกอบ (เล่นอัตโนมัติหลัง Login) ---
if st.session_state.authenticated:
    st.sidebar.markdown("---")
    st.sidebar.subheader("🎵 บรรยากาศสนาม")
    music_on = st.sidebar.toggle("เปิดเสียงเชียร์", value=True)
    if music_on:
        song_path = os.path.join(current_dir, "Shakira Burna Boy Dai Dai Official Video.mp3")
        st.components.v1.html(get_audio_html(song_path), height=0)
        st.sidebar.caption("📻 กำลังบรรเลง: Shakira & Burna Boy - Dai Dai")

menu_options = ["🏟️ ศึกชิงแชมป์โลก 2026", "🏆 ทำเนียบแชมป์ (Leaderboard)"]
if st.session_state.username == "Art":
    menu_options.append("💎 ห้องควบคุมระบบ (Admin)")
menu = st.sidebar.radio("เมนูหลัก", menu_options)

# 2. หน้าทายผลการแข่งขัน
if menu == "🏟️ ศึกชิงแชมป์โลก 2026":
    st.markdown("## <span class='bouncing-icon'>⚽</span> ตารางการแข่งขันและทายผล", unsafe_allow_html=True)
    all_matches = db.get_matches()
    all_matches['match_dt'] = pd.to_datetime(all_matches['match_time'])
    
    def render_match(row, username):
        match_id = row['id']
        home = row['home_team']
        away = row['away_team']
        home_display = get_team_display(home)
        away_display = get_team_display(away)

        m_time = datetime.strptime(row['match_time'], '%Y-%m-%d %H:%M:%S')
        status = row['status']
        now_th = datetime.now(timezone(timedelta(hours=7))).replace(tzinfo=None)
        is_locked = now_th > m_time or status == 'Finished'

        with st.container():
            # แถวแรก: แสดงคู่แข่งขันและเวลาเตะตัวใหญ่สวยงามชัดเจน
            st.subheader(f"{home_display} 🆚 {away_display}")
            st.caption(f"⏰ เวลาเตะ: {m_time.strftime('%d/%m/%Y %H:%M')}")
            
            user_preds = db.get_user_predictions(username)
            has_pred = match_id in user_preds
            default_h, default_a = user_preds.get(match_id, (0, 0))
            
            # แถวสอง: แสดงช่องกรอกคะแนนของทั้งสองทีมพร้อมปุ่มบันทึกผล
            # บน Desktop จะเรียงขนานกันสวยงาม 3 คอลัมน์ บนมือถือจะยุบตัวสแต็กแนวตั้งอย่างเป็นระเบียบเข้าใจง่าย
            col1, col2, col3 = st.columns([3, 3, 2])
            with col1:
                # ใช้ label บอกชื่อประเทศพร้อมธงชาติเหนือช่องกรอกข้อมูลโดยตรงเพื่อให้เข้าใจง่ายบนมือถือ
                pred_h = st.number_input(
                    label=home_display,
                    min_value=0,
                    step=1,
                    value=int(default_h),
                    key=f"h_{match_id}",
                    disabled=is_locked
                )
            with col2:
                pred_a = st.number_input(
                    label=away_display,
                    min_value=0,
                    step=1,
                    value=int(default_a),
                    key=f"a_{match_id}",
                    disabled=is_locked
                )
            with col3:
                # ดันปุ่มลงมาขนานกับช่องกรอกข้อมูลที่มี Label ด้านบนเฉพาะบน Desktop
                st.markdown("<div class='desktop-spacer' style='height: 28px;'></div>", unsafe_allow_html=True)
                if not is_locked:
                    # ปรับข้อความและสีปุ่มตามสถานะการทายผล (ทายแล้วปุ่มจะเขียวเด่นชัด)
                    if has_pred:
                        btn_label = "✅ บันทึกแล้ว (แก้ไข)"
                        btn_type = "primary"
                    else:
                        btn_label = "บันทึกผลทาย"
                        btn_type = "secondary"
                        
                    # ใช้ปุ่มเต็มความกว้างคอลัมน์เพื่อให้กดง่ายสวยงาม
                    if st.button(btn_label, key=f"btn_{match_id}", use_container_width=True, type=btn_type):
                        db.save_prediction(username, match_id, pred_h, pred_a)
                        st.toast(f"⚽ บันทึกผลทาย {home_display} vs {away_display} เรียบร้อยแล้ว!")
                    if has_pred:
                        st.markdown("<div style='color: #4CAF50; font-size: 0.95rem; font-weight: bold; margin-top: 6px; text-align: center;'>✅ บันทึกผลทายแล้ว</div>", unsafe_allow_html=True)
                else:
                    if status == 'Finished':
                        st.warning("🏁 สิ้นสุดการแข่งขัน")
                        winner_name = home if row['home_score'] > row['away_score'] else (away if row['away_score'] > row['home_score'] else "เสมอ")
                        winner_display = get_team_display(winner_name) if winner_name != "เสมอ" else "เสมอ"
                        st.info(f"🏆 **ชนะ:** {winner_display} ({int(row['home_score'])}-{int(row['away_score'])})")
                        if row['scorers']: st.caption(f"⚽ **คนยิง:** {row['scorers']}")
                    else:
                        st.warning("🔒 ปิดรับผลทาย")
            st.divider()

    finished = all_matches[all_matches['status'] == 'Finished'].sort_values('match_time', ascending=False)
    if not finished.empty:
        st.markdown("### 🏁 เกมของวันก่อนที่จบลง")
        for _, row in finished.iterrows():
            render_match(row, username)

    upcoming = all_matches[all_matches['status'] != 'Finished'].sort_values('match_time')
    if not upcoming.empty:
        # แสดงตารางการแข่งขันที่กำลังจะมาถึงทั้งหมดโดยจัดกลุ่มตามวัน
        unique_dates = upcoming['match_dt'].dt.date.unique()
        for d in unique_dates:
            now_th = datetime.now(timezone(timedelta(hours=7))).replace(tzinfo=None)
            today = now_th.date()
            tomorrow = today + pd.Timedelta(days=1)
            day_after = today + pd.Timedelta(days=2)
            
            label_suffix = ""
            if d == today:
                label_suffix = " (วันนี้)"
            elif d == tomorrow:
                label_suffix = " (วันพรุ่งนี้)"
            elif d == day_after:
                label_suffix = " (วันมะรืนนี้)"
                
            st.markdown(f"### <span class='bouncing-icon'>⚽</span> ตารางแข่งขันวันที่ {d.strftime('%d/%m/%Y')}{label_suffix}", unsafe_allow_html=True)
            day_matches = upcoming[upcoming['match_dt'].dt.date == d]
            for _, row in day_matches.iterrows():
                render_match(row, username)
    else:
        st.info("ไม่มีการแข่งขันที่กำลังจะมาถึงในขณะนี้ครับ")

# 3. หน้า Leaderboard
elif menu == "🏆 ทำเนียบแชมป์ (Leaderboard)":
    st.header("🏆 ทำเนียบยอดนักทายผล")
    st.info("💡 **กฎการให้คะแนน:**\n- ✅ ทายถูกฝั่ง: 1 คะแนน\n- 🎯 ทายถูกเป๊ะ (รวมเสมอ): 3 คะแนน\n- ❌ ทายผิด: 0 คะแนน")
    st.markdown("---")
    st.subheader("🌟 อันดับเกียรติยศสะสมรวม")
    leaderboard = db.get_leaderboard()
    if not leaderboard.empty:
        # หาคะแนนสูงสุด 3 อันดับแรก (Unique Scores) เพื่อมอบเหรียญทอง
        top_scores = sorted(leaderboard['total_score'].unique(), reverse=True)[:3]
        
        leaderboard['อันดับ'] = range(1, len(leaderboard) + 1)
        def add_gimmick(row):
            score = row['total_score']
            username = row['username']
            # มอบเหรียญทองให้ผู้ที่มีคะแนนอยู่ใน 3 อันดับแรก และคะแนนต้องมากกว่า 0
            if score > 0 and score in top_scores:
                return f"{username} 🥇"
            return f"{username} ➖"
        
        leaderboard['รายชื่อผู้เล่น'] = leaderboard.apply(add_gimmick, axis=1)
        st.dataframe(
            leaderboard[['อันดับ', 'รายชื่อผู้เล่น', 'total_score']].rename(columns={'total_score': 'คะแนนสะสม'}), 
            width='stretch', 
            hide_index=True,
            column_config={
                "อันดับ": st.column_config.NumberColumn("อันดับ", width="small"),
                "รายชื่อผู้เล่น": st.column_config.TextColumn("รายชื่อผู้เล่น", width="large"),
                "คะแนนสะสม": st.column_config.NumberColumn("คะแนนสะสม", width="medium")
            }
        )
    
    st.markdown("---")
    st.subheader("📜 ประวัติการทายผล")
    history = db.get_prediction_history()
    if not history.empty:
        history['date'] = pd.to_datetime(history['match_time']).dt.date
        now_th = datetime.now(timezone(timedelta(hours=7))).replace(tzinfo=None)
        today = now_th.date()
        tomorrow = today + pd.Timedelta(days=1)
        filtered_history = history[history['date'] <= tomorrow]
        if not filtered_history.empty:
            unique_dates = filtered_history['date'].unique()
            for d in unique_dates:
                is_today, is_tomorrow = (d == today), (d == tomorrow)
                with st.expander(f"📅 {d.strftime('%d/%m/%Y')} {'(วันนี้)' if is_today else ('(พรุ่งนี้)' if is_tomorrow else '')}", expanded=is_today):
                    day_history = filtered_history[filtered_history['date'] == d]
                    st.dataframe(day_history[['username', 'match', 'prediction', 'real_score', 'points']].rename(columns={'username': 'ผู้เล่น', 'match': 'แมตช์', 'prediction': 'ทาย', 'real_score': 'ผลจริง', 'points': 'แต้ม'}), use_container_width=True, hide_index=True)

# 4. หน้า Admin
elif menu == "💎 ห้องควบคุมระบบ (Admin)":
    st.header("💎 ศูนย์ควบคุมการจัดการ (Director)")
    
    # ทางลัดเปิด Google Sheets
    st.sidebar.markdown("---")
    st.sidebar.link_button("🔗 เปิด Google Sheets (DB)", "https://docs.google.com/spreadsheets/d/1MWZoajy6xNEQunVccEqNcb4iV4124qRxrDS5pHLf57c/edit")
    
    # ส่วนการซิงค์ข้อมูลอัตโนมัติ
    st.subheader("🔄 ระบบซิงค์อัตโนมัติ")
    if st.button("ซิงค์ข้อมูลทีมและผลการแข่งขัน (Sync)"):
        with st.spinner("กำลังดึงข้อมูลล่าสุดจากระบบ..."):
            updated = db.sync_results_from_web()
            if updated > 0:
                st.success(f"✅ อัปเดตข้อมูลสำเร็จ! (พบการเปลี่ยนแปลง {updated} รายการ)")
                st.balloons()
            else:
                st.info("ℹ️ ข้อมูลเป็นปัจจุบันอยู่แล้วครับ")
    
    st.divider()
    st.subheader("✍️ กรอกผลคะแนนด้วยตนเอง")
    matches = db.get_matches()
    upcoming = matches[matches['status'] != 'Finished']
    if not upcoming.empty:
        selected = st.selectbox("เลือกแมตช์:", [f"{r['id']}: {r['home_team']} vs {r['away_team']}" for i, r in upcoming.iterrows()])
        m_id = int(selected.split(":")[0])
        c1, c2 = st.columns(2)
        real_h = c1.number_input("สกอร์ Home", min_value=0, step=1)
        real_a = c2.number_input("สกอร์ Away", min_value=0, step=1)
        if st.button("ยืนยันผล"):
            import sqlite3
            conn = sqlite3.connect('worldcup.db')
            conn.execute("UPDATE matches SET home_score=?, away_score=?, status='Finished' WHERE id=?", (real_h, real_a, m_id))
            conn.commit()
            conn.close()
            db.update_scores_logic()
            st.success("อัปเดตเรียบร้อย!")
            st.balloons()

st.sidebar.markdown("---")
st.sidebar.caption("Power by Gemini 3.1 Pro & Streamlit")
