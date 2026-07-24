import os
import json
import time
import urllib.parse
import requests
import streamlit as st
from openai import OpenAI
from streamlit_autorefresh import st_autorefresh

# -----------------------------------------------------------------------------
# 1. 全多語言字典 (UI & System Messages)
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
        "prompt_food": "請推薦土瓜灣落山道 108 號附近的熱門餐廳，並附上 Google Maps 及 OpenRice 連結！",
        "prompt_trans": "請說明由土瓜灣落山道 108 號出發，點去土瓜灣地鐵站 B 出口同附近馬頭圍道巴士站？",
        "spinner_processing": "⏳ AI 正在處理中...",
        "spinner_transcribing": "🎙️ 正在轉換語音為文字...",
        "spinner_sending": "⏳ 正在發送通知畀管業處...",
        "msg_send_success": "✅ 通知發送成功！",
        "msg_send_mock_success": "✅ (系統模擬發送) 已經紀錄並通知管業處！",
        "msg_send_failed": "❌ 發送失敗，請稍後再試。",
        "msg_voice_error": "⚠️ 語音辨識失敗，請重新嘗試。"
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
        "prompt_food": "請推薦土瓜灣落山道 108 號附近的熱門餐廳，並附上 Google Maps 及 OpenRice 連結！",
        "prompt_trans": "請說明由土瓜灣落山道 108 號出發，如何前往土瓜灣地鐵站 B 出口及附近馬頭圍道巴士站？",
        "spinner_processing": "⏳ AI 正在處理中...",
        "spinner_transcribing": "🎙️ 正在轉換語音為文字...",
        "spinner_sending": "⏳ 正在發送通知給管理處...",
        "msg_send_success": "✅ 通知發送成功！",
        "msg_send_mock_success": "✅ (系統模擬發送) 已經紀錄並通知管理處！",
        "msg_send_failed": "❌ 發送失敗，請稍後再試。",
        "msg_voice_error": "⚠️ 語音辨識失敗，請重新嘗試。"
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
        "prompt_food": "请推荐土瓜湾落山道 108 号附近的热门餐厅，并附上 Google Maps 及 OpenRice 链接！",
        "prompt_trans": "请说明由土瓜湾落山道 108 号出发，如何前往土瓜湾地铁站 B 出口及附近马头围道巴士站？",
        "spinner_processing": "⏳ AI 正在处理中...",
        "spinner_transcribing": "🎙️ 正在转换语音为文字...",
        "spinner_sending": "⏳ 正在发送通知给管理处...",
        "msg_send_success": "✅ 通知发送成功！",
        "msg_send_mock_success": "✅ (系统模拟发送) 已经纪录并通知管理处！",
        "msg_send_failed": "❌ 发送失败，请稍后再试。",
        "msg_voice_error": "⚠️ 语音识别失败，请重新尝试。"
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
        "prompt_food": "Please recommend top nearby popular restaurants around 108 Lok Shan Road with Google Maps and OpenRice links!",
        "prompt_trans": "Please explain how to get to To Kwa Wan MTR Station Exit B and nearby bus stops from 108 Lok Shan Road.",
        "spinner_processing": "⏳ AI is processing...",
        "spinner_transcribing": "🎙️ Transcribing audio...",
        "spinner_sending": "⏳ Sending notification to Property Office...",
        "msg_send_success": "✅ Notification sent successfully!",
        "msg_send_mock_success": "✅ (Simulated) Recorded and notified Property Office!",
        "msg_send_failed": "❌ Failed to send. Please try again later.",
        "msg_voice_error": "⚠️ Speech recognition failed. Please try again."
    }
}

# -----------------------------------------------------------------------------
# 2. 頁面與 Session 初始化
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="志昌 AI 智能管家 | 108 Lok Shan Road",
    page_icon="🤖",
    layout="centered"
)

# 閒置自動清理 (120 秒)
st_autorefresh(interval=10000, key="auto_timeout_check")

if "last_active_time" in st.session_state:
    if time.time() - st.session_state["last_active_time"] > 120:
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
# 3. API Key 檢查
# -----------------------------------------------------------------------------
api_key = st.secrets.get("OPENROUTER_API_KEY", os.environ.get("OPENROUTER_API_KEY", ""))

if not api_key:
    st.error("⚠️ 找不到 OPENROUTER_API_KEY！請檢查 Streamlit Cloud Secrets 設定。")
    st.stop()

client = OpenAI(
    api_key=api_key,
    base_url="https://openrouter.ai/api/v1"
)

# -----------------------------------------------------------------------------
# 4. 側邊欄與語言變更
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
# 5. 通告區塊與側邊欄
# -----------------------------------------------------------------------------
with st.sidebar:
    st.header(T["sidebar_control"])
    st.info(T["current_loc"])
    st.markdown("---")
    
    st.markdown(f"📢 **{T['notice_board_title']}**")
    
    notices = []
    try:
        if os.path.exists("notices.json"):
            with open("notices.json", "r", encoding="utf-8") as f:
                notices = json.load(f)
    except Exception:
        pass

    if notices:
        for notice in notices:
            with st.expander(f"【{notice.get('category','通告')}】{notice.get('title','')}"):
                st.write(notice.get('content',''))
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
# 6. 天氣功能
# -----------------------------------------------------------------------------
def get_weather():
    try:
        url = "https://data.weather.gov.hk/weatherAPI/opendata/weather.php?dataType=rhrread&lang=tc"
        res = requests.get(url, timeout=5).json()
        kowloon_temp = res.get("temperature", {}).get("data", [{}])[0].get("value", "N/A")
        humidity = res.get("humidity", {}).get("data", [{}])[0].get("value", "N/A")
        return f"🌤️ **香港實時天氣**：九龍城氣溫 {kowloon_temp}°C，相對濕度 {humidity}%。"
    except Exception:
        return "⚠️ 天氣資料暫時未能載入。"

# -----------------------------------------------------------------------------
# 7. System Prompt 建立
# -----------------------------------------------------------------------------
SYSTEM_PROMPT = f"""You are 'Chi Cheong AI Butler' (志昌 AI 智能管家), located at 108 Lok Shan Road, To Kwa Wan, Hong Kong.
MANDATE: Respond ONLY in 【{T['ai_prompt_lang']}】. If target is Simplified Chinese, use NO Traditional Chinese characters.
Provide Google Maps and OpenRice links for any restaurant suggestions.
"""

# -----------------------------------------------------------------------------
# 8. 快捷按鈕處理邏輯 (Callback 方式)
# -----------------------------------------------------------------------------
st.markdown(T["shortcut_header"])

col1, col2, col3, col4 = st.columns(4)

def send_shortcut(text):
    st.session_state["last_active_time"] = time.time()
    st.session_state.messages.append({"role": "user", "content": text})
    st.session_state.admin_mode = False

with col1:
    st.button(T["btn_food"], use_container_width=True, on_click=send_shortcut, args=(T["prompt_food"],))
with col2:
    st.button(T["btn_trans"], use_container_width=True, on_click=send_shortcut, args=(T["prompt_trans"],))
with col3:
    if st.button(T["btn_weather"], use_container_width=True):
        st.session_state["last_active_time"] = time.time()
        st.session_state.messages.append({"role": "assistant", "content": get_weather()})
        st.session_state.admin_mode = False
        st.rerun()
with col4:
    if st.button(T["btn_admin"], use_container_width=True):
        st.session_state["last_active_time"] = time.time()
        st.session_state.admin_mode = True
        st.rerun()

# -----------------------------------------------------------------------------
# 9. 管理員 Assistance 介面
# -----------------------------------------------------------------------------
if st.session_state.admin_mode:
    st.markdown("---")
    st.error(f"#### {T['admin_title']}")
    issue_text = st.text_area(T["input_admin_placeholder"], value=st.session_state.admin_text)
    if st.button(T["btn_send_admin"], type="primary", use_container_width=True):
        st.success(T["msg_send_mock_success"])
    if st.button(T["btn_close_admin"], use_container_width=True):
        st.session_state.admin_mode = False
        st.rerun()
    st.markdown("---")

# -----------------------------------------------------------------------------
# 10. 顯示已有對話紀錄
# -----------------------------------------------------------------------------
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# -----------------------------------------------------------------------------
# 11. 聊天輸入框處理
# -----------------------------------------------------------------------------
user_input = st.chat_input(T["chat_placeholder"])

if user_input:
    st.session_state["last_active_time"] = time.time()
    st.session_state.messages.append({"role": "user", "content": user_input})
    st.rerun()

# -----------------------------------------------------------------------------
# 12. 觸發 AI 回覆 (當最後一條訊息係 User 時)
# -----------------------------------------------------------------------------
if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
    with st.chat_message("assistant"):
        with st.spinner(T["spinner_processing"]):
            try:
                # 準備發送給 AI 嘅 Messages
                api_msgs = [{"role": "system", "content": SYSTEM_PROMPT}]
                for m in st.session_state.messages:
                    api_msgs.append({"role": m["role"], "content": m["content"]})

                # 調用模型 (先試 deepseek，再試 gpt-3.5)
                try:
                    response = client.chat.completions.create(
                        model="deepseek/deepseek-chat",
                        messages=api_msgs,
                        temperature=0.2
                    )
                except Exception as e_deepseek:
                    # 如果 Deepseek 失敗，轉用 OpenAI GPT-3.5
                    response = client.chat.completions.create(
                        model="openai/gpt-3.5-turbo",
                        messages=api_msgs,
                        temperature=0.2
                    )

                ai_reply = response.choices[0].message.content
                
                if ai_reply:
                    st.session_state.messages.append({"role": "assistant", "content": ai_reply})
                    st.rerun()

            except Exception as err:
                # 🔥 這裡會顯示真正的 Error，方便除錯！
                st.error(f"❌ AI 請求失敗，詳細原因：`{str(err)}`")
