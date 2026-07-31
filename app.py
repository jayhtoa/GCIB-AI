import os
import json
import time
import urllib.parse
import requests
import streamlit as st
from openai import OpenAI
from streamlit_autorefresh import st_autorefresh

# -----------------------------------------------------------------------------
# 1. 多語言介面字典
# -----------------------------------------------------------------------------
TRANSLATIONS = {
    "廣東話 (Cantonese)": {
        "title": "🤖 志昌 AI 智能助手",
        "caption": "📍 隨時為你解答任何問題 | 美食、交通、天氣、即時網絡搜尋及生活百事",
        "sidebar_control": "⚙️ 控制面板",
        "current_loc": "📍 當前定位：土瓜灣落山道 108 號",
        "notice_board_title": "📢 大廈最新通告 / Notice Board",
        "no_notices": "ℹ️ 目前沒有最新通告",
        "clear_history": "🗑️ 清空聊天紀錄",
        "emergency_title": "📞 緊急聯絡：",
        "phone_label": "* 電話：`23646837`",
        "shortcut_header": "##### ⚡ 快捷按鈕：",
        "btn_food": "🍱 附近美食",
        "btn_trans": "🚌 附近交通",
        "btn_weather": "🌤️ 實時天氣",
        "voice_search_label": "🎤 點擊錄音進行語音搜尋 (Voice Search)",
        "chat_placeholder": "請輸入任何問題（例如：Billboard Top 10、最新新聞...）",
        "ai_prompt_lang": "廣東話 (Cantonese)",
        "ai_style_instruction": "必須全程使用純正口語廣東話（粵語）回答。當用戶提及『附近美食/餐廳』或使用快捷按鈕時，必須預設以土瓜灣落山道 108 號為中心，並優先推薦步行距離最近（1-3分鐘步程，落山道/美華工業中心周邊）嘅真實餐廳。若用戶特別指定其他地區（如：銅邏灣美食），則以指定地區為準。回答餐廳時，請附上 OpenRice 及 Google Maps 實時搜尋連結供驗證營業狀態。",
        "prompt_food": "請推薦 3 至 5 間土瓜灣落山道 108 號樓下及 1 分鐘步程內（落山道/美華工業中心周邊）嘅真實餐廳，並附上 OpenRice 同 Google Maps 即時搜尋連結與路線建議！",
        "prompt_trans": "請說明由土瓜灣落山道 108 號出發，點去土瓜灣地鐵站 B 出口同附近馬頭圍道巴士站？",
        "spinner_processing": "⏳ AI 正在即時搜尋網絡並思考中...",
        "spinner_transcribing": "🎙️ 正在轉換語音為文字...",
        "msg_voice_error": "⚠️ 語音辨識失敗，請重新嘗試。",
        "msg_api_error": "⚠️ AI 系統暫時忙碌中，請稍後再試。"
    },
    "繁體中文 (Traditional Chinese)": {
        "title": "🤖 志昌 AI 智能助手",
        "caption": "📍 隨時為您解答任何問題 | 美食、交通、天氣、即時網路搜尋及生活百事",
        "sidebar_control": "⚙️ 控制面板",
        "current_loc": "📍 當前定位：土瓜灣落山道 108 號",
        "notice_board_title": "📢 大廈最新通告 / Notice Board",
        "no_notices": "ℹ️ 目前沒有最新通告",
        "clear_history": "🗑️ 清空對話紀錄",
        "emergency_title": "📞 緊急聯絡：",
        "phone_label": "* 電話：`23646837`",
        "shortcut_header": "##### ⚡ 快捷按鈕：",
        "btn_food": "🍱 附近美食",
        "btn_trans": "🚌 附近交通",
        "btn_weather": "🌤️ 實時天氣",
        "voice_search_label": "🎤 點擊錄音進行語音搜尋 (Voice Search)",
        "chat_placeholder": "請輸入任何問題...",
        "ai_prompt_lang": "繁體中文 (Traditional Chinese)",
        "ai_style_instruction": "必須全程使用規範繁體中文（書面語）回答。當用戶提及『附近美食/餐廳』或使用快捷按鈕時，必須預設以土瓜灣落山道 108 號為中心，並優先推薦步行距離最近（1-3分鐘步行，落山道/美華工業中心周邊）的真實餐廳。若用戶特別指定其他地區，則以指定地區為準。回答餐廳時，請附上 OpenRice 及 Google Maps 實時搜尋連結供驗證營業狀態。",
        "prompt_food": "請推薦 3 至 5 間土瓜灣落山道 108 號樓下及 1 分鐘步行距離內（落山道/美華工業中心周邊）的真實餐廳，並附上 OpenRice 及 Google Maps 即時搜尋連結與路線建議！",
        "prompt_trans": "請說明由土瓜灣落山道 108 號出發，如何前往土瓜灣地鐵站 B 出口及附近馬頭圍道巴士站？",
        "spinner_processing": "⏳ AI 正在即時搜尋網路並處理中...",
        "spinner_transcribing": "🎙️ 正在轉換語音為文字...",
        "msg_voice_error": "⚠️ 語音辨識失敗，請重新嘗試。",
        "msg_api_error": "⚠️ AI 系統暫時忙碌中，請稍後再次發送問題。"
    },
    "简体中文 (Simplified Chinese)": {
        "title": "🤖 志昌 AI 智能助手",
        "caption": "📍 随时为您解答任何问题 | 美食、交通、天气、实时网络搜索及生活百事",
        "sidebar_control": "⚙️ 控制面板",
        "current_loc": "📍 当前定位：土瓜湾落山道 108 号",
        "notice_board_title": "📢 最新通告 / Notice Board",
        "no_notices": "ℹ️ 目前没有最新通告",
        "clear_history": "🗑️ 清空对话纪录",
        "emergency_title": "📞 紧急联络：",
        "phone_label": "* 电话：`23646837`",
        "shortcut_header": "##### ⚡ 快捷按钮：",
        "btn_food": "🍱 附近美食",
        "btn_trans": "🚌 附近交通",
        "btn_weather": "🌤️ 实时天气",
        "voice_search_label": "🎤 点击录音进行语音搜索 (Voice Search)",
        "chat_placeholder": "请输入任何问题...",
        "ai_prompt_lang": "规范简体中文 (Simplified Chinese)",
        "ai_style_instruction": "必须全程使用规范简化字回答，绝对禁止出现任何繁体字或粤语口语。当用户提及『附近美食/餐厅』或使用快捷按钮时，必须默认以土瓜湾落山道 108 号为中心，并优先推荐步行距离最近（1-3分钟步行，落山道/美华工业中心周边）的真实餐厅。若用户特别指定其他地区，则以指定地区为准。回答餐厅时，请附上 OpenRice 及 Google Maps 实时搜索链接供验证营业状态。",
        "prompt_food": "请推荐 3 至 5 家土瓜湾落山道 108 号楼下及 1 分钟步行距离内（落山道/美华工业中心周边）的真实餐厅，并附上 OpenRice 及 Google Maps 实时搜索链接与路线建议！",
        "prompt_trans": "请说明由土瓜湾落山道 108 号出发，如何前往土瓜湾地铁站 B 出口及附近马头围道巴士站？",
        "spinner_processing": "⏳ AI 正在实时网络搜索并处理中...",
        "spinner_transcribing": "🎙️ 正在转换语音为文字...",
        "msg_voice_error": "⚠️ 语音识别失败，请重新尝试。",
        "msg_api_error": "⚠️ AI 系统繁忙，请稍后再试一次。"
    },
    "English": {
        "title": "🤖 Gee Chang AI Assistant",
        "caption": "📍 Ask me anything | Food, Transportation, Weather, Live Web Search & General Knowledge",
        "sidebar_control": "⚙️ Control Panel",
        "current_loc": "📍 Location: 108 Lok Shan Road",
        "notice_board_title": "📢 Notice Board",
        "no_notices": "ℹ️ No notices available.",
        "clear_history": "🗑️ Clear Chat History",
        "emergency_title": "📞 Hotline:",
        "phone_label": "* Phone: `23646837`",
        "shortcut_header": "##### ⚡ Quick Shortcuts:",
        "btn_food": "🍱 Nearby Food",
        "btn_trans": "🚌 Nearby Transport",
        "btn_weather": "🌤️ Real-time Weather",
        "voice_search_label": "🎤 Click to record for Voice Search",
        "chat_placeholder": "Ask any question (e.g. Billboard Top 10, latest news...)",
        "ai_prompt_lang": "English",
        "ai_style_instruction": "You MUST answer 100% in professional English. When the user asks for 'nearby food/restaurants' (either by button or typing), ALWAYS default to 108 Lok Shan Road, To Kwa Wan, and prioritize restaurants with the shortest walking distance (1-3 min walk). If the user specifies another district (e.g. CauseWay Bay food), respect their specified location. Provide OpenRice and Google Maps search links for verification.",
        "prompt_food": "Please recommend 3 to 5 real restaurants near 108 Lok Shan Road (within 1-3 min walk) with OpenRice and Google Maps links and walking route tips!",
        "prompt_trans": "Please explain how to get to To Kwa Wan MTR Station Exit B and nearby bus stops from 108 Lok Shan Road.",
        "spinner_processing": "⏳ AI is performing live web search...",
        "spinner_transcribing": "🎙️ Transcribing audio...",
        "msg_voice_error": "⚠️ Speech recognition failed. Please try again.",
        "msg_api_error": "⚠️ AI system busy. Please try asking again."
    }
}

# -----------------------------------------------------------------------------
# 2. 頁面基本設定與 120 秒閒置重置
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="志昌 AI 智能助手 | Gee Chang AI Assistant",
    page_icon="🤖",
    layout="centered"
)

TIMEOUT_SECONDS = 120
st_autorefresh(interval=10000, key="auto_timeout_check")

if "last_active_time" in st.session_state:
    if time.time() - st.session_state["last_active_time"] > TIMEOUT_SECONDS:
        st.session_state.messages = []
        st.session_state["last_active_time"] = time.time()
        st.rerun()

if "messages" not in st.session_state:
    st.session_state.messages = []
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
    st.session_state["last_active_time"] = time.time()
    st.rerun()

T = TRANSLATIONS[selected_language]

st.title(T["title"])
st.caption(T["caption"])

# -----------------------------------------------------------------------------
# 5. 通告讀取與動態翻譯
# -----------------------------------------------------------------------------
def load_notices():
    try:
        if os.path.exists("notices.json"):
            with open("notices.json", "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception:
        pass
    return []

def get_translated_notice(category, title, content, target_lang):
    if target_lang in ["廣東話 (Cantonese)", "繁體中文 (Traditional Chinese)"]:
        return category, title, content
        
    try:
        prompt = f"""Translate this building notice into target language: {target_lang}.
Translate ALL fields including category, title, and content into {target_lang}.
Ensure 100% proper Simplified Chinese characters if Simplified Chinese is selected, or 100% natural English if English is selected.

Respond with JSON only using key names: "category", "title", "content"

Category: {category}
Title: {title}
Content: {content}"""

        res = client.chat.completions.create(
            model="openai/gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            timeout=8
        )
        data = json.loads(res.choices[0].message.content)
        return (
            data.get("category", category),
            data.get("title", title),
            data.get("content", content)
        )
    except Exception:
        return category, title, content

with st.sidebar:
    st.header(T["sidebar_control"])
    st.info(T["current_loc"])
    st.markdown("---")
    
    st.markdown(f"📢 **{T['notice_board_title']}**")
    notices = load_notices()
    
    if notices:
        for notice in notices:
            raw_category = notice.get('category', '通告')
            raw_title = notice.get('title', '')
            date_str = notice.get('date', '')
            raw_content = notice.get('content', '')
            
            t_category, t_title, t_content = get_translated_notice(raw_category, raw_title, raw_content, selected_language)
            
            with st.expander(f"【{t_category}】{t_title}"):
                if date_str:
                    st.caption(f"🗓️ {date_str}")
                st.write(t_content)
    else:
        st.caption(T["no_notices"])

    st.markdown("---")
    if st.button(T["clear_history"], use_container_width=True):
        st.session_state.messages = []
        st.session_state["last_active_time"] = time.time()
        st.rerun()

    st.markdown("---")
    st.markdown(f"{T['emergency_title']}\n{T['phone_label']}")

# -----------------------------------------------------------------------------
# 6. 香港天文台即時官方天氣 API
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
            return f"🌤️ **Hong Kong Observatory Real-time Weather (108 Lok Shan Road Area):**\n- 📍 **Kowloon City / To Kwa Wan Temp**: {kowloon_temp}°C\n- 💧 **Humidity**: {humidity}%\n- ⚠️ **Warnings**: {warning_str}\n- 🔗 [Official HKO Site](https://www.hko.gov.hk/en/index.html)"
        elif lang == "简体中文 (Simplified Chinese)":
            warning_str = " | ".join(warnings) if warnings else "目前无特别天气警告"
            return f"🌤️ **香港天文台实时官方天气报告（土瓜湾落山道 108 号周边）：**\n- 📍 **九龙城/土瓜湾区气温**：{kowloon_temp}°C\n- 💧 **相对湿度**：{humidity}%\n- ⚠️ **现时天气警告**：{warning_str}\n- 🔗 [点击查看香港天文台官方网站](https://www.hko.gov.hk/sc/index.html)"
        elif lang == "繁體中文 (Traditional Chinese)":
            warning_str = " | ".join(warnings) if warnings else "目前無特別天氣警告"
            return f"🌤️ **香港天文台實時官方天氣報告（土瓜灣落山道 108 號周邊）：**\n- 📍 **九龍城/土瓜灣區氣溫**：{kowloon_temp}°C\n- 💧 **相對濕度**：{humidity}%\n- ⚠️ **現時天氣警告**：{warning_str}\n- 🔗 [點擊查看香港天文台官方網站](https://www.hko.gov.hk/tc/index.html)"
        else:
            warning_str = " | ".join(warnings) if warnings else "目前冇特別天氣警告"
            return f"🌤️ **香港天文台即時官方天氣報告（土瓜灣落山道 108 號周邊）：**\n- 📍 **九龍城/土瓜灣區氣溫**：{kowloon_temp}°C\n- 💧 **相對濕度**：{humidity}%\n- ⚠️ **現時天氣警告**：{warning_str}\n- 🔗 [點此查看香港天文台官方網站](https://www.hko.gov.hk/tc/index.html)"
    except Exception:
        return "⚠️ 天氣資料暫時未能載入，請稍後再試。"

# -----------------------------------------------------------------------------
# 7. 全能通用 System Prompt
# -----------------------------------------------------------------------------
SYSTEM_PROMPT = f"""You are 'Gee Chang AI Assistant' (志昌 AI 智能助手).

【REAL-TIME SEARCH & ACCURACY INSTRUCTIONS】
- You have real-time web search capability enabled.
- NEVER claim "I cannot browse the internet in real-time", "I cannot give live scores/charts", or "Please check the official website".
- Use live search results to answer queries regarding Billboard Top 10, latest news, current stock prices, sports scores, and current events.

【LOCATION ANCHORING & FOOD RECOMMENDATION RULES】
1. DEFAULT LOCATION:
   - When the user asks for food/restaurants/traffic/weather using shortcut buttons, OR types generic phrases like "附近美食", "附近食乜好", "附近餐廳", "附近交通" WITHOUT specifying a city/district:
   - You MUST automatically assume the starting location is **108 Lok Shan Road, To Kwa Wan, Kowloon, Hong Kong (九龍土瓜灣落山道 108 號)**.

2. CLOSEST WALKING DISTANCE PRIORITY:
   - For food recommendations near 108 Lok Shan Road, ALWAYS prioritize places with the **shortest walking distance first** (e.g., 1-3 minutes walking distance: Lok Shan Road, Mei Wah Industrial Centre vicinity, Ma Tau Wai Road).
   - Clearly state the estimated walking time (e.g. 步行約 1 分鐘).

3. SPECIFIED LOCATIONS:
   - If the user explicitly mentions a different area (e.g., "旺角美食", "Mong Kok food", "東京景點"), answer for that specified area instead.

4. REAL-TIME SEARCH LINKS (PREVENT CLOSED SHOPS):
   - For EACH restaurant recommended, provide:
     * OpenRice Real-time Link: `https://www.openrice.com/zh/hongkong/restaurants?what=ENCODED_NAME`
     * Google Maps Link: `https://www.google.com/maps/search/?api=1&query=ENCODED_NAME`

Response Language: STRICTLY 【{T['ai_prompt_lang']}】.
Style Instruction: {T['ai_style_instruction']}
"""

# -----------------------------------------------------------------------------
# 8. 快捷按鈕 (已修正：按鈕標籤隨語言變換)
# -----------------------------------------------------------------------------
st.markdown(T["shortcut_header"])

def send_shortcut(prompt_text):
    st.session_state["last_active_time"] = time.time()
    st.session_state.messages.append({"role": "user", "content": prompt_text})

col1, col2, col3 = st.columns(3)
with col1:
    st.button(T["btn_food"], use_container_width=True, on_click=send_shortcut, args=(T["prompt_food"],))
with col2:
    st.button(T["btn_trans"], use_container_width=True, on_click=send_shortcut, args=(T["prompt_trans"],))
with col3:
    if st.button(T["btn_weather"], use_container_width=True):
        st.session_state["last_active_time"] = time.time()
        real_weather_text = get_real_hk_weather(selected_language)
        st.session_state.messages.append({"role": "assistant", "content": real_weather_text})
        st.rerun()

# -----------------------------------------------------------------------------
# 9. 🎤 語音搜尋
# -----------------------------------------------------------------------------
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
# 10. 對話紀錄顯示
# -----------------------------------------------------------------------------
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# -----------------------------------------------------------------------------
# 11. 自由文字輸入框
# -----------------------------------------------------------------------------
user_text = st.chat_input(T["chat_placeholder"])

if user_text:
    st.session_state["last_active_time"] = time.time()
    st.session_state.messages.append({"role": "user", "content": user_text})
    st.rerun()

# -----------------------------------------------------------------------------
# 12. AI 核心發送與回應
# -----------------------------------------------------------------------------
if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
    with st.chat_message("assistant"):
        with st.spinner(T["spinner_processing"]):
            ai_reply = None
            api_messages = [{"role": "system", "content": SYSTEM_PROMPT}] + [
                {"role": m["role"], "content": m["content"]}
                for m in st.session_state.messages
            ]

            models_to_try = [
                "google/gemini-2.0-flash-001",
                "openai/gpt-4o-mini",
                "deepseek/deepseek-chat"
            ]
            last_err = ""

            for m in models_to_try:
                try:
                    res = client.chat.completions.create(
                        model=m,
                        messages=api_messages,
                        temperature=0.3,
                        timeout=25,
                        extra_body={
                            "plugins": [{"id": "web"}]
                        }
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
