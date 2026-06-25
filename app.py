import streamlit as st
import database as db
from datetime import datetime, timedelta, timezone
import pandas as pd
import base64
import os

# ฟังก์ชันล้างไฟล์ขยะ Icon\r ในโฟลเดอร์ .git ป้องกันปัญหา git bad ref refs/tags/Icon? ถาวร
def cleanup_git_icons():
    try:
        git_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".git")
        if os.path.exists(git_dir):
            for root, dirs, files in os.walk(git_dir):
                for file in files:
                    if file.startswith("Icon"):
                        try:
                            os.remove(os.path.join(root, file))
                        except:
                            pass
    except:
        pass

cleanup_git_icons()

# ฟังก์ชันสำหรับแปลงค่าตัวเลขอย่างปลอดภัย (ดักจับ None, NaN, ช่องว่าง)
def safe_int(val, default=0):
    if val is None:
        return default
    if isinstance(val, float):
        import math
        if math.isnan(val):
            return default
        return int(val)
    val_str = str(val).strip()
    if val_str == "" or val_str.lower() in ("nan", "none", "null"):
        return default
    try:
        return int(val_str)
    except:
        return default


# ฟังก์ชันแปลงรูปภาพในเครื่องเป็น Base64
def get_base64_image(image_path):
    if not os.path.exists(image_path):
        return ""
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

current_dir = os.path.dirname(os.path.abspath(__file__))
image_full_path = os.path.join(current_dir, "ต่างดาว_optimized.webp")
ufo_base64 = get_base64_image(image_full_path)

# โหลดภาพพิซซ่านาโปลี (พิซซ่า.png) สำหรับลอยเป็น Easter Egg ลำที่ 4
pizza_path = os.path.join(current_dir, "พิซซ่า.png")
pizza_base64 = get_base64_image(pizza_path)

# โหลดภาพ Artwork พื้นหลัง Sidebar (เปลี่ยนจาก Messi เป็น 02.png ตามสั่ง)
bg_sidebar_path = os.path.join(current_dir, "02_optimized.png")
bg_sidebar_base64 = get_base64_image(bg_sidebar_path)

# โหลดภาพแบนเนอร์ของคุณอาร์ต เครซีเว็ป.png
banner_path = os.path.join(current_dir, "เครซีเว็ป.png")
banner_base64 = get_base64_image(banner_path)

# โหลดภาพลูกบอลทัวร์นาเมนต์ ball2026.png
ball_path = os.path.join(current_dir, "ball2026.png")
ball_base64 = get_base64_image(ball_path)

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

# แผนผังธงชาติ (Lowercase keys สำหรับความยืดหยุ่นสูง)
FLAG_MAP = {
    'mexico': '🇲🇽', 'south africa': '🇿🇦', 'south korea': '🇰🇷', 'czech republic': '🇨🇿',
    'canada': '🇨🇦', 'bosnia and herzegovina': '🇧🇦', 'usa': '🇺🇸', 'paraguay': '🇵🇾',
    'spain': '🇪🇸', 'morocco': '🇲🇦', 'england': '🏴󠁧󠁢󠁥󠁮󠁧󠁿', 'australia': '🇦🇺',
    'qatar': '🇶🇦', 'switzerland': '🇨🇭', 'brazil': '🇧🇷', 'haiti': '🇭🇹',
    'scotland': '🏴󠁧󠁢󠁳󠁣󠁴󠁿', 'turkey': '🇹🇷', 'argentina': '🇦🇷', 'france': '🇫🇷',
    'germany': '🇩🇪', 'japan': '🇯🇵', 'portugal': '🇵🇹', 'netherlands': '🇳🇱',
    'curaçao': '🇨🇼', 'côte d\'ivoire': '🇨🇮', 'ecuador': '🇪🇨', 'sweden': '🇸🇪',
    'tunisia': '🇹🇳', 'cape verde': '🇨🇻', 'belgium': '🇧🇪', 'egypt': '🇪🇬',
    'saudi arabia': '🇸🇦', 'uruguay': '🇺🇾', 'iran': '🇮🇷', 'new zealand': '🇳🇿',
    'senegal': '🇸🇳', 'iraq': '🇮🇶', 'norway': '🇳🇴', 'algeria': '🇩🇿',
    'austria': '🇦🇹', 'jordan': '🇯🇴', 'dr congo': '🇨🇩', 'croatia': '🇭🇷',
    'ghana': '🇬🇭', 'panama': '🇵🇦', 'uzbekistan': '🇺🇿', 'colombia': '🇨🇴',
    'italy': '🇮🇹', 'costa rica': '🇨🇷', 'jamaica': '🇯🇲', 'honduras': '🇭🇳',
    'chile': '🇨🇱', 'peru': '🇵🇪', 'venezuela': '🇻🇪', 'nigeria': '🇳🇬',
    'cameroon': '🇨🇲', 'denmark': '🇩🇰', 'poland': '🇵🇱', 'ukraine': '🇺🇦',
    'wales': '🏴󠁧󠁢󠁷󠁬󠁳󠁿', 'serbia': '🇷🇸', 'slovenia': '🇸🇮', 'romania': '🇷🇴',
    'georgia': '🇬🇪', 'albania': '🇦🇱', 'hungary': '🇭🇺', 'slovakia': '🇸🇰',
    'china': '🇨🇳', 'vietnam': '🇻🇳', 'thailand': '🇹🇭', 'malaysia': '🇲🇾',
}

@st.cache_data(ttl=1800)
def check_and_sync_scores():
    try:
        db.auto_sync_scores()
    except Exception as e:
        pass



# แผนผังแปลชื่อทีมเป็นภาษาไทยพรีเมี่ยม เพื่อความสมบูรณ์แบบของหน้าตารางคะแนนและผลทาย
TEAM_TRANSLATION_MAP = {
    'mexico': 'เม็กซิโก', 'south africa': 'แอฟริกาใต้', 'south korea': 'เกาหลีใต้', 'czech republic': 'สาธารณรัฐเช็ก',
    'canada': 'แคนาดา', 'bosnia and herzegovina': 'บอสเนียและเฮอร์เซโกวีนา', 'usa': 'สหรัฐอเมริกา', 'paraguay': 'ปารากวัย',
    'spain': 'สเปน', 'morocco': 'โมร็อกโก', 'england': 'อังกฤษ', 'australia': 'ออสเตรเลีย',
    'qatar': 'กาตาร์', 'switzerland': 'สวิตเซอร์แลนด์', 'brazil': 'บราซิล', 'haiti': 'เฮติ',
    'scotland': 'สกอตแลนด์', 'turkey': 'ตุรกี', 'argentina': 'อาร์เจนตินา', 'france': 'ฝรั่งเศส',
    'germany': 'เยอรมนี', 'japan': 'ญี่ปุ่น', 'portugal': 'โปรตุเกส', 'netherlands': 'เนเธอร์แลนด์',
    'curaçao': 'คูราเซา', 'côte d\'ivoire': 'คอตดิวัวร์', 'ecuador': 'เอกวาดอร์', 'sweden': 'สวีเดน',
    'tunisia': 'ตูนิเซีย', 'cape verde': 'เคปเวิร์ด', 'belgium': 'เบลเยียม', 'egypt': 'อียิปต์',
    'saudi arabia': 'ซาอุดีอาระเบีย', 'uruguay': 'อุรุกวัย', 'iran': 'อิหร่าน', 'new zealand': 'นิวซีแลนด์',
    'senegal': 'เซเนกัล', 'iraq': 'อิรัก', 'norway': 'นอร์เวย์', 'algeria': 'แอลจีเรีย',
    'austria': 'ออสเตรีย', 'jordan': 'จอร์แดน', 'dr congo': 'ดีอาร์ คองโก', 'croatia': 'โครเอเชีย',
    'ghana': 'กานา', 'panama': 'ปานามา', 'uzbekistan': 'อุซเบกิสถาน', 'colombia': 'โคลอมเบีย',
    'italy': 'อิตาลี', 'costa rica': 'คอสตาริกา', 'jamaica': 'จาเมกา', 'honduras': 'ฮอนดูรัส',
    'chile': 'ชิลี', 'peru': 'เปรู', 'venezuela': 'เวเนซุเอลา', 'nigeria': 'ไนจีเรีย',
    'cameroon': 'แคเมอรูน', 'denmark': 'เดนมาร์ก', 'poland': 'โปแลนด์', 'ukraine': 'ยูเครน',
    'wales': 'เวลส์', 'serbia': 'เซอร์เบีย', 'slovenia': 'สโลวีเนีย', 'romania': 'โรมาเนีย',
    'georgia': 'จอร์เจีย', 'albania': 'แอลเบเนีย', 'hungary': 'ฮังการี', 'slovakia': 'สโลวาเกีย',
    'china': 'จีน', 'vietnam': 'เวียดนาม', 'thailand': 'ไทย', 'malaysia': 'มาเลเซีย',
    'china pr': 'จีน', 'united states': 'สหรัฐอเมริกา'
}

def get_team_display(team_name):
    clean_name = team_name.strip()
    alias_map = {
        'cabo verde': 'cape verde',
        'czechia': 'czech republic',
        'türkiye': 'turkey',
        'ir iran': 'iran',
        'ivory coast': 'côte d\'ivoire',
        'korea republic': 'south korea',
        'united states': 'usa',
        'china pr': 'china'
    }
    lookup_name = clean_name.lower()
    if lookup_name in alias_map:
        lookup_name = alias_map[lookup_name]
        
    flag = FLAG_MAP.get(lookup_name, '🏳️')
    thai_name = TEAM_TRANSLATION_MAP.get(lookup_name, clean_name)
    
    # แสดงผลเป็น "ธงชาติ ชื่อภาษาไทย" (เช่น 🇩🇪 เยอรมนี) เพื่อความสมมาตร พรีเมี่ยม และเหมาะสมกับทุกพื้นที่แสดงผล
    return f"{flag} {thai_name}"

# เริ่มต้นฐานข้อมูล
db.init_db()

bg_opacity_val = 0.67
bg_opacity_bottom = 0.70

# --- CSS ส่วนหัวและแอนิเมชัน ---
st.markdown(f"""
<!-- SVG Filter สำหรับทำเอฟเฟกต์ธงสะบัดช้าๆ (Slow Flag Waving/Ripple Effect) - ปรับให้นุ่มนวลขึ้นไม่ลายตา -->
<svg style="position: fixed; width: 0; height: 0; pointer-events: none;">
  <filter id="slow-waving-filter" x="-10%" y="-10%" width="120%" height="120%">
    <feTurbulence type="fractalNoise" baseFrequency="0.01 0.03" numOctaves="1" result="turbulence">
      <animate attributeName="baseFrequency" 
               values="0.01 0.03; 0.01 0.04; 0.01 0.03" 
               dur="12s" 
               repeatCount="indefinite" />
    </feTurbulence>
    <feDisplacementMap in="SourceGraphic" in2="turbulence" scale="12" xChannelSelector="R" yChannelSelector="G" />
  </filter>
</svg>

<style>
    @import url('https://fonts.googleapis.com/css2?family=Kanit:wght@300;400;600&display=swap');
    
    html, body, [class*="css"] {{
        font-family: 'Kanit', sans-serif;
    }}
    
    /* ปรับแต่ง Sidebar ให้ดูพรีเมี่ยม โทนเขียวตุ่น */
    [data-testid="stSidebar"] {{
        background: linear-gradient(180deg, #2d3a31 0%, #1a241e 100%);
        position: relative;
        overflow: hidden !important; /* ล็อกความสูงเพื่อคลิปแสงและถ้วยไม่ให้ทะลุออก */
        border-right: none;
        box-shadow: 2px 0 15px rgba(0,0,0,0.3);
        height: 100vh !important;
    }}
    
    [data-testid="stSidebarContent"] {{
        overflow-y: auto !important; /* ย้ายสกรอลล์มาไว้ที่เนื้อหาหลัก เพื่อไม่ให้โดนเอฟเฟกต์เบียดบัง */
        height: 100% !important;
        max-height: 100vh !important;
    }}

    [data-testid="stSidebarUserContent"] {{
        overflow-y: visible !important;
        max-height: none !important;
    }}

    
    /* เลเยอร์เส้นแสงสะท้อนพาดผ่าน (Premium Soft Light Sweep) - แก้ไขให้วิ่งทะลุไม่ค้างที่ขอบ */
    [data-testid="stSidebar"]::before {{
        content: "";
        position: absolute;
        top: -50%; /* ขยายพื้นที่ด้านบนเพื่อให้คลุมแนวเฉียง */
        left: 0;
        width: 400px; /* เพิ่มความกว้างแสง */
        height: 200%;
        background: linear-gradient(
            to right, 
            rgba(255, 255, 255, 0) 0%, 
            rgba(255, 255, 255, 0.15) 50%, 
            rgba(255, 255, 255, 0) 100%
        );
        transform: translateX(-150%) rotate(-45deg); /* เริ่มต้นนอกจอ */
        filter: blur(40px);
        mix-blend-mode: soft-light;
        animation: light-sweep 6s infinite ease-in-out;
        pointer-events: none;
        z-index: -1;
    }}

    @keyframes light-sweep {{
        0% {{ transform: translateX(-200%) rotate(-45deg); }}
        30% {{ transform: translateX(400%) rotate(-45deg); }} /* วิ่งทะลุออกไปไกลๆ */
        100% {{ transform: translateX(400%) rotate(-45deg); }}
    }}

    /* เลเยอร์พื้นหลัง Sidebar: ลายถ้วยบอลโลกพร้อมเอฟเฟกต์สะบัดช้าๆ */
    [data-testid="stSidebar"]::after {{
        content: "";
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background-image: url("data:image/png;base64,{bg_sidebar_base64}");
        background-repeat: no-repeat;
        background-size: cover;
        background-position: center;
        opacity: 0.22;
        filter: grayscale(100%) contrast(110%) brightness(85%) url(#slow-waving-filter); /* ใช้ SVG Filter กวนพิกเซล */
        pointer-events: none;
        z-index: -2; /* ล็อคไว้หลังสุดไม่ให้รบกวนเมนู */
        transform: scale(1.1); /* ขยายเผื่อขอบจากการบิดเบี้ยวของ Filter */
    }}

    /* ระบายสีข้อความเฉพาะจุดอย่างถูกต้องเพื่อไม่ให้ชนโครงสร้าง z-index */
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {{
        color: #e2e8f0 !important;
    }}
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3, [data-testid="stSidebar"] h4 {{
        color: #ffffff !important;
    }}
    
    /* ปรับแต่งปุ่มเมนูหลักของไซด์บาร์ให้กรอบกว้างและแผ่ขนาดเท่ากันเป๊ะเสมอกันทุกปุ่ม 100% */
    div[role="radiogroup"] {{
        width: 100% !important;
        display: flex !important;
        flex-direction: column !important;
    }}
    div[role="radiogroup"] > label {{
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid #c0c0c066; /* ขอบเงินโครเมี่ยมจางๆ */
        padding: 10px 15px;
        border-radius: 12px;
        margin-bottom: 8px;
        transition: all 0.2s ease;
        cursor: pointer !important;
        width: 100% !important; /* บังคับให้ขนาดกรอบขยายตัวสมมาตรเท่ากันทั้งหมด */
        box-sizing: border-box !important;
        display: flex !important;
    }}
    div[role="radiogroup"] > label:hover {{
        background: rgba(255, 255, 255, 0.08) !important;
        border: 1px solid rgba(255, 255, 255, 0.5) !important; /* ขัดขอบเงินให้ชัดขึ้นเมื่อ hover */
        box-shadow: 0 2px 10px rgba(255, 255, 255, 0.05) !important;
    }}
    div[role="radiogroup"] > label[data-selected="true"] {{
        background: linear-gradient(90deg, #5c7a67 0%, #3d5244 100%) !important;
        border: 1.5px solid #ffffff !important; /* ขอบสีขาวสว่างแบบโครเมี่ยมสะท้อนแสง */
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3) !important;
    }}
    div[role="radiogroup"] > label[data-selected="true"] span {{
        color: #ffffff !important;
        font-weight: 600;
    }}

    /* ปรับแต่งช่องกรอกคะแนน (st.number_input) ให้ดูโมเดิร์นคลีนและมีมิติ */
    div[data-testid="stNumberInput"] {{
        background: rgba(255, 255, 255, 0.02) !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 12px !important;
        padding: 5px 8px !important;
        transition: all 0.3s ease !important;
    }}
    div[data-testid="stNumberInput"]:hover {{
        background: rgba(255, 255, 255, 0.05) !important;
        border-color: rgba(255, 255, 255, 0.2) !important;
    }}
    /* ปรับตัวอักษร Label ของช่องกรอกข้อมูลให้ดูมีระเบียบและไม่รกรุงรัง */
    div[data-testid="stNumberInput"] label p {{
        font-size: 0.9rem !important;
        color: #a0aec0 !important;
        font-weight: 500 !important;
        letter-spacing: 0.5px !important;
    }}

    /* สไตล์ส่วนหัวพรีเมี่ยมแบบโปร่งใส ไร้รอยต่อ */
    .premium-header {{
        position: relative;
        width: 100%;
        max-width: 1200px;
        height: 250px;
        display: flex;
        justify-content: center;
        align-items: center;
        text-align: center;
        background: transparent;
        border: none;
        box-shadow: none;
        margin-top: -35px;
        margin-bottom: 5px;
        z-index: 10;
        overflow: visible;
    }}

    .title-wrapper {{
        position: relative;
        display: flex;
        align-items: center;
        justify-content: center;
        width: 100%;
        max-width: 950px;
        padding: 0 30px;
        z-index: 2;
    }}

    /* รูปภาพแบนเนอร์ เครซีเว็ป.png กรองพื้นดำมองทะลุ 100% */
    .crazyweb-img {{
        width: 100%;
        height: auto;
        max-height: 210px;
        object-fit: contain;
        mix-blend-mode: screen;
        animation: imageGlowMutedPulse 3.5s ease-in-out infinite alternate;
        will-change: filter, transform;
    }}

    /* แอนิเมชันกระเพื่อมเรืองแสงออร่านีออนสีฟ้าสวยงามชัดเจนระดับกำลังดี (4px ถึง 8px) ไม่บวมหนา */
    @keyframes imageGlowMutedPulse {{
        0% {{
            filter: drop-shadow(0 0 4px rgba(58, 226, 255, 0.35));
            transform: scale(1);
        }}
        100% {{
            filter: drop-shadow(0 0 8px rgba(58, 226, 255, 0.55));
            transform: scale(1.006);
        }}
    }}

    /* แผงมาร์กพิกเซลกาวเป้าถ้วยรางวัลทองคำของคุณอาร์ต */
    .trophy-target-overlay {{
        position: absolute;
        right: 12.9%; /* พิกัดขวาทองคำเป๊ะๆ โดยคุณอาร์ต (ปรับจาก 10.2% กลับสู่สัดส่วนทองคำ) */
        top: 17.0%;    /* พิกัดบนทองคำเป๊ะๆ โดยคุณอาร์ต */
        width: 40px;
        height: 40px;
        pointer-events: none;
        z-index: 12;
        display: flex;
        justify-content: center;
        align-items: center;
        border: none;
        box-shadow: none;
    }}

    /* วงกลมออร่าแสงสีฟ้านีออนชีพจรเต้นเบื้องหลังถ้วยในรูป */
    .trophy-target-overlay::before {{
        content: "";
        position: absolute;
        width: 120px;
        height: 120px;
        background: radial-gradient(circle, rgba(58, 226, 255, 0.55) 0%, transparent 70%);
        border-radius: 50%;
        pointer-events: none;
        z-index: -1;
        filter: blur(10px);
        animation: trophyGlowPulse 3.5s ease-in-out infinite alternate;
        will-change: transform, opacity;
    }}

    @keyframes trophyGlowPulse {{
        0% {{
            transform: scale(0.85);
            opacity: 0.55;
        }}
        100% {{
            transform: scale(1.18);
            opacity: 1.0;
        }}
    }}

    .animated-ball-x {{
        position: absolute;
        width: 38px;
        height: 38px;
        top: 1px;
        left: 1px;
        z-index: 15;
        animation: goal-x 4s infinite;
        will-change: transform;
    }}
    .animated-ball-y {{
        animation: goal-y 4s infinite;
        will-change: transform;
    }}
    .animated-ball {{
        display: inline-block;
        width: 38px;
        height: 38px;
        object-fit: contain;
        animation: goal-ball 4s infinite;
        will-change: transform;
        filter: drop-shadow(0 0 6px rgba(255, 215, 0, 0.95)) drop-shadow(0 0 15px rgba(255, 255, 255, 0.7));
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

.p1 {{ animation: burst 4s infinite; --tx: -120px; --ty: -150px; }}
.p2 {{ animation: burst 4s infinite; --tx: 120px; --ty: -150px; animation-delay: 0.03s; }}
.p3 {{ animation: burst 4s infinite; --tx: -60px; --ty: -200px; animation-delay: 0.01s; }}
.p4 {{ animation: burst 4s infinite; --tx: 60px; --ty: -200px; animation-delay: 0.04s; }}
.p5 {{ animation: burst 4s infinite; --tx: 0px; --ty: -230px; }}
.p6 {{ animation: burst 4s infinite; --tx: -180px; --ty: -80px; animation-delay: 0.05s; }}
.p7 {{ animation: burst 4s infinite; --tx: 180px; --ty: -80px; animation-delay: 0.07s; }}

@keyframes burst {{
    0%, 34% {{ transform: translate3d(0, 0, 0) scale(1); opacity: 0; }}
    35% {{ opacity: 1; }}
    45% {{ transform: translate3d(var(--tx), var(--ty), 0) scale(0.8); opacity: 0.9; }}
    55% {{ transform: translate3d(calc(var(--tx) * 1.2), calc(var(--ty) * 1.2), 0) scale(0.1); opacity: 0; }}
    100% {{ opacity: 0; }}
}}

@keyframes goal-x {{
    0% {{ transform: translateX(-780px); }}
    3% {{ transform: translateX(-710px); }}
    10% {{ transform: translateX(-420px); }}
    18% {{ transform: translateX(-310px); }}
    26% {{ transform: translateX(-200px); }}
    32% {{ transform: translateX(-80px); }}
    35% {{ transform: translateX(0px); }}
    40% {{ transform: translateX(0px); }}
    100% {{ transform: translateX(0px); }}
}}

@keyframes goal-y {{
    0% {{ transform: translateY(120px); }}
    18% {{ transform: translateY(-120px); }}
    35% {{ transform: translateY(0px); }}
    40% {{ transform: translateY(0px); }}
    100% {{ transform: translateY(0px); }}
}}

@keyframes goal-ball {{
    0% {{ transform: rotate(0deg) scale(2.8); opacity: 0; }}
    3% {{ opacity: 1; }}
    18% {{ transform: rotate(270deg) scale(1.5); }}
    35% {{ transform: rotate(540deg) scale(0.7); opacity: 1; }}
    38% {{ transform: rotate(560deg) scale(0.1); opacity: 0; }}
    40% {{ transform: rotate(560deg) scale(0); opacity: 0; }}
    100% {{ transform: rotate(560deg) scale(0); opacity: 0; }}
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

.ufo-flyer-lg {{
    position: fixed;
    font-size: 1.6rem;
    z-index: 99999;
    top: 65px;
    pointer-events: none;
    animation: ufo-flight-lg 15s linear infinite;
    will-change: transform;
    filter: drop-shadow(0 0 6px rgba(0, 255, 255, 0.9)) drop-shadow(0 0 15px rgba(0, 191, 255, 0.6));
}}

.ufo-flyer-sm {{
    position: fixed;
    font-size: 0.9rem;
    z-index: 99998;
    top: 35px;
    pointer-events: none;
    animation: ufo-flight-sm 22s linear infinite;
    animation-delay: 6s;
    will-change: transform;
    filter: drop-shadow(0 0 4px rgba(223, 0, 254, 0.9)) drop-shadow(0 0 10px rgba(128, 0, 128, 0.6));
}}

.ufo-flyer-mid {{
    position: fixed;
    font-size: 2.2rem; /* ลำใหญ่เด่นๆ */
    z-index: 99999;
    top: 120px; /* วิ่งระดับต่ำลงมาช่วงกลางเว็บ */
    pointer-events: none;
    animation: ufo-flight-mid 12s linear infinite;
    animation-delay: 3s; /* ปล่อยคนละช่วงเวลา */
    will-change: transform;
    filter: drop-shadow(0 0 8px rgba(0, 255, 0, 1)) drop-shadow(0 0 20px rgba(50, 205, 50, 0.7)); /* ออร่าสีเขียวเรืองแสงเด่นๆ */
}}

.pizza-flyer {{
    position: fixed;
    width: 65px;
    height: 65px;
    z-index: 99999;
    top: 95px; /* ความสูงระดับกลางๆ กำลังพอดี */
    pointer-events: none;
    animation: pizza-flight 18s linear infinite;
    animation-delay: 1.5s; /* หลบหลีกจานบินอื่นๆ ไม่ให้ทับซ้อนกัน */
    will-change: transform;
    filter: drop-shadow(0 0 8px rgba(255, 102, 0, 1)) drop-shadow(0 0 20px rgba(255, 69, 0, 0.7)); /* ออร่าสีส้มไฟเตาถ่านร้อนๆ ของแบรนด์ VOILA_PIZZA */
}}

@keyframes ufo-flight-lg {{
    0% {{
        transform: translate3d(120vw, 0px, 0);
    }}
    25% {{
        transform: translate3d(60vw, -15px, 0);
    }}
    50% {{
        transform: translate3d(0vw, 15px, 0);
    }}
    75% {{
        transform: translate3d(-60vw, -10px, 0);
    }}
    100% {{
        transform: translate3d(-120vw, 0px, 0);
    }}
}}

@keyframes ufo-flight-sm {{
    0% {{
        transform: translate3d(120vw, 0px, 0);
    }}
    30% {{
        transform: translate3d(50vw, 10px, 0);
    }}
    60% {{
        transform: translate3d(-20vw, -15px, 0);
    }}
    85% {{
        transform: translate3d(-80vw, 5px, 0);
    }}
    100% {{
        transform: translate3d(-120vw, 0px, 0);
    }}
}}

@keyframes ufo-flight-mid {{
    0% {{
        transform: translate3d(120vw, 0px, 0);
    }}
    25% {{
        transform: translate3d(60vw, 30px, 0);
    }}
    50% {{
        transform: translate3d(0vw, -30px, 0);
    }}
    75% {{
        transform: translate3d(-60vw, 20px, 0);
    }}
    100% {{
        transform: translate3d(-120vw, 0px, 0);
    }}
}}

@keyframes pizza-flight {{
    0% {{
        transform: translate3d(120vw, 0px, 0);
    }}
    20% {{
        transform: translate3d(80vw, -20px, 0);
    }}
    40% {{
        transform: translate3d(40vw, 15px, 0);
    }}
    60% {{
        transform: translate3d(0vw, -15px, 0);
    }}
    80% {{
        transform: translate3d(-50vw, 20px, 0);
    }}
    100% {{
        transform: translate3d(-120vw, 0px, 0);
    }}
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
    background-image: linear-gradient(to bottom, rgba(4, 6, 5, {bg_opacity_val}) 0%, rgba(3, 5, 4, {bg_opacity_bottom}) 100%), url('data:image/webp;base64,{ufo_base64}');
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
    background-color: rgba(4, 6, 5, {bg_opacity_val}); /* ปรับระดับความมืดของอวกาศแบบไดนามิกเพื่อขับเน้นให้แบนเนอร์และถ้วยรางวัลเด่นชัดสะดุดตาสุดๆ */
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
    [data-testid="stSidebarContent"] {{
        overflow-y: auto !important;
    }}
    /* ปล่อยให้เฉพาะเนื้อหาภายใน Sidebar เลื่อนแนวตั้งได้ และจะหยุดทันทีเมื่อสุดเนื้อหา */
    [data-testid="stSidebarUserContent"] {{
        overflow-y: visible !important;
        max-height: none !important;
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

<!-- จานบินลอยจำลอง (แยกอยู่นอกโครงสร้าง Layout แบนเนอร์เพื่อความเสถียรของพิกัดถ้วยทองคำ) -->
<div class='ufo-flyer-lg'>🛸</div>
<div class='ufo-flyer-sm'>🛸</div>
<div class='ufo-flyer-mid'>🛸</div>
<div class='pizza-flyer'><img src="data:image/png;base64,{pizza_base64}" style="width:100%; height:100%; object-fit:contain;" alt="🍕"></div>

<header class="premium-header">
<div class="title-wrapper">
<!-- ภาพแบนเนอร์ เครซีเว็ป.png โหลดผ่าน Base64 โปร่งแสงพรีเมี่ยม -->
<img class="crazyweb-img" src="data:image/png;base64,{banner_base64}" alt="CRAZYFIFA 2026 Header">
<!-- จุดฉายแอนิเมชันลูกบอลทองคำตกกระทบและส่องประกายออร่าเฉพาะยอดถ้วยฝั่งขวา -->
<div class="trophy-target-overlay">
<div class='animated-ball-x'>
<div class='animated-ball-y'>
<img class='animated-ball' src="data:image/png;base64,{ball_base64}" alt="⚽">
</div>
</div>
<div class='firework-particle p1'></div>
<div class='firework-particle p2'></div>
<div class='firework-particle p3'></div>
<div class='firework-particle p4'></div>
<div class='firework-particle p5'></div>
<div class='firework-particle p6 white-p'></div>
<div class='firework-particle p7 white-p'></div>
</div>
</div>
</header>
""", unsafe_allow_html=True)

# 1. ระบบผู้ใช้งาน (Sidebar)
if 'username' not in st.session_state:
    st.session_state.username = ""
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

st.sidebar.header("👤 เข้าสู่ระบบ")
try:
    leaderboard_df = db.get_leaderboard()
    existing_users = leaderboard_df['username'].tolist() if not leaderboard_df.empty else []
except Exception as e:
    st.sidebar.error(f"⚠️ ไม่สามารถเชื่อมต่อฐานข้อมูลได้: {e}")
    existing_users = []

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
            st.session_state.show_congrats_popup = True
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
                    st.session_state.toast_shown = False
                    st.session_state.show_congrats_popup = True
                    st.rerun()
        else:
            pin_input = st.sidebar.text_input(f"ใส่รหัส PIN ({selected_user}):", type="password", max_chars=4)
            if st.sidebar.button("ยืนยันตัวตน"):
                if db.verify_user(selected_user, pin_input):
                    st.session_state.username = selected_user
                    st.session_state.authenticated = True
                    st.session_state.toast_shown = False
                    st.session_state.show_congrats_popup = True
                    st.rerun()
                else:
                    st.sidebar.error("❌ PIN ไม่ถูกต้อง")
    else:
        st.session_state.username = selected_user
        st.sidebar.success(f"ยินดีต้อนรับคุณ **{st.session_state.username}**")
        if st.sidebar.button("ออกจากระบบ"):
            st.session_state.username = ""
            st.session_state.authenticated = False
            st.session_state.toast_shown = False
            st.rerun()
else:
    st.info("👈 กรุณาเลือกชื่อเพื่อเริ่มเล่นครับ")
    st.stop()

if not st.session_state.authenticated:
    st.stop()

username = st.session_state.username

# --- ระบบป๊อบอัพเด้งพลุแตกเฉลิมฉลองผู้ได้คะแนนสูงสุดตรงกลางจอใหญ่เมื่อล็อกอินใหม่ ---
if st.session_state.get('show_congrats_popup', False):
    try:
        import time
        # เก็บบันทึกเวลาเริ่มต้นแสดงผลของป๊อปอัป
        if 'congrats_start_time' not in st.session_state:
            st.session_state.congrats_start_time = time.time()
            
        # หากเวลาผ่านไปมากกว่า 5.5 วินาที ให้ปิดป๊อปอัปนี้อัตโนมัติทางหลังบ้านในการรีรันรอบถัดไป
        if time.time() - st.session_state.congrats_start_time > 5.5:
            st.session_state.show_congrats_popup = False
            st.rerun()
            
        leaderboard_df = db.get_leaderboard()
        if not leaderboard_df.empty:
            max_score = leaderboard_df['total_score'].max()
            if max_score > 0:
                leaders_at_top = leaderboard_df[leaderboard_df['total_score'] == max_score]['username'].tolist()
                leaders_str = " & ".join(leaders_at_top)
                
                with st.container():
                    # 1. พ่นกล่อง Backdrop, Modal, ปุ่มปิด HTML สำรอง และ JavaScript ดักคลิกกับ Auto-dismiss
                    st.markdown(
                        f"""<div class='congrats-modal-backdrop'>
<div class='congrats-modal'>
<!-- ปุ่มปิดตัว X กากบาทสีทองพรีเมียมที่หาง่ายและใช้สัมผัสปิดได้เร็วบนมือถือ -->
<div class='congrats-close-x' onclick='dismissCongratsPopup()'>&times;</div>

<!-- เอฟเฟกต์ประกายดวงดาวลอยละล่อง -->
<div class='congrats-sparkle sp1'>✨</div>
<div class='congrats-sparkle sp2'>⭐</div>
<div class='congrats-sparkle sp3'>✨</div>
<div class='congrats-sparkle sp4'>⭐</div>
<div class='congrats-sparkle sp5'>✨</div>

<!-- พลุกระจายตัวฉลองชัย -->
<div class='firework-particle p1'></div>
<div class='firework-particle p2'></div>
<div class='firework-particle p3'></div>
<div class='firework-particle p4'></div>
<div class='firework-particle p5'></div>

<div class='congrats-title'>🏆 ทำเนียบผู้นำคะแนนสูงสุด 🏆</div>
<div style='font-size: 1.05rem; color: #a0aec0; margin-bottom: 5px; font-family: Kanit, sans-serif;'>ขอแสดงความยินดีกับผู้ที่ได้คะแนนนำลิ่วสูงสุดขณะนี้!</div>
<div class='congrats-leader'>🎉 {leaders_str} 🎉</div>
<div class='congrats-score'>👑 นำอันดับหนึ่งด้วยคะแนนสะสม: {int(max_score)} แต้ม 👑</div>
<div style='color: #FFD700; font-size: 0.95rem; font-family: Kanit, sans-serif; font-weight: bold; margin-bottom: 30px; animation: heartbeat 1.5s infinite;'>🔥 ใครจะเป็นผู้มาโค่นบัลลังก์นี้ได้สำเร็จ? 🔥</div>

<!-- เว้นพื้นที่ว่างสำหรับวางปุ่มปิด Streamlit ที่ถูกดึงขึ้นมาทับพอดี -->
<div class='congrats-btn-placeholder'></div>
</div>
</div>
<div class='congrats-trigger-marker'></div>

<script>
function dismissCongratsPopup() {{
    // 1. ค้นหาและทำลายฉากหลังและกล่องป๊อปอัปฝั่งเบราว์เซอร์ทันทีเพื่อปลดล็อกหน้าจอ
    var backdrop = document.querySelector('.congrats-modal-backdrop');
    if (backdrop) {{
        backdrop.style.display = 'none';
        backdrop.remove();
    }}
    
    // 2. ค้นหามาร์กเกอร์และทำการสกัดปุ่มกดปิดของ Streamlit เพื่อทำการกระตุ้นคลิกหลังบ้าน
    var marker = document.querySelector('.congrats-trigger-marker');
    if (marker) {{
        var parentContainer = marker.parentElement;
        if (parentContainer) {{
            // หา container ของปุ่มสตรีมลิตที่อยู่ถัดไป
            var nextEl = parentContainer.nextElementSibling;
            if (nextEl) {{
                var btn = nextEl.querySelector('button');
                if (btn) {{
                    btn.click();
                }}
            }}
        }}
    }}
}}

// ปิดอัตโนมัติเมื่อครบ 5 วินาที
setTimeout(function() {{
    dismissCongratsPopup();
}}, 5000);
</script>""",
                        unsafe_allow_html=True
                    )
                    
                    # 2. ปุ่ม Streamlit ที่จัดวางพิกัดให้อยู่เหนือกำแพง backdrop เสมอ
                    if st.button("ลุยต่อกันเลย! ⚽🔥", key="close_popup_btn", use_container_width=True):
                        st.session_state.show_congrats_popup = False
                        st.rerun()
                        
                    # 3. พ่น CSS ควบคุมการเลือนหายไปเอง และยอมให้นิ้วสไลด์เลื่อนผ่าน (Pointer Events PASS-THROUGH)
                    st.markdown(
                        """<style>
/* สำหรับอุปกรณ์โทรศัพท์มือถือและหน้าจอขนาดเล็ก: ปิดการทำงานและการครอบสัมผัสของระบบ Congrats ทั้งหมดโดยสมบูรณ์ เพื่อป้องกันไม่ให้โทรศัพท์ค้างแข็งและเปิดให้เลื่อนหน้าจอโฮมกรอกคะแนนได้ฉลุยทันที! */
@media (max-width: 768px) {
    .congrats-modal-backdrop {
        display: none !important;
        pointer-events: none !important;
    }
    .congrats-modal {
        display: none !important;
        pointer-events: none !important;
    }
    div[data-testid="element-container"]:has(.congrats-trigger-marker),
    div[data-testid="element-container"]:has(.congrats-trigger-marker) + div[data-testid="element-container"] {
        display: none !important;
        pointer-events: none !important;
        position: static !important;
        height: 0 !important;
        width: 0 !important;
        overflow: hidden !important;
    }
}

/* แผงกั้นสีเบลอพื้นหลังเต็มจอ */
.congrats-modal-backdrop {
    position: fixed !important;
    top: 0 !important;
    left: 0 !important;
    width: 100vw !important;
    height: 100vh !important;
    background: rgba(8, 8, 16, 0.88) !important;
    backdrop-filter: blur(15px) !important;
    z-index: 999990 !important;
    display: flex !important;
    justify-content: center !important;
    align-items: center !important;
    
    /* กุญแจสำคัญ: ปรับเป็น none เพื่อยอมให้เลื่อนหน้าจอ/รูดจอหลักด้านหลังบนมือถือได้ทันที ไม่ค้างแข็ง! */
    pointer-events: none !important;
    
    /* แอนิเมชันเฟดหายไปเองใน 5 วินาที */
    animation: fade-out-disappear 5s forwards cubic-bezier(0.25, 1, 0.5, 1) !important;
}

/* ตัวการ์ดป๊อปอัปเฉลิมฉลองแชมป์ */
.congrats-modal {
    background: linear-gradient(135deg, rgba(20, 20, 38, 0.95) 0%, rgba(32, 32, 58, 0.98) 100%) !important;
    border: 3px solid #FFD700 !important;
    box-shadow: 0 0 50px rgba(255, 215, 0, 0.5), inset 0 0 20px rgba(255, 215, 0, 0.2) !important;
    border-radius: 28px !important;
    padding: 45px 35px !important;
    text-align: center !important;
    max-width: 520px !important;
    width: 90% !important;
    position: relative !important;
    
    /* เปิดใช้งาน touch / click บนตัวกล่อง Modal เองเพื่อให้กดปุ่มได้ปกติ */
    pointer-events: auto !important;
    
    /* สเกลเด้ง และเฟดหายพร้อมฉากหลัง */
    animation: popup-scale 0.55s cubic-bezier(0.175, 0.885, 0.32, 1.275) both,
               popup-fade-out 5s forwards ease-in-out !important;
}

/* ปุ่มกากบาทปิดสำรองที่มุมขวาบนของการ์ดเพื่อใช้งานง่ายบนโทรศัพท์ */
.congrats-close-x {
    position: absolute !important;
    top: 15px !important;
    right: 20px !important;
    font-size: 2.3rem !important;
    color: rgba(255, 255, 255, 0.4) !important;
    cursor: pointer !important;
    line-height: 1 !important;
    transition: all 0.25s ease !important;
    z-index: 1000005 !important;
    pointer-events: auto !important;
    font-family: Arial, sans-serif !important;
}
.congrats-close-x:hover {
    color: #FFD700 !important;
    transform: scale(1.15) !important;
}

/* ตัวจองพื้นที่ปุ่ม */
.congrats-btn-placeholder {
    height: 55px !important;
}

/* ยึดและดึงคอนเทนเนอร์ปุ่มของสตรีมลิตขึ้นมาลอยตัวบนสุด */
div[data-testid="element-container"]:has(.congrats-trigger-marker) + div[data-testid="element-container"] {
    position: fixed !important;
    top: calc(50vh + 125px) !important;
    left: 50vw !important;
    transform: translate(-50%, -50%) !important;
    z-index: 1000000 !important; /* ชั้นสูงสุดเหนือ backdrop */
    width: auto !important;
    min-width: 260px !important;
    max-width: 440px !important;
    display: block !important;
    pointer-events: auto !important;
    
    /* เลือนหายไปพร้อมกล่อง */
    animation: button-fade-out 5s forwards ease-in-out !important;
}

/* สไตล์ปุ่มกดปิดสีทองพรีเมียมตระการตา */
div[data-testid="element-container"]:has(.congrats-trigger-marker) + div[data-testid="element-container"] button {
    background: linear-gradient(135deg, #FFD700 0%, #FF9F00 100%) !important;
    color: #000000 !important;
    font-weight: 800 !important;
    border: 2px solid #FFFFFF !important;
    padding: 12px 40px !important;
    border-radius: 50px !important;
    box-shadow: 0 8px 25px rgba(255, 215, 0, 0.5), 0 0 15px rgba(255, 215, 0, 0.3) !important;
    font-family: 'Kanit', sans-serif !important;
    font-size: 1.15rem !important;
    transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275) !important;
    width: 100% !important;
    cursor: pointer !important;
    pointer-events: auto !important;
}

div[data-testid="element-container"]:has(.congrats-trigger-marker) + div[data-testid="element-container"] button:hover {
    transform: scale(1.06) !important;
    box-shadow: 0 12px 30px rgba(255, 215, 0, 0.7), 0 0 25px rgba(255, 215, 0, 0.5) !important;
}

div[data-testid="element-container"]:has(.congrats-trigger-marker) + div[data-testid="element-container"] button:active {
    transform: scale(0.97) !important;
}

/* แอนิเมชันเลือนหาย (Fade Out) และปลอดการบังคลิก */
@keyframes fade-out-disappear {
    0% { opacity: 1; pointer-events: none; }
    70% { opacity: 1; pointer-events: none; }
    95% { opacity: 0; pointer-events: none; }
    100% { opacity: 0; pointer-events: none; display: none !important; }
}

@keyframes popup-fade-out {
    0% { opacity: 1; }
    70% { opacity: 1; transform: scale(1); }
    95% { opacity: 0; transform: scale(0.9); }
    100% { opacity: 0; display: none !important; }
}

@keyframes button-fade-out {
    0% { opacity: 1; pointer-events: auto; }
    70% { opacity: 1; pointer-events: auto; }
    95% { opacity: 0; pointer-events: none; }
    100% { opacity: 0; pointer-events: none; display: none !important; }
}

@keyframes popup-scale {
    0% { transform: scale(0.5); opacity: 0; }
    100% { transform: scale(1); opacity: 1; }
}

@keyframes heartbeat {
    0% { transform: scale(1); }
    50% { transform: scale(1.04); }
    100% { transform: scale(1); }
}

.congrats-title {
    font-size: 1.7rem !important;
    color: #FFD700 !important;
    font-weight: 850 !important;
    margin-bottom: 8px !important;
    text-shadow: 0 0 15px rgba(255, 215, 0, 0.6) !important;
    font-family: 'Kanit', sans-serif !important;
}

.congrats-leader {
    font-size: 2.4rem !important;
    color: #FFFFFF !important;
    font-weight: 900 !important;
    margin: 18px 0 !important;
    text-shadow: 0 0 20px rgba(255, 255, 255, 0.7), 0 0 10px rgba(255, 215, 0, 0.4) !important;
    font-family: 'Kanit', sans-serif !important;
    animation: heartbeat 2s infinite !important;
}

.congrats-score {
    font-size: 1.3rem !important;
    color: #00E676 !important;
    font-weight: bold !important;
    margin-bottom: 20px !important;
    text-shadow: 0 0 10px rgba(0, 230, 118, 0.4) !important;
    font-family: 'Kanit', sans-serif !important;
}

/* วิ้งวิ้งและประกายดาว */
.congrats-sparkle {
    position: absolute !important;
    font-size: 1.5rem !important;
    animation: float-sparkle 3s infinite ease-in-out !important;
}
.sp1 { top: 10%; left: 8%; animation-delay: 0s !important; }
.sp2 { top: 15%; right: 10%; animation-delay: 0.5s !important; }
.sp3 { bottom: 25%; left: 12%; animation-delay: 1s !important; }
.sp4 { bottom: 20%; right: 15%; animation-delay: 1.5s !important; }
.sp5 { top: 50%; left: 5%; animation-delay: 0.8s !important; }

@keyframes float-sparkle {
    0%, 100% { transform: translateY(0) scale(0.8); opacity: 0.3; }
    50% { transform: translateY(-15px) scale(1.2); opacity: 1; text-shadow: 0 0 12px #FFD700; }
}

/* พลุกระจายแฉก */
.firework-particle {
    position: absolute !important;
    width: 6px !important;
    height: 6px !important;
    border-radius: 50% !important;
    background: #FFD700 !important;
    animation: explode 4s infinite ease-out !important;
    opacity: 0 !important;
}
.p1 { top: 20%; left: 20%; background: #FF3D00 !important; animation-delay: 0.2s !important; }
.p2 { top: 30%; right: 25%; background: #00E676 !important; animation-delay: 1.2s !important; }
.p3 { bottom: 35%; left: 25%; background: #29B6F6 !important; animation-delay: 2.2s !important; }
.p4 { bottom: 40%; right: 20%; background: #EC407A !important; animation-delay: 0.7s !important; }
.p5 { top: 12%; left: 50%; background: #FFEB3B !important; animation-delay: 1.7s !important; }

@keyframes explode {
    0% { transform: scale(0); opacity: 1; }
    20% { transform: scale(1.5) translate(var(--dx, 20px), var(--dy, -20px)); opacity: 0.9; }
    80%, 100% { transform: scale(0.5) translate(var(--dx, 40px), var(--dy, -40px)); opacity: 0; }
}

.p1 { --dx: -30px; --dy: -40px; }
.p2 { --dx: 45px; --dy: -30px; }
.p3 { --dx: -40px; --dy: 35px; }
.p4 { --dx: 35px; --dy: 40px; }
.p5 { --dx: 10px; --dy: -45px; }
</style>""",
                        unsafe_allow_html=True
                    )
                    
                    st.balloons()
    except Exception as e:
        pass

# --- ตรวจสอบอัปเดตผลสกอร์แบบเรียลไทม์อัตโนมัติ (แคชไว้ 30 นาที) ---
check_and_sync_scores()


# --- คำนวณคู่แข่งขันที่ยังไม่ได้ทายผลสำหรับเตือนความจำ ---
if 'toast_shown' not in st.session_state:
    st.session_state.toast_shown = False
if 'music_enabled' not in st.session_state:
    st.session_state.music_enabled = True

try:
    all_matches_rem = db.get_matches()
    all_matches_rem['match_dt'] = pd.to_datetime(all_matches_rem['match_time'])
    now_th_rem = datetime.now(timezone(timedelta(hours=7))).replace(tzinfo=None)
    
    # ดึงคู่ที่ยังไม่จบการแข่งขัน และเวลาเตะยังไม่ถึงกำหนด (ยังแก้ไขได้)
    active_upcoming_rem = all_matches_rem[
        (all_matches_rem['status'] != 'Finished') & 
        (all_matches_rem['match_dt'] > now_th_rem)
    ]
    
    user_preds_rem = db.get_user_predictions(username)
    unpredicted_list = []
    
    for _, row in active_upcoming_rem.iterrows():
        m_id = safe_int(row['id'])
        if m_id not in user_preds_rem:
            unpredicted_list.append(row)
            
    st.session_state.unpredicted_count = len(unpredicted_list)
    st.session_state.unpredicted_matches = unpredicted_list
    
    # สั่นแจ้งเตือน (Toast) ครั้งแรกตอนล็อกอินสำเร็จ
    if not st.session_state.toast_shown and len(unpredicted_list) > 0:
        st.toast(f"🚨 คุณ {username}! ยังมีคู่แข่งขันที่ยังไม่ได้ทายผลอีก {len(unpredicted_list)} คู่ครับ!", icon="🚨")
        st.session_state.toast_shown = True
except Exception as e:
    st.session_state.unpredicted_count = 0
    st.session_state.unpredicted_matches = []

# --- ระบบเมนูและเพลงประกอบ (จัดลำดับประมวลผลสูงสุดเพื่อขจัดอาการกดย้ำ) ---
if st.session_state.authenticated:
    # 🧭 เมนูนำทางหลัก (ย้ายขึ้นบนสุดเพื่อลำดับสิทธิ์การทำงานลำดับแรก ขจัดปัญหาความหน่วงและอาการกดย้ำ)
    menu_options = ["🏟️ ศึกชิงแชมป์โลก 2026 (World Cup)", "📜 ผลการแข่งขันย้อนหลัง (Match Results)", "🏅 ตารางคะแนนกลุ่ม (Standings)", "📑 ประวัติการทายผล (My Predictions)", "🏆 ทำเนียบแชมป์ (Leaderboard)"]
    if st.session_state.username == "Art":
        menu_options.append("💎 ห้องควบคุมระบบ (Admin)")
    menu = st.sidebar.radio("เมนูหลัก", menu_options)
    
    st.sidebar.markdown("---")
    st.sidebar.subheader("🎵 บรรยากาศสนาม")
    
    # ป้องกันความคลาดเคลื่อนทางสถานะ (State Desynchronization: ความไม่สอดคล้องกันของสถานะตัวแปรและการเรนเดอร์)
    # โดยผูกกับ Session State (เซสชัน สเตต: หน่วยความจำชั่วคราวสำหรับเก็บบันทึกค่าสถานะต่างๆ ของผู้ใช้) ผ่าน key ตรงตัว
    music_on = st.sidebar.toggle(
        "เปิดเสียงเชียร์", 
        key="music_enabled"
    )
    
    # จองพื้นที่ (Placeholder: กล่องจองพื้นที่บนหน้าเว็บ) เพื่อบังคับให้ระบบประมวลผลเขียนทับและลบตัวเล่นเพลงอย่างทันทีทันใด
    music_placeholder = st.sidebar.empty()
    
    if music_on:
        song_path = os.path.join(current_dir, "Shakira Burna Boy Dai Dai Official Video.mp3")
        with music_placeholder.container():
            st.iframe(src=get_audio_html(song_path), height=1)
        st.sidebar.caption("📻 กำลังบรรเลง: Shakira & Burna Boy - Dai Dai")
    else:
        # หากกดปิด: บังคับทำลายออบเจกต์ตัวเล่นเสียงและเคลียร์กล่องจองพื้นที่ให้ว่างเปล่าทันที ส่งผลให้เสียงเงียบสนิทใน 1 คลิก!
        music_placeholder.empty()

    # --- แถบสรุปผลการแข่งขันของวันนี้/วันล่าสุดย้อนหลัง 1 วันใน Sidebar ---
    st.sidebar.markdown("---")

    try:
        # ดึงข้อมูลแมตช์และประวัติการทายผลทั้งหมด
        all_matches_sb = db.get_matches()
        all_matches_sb['match_dt'] = pd.to_datetime(all_matches_sb['match_time'])
        finished_sb = all_matches_sb[all_matches_sb['status'] == 'Finished'].sort_values('match_time', ascending=False)

        if not finished_sb.empty:
            # คำนวณวันปัจจุบัน (เวลาไทย UTC+7)
            now_th_sb = datetime.now(timezone(timedelta(hours=7))).replace(tzinfo=None)
            today_date_sb = now_th_sb.date()
            
            # กรองเฉพาะแมตช์ที่แข่งเสร็จในวันนี้จริง ๆ (ตามเวลาไทย UTC+7)
            day_matches_sb = finished_sb[finished_sb['match_dt'].dt.date == today_date_sb]
            
            st.sidebar.subheader("📅 สรุปผลแข่งวันนี้")
            
            if day_matches_sb.empty:
                st.sidebar.info("ไม่มีสรุปผลแข่งของวันนี้")
            
            # ดึงประวัติการทายเพื่อประมวลผลความถูกต้องของผู้ใช้งานทั้งหมด
            predictions_sb = db.get_predictions_df()
            
            for _, row_m in day_matches_sb.iterrows():
                m_id = str(row_m['id'])
                h_real = safe_int(row_m['home_score'])
                a_real = safe_int(row_m['away_score'])
                real_win = (h_real > a_real) - (h_real < a_real)
                
                home_display = get_team_display(row_m['home_team'])
                away_display = get_team_display(row_m['away_team'])
                
                exp_title = f"{home_display} {h_real} - {a_real} {away_display}"
                
                with st.sidebar.expander(exp_title):
                    st.markdown(f"**⚽ ผู้ทำประตู:** {row_m['scorers'] if row_m['scorers'] else 'ไม่มีข้อมูล'}")
                    st.markdown("**🎯 ผลทายของทุกคน in คู่นี้:**")
                    
                    # กรองคำทายของคู่นี้
                    m_preds = predictions_sb[predictions_sb['match_id'].astype(str) == m_id]
                    if m_preds.empty:
                        st.markdown("<small style='color:#888;'>ยังไม่มีผู้เล่นทายคู่นี้</small>", unsafe_allow_html=True)
                    else:
                        preds_html_list = []
                        for _, row_p in m_preds.iterrows():
                            u_name = row_p['username']
                            p_h = safe_int(row_p['pred_home'])
                            p_a = safe_int(row_p['pred_away'])
                            pred_win = (p_h > p_a) - (p_h < p_a)
                            
                            # คำนวณแต้มและสไตล์สีสันเพื่อความพรีเมี่ยมตระการตา
                            if p_h == h_real and p_a == a_real:
                                hl_style = "background: rgba(46, 204, 113, 0.15); border: 1px solid rgba(46, 204, 113, 0.3); color: #2ecc71;"
                                pt_txt = "🏆 3 แต้ม"
                            elif pred_win == real_win:
                                hl_style = "background: rgba(241, 196, 15, 0.1); border: 1px solid rgba(241, 196, 15, 0.25); color: #ffd700;"
                                pt_txt = "🟢 1 แต้ม"
                            else:
                                hl_style = "background: rgba(231, 76, 60, 0.08); border: 1px solid rgba(231, 76, 60, 0.15); color: #e74c3c;"
                                pt_txt = "❌ 0 แต้ม"
                            
                            preds_html_list.append(
                                f"<div style='font-size:0.8rem; padding:6px 10px; border-radius:6px; margin-bottom:5px; {hl_style}'>"
                                f"👤 <b>{u_name}</b>: ทาย {p_h} - {p_a} ({pt_txt})"
                                f"</div>"
                            )
                        
                        # หุ้มผลทายทั้งหมดไว้ในกล่อง scroll ย่อยเพื่อจำกัดความสูงไม่ให้ล้นหน้าจอ
                        all_preds_html = "".join(preds_html_list)
                        st.markdown(
                            f"<div style='max-height:180px; overflow-y:auto; padding-right:5px; scrollbar-width:thin; scrollbar-color:rgba(255,215,0,0.35) transparent;'>"
                            f"{all_preds_html}"
                            f"</div>",
                            unsafe_allow_html=True
                        )
        else:
            st.sidebar.info("ไม่มีสรุปผลแข่งของวันนี้")
    except Exception as sb_err:
        st.sidebar.error(f"⚠️ เกิดข้อผิดพลาดในการสรุปผลวันนี้: {sb_err}")

    st.sidebar.markdown("---")



# 2. หน้าทายผลการแข่งขัน
if menu == "🏟️ ศึกชิงแชมป์โลก 2026 (World Cup)":
    # 🚨 แสดงระบบกันลืม (Smart Prediction Reminder)
    if 'unpredicted_matches' in st.session_state and st.session_state.unpredicted_matches:
        matches_list_html = []
        for m in st.session_state.unpredicted_matches:
            h_disp = get_team_display(m['home_team'])
            a_disp = get_team_display(m['away_team'])
            m_t = pd.to_datetime(m['match_time']).strftime('%d/%m/%Y %H:%M น.')
            matches_list_html.append(
                f"<div style='margin-bottom: 5px;'>⚽ <b>{h_disp} vs {a_disp}</b> (⏰ เริ่มเตะ {m_t})</div>"
            )
        matches_html = "".join(matches_list_html)
        
        st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)
        st.markdown(
            f"""
            <div style='background: linear-gradient(135deg, rgba(255, 75, 75, 0.15) 0%, rgba(255, 0, 0, 0.05) 100%); 
                        border: 1px solid #FF4B4B; padding: 15px 20px; border-radius: 12px; margin-bottom: 10px; 
                        box-shadow: 0 0 15px rgba(255, 75, 75, 0.2);'>
                <div style='color: #FF4B4B; font-weight: bold; font-size: 1.1rem; margin-bottom: 10px; font-family: Kanit, sans-serif;'>
                    🚨 คุณ {username} ครับ! ยังมีคู่แข่งขันที่ยังไม่ได้ทายผลอีก {len(st.session_state.unpredicted_matches)} คู่:
                </div>
                <div style='color: #e2e8f0; font-size: 0.95rem; font-family: Kanit, sans-serif; padding-left: 10px;'>
                    {matches_html}
                </div>
                <div style='color: #a0aec0; font-size: 0.85rem; margin-top: 10px; font-style: italic;'>
                    *กรุณากรอกผลและกด \"บันทึกผลทาย\" ด้านล่างก่อนเวลาเตะเพื่อป้องกันการเสียแต้มสะสม
                </div>
            </div>
            """, 
            unsafe_allow_html=True
        )
    # ระบบแสดงข้อมูลทำเนียบผู้นำเฉพาะผู้เล่นที่มีคะแนนสะสมมากกว่า 0 ขึ้นมาทันที
    try:
        leaderboard_df = db.get_leaderboard()
        # กรองเฉพาะผู้เล่นที่มีคะแนนมากกว่า 0 คะแนนเท่านั้น
        leaderboard_df = leaderboard_df[leaderboard_df['total_score'] > 0]
        
        if not leaderboard_df.empty:
            top_3 = leaderboard_df.head(3)
            leaders_list = []
            for idx, (_, row) in enumerate(top_3.iterrows(), 1):
                medal = "🥇" if idx == 1 else ("🥈" if idx == 2 else "🥉")
                leaders_list.append(f"{medal} <b>{row['username']}</b> ({int(row['total_score'])} แต้ม)")
            
            leaders_html = " &nbsp;&nbsp;|&nbsp;&nbsp; ".join(leaders_list)
            
            # เพิ่มระยะห่างไม่ให้เบียดชิดกับป้ายแบนเนอร์ CRAZYFIFA 2026 หัวข้อหลักด้านบน
            st.markdown("<div style='height: 35px;'></div>", unsafe_allow_html=True)
            
            # เรนเดอร์กล่องแสดงทำเนียบผู้เล่น Top 3 แบบเรียบง่ายขนาดกะทัดรัด (ไม่ต้องคลิกเปิด)
            st.markdown(
                f"""
                <div style='background: rgba(255, 215, 0, 0.05); border: 1px solid rgba(255, 215, 0, 0.2); 
                            padding: 10px 20px; border-radius: 12px; text-align: center; margin-bottom: 25px;'>
                    <span style='color: #FFD700; font-weight: bold; font-size: 0.95rem; margin-right: 15px; font-family: Kanit, sans-serif;'>🔥 3 อันดับผู้นำท็อปฟอร์ม:</span>
                    <span style='color: #e2e8f0; font-size: 0.95rem; font-family: Kanit, sans-serif;'>{leaders_html}</span>
                </div>
                """, 
                unsafe_allow_html=True
            )
    except Exception as e:
        pass

    # 🎙️ เพิ่มบอร์ดวิเคราะห์วิจารณ์บอลโลกประจำวันโดย "ปีเตอร์ AI" (Glassmorphism AI Analyst Board)
    try:
        # อิมพอร์ต ai_analyst ท้องถิ่นเพื่อรันงาน
        import importlib
        import ai_analyst
        importlib.reload(ai_analyst)
        
        # ดึงสถานะชื่อผู้ใช้
        current_username = username
        is_admin = (current_username == "Art")
        
        # จัดตั้งตัวแปรส่งสัญญาณ Force Refresh
        force_ai = False
        if is_admin:
            # วาง Marker นำทางและแต่งปุ่มแอดมินให้คลิกได้ลื่นไหล 100%
            st.markdown("<span class='force-ai-marker'></span>", unsafe_allow_html=True)
            if st.button("🔄 ปลุกพลังปีเตอร์ AI วิเคราะห์ข้อมูลใหม่ (Admin Only)", key="btn_force_ai"):
                force_ai = True
                
        # ดึงบทสรุปและจัดการแคชอัตโนมัติ
        predictions_df_for_ai = db.get_predictions_df()
        current_matches_for_ai = db.get_matches()
        
        ai_report, model_used, is_cached = ai_analyst.get_ai_summary(
            leaderboard_df if 'leaderboard_df' in locals() else db.get_leaderboard(), 
            current_matches_for_ai, 
            predictions_df_for_ai, 
            force_refresh=force_ai
        )
        
        if ai_report:
            # กำหนดป้ายแสดงสถานะ (Badge Text) สำหรับแอดมินและผู้ใช้งานทั่วไปเพื่อความสวยงามเป็นส่วนตัว
            if is_admin:
                badge_text = f"🤖 {model_used} {'(จากแคช)' if is_cached else '(คำนวณใหม่)'}"
            else:
                badge_text = "🟢 ปีเตอร์ AI วิเคราะห์ล่าสุด"

            # ใช้ Glassmorphism CSS สไตล์พรีเมี่ยม
            st.markdown(
                f"""
                <style>
                /* ดันปุ่มสั่งรัน AI ของแอดมินให้ลอยขึ้นชั้นบนสุดเพื่อแก้ปัญหากล่องล่างบังปุ่มคลิกยาก */
                div[data-testid="element-container"]:has(.force-ai-marker) + div[data-testid="element-container"] {{
                    position: relative !important;
                    z-index: 9999 !important;
                    margin-bottom: 12px !important;
                }}
                div[data-testid="element-container"]:has(.force-ai-marker) + div[data-testid="element-container"] button {{
                    pointer-events: auto !important;
                    cursor: pointer !important;
                    z-index: 10000 !important;
                }}
                .peter-ai-box {{
                    background: linear-gradient(135deg, rgba(45, 58, 49, 0.4) 0%, rgba(26, 36, 30, 0.5) 100%);
                    border: 1px solid rgba(255, 215, 0, 0.25);
                    padding: 22px 26px;
                    border-radius: 16px;
                    margin-bottom: 25px;
                    box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.35);
                    backdrop-filter: blur(8px);
                    -webkit-backdrop-filter: blur(8px);
                    font-family: 'Kanit', sans-serif;
                    position: relative;
                    overflow: hidden;
                }}
                .peter-ai-header {{
                    display: flex;
                    align-items: center;
                    justify-content: space-between;
                    margin-bottom: 12px;
                    border-bottom: 1px solid rgba(255, 215, 0, 0.15);
                    padding-bottom: 10px;
                }}
                .peter-ai-title {{
                    color: #FFD700;
                    font-weight: 600;
                    font-size: 1.15rem;
                    display: flex;
                    align-items: center;
                    gap: 8px;
                }}
                .peter-ai-badge {{
                    background: rgba(255, 215, 0, 0.12);
                    color: #FFD700;
                    font-size: 0.72rem;
                    padding: 3px 10px;
                    border-radius: 20px;
                    font-family: 'Kanit', sans-serif, monospace;
                    border: 1px solid rgba(255, 215, 0, 0.2);
                }}
                .peter-ai-content {{
                    color: #e2e8f0;
                    font-size: 0.95rem;
                    line-height: 1.6;
                }}
                </style>
                <div class="peter-ai-box">
                    <div class="peter-ai-header">
                        <div class="peter-ai-title">🎙️ ปีเตอร์ AI สรุปวิเคราะห์และวิจารณ์ประจำวัน</div>
                        <div class="peter-ai-badge">{badge_text}</div>
                    </div>
                """,
                unsafe_allow_html=True
            )
            # ปรับแต่งคำทักทายแบบ Dynamic ตามชื่อผู้ใช้ที่ล็อกอินจริงใน Session (เซสชัน: ช่วงเวลาการใช้งานของผู้ใช้)
            personalized_report = ai_report
            if "{USERNAME}" in personalized_report:
                personalized_report = personalized_report.replace("{USERNAME}", current_username)
            else:
                # รองรับการแทนที่คำทักทายแบบเก่า (Static) เผื่อในไฟล์แคชเก่ายังไม่มีตัวแปร {USERNAME} เพื่อให้ทำงานได้ทันทีโดยไม่ต้องรอแอดมินล้างแคช
                for old_greet in ["คุณอาร์ตและผองเพื่อน", "คุณอาร์ตและเหล่านักล่าแต้มทุกคน", "คุณอาร์ตและเหล่านักล่าแต้ม", "คุณอาร์ตและแก๊งผู้ร่วมทายผล", "คุณอาร์ต"]:
                    if old_greet in personalized_report:
                        # แทนที่คำทักทายด้วยชื่อของผู้ใช้ที่ล็อกอินจริง
                        personalized_report = personalized_report.replace(old_greet, f"คุณ {current_username} และเหล่านักล่าแต้มทุกคน")
                        break
            
            # ดำเนินการลบเครื่องหมายแบ็กทิกที่ครอบรอบคำสำคัญที่อาจหลงเหลือมาจากประวัติแคชเดิม
            for term in [
                "Leaderboard (ลีดเดอร์บอร์ด: ตารางคะแนนผู้นำ)", 
                "Daily MVP (เดลี เอ็มวีพี: ผู้ทำคะแนนหรือผลงานได้โดดเด่นสะดุดตาประจำวัน)",
                "Daily MVP (เดลี เอ็มวีพี: ผู้เล่นทำผลงานโดดเด่นประจำวัน)",
                "Perfect Prediction (เพอร์เฟกต์ พรีดิกชัน: การทายผลสกอร์ได้อย่างถูกต้องแม่นยำร้อยเปอร์เซ็นต์)"
            ]:
                personalized_report = personalized_report.replace(f"`{term}`", term)
            
            # ตกแต่งเสริมสีสันและไฮไลท์แบบไฮเอนด์ด้วยการตรวจจับประเด็น (Fallback High-end Highlights) สำหรับแคชเดิมที่ยังไม่มีโค้ดสี HTML ติดมาจากระบบหลังบ้าน
            personalized_report = personalized_report.replace(
                "Daily MVP (เดลี เอ็มวีพี: ผู้เล่นทำผลงานโดดเด่นประจำวัน)",
                "🏆 <span style='color: #00FF87; font-weight: bold; text-shadow: 0 0 10px rgba(0,255,135,0.15);'>วิเคราะห์ Daily MVP ประจำวัน</span>"
            ).replace(
                "Daily MVP (เดลี เอ็มวีพี: ผู้ทำคะแนนหรือผลงานได้โดดเด่นสะดุดตาประจำวัน)",
                "🏆 <span style='color: #00FF87; font-weight: bold; text-shadow: 0 0 10px rgba(0,255,135,0.15);'>วิเคราะห์ Daily MVP ประจำวัน</span>"
            ).replace(
                "Leaderboard (ลีดเดอร์บอร์ด: ตารางคะแนนผู้นำ)",
                "📊 <span style='color: #00E5FF; font-weight: bold; text-shadow: 0 0 10px rgba(0,229,255,0.15);'>ความเคลื่อนไหวบน Leaderboard</span>"
            ).replace(
                "Perfect Prediction (เพอร์เฟกต์ พรีดิกชัน: การทายผลสกอร์ได้อย่างถูกต้องแม่นยำร้อยเปอร์เซ็นต์)",
                "<span style='color: #FFD700; font-weight: bold;'>Perfect Prediction (เพอร์เฟกต์ พรีดิกชัน: การทายผลสกอร์ได้อย่างถูกต้องแม่นยำร้อยเปอร์เซ็นต์)</span>"
            )

            # แทรกขีดคั่นสวยงามแบบอัตโนมัติหากพบหัวข้อย่อยแบบเดิมเพื่อแบ่งสัดส่วนบอร์ดไม่ให้อ่านยาก
            for old_section in ["ตำแหน่ง Daily MVP", "สถานการณ์บน Leaderboard", "คืนนี้เตรียมตัวรับแรงกระแทก", "แมตช์ต่อไปที่กำลังจะมาถึง"]:
                if old_section in personalized_report:
                    personalized_report = personalized_report.replace(
                        old_section,
                        f"<hr style='border: 0; border-top: 1px solid rgba(255, 215, 0, 0.08); margin: 12px 0;'>{old_section}"
                    )

            # ตกแต่งรายชื่อคู่แข่งขันเปลี่ยนชีวิตของคืนนี้ให้เรืองแสงส้มสะดุดตาโดดเด่น
            for tonight_match in ["Portugal พบ Uzbekistan", "England ดวลเดือด Ghana"]:
                if tonight_match in personalized_report:
                    personalized_report = personalized_report.replace(
                        tonight_match,
                        f"<span style='background: rgba(255, 94, 54, 0.12); color: #FF5E36; border: 1px solid rgba(255, 94, 54, 0.25); padding: 2px 8px; border-radius: 6px; font-weight: bold;'>🔥 {tonight_match}</span>"
                    )

            # ดำเนินการคลีนแบ็กทิก (Backticks Strip) ที่อาจครอบรอบแท็ก HTML ทั้งหมดออกไปเพื่อป้องกัน Markdown เอสเคปคีย์
            # เช่น `📊 <span ...>...</span>` -> 📊 <span ...>...</span>
            import re
            personalized_report = re.sub(r'`([^`]*<[^`]+>[^`]*)`', r'\1', personalized_report)

            # แสดงเนื้อหาบทสรุปเป็น markdown เพื่อประมวลผลข้อความและ HTML ให้สวยงาม
            st.markdown(personalized_report, unsafe_allow_html=True)
            
            # ปิดกล่อง HTML
            st.markdown("</div>", unsafe_allow_html=True)
            if force_ai:
                st.success("🔄 ปลดล็อกพลังปีเตอร์และเขียนสรุปบทวิเคราะห์ใหม่สำเร็จเรียบร้อยครับ!")
    except Exception as e_ai:
        # ใช้ Try-Except ครอบโครงสร้าง AI ทั้งหมดเพื่อความปลอดภัย 100% ต่อระบบ
        pass

    all_matches = db.get_matches()
    all_matches['match_dt'] = pd.to_datetime(all_matches['match_time'])

    # ดึงผลทำนายของผู้เล่นในครั้งเดียวที่นี่! เพื่อประหยัดการเชื่อมต่อ API ของ Google Sheets (Quota Saving)
    try:
        user_preds_cached = db.get_user_predictions(username)
    except Exception as e:
        user_preds_cached = {}

    def render_match(row, username):
        match_id = safe_int(row['id'])
        home = row['home_team']
        away = row['away_team']
        home_display = get_team_display(home)
        away_display = get_team_display(away)

        # แปลงเวลาเตะอย่างยืดหยุ่นและปลอดภัยจากประเภทข้อมูล Timestamp/String
        m_time = row['match_dt'] if 'match_dt' in row and pd.notnull(row['match_dt']) else pd.to_datetime(row['match_time'])
        if not isinstance(m_time, datetime):
            m_time = m_time.to_pydatetime()
        status = row['status']
        now_th = datetime.now(timezone(timedelta(hours=7))).replace(tzinfo=None)
        is_locked = now_th > m_time or status == 'Finished'

        has_pred = match_id in user_preds_cached
        default_h, default_a = user_preds_cached.get(match_id, (0, 0))
        
        # กำหนดคะแนนที่จะแสดงในช่องกรอก (ถ้าเกมจบแล้ว ให้แสดงสกอร์จริงในช่องที่ปิดการแก้ไข)
        if status == 'Finished':
            val_h = safe_int(row['home_score'])
            val_a = safe_int(row['away_score'])
        else:
            val_h = safe_int(default_h)
            val_a = safe_int(default_a)

        # ใช้ Hybrid Form-Container: 
        # หากไม่โดนล็อก (สามารถทายผลได้) ให้ครอบด้วย st.form เพื่อป้องกันหน้าจอ Rerun ทันทีขณะเปลี่ยนค่าตัวเลข
        if not is_locked:
            with st.form(key=f"form_match_{match_id}", clear_on_submit=False):
                # แถวแรก: แสดงคู่แข่งขันและเวลาเตะตัวใหญ่สวยงามชัดเจน
                st.subheader(f"{home_display} 🆚 {away_display}")
                st.caption(f"⏰ เวลาเตะ: {m_time.strftime('%d/%m/%Y %H:%M')}")
                
                # แถวสอง: แสดงช่องกรอกคะแนนของทั้งสองทีมพร้อมปุ่มบันทึกผล
                col1, col2, col3 = st.columns([3, 3, 2])
                with col1:
                    pred_h = st.number_input(
                        label="⚽ สกอร์ทีมเหย้า",
                        min_value=0,
                        step=1,
                        value=val_h,
                        key=f"h_{match_id}"
                    )
                with col2:
                    pred_a = st.number_input(
                        label="⚽ สกอร์ทีมเยือน",
                        min_value=0,
                        step=1,
                        value=val_a,
                        key=f"a_{match_id}"
                    )
                with col3:
                    st.markdown("<div class='desktop-spacer' style='height: 28px;'></div>", unsafe_allow_html=True)
                    if has_pred:
                        btn_label = "✅ บันทึกแล้ว (แก้ไข)"
                        btn_type = "primary"
                    else:
                        btn_label = "บันทึกผลทาย"
                        btn_type = "secondary"
                        
                    # ใช้ปุ่ม st.form_submit_button แทน st.button สำหรับส่วนประกอบภายใน st.form
                    if st.form_submit_button(btn_label, use_container_width=True, type=btn_type):
                        db.save_prediction(username, match_id, pred_h, pred_a)
                        st.toast(f"⚽ บันทึกผลทาย {home_display} vs {away_display} เรียบร้อยแล้ว!")
                        # บังคับให้หน้าจอ Rerun ทันทีหลังกดส่ง เพื่อแสดงปุ่มติ๊กถูก
                        st.rerun()
                        
                    if has_pred:
                        st.markdown("<div style='color: #4CAF50; font-size: 0.95rem; font-weight: bold; margin-top: 6px; text-align: center;'>✅ บันทึกผลทายแล้ว</div>", unsafe_allow_html=True)
        else:
            # หากโดนล็อกแล้ว (ปิดรับทายหรือเกมแข่งจบแล้ว) เรนเดอร์แบบธรรมดาด้วย st.container() โดยไม่ต้องใช้ st.form()
            with st.container():
                st.subheader(f"{home_display} 🆚 {away_display}")
                st.caption(f"⏰ เวลาเตะ: {m_time.strftime('%d/%m/%Y %H:%M')}")
                
                col1, col2, col3 = st.columns([3, 3, 2])
                with col1:
                    st.number_input(
                        label="⚽ สกอร์ทีมเหย้า",
                        min_value=0,
                        step=1,
                        value=val_h,
                        key=f"h_{match_id}",
                        disabled=True
                    )
                with col2:
                    st.number_input(
                        label="⚽ สกอร์ทีมเยือน",
                        min_value=0,
                        step=1,
                        value=val_a,
                        key=f"a_{match_id}",
                        disabled=True
                    )
                with col3:
                    st.markdown("<div class='desktop-spacer' style='height: 28px;'></div>", unsafe_allow_html=True)
                    if status == 'Finished':
                        st.warning("🏁 สิ้นสุดการแข่งขัน")
                        h_score_val = safe_int(row['home_score'])
                        a_score_val = safe_int(row['away_score'])
                        winner_name = home if h_score_val > a_score_val else (away if a_score_val > h_score_val else "เสมอ")
                        winner_display = get_team_display(winner_name) if winner_name != "เสมอ" else "เสมอ"
                        st.info(f"🏆 **ชนะ:** {winner_display} ({h_score_val}-{a_score_val})")
                        if row['scorers']: st.caption(f"⚽ **คนยิง:** {row['scorers']}")
                        if has_pred:
                            st.info(f"🎯 **คุณทายผลไว้:** {safe_int(default_h)} - {safe_int(default_a)}")
                        else:
                            st.info("🎯 **คุณไม่ได้ทายคู่นี้ไว้**")
                    else:
                        st.warning("🔒 ปิดรับผลทาย")
        st.divider()

    finished = all_matches[all_matches['status'] == 'Finished'].sort_values('match_time', ascending=False)
    if not finished.empty:
        with st.expander("🏁 ดูผลการแข่งขันนัดก่อนหน้าที่สิ้นสุดลงแล้ว (คลิกเพื่อขยายดู)"):
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
                
            fifa_label = ""
            if d.strftime('%d/%m/%Y') == "24/06/2026":
                fifa_label = " 🇺🇸 (ตรงกับโปรแกรมฟีฟ่าวันที่ 23 มิ.ย.)"
            elif d.strftime('%d/%m/%Y') == "25/06/2026":
                fifa_label = " 🇺🇸 (ตรงกับโปรแกรมฟีฟ่าวันที่ 24 มิ.ย.)"
            elif d.strftime('%d/%m/%Y') == "26/06/2026":
                fifa_label = " 🇺🇸 (ตรงกับโปรแกรมฟีฟ่าวันที่ 25 มิ.ย.)"
                
            st.markdown(f"### <span class='bouncing-icon'>⚽</span> ตารางแข่งขันวันที่ {d.strftime('%d/%m/%Y')}{label_suffix}{fifa_label}", unsafe_allow_html=True)
            day_matches = upcoming[upcoming['match_dt'].dt.date == d]
            for _, row in day_matches.iterrows():
                render_match(row, username)
    else:
        st.info("ไม่มีการแข่งขันที่กำลังจะมาถึงในขณะนี้ครับ")

# 3. หน้าผลการแข่งขันย้อนหลัง
elif menu == "📜 ผลการแข่งขันย้อนหลัง (Match Results)":
    st.header("📜 ผลการแข่งขันย้อนหลังทั้งหมด")
    st.info("💡 รวบรวมข้อมูลผลสกอร์และรายชื่อผู้ทำประตูในทุกแมตช์ที่จบการแข่งขันแล้ว")
    st.markdown("---")
    
    all_matches = db.get_matches()
    finished = all_matches[all_matches['status'] == 'Finished'].sort_values('match_time', ascending=False)
    
    if finished.empty:
        st.info("ยังไม่มีการแข่งขันใดที่สิ้นสุดลงในขณะนี้ครับ")
    else:
        # จัดกลุ่มการแข่งขันย้อนหลังตามวันที่เตะเพื่อความเป็นระเบียบและให้เปิดดูง่าย
        finished['match_dt'] = pd.to_datetime(finished['match_time'])
        unique_dates = finished['match_dt'].dt.date.unique()
        
        for d in unique_dates:
            st.subheader(f"🗓️ วันที่ {d.strftime('%d/%m/%Y')}")
            day_matches = finished[finished['match_dt'].dt.date == d]
            
            for _, row in day_matches.iterrows():
                home = row['home_team']
                away = row['away_team']
                home_display = get_team_display(home)
                away_display = get_team_display(away)
                h_score = safe_int(row['home_score'])
                a_score = safe_int(row['away_score'])
                
                expander_label = f"⚽ {home_display}  {h_score} - {a_score}  {away_display}"
                
                with st.expander(expander_label):
                    st.markdown(f"### 🏟️ {home_display} vs {away_display}")
                    st.write(f"🗓️ **เวลาแข่งขัน:** {pd.to_datetime(row['match_time']).strftime('%d/%m/%Y %H:%M น.')}")
                    
                    winner_name = home if h_score > a_score else (away if a_score > h_score else "เสมอ")
                    winner_display = get_team_display(winner_name) if winner_name != "เสมอ" else "เสมอ"
                    st.write(f"🏆 **ผลการแข่งขัน:** {winner_display}")
                    
                    st.markdown("---")
                    st.markdown("⚽ **รายชื่อผู้ยิงประตู:**")
                    if row['scorers'] and row['scorers'].strip() != "":
                        scorers_list = [s.strip() for s in row['scorers'].split(',')]
                        for s in scorers_list:
                            st.write(f"- {s}")
                    else:
                        st.write("ไม่มีข้อมูลการยิงประตู")
            st.divider()

elif menu == "🏅 ตารางคะแนนกลุ่ม (Standings)":
    st.header("🏅 ตารางคะแนนแบ่งกลุ่มศึกฟุตบอลโลก 2026")
    st.info("💡 **กฎการเข้ารอบน็อกเอาต์ (รอบ 32 ทีมสุดท้าย):**\n- 🟢 อันดับ 1 และ 2 ของทุกกลุ่ม (A ถึง L) เข้ารอบโดยอัตโนมัติ (รวม 24 ทีม)\n- 🟡 ทีมอันดับ 3 ที่มีผลงานดีที่สุด 8 ทีม จากทั้ง 12 กลุ่ม จะได้รับตั๋วเข้ารอบเช่นกัน!")
    st.markdown("---")
    
    # ดึงข้อมูลตารางคะแนนจากหลังบ้าน
    with st.spinner("🔄 กำลังดึงตารางคะแนนเรียลไทม์จากระบบสากล..."):
        standings = db.get_world_cup_standings()
        
    if not standings:
        st.error("⚠️ ไม่สามารถดึงข้อมูลตารางคะแนนได้ในขณะนี้ กรุณาลองใหม่อีกครั้ง")
    else:
        # แทรก CSS สำหรับแต่งตารางให้พรีเมี่ยม
        st.markdown("""
        <style>
        .standings-table {
            width: 100%;
            border-collapse: collapse;
            background: rgba(30, 45, 36, 0.3) !important;
            border-radius: 8px !important;
            overflow: hidden !important;
            color: #e0e6ed !important;
            font-family: 'Kanit', sans-serif !important;
            margin-bottom: 5px !important;
        }
        .standings-table th {
            background: rgba(20, 32, 24, 0.85) !important;
            color: #ffd700 !important;
            font-weight: 600 !important;
            padding: 8px 2px !important;
            text-align: center !important;
            border-bottom: 2px solid rgba(255, 215, 0, 0.15) !important;
            font-size: 0.76rem !important;
            line-height: 1.25 !important;
            white-space: nowrap !important; /* บังคับตัวหนังสือหัวข้อเรียงบรรทัดเดียวกัน ห้ามแตกตัวแนวตั้ง */
        }
        .standings-table td {
            padding: 8px 4px !important;
            text-align: center !important;
            border-bottom: 1px solid rgba(255, 255, 255, 0.05) !important;
            font-size: 0.84rem !important;
        }
        .standings-table tr:hover {
            background-color: rgba(255, 215, 0, 0.08) !important;
        }
        .standings-table .team-cell {
            text-align: left !important;
            font-weight: 500 !important;
            color: #ffffff !important;
            padding-left: 10px !important;
        }
        .standings-table .qualified-glow {
            background: rgba(46, 204, 113, 0.08) !important;
            border-left: 4px solid #2ecc71 !important;
        }
        .standings-table .qualified-warning {
            background: rgba(241, 196, 15, 0.05) !important;
            border-left: 4px solid #f1c40f !important;
        }
        .standings-table .pts-cell {
            font-weight: bold !important;
            color: #ffd700 !important;
        }
        /* ตกแต่งการ์ดตารางเปรียบเทียบอันดับ 3 เป็นกรอบทองเรืองแสงหรูหราพรีเมียม */
        .third-placed-gold-card {
            background: linear-gradient(180deg, rgba(255, 215, 0, 0.04) 0%, rgba(15, 23, 18, 0.65) 100%) !important;
            padding: 20px !important;
            border-radius: 16px !important;
            border: 2.2px solid #ffd700 !important; /* ขอบทองคำสว่างชัดเจน */
            margin-bottom: 25px !important;
            overflow-x: auto !important;
            /* เงาเรืองแสงสีทองพรีเมียมแบบมีมิติไล่ระดับชั้นลึกตระการตา */
            box-shadow: 0 8px 32px rgba(255, 215, 0, 0.15), inset 0 0 15px rgba(255, 215, 0, 0.08) !important;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        }
        .third-placed-gold-card:hover {
            border-color: #ffe066 !important; /* ทองสว่างขึ้นเมื่อเมาส์ชี้ผ่าน */
            box-shadow: 0 12px 40px rgba(255, 215, 0, 0.28), inset 0 0 20px rgba(255, 215, 0, 0.15) !important;
            transform: translateY(-2px) !important;
        }
        
        /* ตกแต่งการ์ดตารางกลุ่มปกติ (A-L) ให้ดูเป็นระเบียบสวยงาม */
        .normal-table-card {
            background: rgba(15, 23, 18, 0.55) !important;
            padding: 15px !important;
            border-radius: 12px !important;
            border: 1px solid rgba(255, 215, 0, 0.1) !important;
            margin-bottom: 20px !important;
            overflow-x: auto !important;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2) !important;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        }
        .normal-table-card:hover {
            border-color: rgba(255, 215, 0, 0.25) !important;
            box-shadow: 0 6px 20px rgba(255, 215, 0, 0.05) !important;
            transform: translateY(-1px) !important;
        }
        </style>
        """, unsafe_allow_html=True)
        
        # สร้างฟังก์ชันวาดตาราง HTML ในบล็อกนี้เพื่อความง่ายและปลอดภัย
        def render_html_table(df, title, is_third_placed=False):
            team_width = "25%" if is_third_placed else "33%"
            wrapper_class = "third-placed-gold-card" if is_third_placed else "normal-table-card"
            html_code = f"""<div class='{wrapper_class}'>
<h4 style='color: #ffd700; margin-top: 0; margin-bottom: 12px; font-family: "Kanit", sans-serif; display: flex; align-items: center; gap: 8px;'>🏆 {title}</h4>
<table class='standings-table' style='width: 100%; table-layout: fixed;'>
<thead>
<tr>
<th style='width: 7%;'>อันดับ<br><span style='font-size: 0.66rem; opacity: 0.75; font-weight: normal;'>Pos</span></th>
{"<th style='width: 8%;'>กลุ่ม<br><span style='font-size: 0.66rem; opacity: 0.75; font-weight: normal;'>Grp</span></th>" if is_third_placed else ""}
<th style='text-align: left; width: {team_width}; padding-left: 10px;'>ทีมชาติ<br><span style='font-size: 0.66rem; opacity: 0.75; font-weight: normal;'>Team</span></th>
<th style='width: 7%;'>แข่ง<br><span style='font-size: 0.66rem; opacity: 0.75; font-weight: normal;'>Pld</span></th>
<th style='width: 7%;'>ชนะ<br><span style='font-size: 0.66rem; opacity: 0.75; font-weight: normal;'>W</span></th>
<th style='width: 7%;'>เสมอ<br><span style='font-size: 0.66rem; opacity: 0.75; font-weight: normal;'>D</span></th>
<th style='width: 7%;'>แพ้<br><span style='font-size: 0.66rem; opacity: 0.75; font-weight: normal;'>L</span></th>
<th style='width: 7%;'>ได้<br><span style='font-size: 0.66rem; opacity: 0.75; font-weight: normal;'>GF</span></th>
<th style='width: 7%;'>เสีย<br><span style='font-size: 0.66rem; opacity: 0.75; font-weight: normal;'>GA</span></th>
<th style='width: 8%;'>+/-<br><span style='font-size: 0.66rem; opacity: 0.75; font-weight: normal;'>GD</span></th>
<th style='width: 10%;'>แต้ม<br><span style='font-size: 0.66rem; opacity: 0.75; font-weight: normal;'>Pts</span></th>
</tr>
</thead>
<tbody>"""
            
            for idx, row in df.iterrows():
                pos = str(row['Pos']).strip()
                team_name = str(row['Team']).strip()
                team_display = get_team_display(team_name)
                
                # แยกธงและชื่อชาติเพื่อจัดระเบียบ UI ให้ไม่มีปัญหารอยต่อและการตัดบรรทัดใหม่
                parts = team_display.split(" ", 1)
                if len(parts) == 2:
                    flag_emoji, clean_thai_name = parts[0], parts[1]
                else:
                    flag_emoji, clean_thai_name = "🏳️", team_display
                
                # ตกแต่งแถวตามสถานการณ์เข้ารอบ
                row_class = ""
                badge = ""
                if is_third_placed:
                    try:
                        pos_num = int(pos)
                        if pos_num <= 8:
                            row_class = "qualified-glow"
                            badge = " <span style='color: #2ecc71; font-size: 0.72rem; font-weight: bold; margin-left: auto; padding-left: 5px; white-space: nowrap;'>[เข้ารอบ]</span>"
                        else:
                            row_class = ""
                            badge = " <span style='color: #e74c3c; font-size: 0.72rem; font-weight: bold; margin-left: auto; padding-left: 5px; white-space: nowrap;'>[ตกรอบ]</span>"
                    except:
                        pass
                else:
                    if pos == "1" or pos == "2":
                        row_class = "qualified-glow"
                        badge = " <span style='color: #2ecc71; font-size: 0.72rem; font-weight: bold; margin-left: auto; padding-left: 5px; white-space: nowrap;'>[เข้ารอบ]</span>"
                    elif pos == "3":
                        row_class = "qualified-warning"
                        badge = " <span style='color: #f1c40f; font-size: 0.72rem; font-weight: bold; margin-left: auto; padding-left: 5px; white-space: nowrap;'>[ลุ้นอันดับ 3]</span>"
                    else:
                        row_class = ""
                        badge = ""
                        
                html_code += f"<tr class='{row_class}'>"
                html_code += f"<td><b>{pos}</b></td>"
                if is_third_placed:
                    grp = str(row.get('Grp', '')).strip()
                    html_code += f"<td><span style='background: rgba(255,255,255,0.1); padding: 2px 6px; border-radius: 4px; font-size: 0.75rem;'><b>{grp}</b></span></td>"
                    
                html_code += f"""<td class='team-cell'>
<div style='display: flex; align-items: center; gap: 6px; white-space: nowrap; overflow: hidden;'>
<span style='font-size: 1.15rem; filter: drop-shadow(0 2px 4px rgba(0,0,0,0.3)); line-height: 1; display: inline-block;'>{flag_emoji}</span>
<span style='font-weight: 500; text-overflow: ellipsis; overflow: hidden; white-space: nowrap;' title='{clean_thai_name}'>{clean_thai_name}</span>
{badge}
</div>
</td>"""
                html_code += f"<td>{row['Pld']}</td>"
                html_code += f"<td>{row['W']}</td>"
                html_code += f"<td>{row['D']}</td>"
                html_code += f"<td>{row['L']}</td>"
                html_code += f"<td>{row['GF']}</td>"
                html_code += f"<td>{row['GA']}</td>"
                
                # ตกแต่งสีสันของผลต่างประตูได้เสีย (+ เป็นเขียว, - เป็นแดง)
                gd = str(row['GD']).strip()
                gd_style = "color: #e0e6ed;"
                if gd.startswith('+'):
                    gd_style = "color: #2ecc71; font-weight: bold;"
                elif gd.startswith('-') or gd.startswith('−'):
                    gd_style = "color: #e74c3c; font-weight: bold;"
                html_code += f"<td><span style='{gd_style}'>{gd}</span></td>"
                
                html_code += f"<td class='pts-cell'>{row['Pts']}</td>"
                html_code += f"</tr>"
                
            html_code += """</tbody></table></div>"""
            return html_code

        # สร้างแท็บย่อยสลับดูตารางคะแนนแบบสวยงาม
        t1, t2, t3, t4 = st.tabs(["🔥 กลุ่ม A - D", "⚡ กลุ่ม E - H", "🌟 กลุ่ม I - L", "🏅 ทีมอันดับ 3 ที่ดีที่สุด"])
        
        with t1:
            col1, col2 = st.columns(2)
            with col1:
                if "Group A" in standings:
                    st.markdown(render_html_table(standings["Group A"], "กลุ่ม A"), unsafe_allow_html=True)
                if "Group C" in standings:
                    st.markdown(render_html_table(standings["Group C"], "กลุ่ม C"), unsafe_allow_html=True)
            with col2:
                if "Group B" in standings:
                    st.markdown(render_html_table(standings["Group B"], "กลุ่ม B"), unsafe_allow_html=True)
                if "Group D" in standings:
                    st.markdown(render_html_table(standings["Group D"], "กลุ่ม D"), unsafe_allow_html=True)
                    
        with t2:
            col1, col2 = st.columns(2)
            with col1:
                if "Group E" in standings:
                    st.markdown(render_html_table(standings["Group E"], "กลุ่ม E"), unsafe_allow_html=True)
                if "Group G" in standings:
                    st.markdown(render_html_table(standings["Group G"], "กลุ่ม G"), unsafe_allow_html=True)
            with col2:
                if "Group F" in standings:
                    st.markdown(render_html_table(standings["Group F"], "กลุ่ม F"), unsafe_allow_html=True)
                if "Group H" in standings:
                    st.markdown(render_html_table(standings["Group H"], "กลุ่ม H"), unsafe_allow_html=True)
                    
        with t3:
            col1, col2 = st.columns(2)
            with col1:
                if "Group I" in standings:
                    st.markdown(render_html_table(standings["Group I"], "กลุ่ม I"), unsafe_allow_html=True)
                if "Group K" in standings:
                    st.markdown(render_html_table(standings["Group K"], "กลุ่ม K"), unsafe_allow_html=True)
            with col2:
                if "Group J" in standings:
                    st.markdown(render_html_table(standings["Group J"], "กลุ่ม J"), unsafe_allow_html=True)
                if "Group L" in standings:
                    st.markdown(render_html_table(standings["Group L"], "กลุ่ม L"), unsafe_allow_html=True)
                    
        with t4:
            if "Third-placed" in standings:
                st.markdown(render_html_table(standings["Third-placed"], "ตารางเปรียบเทียบอันดับ 3 (คัดเลือก 8 ทีมที่ดีที่สุดเข้ารอบ)", is_third_placed=True), unsafe_allow_html=True)
            else:
                st.info("ยังไม่มีข้อมูลการเปรียบเทียบทีมอันดับ 3 ในขณะนี้")

# 4. หน้า Leaderboard
elif menu == "🏆 ทำเนียบแชมป์ (Leaderboard)":
    st.header("🏆 ทำเนียบยอดนักทายผล")
    st.info("💡 **กฎการให้คะแนน:**\n- ✅ ทายถูกฝั่ง: 1 คะแนน\n- 🎯 ทายถูกเป๊ะ (รวมเสมอ): 3 คะแนน\n- ❌ ทายผิด: 0 คะแนน")
    st.markdown("---")
    st.subheader("🌟 อันดับเกียรติยศสะสมรวม")
    leaderboard = db.get_leaderboard()
    if not leaderboard.empty:
        # หาคะแนนสะสมสูงสุดเรียงตามลำดับ (Unique Scores) เพื่อมอบรางวัลเหรียญทอง เงิน และทองแดงตามลำดับ
        top_scores = sorted(leaderboard['total_score'].unique(), reverse=True)
        gold_score = top_scores[0] if len(top_scores) > 0 else -1
        silver_score = top_scores[1] if len(top_scores) > 1 else -1
        bronze_score = top_scores[2] if len(top_scores) > 2 else -1
        
        leaderboard['อันดับ'] = range(1, len(leaderboard) + 1)
        def add_gimmick(row):
            score = row['total_score']
            username = row['username']
            if score > 0:
                if score == gold_score:
                    return f"👑 {username} 🥇"
                elif score == silver_score:
                    return f"⭐️ {username} 🥈"
                elif score == bronze_score:
                    return f"✨ {username} 🥉"
            return f"👤 {username}"
        
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

# 5. หน้าประวัติการทายผล (แยกออกมาตามคำปรึกษาคุณอาร์ต)
elif menu == "📑 ประวัติการทายผล (My Predictions)":
    st.header("📑 ประวัติการทายผลการแข่งขัน")
    
    # 🎨 แทรก CSS (ซีเอสเอส: ภาษาที่ใช้ในการกำหนดรูปแบบการแสดงผลของหน้าเว็บ) เพื่อตกแต่งกรอบและการไฮไลท์แบบพรีเมียม
    st.markdown("""
        <style>
        /* ================================================================= */
        /* 0. ตกแต่งหัวข้อแท็บย่อย (st.tabs) ให้มีขอบมนและไฮไลท์กรอบเรืองแสงหรูหรา */
        /* ================================================================= */
        /* สั่งให้โครงสร้างแท็บทั้งหมดเปิดเผยเงาเรืองแสง ไม่โดนตัดขอบเป็นสี่เหลี่ยม */
        .stTabs, 
        div[data-testid="stTabs"],
        .stTabs [data-baseweb="tab-list"] {
            overflow: visible !important;
        }

        /* จัดระยะห่างของลิสต์แท็บให้สวยงาม และนำเส้นใต้พื้นหลังเดิมออก */
        .stTabs [data-baseweb="tab-list"] {
            gap: 12px !important;
            border-bottom: none !important; /* ปิดเส้นนอนใต้แท็บแบบเดิมถาวร */
            padding-bottom: 12px !important; /* เพิ่มช่องว่างด้านล่างเพื่อเว้นระยะห่าง */
        }

        /* ตกแต่งแท็บแต่ละอันในสถานะปกติ (Inactive) เป็นรูปทรงแคปซูลยาเม็ดพรีเมียม */
        .stTabs [data-baseweb="tab"] {
            border: 1.5px solid rgba(255, 255, 255, 0.15) !important;
            border-radius: 20px !important; /* ปรับเป็นขอบมนเต็มรูปแบบทรงแคปซูลลอยตัว */
            padding: 8px 24px !important;
            background-color: rgba(255, 255, 255, 0.02) !important;
            color: rgba(255, 255, 255, 0.6) !important;
            font-weight: 500 !important;
            font-size: 1.05rem !important;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        }

        /* เอฟเฟกต์โฮเวอร์ (Hover) ของปุ่มแท็บ */
        .stTabs [data-baseweb="tab"]:hover {
            color: #ffffff !important;
            border-color: rgba(255, 215, 0, 0.4) !important;
            background-color: rgba(255, 215, 0, 0.05) !important;
            box-shadow: 0 2px 8px rgba(255, 215, 0, 0.05) !important;
        }

        /* ตกแต่งแท็บเมื่อถูกคลิกเลือกใช้งาน (Active) ด้วยขอบทองสว่างรอบตัว 100% */
        .stTabs [aria-selected="true"] {
            color: #ffd700 !important; /* อักษรและไอคอนสีทอง */
            border: 2px solid #ffd700 !important; /* ขอบทองสว่างชัดรอบด้าน 100% ครบทุกด้าน */
            border-radius: 20px !important;
            background: linear-gradient(180deg, rgba(255, 215, 0, 0.15) 0%, rgba(255, 215, 0, 0.03) 100%) !important;
            font-weight: 700 !important;
            /* ใช้เงานอกบางเบาสลัว ร่วมกับเงาเรืองแสงด้านใน (inset) เพื่อให้แผ่ออร่าหรูหรามีมิติโดยไม่มีวันโดนตัดขอบเหลี่ยม */
            box-shadow: 0 2px 6px rgba(255, 215, 0, 0.12), inset 0 0 10px rgba(255, 215, 0, 0.25) !important;
        }

        /* ซ่อนขีดไฮไลท์สไตล์ดั้งเดิมเพื่อไม่ให้รบกวนขอบทองของเรา */
        div[data-baseweb="tab-highlight"] {
            background-color: transparent !important;
        }
        div[data-baseweb="tab-border"] {
            display: none !important;
        }

        /* ================================================================= */
        /* 1. ตกแต่งครอบการ์ดผลแข่งเสร็จแล้ว (Match Card Wrapper) ด้วยกรอบหนาเรืองแสง */
        /* ================================================================= */
        .match-card-wrapper {
            background-color: rgba(255, 255, 255, 0.02) !important;
            border: 1.5px solid rgba(255, 255, 255, 0.15) !important;
            border-radius: 14px !important;
            padding: 4px !important; /* เว้นระยะห่างรอบ expander เล็กน้อยให้เห็นกรอบโค้งเด่นชัด */
            margin-bottom: 16px !important;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.25) !important;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        }
        
        .match-card-wrapper:hover {
            border-color: rgba(255, 215, 0, 0.5) !important; /* เปลี่ยนเป็นสีทองเรืองแสงเมื่อเมาส์ชี้ผ่าน */
            box-shadow: 0 6px 22px rgba(255, 215, 0, 0.2) !important;
            background-color: rgba(255, 255, 255, 0.04) !important;
            transform: translateY(-2px);
        }
        
        /* ซ่อนกรอบเดิมของ st.expander เพื่อป้องกันกรอบซ้อนและขัดแย้งกันในแต่ละเบราว์เซอร์ */
        div[data-testid="stExpander"], div.stExpander, .streamlit-expander {
            background-color: transparent !important;
            border: none !important;
            margin-bottom: 0px !important;
            box-shadow: none !important;
        }
        
        /* ตกแต่งส่วนหัวของ expander (ปุ่มสรุปข้อมูลแมตช์) */
        div[data-testid="stExpander"] > details > summary,
        div.stExpander > details > summary,
        .streamlit-expander > details > summary {
            background-color: rgba(0, 0, 0, 0.2) !important;
            border-radius: 10px 10px 0 0 !important;
            padding: 14px 18px !important;
            color: #f8fafc !important;
            font-size: 1.05rem !important;
            font-weight: 600 !important;
            transition: color 0.2s ease !important;
        }
        
        div[data-testid="stExpander"] > details > summary:hover,
        div.stExpander > details > summary:hover,
        .streamlit-expander > details > summary:hover {
            color: #ffd700 !important; /* ตัวอักษรเปลี่ยนเป็นสีทองเมื่อโฮเวอร์ */
        }
        
        /* ตกแต่งเนื้อหาด้านในเมื่อขยาย expander ออกมา */
        div[data-testid="stExpander"] > details > div[role="region"],
        div.stExpander > details > div[role="region"],
        .streamlit-expander > details > div[role="region"] {
            padding: 20px !important;
            background-color: rgba(0, 0, 0, 0.25) !important;
            border-radius: 0 0 10px 10px !important;
        }

        /* ================================================================= */
        /* 2. ตกแต่งการ์ดผลทายล่วงหน้า (Upcoming Match Cards) ให้เด่นชัดพรีเมียม */
        /* ================================================================= */
        .upcoming-card {
            padding: 18px 22px;
            border-radius: 14px;
            margin-bottom: 15px;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            position: relative;
            box-sizing: border-box;
        }
        
        /* กรณีทายผลแล้ว: ดีไซน์สีฟ้าน้ำทะเล (Cyan/Aqua) */
        .upcoming-card.has-prediction {
            background: linear-gradient(135deg, rgba(0, 212, 255, 0.08) 0%, rgba(0, 150, 255, 0.03) 100%);
            border: 1.5px solid rgba(0, 212, 255, 0.35) !important;
            box-shadow: 0 4px 15px rgba(0, 212, 255, 0.05) !important;
        }
        
        .upcoming-card.has-prediction:hover {
            border-color: rgba(0, 212, 255, 0.75) !important;
            box-shadow: 0 6px 22px rgba(0, 212, 255, 0.2) !important;
            background: linear-gradient(135deg, rgba(0, 212, 255, 0.12) 0%, rgba(0, 150, 255, 0.05) 100%);
            transform: translateY(-2px);
        }
        
        /* กรณีที่ยังไม่ทายผล: ดีไซน์ขอบประสีส้มแดงเพื่อเตือนสายตา */
        .upcoming-card.no-prediction {
            background: linear-gradient(135deg, rgba(255, 107, 107, 0.05) 0%, rgba(255, 107, 107, 0.02) 100%);
            border: 1.5px dashed rgba(255, 107, 107, 0.45) !important;
            box-shadow: 0 4px 15px rgba(255, 107, 107, 0.02) !important;
        }
        
        .upcoming-card.no-prediction:hover {
            border-color: rgba(255, 107, 107, 0.8) !important;
            box-shadow: 0 6px 22px rgba(255, 107, 107, 0.15) !important;
            background: linear-gradient(135deg, rgba(255, 107, 107, 0.08) 0%, rgba(255, 107, 107, 0.04) 100%);
            transform: translateY(-2px);
        }
        </style>
    """, unsafe_allow_html=True)
    
    st.info("💡 เลือกดูสรุปผลการแข่งขันและการทายผลของเพื่อนๆ แยกตามวัน โดยคนที่ทายถูกเป๊ะได้รับ 3 แต้ม (สีทอง 🏆) และถูกฝั่งได้รับ 1 แต้ม (สีเขียว 🟢)")
    st.markdown("---")
    
    # ดึงข้อมูลแมตช์และคำทำนาย
    all_matches = db.get_matches()
    all_matches['match_dt'] = pd.to_datetime(all_matches['match_time'])
    
    # สร้าง Tab แยกข้อมูล
    tab_finished, tab_upcoming = st.tabs(["🏁 ผลการทายที่แข่งเสร็จแล้ว", "🔮 ผลทายล่วงหน้าของคุณ"])
    
    with tab_finished:
        finished_matches = all_matches[all_matches['status'] == 'Finished'].sort_values('match_time', ascending=False)
        if finished_matches.empty:
            st.info("ยังไม่มีผลการแข่งขันที่เสร็จสิ้นในขณะนี้ครับ")
        else:
            # ดึงประวัติการทายทั้งหมด
            predictions_df = db.get_predictions_df()
            
            # จัดกลุ่มตามวันแข่งขัน
            unique_dates = finished_matches['match_dt'].dt.date.unique()
            
            for d in unique_dates:
                date_str = d.strftime('%d/%m/%Y')
                st.subheader(f"🗓️ ผลแข่งขันประจำวันที่ {date_str}")
                day_matches = finished_matches[finished_matches['match_dt'].dt.date == d]
                
                for _, row_m in day_matches.iterrows():
                    m_id = str(row_m['id'])
                    home_team = row_m['home_team']
                    away_team = row_m['away_team']
                    h_real = safe_int(row_m['home_score'])
                    a_real = safe_int(row_m['away_score'])
                    real_win = (h_real > a_real) - (h_real < a_real)
                    
                    home_disp = get_team_display(home_team)
                    away_disp = get_team_display(away_team)
                    
                    expander_label = f"⚽ {home_disp}  {h_real} - {a_real}  {away_disp}"
                    
                    with st.expander(expander_label):
                        st.markdown(f"**⏰ เวลาแข่ง:** {pd.to_datetime(row_m['match_time']).strftime('%d/%m/%Y %H:%M น.')}")
                        if row_m['scorers']:
                            st.markdown(f"⚽ **ผู้ทำประตู:** {row_m['scorers']}")
                        
                        st.markdown("---")
                        st.markdown("**🎯 ผลการทายของผู้เล่นทั้งหมดในคู่นี้:**")
                        
                        m_preds = predictions_df[predictions_df['match_id'].astype(str) == m_id]
                        if m_preds.empty:
                            st.write("ยังไม่มีผู้เล่นใดทายผลคู่นี้ไว้ในระบบ")
                        else:
                            for _, row_p in m_preds.iterrows():
                                u_name = row_p['username']
                                p_h = safe_int(row_p['pred_home'])
                                p_a = safe_int(row_p['pred_away'])
                                pred_win = (p_h > p_a) - (p_h < p_a)
                                
                                # ตรวจแต้มทายผล
                                if p_h == h_real and p_a == a_real:
                                    pt_label = "🏆 ทายถูกตรงเป๊ะ! ได้ 3 คะแนน"
                                    card_style = """
                                    background: linear-gradient(135deg, rgba(212, 175, 55, 0.2) 0%, rgba(153, 101, 21, 0.1) 100%);
                                    border: 1px solid #FFD700;
                                    color: #FFD700;
                                    """
                                elif pred_win == real_win:
                                    pt_label = "🟢 ทายถูกฝั่ง! ได้ 1 คะแนน"
                                    card_style = """
                                    background: linear-gradient(135deg, rgba(46, 125, 50, 0.2) 0%, rgba(27, 94, 32, 0.1) 100%);
                                    border: 1px solid #4CAF50;
                                    color: #81C784;
                                    """
                                else:
                                    pt_label = "❌ ทายผิด! ได้ 0 คะแนน"
                                    card_style = """
                                    background: rgba(255, 255, 255, 0.02);
                                    border: 1px solid rgba(255, 255, 255, 0.08);
                                    color: #a0aec0;
                                    """
                                
                                st.markdown(
                                    f"""
                                    <div style='padding: 10px 15px; border-radius: 8px; margin-bottom: 6px; {card_style}'>
                                        👤 ผู้เล่น: <b>{u_name}</b> | ผลทาย: <b>{p_h} - {p_a}</b> &nbsp;&nbsp;&nbsp;&nbsp; ({pt_label})
                                    </div>
                                    """,
                                    unsafe_allow_html=True
                                )
                st.divider()

    with tab_upcoming:
        st.info("💡 หน้านี้แสดงข้อมูลเฉพาะสกอร์ที่คุณทายไว้ล่วงหน้าสำหรับคู่แข่งขันที่ยังไม่เริ่มเตะ เพื่อความปลอดภัยในการป้องกันการลอกเลียนแบบผลทายของกันและกันครับ")
        upcoming_matches = all_matches[all_matches['status'] != 'Finished'].sort_values('match_time')
        
        if upcoming_matches.empty:
            st.success("คุณเข้าร่วมการแข่งครบถ้วนหมดแล้ว ไม่มีคู่การแข่งขันล่วงหน้าค้างอยู่ครับ")
        else:
            user_preds = db.get_user_predictions(username)
            unique_dates_uc = upcoming_matches['match_dt'].dt.date.unique()
            
            for d in unique_dates_uc:
                date_str = d.strftime('%d/%m/%Y')
                
                # ตรวจป้าย วันนี้ / วันพรุ่งนี้ / วันมะรืนนี้
                now_th = datetime.now(timezone(timedelta(hours=7))).replace(tzinfo=None)
                today_d = now_th.date()
                tomorrow_d = today_d + pd.Timedelta(days=1)
                day_after_d = today_d + pd.Timedelta(days=2)
                
                label_suffix = ""
                if d == today_d:
                    label_suffix = " (วันนี้)"
                elif d == tomorrow_d:
                    label_suffix = " (วันพรุ่งนี้)"
                elif d == day_after_d:
                    label_suffix = " (วันมะรืนนี้)"
                
                fifa_label = ""
                if date_str == "24/06/2026":
                    fifa_label = " 🇺🇸 (ตรงกับโปรแกรมฟีฟ่าวันที่ 23 มิ.ย.)"
                elif date_str == "25/06/2026":
                    fifa_label = " 🇺🇸 (ตรงกับโปรแกรมฟีฟ่าวันที่ 24 มิ.ย.)"
                elif date_str == "26/06/2026":
                    fifa_label = " 🇺🇸 (ตรงกับโปรแกรมฟีฟ่าวันที่ 25 มิ.ย.)"
                
                st.subheader(f"🗓️ ตารางแข่งขันวันที่ {date_str}{label_suffix}{fifa_label}")
                day_matches = upcoming_matches[upcoming_matches['match_dt'].dt.date == d]
                
                for _, row_m in day_matches.iterrows():
                    m_id = row_m['id']
                    home_team = row_m['home_team']
                    away_team = row_m['away_team']
                    
                    has_pred = safe_int(m_id) in user_preds
                    home_disp = get_team_display(home_team)
                    away_disp = get_team_display(away_team)
                    
                    # แปลงเวลาเตะอย่างยืดหยุ่นและปลอดภัยจากประเภทข้อมูล Timestamp/String
                    m_time = row_m['match_dt'] if 'match_dt' in row_m and pd.notnull(row_m['match_dt']) else pd.to_datetime(row_m['match_time'])
                    if not isinstance(m_time, datetime):
                        m_time = m_time.to_pydatetime()
                    is_locked = now_th > m_time or row_m['status'] == 'Finished'
                    
                    if has_pred:
                        pred_h, pred_a = user_preds[safe_int(m_id)]
                        pred_text = f"🔥 ผลทายของคุณ: &nbsp;<b>{pred_h} - {pred_a}</b>"
                        card_class = "upcoming-card has-prediction"
                    else:
                        pred_text = "⚠️ คุณยังไม่ได้ทายผลคู่นี้"
                        card_class = "upcoming-card no-prediction"
                    
                    status_text = "🔒 ปิดรับผลทายแล้ว" if is_locked else "🔓 เปิดรับผลทาย (สามารถแก้ไขได้ที่หน้าแรก)"
                    st.markdown(
                        f"""
                        <div class='{card_class}'>
                            <div style='display: flex; justify-content: space-between; align-items: center;'>
                                <span style='font-size: 1.05rem; font-weight: bold;'>⚽ {home_disp} vs {away_disp}</span>
                                <span style='font-size: 0.85rem; color: #a0aec0;'>⏰ เวลาเตะ: {m_time.strftime('%H:%M น.')}</span>
                            </div>
                            <div style='margin-top: 10px; font-size: 1rem;'>
                                {pred_text}
                            </div>
                            <div style='margin-top: 8px; font-size: 0.8rem; color: #888;'>
                                สถานะ: {status_text}
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

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
