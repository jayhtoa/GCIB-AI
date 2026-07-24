import os
import json
import time
import urllib.parse
import requests
import streamlit as st
from openai import OpenAI
from streamlit_autorefresh import st_autorefresh

# -----------------------------------------------------------------------------
# 1. 100% 完整多語言介面字典
# -----------------------------------------------------------------------------
TRANSLATIONS = {
    "廣東話 (Cantonese)": {
        "title": "🤖 志昌 AI 智能管家",
        "caption": "📍 服務地點：九龍土瓜灣落山道 108 號 (108 Lok Shan Road, To Kwa Wan)",
        "sidebar_control": "⚙️ 控制面板",
        "current_loc": "📍 當前定位：土瓜灣落山道 108 號",
        "notice_board_title": "📢 大廈最新通告 / Notice Board",
        "no_notices": "ℹ️ 目前沒有最新通告",
        "clear_history": "🗑️ 清空聊天紀錄",
        "emergency_title": "📞 管業處緊急聯絡：",
        "phone_label": "* 電話：`23646837`",
        "service_label": "* 服務：報修 / 設備協助",
        "shortcut_header": "##### ⚡ 快捷按鈕：",
        "btn_food": "🍱 附近美食",
        "btn_trans": "🚌 附近交通",
        "btn_weather": "🌤️ 實時天氣",
        "btn_admin": "🛠️ 管理員協助",
        "admin_title": "🛠️ 管理員協助版面 (直接發送系統訊息)",
        "admin_phone_info": "📞 管業處電話：`23646837`",
        "voice_record_admin": "🎤 點擊錄音講出問題 (會自動轉換為文字)",
        "input_admin_placeholder": "✍️ 請文字輸入需要協助的事項：",
        "admin_text_placeholder": "例如：茶水間咖啡機冇豆 / 冷氣唔凍...",
        "btn_send_admin": "🚀 確認直接發送通知畀管業處",
        "btn_close_admin": "❌ 關閉協助版面",
        "voice_search_label": "🎤 點擊錄音進行語音搜尋 (Voice Search)",
        "chat_placeholder": "請輸入問題...",
        "ai_prompt_lang": "廣東話 (Cantonese)",
        "ai_style_instruction": "必須全程使用純正口語廣東話（粵語）回答。所有地址、交通與餐廳資訊必須 100% 真實，嚴禁捏造虛假資料。",
        "prompt_food": "請推薦土瓜灣落山道 108 號附近的真實熱門餐廳，並附上 Google Maps 同 OpenRice 搜尋連結！",
        "prompt_trans": "請說明由土瓜灣落山道 108 號出發，點去土瓜灣地鐵站 B 出口同附近馬頭圍道巴士站？",
        "spinner_processing": "⏳ AI 正在處理中...",
        "spinner_transcribing": "🎙️ 正在轉換語音為文字...",
        "spinner_sending": "⏳ 正在發送通知畀管業處...",
        "msg_send_success": "✅ 通知發送成功！",
        "msg_send_mock_success": "✅ (系統模擬發送) 已經紀錄並通知管業處！",
        "msg_send_failed": "❌ 發送失敗，請稍後再試。",
        "msg_voice_error": "⚠️ 語音辨識失敗，請重新嘗試。",
        "msg_api_error": "⚠️ AI 系統暫時忙碌中，請稍後再試。"
    },
    "繁體中文 (Traditional Chinese)": {
        "title": "🤖 志昌 AI 智能管家",
        "caption": "📍 服務地點：九龍土瓜灣落山道 108 號 (108 Lok Shan Road, To Kwa Wan)",
        "sidebar_control": "⚙️ 控制面板",
        "current_loc": "📍 當前定位：土瓜灣落山道 108 號",
        "notice_board_title": "📢 大廈最新通告 / Notice Board",
        "no_notices": "ℹ️ 目前沒有最新通告",
        "clear_history": "🗑️ 清空對話紀錄",
        "emergency_title": "📞 管理處緊急聯絡：",
        "phone_label": "* 電話：`23646837`",
        "service_label": "* 服務：報修 / 設備協助",
        "shortcut_header": "##### ⚡ 快捷按鈕：",
        "btn_food": "🍱 附近美食",
        "btn_trans": "🚌 附近交通",
        "btn_weather": "🌤️ 實時天氣",
        "btn_admin": "🛠️ 管理員協助",
        "admin_title": "🛠️ 管理員協助版面 (直接發送系統訊息)",
        "admin_phone_info": "📞 管理處電話：`23646837`",
        "voice_record_admin": "🎤 點擊錄音說出問題 (將自動轉換為文字)",
        "input_admin_placeholder": "✍️ 請文字輸入需要協助的事項：",
        "admin_text_placeholder": "例如：茶水間咖啡機無豆 / 冷氣不夠冷...",
        "btn_send_admin": "🚀 確認直接發送通知給管理處",
        "btn_close_admin": "❌ 關閉協助版面",
        "voice_search_label": "🎤 點擊錄音進行語音搜尋 (Voice Search)",
        "chat_placeholder": "請輸入問題...",
        "ai_prompt_lang": "繁體中文 (Traditional Chinese)",
        "ai_style_instruction": "必須全程使用規範繁體中文（書面語）回答。所有地址、交通與餐廳資訊必須 100% 真實，嚴禁捏造虛假資料。",
        "prompt_food": "請推薦土瓜灣落山道 108 號附近的真實熱門餐廳，並附上 Google Maps 及 OpenRice 搜尋連結！",
        "prompt_trans": "請說明由土瓜灣落山道 108 號出發，如何前往土瓜灣地鐵站 B 出口及附近馬頭圍道巴士站？",
        "spinner_processing": "⏳ AI 正在處理中...",
        "spinner_transcribing": "🎙️ 正在轉換語音為文字...",
        "spinner_sending": "⏳ 正在發送通知給管理處...",
        "msg_send_success": "✅ 通知發送成功！",
        "msg_send_mock_success": "✅ (系統模擬發送) 已經紀錄並通知管理處！",
        "msg_send_failed": "❌ 發送失敗，請稍後再試。",
        "msg_voice_error": "⚠️ 語音辨識失敗，請重新嘗試。",
        "msg_api_error": "⚠️ AI 系統暫時忙碌中，請稍後再次發送問題。"
    },
    "简体中文 (Simplified Chinese)": {
        "title": "🤖 志昌 AI 智能管家",
        "caption": "📍 服务地点：九龙土瓜湾落山道 108 号 (108 Lok Shan Road, To Kwa Wan)",
        "sidebar_control": "⚙️ 控制面板",
        "current_loc": "📍 当前定位：土瓜湾落山道 108 号",
        "notice_board_title": "📢 大厦最新通告 / Notice Board",
        "no_notices": "ℹ️ 目前没有最新通告",
        "clear_history": "🗑️ 清空对话纪录",
        "emergency_title": "📞 管理处紧急联络：",
        "phone_label": "* 电话：`23646837`",
        "service_label": "* 服务：报修 / 设备协助",
        "shortcut_header": "##### ⚡ 快捷按钮：",
        "btn_food": "🍱 附近美食",
        "btn_trans": "🚌 附近交通",
        "btn_weather": "🌤️ 实时天气",
        "btn_admin": "🛠️ 管理员协助",
        "admin_title": "🛠️ 管理员协助界面 (直接发送系统消息)",
        "admin_phone_info": "📞 管理处电话：`23646837`",
        "voice_record_admin": "🎤 点击录音说出问题 (将自动转换为文字)",
        "input_admin_placeholder": "✍️ 请文字输入需要协助的事项：",
        "admin_text_placeholder": "例如：茶水间咖啡机无豆 / 空调不够冷...",
        "btn_send_admin": "🚀 确认直接发送通知给管理处",
        "btn_close_admin": "❌ 关闭协助界面",
        "voice_search_label": "🎤 点击录音进行语音搜索 (Voice Search)",
        "chat_placeholder": "请输入问题...",
        "ai_prompt_lang": "规范简体中文 (Simplified Chinese)",
        "ai_style_instruction": "必须全程使用规范简化字回答，绝对禁止出现任何繁体字或粤语口语。所有地址、交通与餐厅信息必须 100% 真实，严禁虚构假信息。",
        "prompt_food": "请推荐土瓜湾落山道 108 号附近的真实热门餐厅，并附上 Google Maps 及 OpenRice 搜索链接！",
        "prompt_trans": "请说明由土瓜湾落山道 108 号出发，如何前往土瓜湾地铁站 B 出口及附近马头围道巴士站？",
        "spinner_processing": "⏳ AI 正在处理中...",
        "spinner_transcribing": "🎙️ 正在转换语音为文字...",
        "spinner_sending": "⏳ 正在发送通知给管理处...",
        "msg_send_success": "✅ 通知发送成功！",
        "msg_send_mock_success": "✅ (系统模拟发送) 已经纪录并通知管理处！",
        "msg_send_failed": "❌ 发送失败，请稍后再试。",
        "msg_voice_error": "⚠️ 语音识别失败，请重新尝试。",
        "msg_api_error": "⚠️ AI 系统繁忙，请稍后再试一次。"
    },
    "English": {
        "title": "🤖 Chi Cheong AI Butler",
        "caption": "📍 Location: 108 Lok Shan Road, To Kwa Wan, Kowloon",
        "sidebar_control": "⚙️ Control Panel",
        "current_loc": "📍 Current Location: 108 Lok Shan Road",
        "notice_board_title": "📢 Building Notices",
        "no_notices": "ℹ️ No notices available.",
        "clear_history": "🗑️ Clear Chat History",
        "emergency_title": "📞 Property Office Hotline:",
        "phone_label": "* Phone: `23646837`",
        "service_label": "* Services: Repairs / Facility Assistance",
        "shortcut_header": "##### ⚡ Quick Buttons:",
        "btn_food": "🍱 Nearby Food",
        "btn_trans": "🚌 Transportation",
        "btn_weather": "🌤️ Live Weather",
        "btn_admin": "🛠️ Admin Help",
        "admin_title": "🛠️ Admin Assistance (Send System Notification)",
        "admin_phone_info": "📞 Property Office: `23646837`",
        "voice_record_admin": "🎤 Click to record issue (Auto-transcribed)",
        "input_admin_placeholder": "✍️ Enter details for assistance:",
        "admin_text_placeholder": "e.g., Coffee machine empty / AC not cold...",
        "btn_send_admin": "🚀 Send Notification to Property Office",
        "btn_close_admin": "❌ Close Admin Panel",
        "voice_search_label": "🎤 Click to record for Voice Search",
        "chat_placeholder": "Ask a question...",
        "ai_prompt_lang": "English",
        "ai_style_instruction": "You MUST answer 100% in professional English. All location, transit, and restaurant details MUST be factual and real.",
        "prompt_food": "Please recommend real top nearby popular restaurants around 108 Lok Shan Road with Google Maps and OpenRice links!",
        "prompt_trans": "Please explain how to get to To Kwa Wan MTR Station Exit B and nearby bus stops from 108 Lok Shan Road factual path.",
        "spinner_processing": "⏳ AI is processing...",
        "spinner_transcribing": "🎙️ Transcribing audio...",
        "spinner_sending": "⏳ Sending notification to Property Office...",
        "msg_send_success": "✅ Notification sent successfully!",
        "msg_send_mock_success": "✅ (Simulated) Recorded and notified Property Office!",
        "msg_send_failed": "❌ Failed to send. Please try again later.",
        "msg_voice_error": "⚠️ Speech recognition failed. Please try again.",
        "msg_api_error": "⚠️ AI system busy. Please try asking again."
    }
}

# -----------------------------------------------------------------------------
# 2. 頁面基本設定與 120 秒閒置重置
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="志昌 AI 智能管家 | 108 Lok Shan Road",
    page_icon="🤖",
    layout="centered"
)

TIMEOUT_SECONDS = 120
st_autorefresh(interval=10000, key="auto_timeout_check")

if "last_active_time" in st.session_state:
    if time.time() - st.session_state["last_active_time"] > TIMEOUT_SECONDS:
        st.session_state.messages = []
        st.session_state.admin_mode = False
        st.session_state.admin_text = ""
        st.session_state["last_active_time"] = time.time()
        st.rerun()

if "messages" not in st.session_state:
    st.session_state.messages = []
if "admin_mode" not in st.session_state:
    st.session_state.admin_mode = False
if "admin_text" not in st.session_state:
    st.session_state.admin_text = ""
if "last_active_time" not in st.session_state:
    st.session_state["last_active_time"] = time.time()

# -----------------------------------------------------------------------------
# 3. 安全讀取 OpenRouter API Key
# -----------------------------------------------------------------------------
api_key = st.secrets.get("OPENROUTER_API_KEY", os.environ.get("OPENROUTER_API_KEY", ""))

if not api_key:
    st.error("⚠️ 找不到 OPENROUTER_API_KEY！請前往 Streamlit Cloud Settings 設定 Secrets。")
    st.stop()

client = OpenAI(
    api_key=api_key,
    base_url="https://openrouter.ai/api/v1"
)

# -----------------------------------------------------------------------------
# 4. 側邊欄與語言選擇
# -----------------------------------------------------------------------------
with st.sidebar:
    st.markdown("🌐 **Language / 語言設定**")
    selected_language = st.radio(
        "請選擇語言：",
        options=list(TRANSLATIONS.keys()),
        label_visibility="collapsed"
    )

if "prev_language" not in st.session_state:
    st.session_state.prev_language = selected_language

if st.session_state.prev_language != selected_language:
    st.session_state.prev_language = selected_language
    st.session_state.messages = []
    st.session_state.admin_mode = False
    st.session_state.admin_text = ""
    st.rerun()

T = TRANSLATIONS[selected_language]

st.title(T["title"])
st.caption(T["caption"])

# -----------------------------------------------------------------------------
# 5. 高效快取通告翻譯
# -----------------------------------------------------------------------------
def load_notices():
    try:
        if os.path.exists("notices.json"):
            with open("notices.json", "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception:
        pass
    return []

@st.cache_data(ttl=86400)
def get_translated_notice(title, content, target_lang):
    if target_lang in ["廣東話 (Cantonese)", "繁體中文 (Traditional Chinese)"]:
        return title, content
        
    try:
        prompt = f"""Translating building notice into: {target_lang}.
Ensure 100% proper Simplified Chinese characters if Simplified Chinese is selected (Replace Cantonese terms like 冇, 嘅 with 没有, 的).
Respond JSON only: {{"title": "...", "content": "..."}}

Title: {title}
Content: {content}"""

        res = client.chat.completions.create(
            model="openai/gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            timeout=8
        )
        data = json.loads(res.choices[0].message.content)
        return data.get("title", title), data.get("content", content)
    except Exception:
        return title, content

with st.sidebar:
    st.header(T["sidebar_control"])
    st.info(T["current_loc"])
    st.markdown("---")
    
    st.markdown(f"📢 **{T['notice_board_title']}**")
    notices = load_notices()
    
    if notices:
        for notice in notices:
            category = notice.get('category', '通告')
            raw_title = notice.get('title', '')
            date_str = notice.get('date', '')
            raw_content = notice.get('content', '')
            
            t_title, t_content = get_translated_notice(raw_title, raw_content, selected_language)
            
            with st.expander(f"【{category}】{t_title}"):
                if date_str:
                    st.caption(f"🗓️ {date_str}")
                st.write(t_content)
    else:
        st.caption(T["no_notices"])

    st.markdown("---")
    if st.button(T["clear_history"], use_container_width=True):
        st.session_state.messages = []
        st.session_state.admin_mode = False
        st.session_state.admin_text = ""
        st.session_state["last_active_time"] = time.time()
        st.rerun()

    st.markdown("---")
    st.markdown(f"{T['emergency_title']}\n{T['phone_label']}\n{T['service_label']}")

# -----------------------------------------------------------------------------
# 6. 天文台即時官方天氣 API
# -----------------------------------------------------------------------------
def get_real_hk_weather(lang):
    api_lang = "tc"
    if lang == "English":
        api_lang = "en"
    elif lang == "简体中文 (Simplified Chinese)":
        api_lang = "sc"

    try:
        url = f"https://data.weather.gov.hk/weatherAPI/opendata/weather.php?dataType=rhrread&lang={api_lang}"
        res = requests.get(url, timeout=5).json()
        
        temp_data = res.get("temperature", {}).get("data", [])
        kowloon_name = "Kowloon City" if api_lang == "en" else "九龍城"
        kowloon_temp = next((item["value"] for item in temp_data if item.get("place") == kowloon_name), None)
        if not kowloon_temp and temp_data:
            kowloon_temp = temp_data[0].get("value", "N/A")
            
        humidity = res.get("humidity", {}).get("data", [{}])[0].get("value", "N/A")
        warnings = res.get("warningMessage", [])
        
        if lang == "English":
            warning_str = " | ".join(warnings) if warnings else "No special weather warnings"
            return f"🌤️ **Hong Kong Observatory Real-time Weather Report:**\n- 📍 **Kowloon City Temp**: {kowloon_temp}°C\n- 💧 **Humidity**: {humidity}%\n- ⚠️ **Warnings**: {warning_str}\n- 🔗 [Official HKO Site](https://www.hko.gov.hk/en/index.html)"
        elif lang == "简体中文 (Simplified Chinese)":
            warning_str = " | ".join(warnings) if warnings else "目前无特别天气警告"
            return f"🌤️ **香港天文台实时官方天气报告：**\n- 📍 **九龙城/土瓜湾区气温**：{kowloon_temp}°C\n- 💧 **相对湿度**：{humidity}%\n- ⚠️ **现时天气警告**：{warning_str}\n- 🔗 [点击查看香港天文台官方网站](https://www.hko.gov.hk/sc/index.html)"
        elif lang == "繁體中文 (Traditional Chinese)":
            warning_str = " | ".join(warnings) if warnings else "目前無特別天氣警告"
            return f"🌤️ **香港天文台實時官方天氣報告：**\n- 📍 **九龍城/土瓜灣區氣溫**：{kowloon_temp}°C\n- 💧 **相對濕度**：{humidity}%\n- ⚠️ **現時天氣警告**：{warning_str}\n- 🔗 [點擊查看香港天文台官方網站](https://www.hko.gov.hk/tc/index.html)"
        else:
            warning_str = " | ".join(warnings) if warnings else "目前冇特別天氣警告"
            return f"🌤️ **香港天文台即時官方天氣報告：**\n- 📍 **九龍城/土瓜灣區氣溫**：{kowloon_temp}°C\n- 💧 **相對濕度**：{humidity}%\n- ⚠️ **現時天氣警告**：{warning_str}\n- 🔗 [點此查看香港天文台官方網站](https://www.hko.gov.hk/tc/index.html)"
    except Exception:
        return "⚠️ 天氣資料暫時未能載入，請稍後再試。"

# -----------------------------------------------------------------------------
# 7. System Prompt (精準網址格式指令)
# -----------------------------------------------------------------------------
SYSTEM_PROMPT = f"""You are 'Chi Cheong AI Butler' (志昌 AI 智能管家), stationed ONLY at 108 Lok Shan Road, To Kwa Wan, Kowloon, Hong Kong.

【STRICT MANDATE】
1. Response Language: STRICTLY 【{T['ai_prompt_lang']}】.
2. Style Instruction: {T['ai_style_instruction']}
3. Real Places Near 108 Lok Shan Road:
   - 遙 Haruka Japanese Restaurant (Address: G/F, 1A Lok Shan Road, To Kwa Wan - 1 min walk)
   - 楚撚記大排檔 Chor Lun Kee (Address: Pok Kwong Building, To Kwa Wan)
   - HeySoNuts Cafe (Address: Shop 3, G/F, 149 Pak Tai Street, To Kwa Wan)
   - 哥登堡餐廳 Gothenburg Restaurant (Address: 423 Ma Tau Wai Road)

4. URL LINK GENERATION RULES (CRITICAL):
   - ONLY output standard, valid web links for Google Maps and OpenRice using URL-encoded terms!
   - Google Maps Format: `https://www.google.com/maps/search/?api=1&query=<URL_ENCODED_RESTAURANT_NAME_AND_LOCATION>`
   - OpenRice Format: `https://www.openrice.com/zh/hongkong/restaurants?where=<URL_ENCODED_RESTAURANT_NAME>`
   - DO NOT make up fake domain names or invalid link paths.
"""

# -----------------------------------------------------------------------------
# 8. 快捷按鈕
# -----------------------------------------------------------------------------
st.markdown(T["shortcut_header"])

def send_shortcut(prompt_text):
    st.session_state["last_active_time"] = time.time()
    st.session_state.messages.append({"role": "user", "content": prompt_text})
    st.session_state.admin_mode = False

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.button(T["btn_food"], use_container_width=True, on_click=send_shortcut, args=(T["prompt_food"],))
with col2:
    st.button(T["btn_trans"], use_container_width=True, on_click=send_shortcut, args=(T["prompt_trans"],))
with col3:
    if st.button(T["btn_weather"], use_container_width=True):
        st.session_state["last_active_time"] = time.time()
        real_weather_text = get_real_hk_weather(selected_language)
        st.session_state.messages.append({"role": "assistant", "content": real_weather_text})
        st.session_state.admin_mode = False
        st.rerun()
with col4:
    if st.button(T["btn_admin"], use_container_width=True):
        st.session_state["last_active_time"] = time.time()
        st.session_state.admin_mode = True
        st.rerun()

# -----------------------------------------------------------------------------
# 9. 管理員協助版面
# -----------------------------------------------------------------------------
if st.session_state.admin_mode:
    st.markdown("---")
    st.error(f"#### {T['admin_title']}")
    st.info(T["admin_phone_info"])
    
    admin_audio = st.audio_input(T["voice_record_admin"])
    if admin_audio is not None:
        st.session_state["last_active_time"] = time.time()
        with st.spinner(T["spinner_transcribing"]):
            try:
                transcription = client.audio.transcriptions.create(
                    model="openai/whisper-1",
                    file=admin_audio
                )
                st.session_state.admin_text = transcription.text
                st.rerun()
            except Exception:
                st.warning(T["msg_voice_error"])
    
    issue_text = st.text_area(
        T["input_admin_placeholder"], 
        value=st.session_state.admin_text,
        placeholder=T["admin_text_placeholder"]
    )
    
    if issue_text.strip():
        if st.button(T["btn_send_admin"], type="primary", use_container_width=True):
            st.session_state["last_active_time"] = time.time()
            with st.spinner(T["spinner_sending"]):
                try:
                    webhook_url = st.secrets.get("WHATSAPP_WEBHOOK_URL", "")
                    if webhook_url:
                        payload = {
                            "phone": "85223646837",
                            "message": f"🤖【志昌智能管家】\n📍 地點：土瓜灣落山道 108 號\n⚠️ 事項：{issue_text.strip()}"
                        }
                        response = requests.post(webhook_url, json=payload, timeout=5)
                        if response.status_code in [200, 201]:
                            st.success(T["msg_send_success"])
                            st.session_state.admin_text = ""
                        else:
                            st.error(T["msg_send_failed"])
                    else:
                        st.success(T["msg_send_mock_success"])
                except Exception:
                    st.error(T["msg_send_failed"])
                    
        encoded_msg = urllib.parse.quote(issue_text.strip())
        st.markdown(f"<div style='text-align:center;'><a href='https://wa.me/85223646837?text={encoded_msg}' target='_blank' style='font-size:12px; color:gray; text-decoration:none;'>👉 WhatsApp Direct Link</a></div>", unsafe_allow_html=True)

    if st.button(T["btn_close_admin"], use_container_width=True):
        st.session_state["last_active_time"] = time.time()
        st.session_state.admin_mode = False
        st.session_state.admin_text = ""
        st.rerun()
    st.markdown("---")

# -----------------------------------------------------------------------------
# 10. 🎤 語音搜尋
# -----------------------------------------------------------------------------
if not st.session_state.admin_mode:
    st.markdown("---")
    audio_input = st.audio_input(T["voice_search_label"])
    if audio_input is not None:
        st.session_state["last_active_time"] = time.time()
        with st.spinner(T["spinner_transcribing"]):
            try:
                transcription = client.audio.transcriptions.create(
                    model="openai/whisper-1",
                    file=audio_input
                )
                if transcription.text:
                    st.session_state.messages.append({"role": "user", "content": transcription.text})
                    st.rerun()
            except Exception:
                st.warning(T["msg_voice_error"])

# -----------------------------------------------------------------------------
# 11. 對話紀錄顯示
# -----------------------------------------------------------------------------
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# -----------------------------------------------------------------------------
# 12. 文字輸入框
# -----------------------------------------------------------------------------
user_text = st.chat_input(T["chat_placeholder"])

if user_text:
    st.session_state["last_active_time"] = time.time()
    st.session_state.messages.append({"role": "user", "content": user_text})
    st.rerun()

# -----------------------------------------------------------------------------
# 13. AI 核心發送
# -----------------------------------------------------------------------------
if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
    with st.chat_message("assistant"):
        with st.spinner(T["spinner_processing"]):
            ai_reply = None
            api_messages = [{"role": "system", "content": SYSTEM_PROMPT}] + [
                {"role": m["role"], "content": m["content"]}
                for m in st.session_state.messages
            ]

            models_to_try = ["openai/gpt-4o-mini", "deepseek/deepseek-chat"]
            last_err = ""

            for m in models_to_try:
                try:
                    res = client.chat.completions.create(
                        model=m,
                        messages=api_messages,
                        temperature=0.1,
                        timeout=12
                    )
                    ai_reply = res.choices[0].message.content.strip()
                    if ai_reply:
                        break
                except Exception as e:
                    last_err = str(e)
                    continue

            if ai_reply:
                st.session_state.messages.append({"role": "assistant", "content": ai_reply})
                st.rerun()
            else:
                st.error(f"❌ 連線逾時或 API 錯誤：`{last_err}`")
