import os
import json
import urllib.parse
import requests
import streamlit as st
from openai import OpenAI

# -----------------------------------------------------------------------------
# 1. 多語言介面字典 (UI Translations)
# -----------------------------------------------------------------------------
TRANSLATIONS = {
    "廣東話 (Cantonese)": {
        "title": "🤖 志昌 AI 智能管家",
        "caption": "📍 服務地點：九龍土瓜灣落山道 108 號 (108 Lok Shan Road, To Kwa Wan)",
        "sidebar_control": "⚙️ 控制面板",
        "current_loc": "📍 當前定位：土瓜灣落山道 108 號",
        "lang_select": "🌐 語言設定 / Language",
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
        "ai_prompt_lang": "廣東話 (Cantonese)"
    },
    "繁體中文 (Traditional Chinese)": {
        "title": "🤖 志昌 AI 智能管家",
        "caption": "📍 服務地點：九龍土瓜灣落山道 108 號 (108 Lok Shan Road, To Kwa Wan)",
        "sidebar_control": "⚙️ 控制面板",
        "current_loc": "📍 當前定位：土瓜灣落山道 108 號",
        "lang_select": "🌐 語言設定 / Language",
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
        "ai_prompt_lang": "繁體中文 (Traditional Chinese)"
    },
    "简体中文 (Simplified Chinese)": {
        "title": "🤖 志昌 AI 智能管家",
        "caption": "📍 服务地点：九龙土瓜湾落山道 108 号 (108 Lok Shan Road, To Kwa Wan)",
        "sidebar_control": "⚙️ 控制面板",
        "current_loc": "📍 当前定位：土瓜湾落山道 108 号",
        "lang_select": "🌐 语言设置 / Language",
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
        "ai_prompt_lang": "简体中文 (Simplified Chinese)"
    },
    "English": {
        "title": "🤖 Chi Cheong AI Butler",
        "caption": "📍 Location: 108 Lok Shan Road, To Kwa Wan, Kowloon",
        "sidebar_control": "⚙️ Control Panel",
        "current_loc": "📍 Current Location: 108 Lok Shan Road",
        "lang_select": "🌐 Language Settings",
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
        "ai_prompt_lang": "English"
    }
}

# -----------------------------------------------------------------------------
# 2. 頁面基本設定
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="志昌 AI 智能管家 | 108 Lok Shan Road",
    page_icon="🤖",
    layout="centered"
)

# -----------------------------------------------------------------------------
# 3. 初始化對話紀錄與狀態
# -----------------------------------------------------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []
if "admin_mode" not in st.session_state:
    st.session_state.admin_mode = False
if "admin_text" not in st.session_state:
    st.session_state.admin_text = ""

# -----------------------------------------------------------------------------
# 4. 安全讀取 API Key (提早載入供 AI 翻譯使用)
# -----------------------------------------------------------------------------
api_key = st.secrets.get("OPENROUTER_API_KEY", os.environ.get("OPENROUTER_API_KEY", ""))

if not api_key:
    st.error("⚠️ 找不到 API Key！請前往 Streamlit Cloud Settings 內的 Secrets 設定 `OPENROUTER_API_KEY`。")
    st.stop()

client = OpenAI(
    api_key=api_key,
    base_url="https://openrouter.ai/api/v1"
)

# -----------------------------------------------------------------------------
# 5. 讀取 notices.json 檔與 AI 自動翻譯/繁簡轉換函式
# -----------------------------------------------------------------------------
def load_notices():
    try:
        if os.path.exists("notices.json"):
            with open("notices.json", "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception:
        pass
    return []

@st.cache_data(ttl=3600)  # 快取 1 小時，節省 API Calls 與提高載入速度
def translate_notice(title, content, target_lang):
    # 只有揀廣東話或繁體中文時先跳過（因為 JSON 原文係繁體）
    if target_lang in ["廣東話 (Cantonese)", "繁體中文 (Traditional Chinese)"]:
        return title, content

    try:
        prompt = f"""請將以下大廈通告標題與內容翻譯或轉換成【{target_lang}】。
如果目標語言是簡體中文 (Simplified Chinese)，請務必將所有繁體字轉換為規範簡體字。
請嚴格以 JSON 格式回覆，格式如下：
{{"title": "翻譯後的標題", "content": "翻譯後的內容"}}

標題：{title}
內容：{content}
"""
        response = client.chat.completions.create(
            model="deepseek/deepseek-chat",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            temperature=0.1
        )
        result = json.loads(response.choices[0].message.content)
        return result.get("title", title), result.get("content", content)
    except Exception:
        return title, content

# -----------------------------------------------------------------------------
# 6. 側邊欄控制面板 (包含語言切換與 AI 通告翻譯)
# -----------------------------------------------------------------------------
with st.sidebar:
    st.markdown("🌐 **Language / 語言設定**")
    selected_language = st.radio(
        "請選擇語言：",
        options=list(TRANSLATIONS.keys()),
        label_visibility="collapsed"
    )

# 取得當前語言字典
T = TRANSLATIONS[selected_language]

# 渲染動態標題與側邊欄文字
st.title(T["title"])
st.caption(T["caption"])

with st.sidebar:
    st.header(T["sidebar_control"])
    st.info(T["current_loc"])
    st.markdown("---")
    
    # 📢 大廈最新通告區塊 (支援 AI 多語言自動翻譯/繁簡轉換)
    st.markdown(f"📢 **{T['notice_board_title']}**")
    notices = load_notices()
    
    if notices:
        for notice in notices:
            category = notice.get('category', '通告')
            raw_title = notice.get('title', '無標題')
            date_str = notice.get('date', '')
            raw_content = notice.get('content', '')
            
            # 呼叫 AI 即時翻譯通告
            translated_title, translated_content = translate_notice(
                raw_title, 
                raw_content, 
                selected_language
            )
            
            with st.expander(f"【{category}】{translated_title}"):
                if date_str:
                    st.caption(f"🗓️ {date_str}")
                st.write(translated_content)
    else:
        st.caption(T["no_notices"])

    st.markdown("---")
    if st.button(T["clear_history"], use_container_width=True):
        st.session_state.messages = []
        st.session_state.admin_mode = False
        st.session_state.admin_text = ""
        st.rerun()

    st.markdown("---")
    st.markdown(f"{T['emergency_title']}\n{T['phone_label']}\n{T['service_label']}")

# -----------------------------------------------------------------------------
# 7. 香港天文台 API 即時天氣
# -----------------------------------------------------------------------------
def get_real_hk_weather():
    try:
        url = "https://data.weather.gov.hk/weatherAPI/opendata/weather.php?dataType=rhrread&lang=tc"
        res = requests.get(url, timeout=5).json()
        
        temp_data = res.get("temperature", {}).get("data", [])
        kowloon_temp = next((item["value"] for item in temp_data if item.get("place") == "九龍城"), None)
        if not kowloon_temp and temp_data:
            kowloon_temp = temp_data[0].get("value", "N/A")
            
        humidity = res.get("humidity", {}).get("data", [{}])[0].get("value", "N/A")
        warnings = res.get("warningMessage", [])
        warning_str = " | ".join(warnings) if warnings else "目前無特別天氣警告"
        
        return f"""🌤️ **香港天文台即時官方天氣報告：**
- 📍 **九龍城/土瓜灣區氣溫**：{kowloon_temp}°C
- 💧 **相對濕度**：{humidity}%
- ⚠️ **現時天氣警告**：{warning_str}
- 🔗 [點此查看香港天文台官方網站](https://www.hko.gov.hk/tc/index.html)"""
    except Exception:
        return "⚠️ 天氣 API 連線暫時繁忙，請直接點擊 [香港天文台官網](https://www.hko.gov.hk/tc/index.html) 查看實時天氣。"

# -----------------------------------------------------------------------------
# 8. 動態 System Prompt (連動 Selected Language - 強制語言輸出)
# -----------------------------------------------------------------------------
SYSTEM_PROMPT = f"""你係「志昌 AI 智能管家」，服務地位於【香港九龍土瓜灣落山道 108 號】。

【最高指令：語言強制規定（最高優先級！）】
- 使用者目前選擇的語言是：【{T['ai_prompt_lang']}】。
- 你的**整個回覆內容**（包括餐廳名稱介紹、地址描述、交通指引、結語等）必須【完全且100%】使用【{T['ai_prompt_lang']}】撰寫。
- 即使資料庫或搜尋結果是繁體中文或其他語言，你也【必須翻譯並轉換】為【{T['ai_prompt_lang']}】後才輸出！絕不可出現混合語言。

【嚴格真實性原則】
1. 所有介紹的餐廳、地址、地鐵出口必須為真實存在資料。

【跨區搜尋與交通規則】
- 如果使用者尋找「土瓜灣以外」的其他地區（例如 Soho、中環、旺角等）的餐廳或設施，你必須「只推薦該目標地區」的真實地點，絕對不要混入土瓜灣區的餐廳。
- 介紹完其他地區餐廳後，請在結尾提供「由土瓜灣落山道 108 號出發，前往該地區的建議交通路線」。

【真實地點與交通 Context】
- 本工廠地址：土瓜灣落山道 108 號。
- 港鐵站：港鐵土瓜灣站 B 出口。
- 巴士線：5C、11X、21、26、85X、116 等。

【餐廳搜尋超連結格式】
每當推薦任何餐廳，必須輸出以下真實搜尋連結：
- 📍 Google Maps 導航：`[📍 Google 地圖導航](https://www.google.com/maps/search/?api=1&query=餐廳名稱+地區)`
- 🍽️ OpenRice Book 枱：`[👉 點我 Book 枱/睇 OpenRice](https://www.openrice.com/zh/hongkong/restaurants?where=餐廳名稱)`
"""

# -----------------------------------------------------------------------------
# 9. 快捷按鈕區 (語言動態替換)
# -----------------------------------------------------------------------------
st.markdown(T["shortcut_header"])

shortcut_prompt = None

col1, col2, col3, col4 = st.columns(4)
with col1:
    if st.button(T["btn_food"], use_container_width=True):
        shortcut_prompt = "請推薦土瓜灣落山道108號附近的真實熱門餐廳，並附上 Google Maps 及 OpenRice 連結！"
        st.session_state.admin_mode = False
with col2:
    if st.button(T["btn_trans"], use_container_width=True):
        shortcut_prompt = "請詳細說明由土瓜灣落山道108號出發，點去土瓜灣地鐵站 B 出口同附近馬頭圍道巴士站？"
        st.session_state.admin_mode = False
with col3:
    if st.button(T["btn_weather"], use_container_width=True):
        real_weather_text = get_real_hk_weather()
        st.session_state.messages.append({"role": "assistant", "content": real_weather_text})
        st.session_state.admin_mode = False
        st.rerun()
with col4:
    if st.button(T["btn_admin"], use_container_width=True):
        st.session_state.admin_mode = True
        st.rerun()

# -----------------------------------------------------------------------------
# 10. 專屬「管理員協助」版面
# -----------------------------------------------------------------------------
if st.session_state.admin_mode:
    st.markdown("---")
    st.error(f"#### {T['admin_title']}")
    st.info(T["admin_phone_info"])
    
    admin_audio = st.audio_input(T["voice_record_admin"])
    if admin_audio is not None:
        with st.spinner("🎙️ Transcribing audio..."):
            try:
                transcription = client.audio.transcriptions.create(
                    model="openai/whisper-1",
                    file=admin_audio
                )
                st.session_state.admin_text = transcription.text
                st.rerun()
            except Exception as e:
                st.warning("⚠️ 語音辨識失敗 / Audio transcription failed.")
    
    issue_text = st.text_area(
        T["input_admin_placeholder"], 
        value=st.session_state.admin_text,
        placeholder=T["admin_text_placeholder"]
    )
    
    if issue_text.strip():
        if st.button(T["btn_send_admin"], type="primary", use_container_width=True):
            with st.spinner("⏳ Sending WhatsApp..."):
                try:
                    webhook_url = st.secrets.get("WHATSAPP_WEBHOOK_URL", "")
                    if webhook_url:
                        payload = {
                            "phone": "85223646837",
                            "message": f"🤖【志昌智能管家】\n📍 地點：土瓜灣落山道 108 號\n⚠️ 事項：{issue_text.strip()}"
                        }
                        response = requests.post(webhook_url, json=payload, timeout=10)
                        
                        if response.status_code in [200, 201]:
                            st.success("✅ 通知發送成功！ / Sent successfully!")
                            st.session_state.admin_text = ""
                        else:
                            st.error(f"❌ API 發送失敗 (Status Code: {response.status_code})")
                    else:
                        st.success("✅ (系統模擬發送) 已經紀錄並通知管業處！")
                except Exception as e:
                    st.error(f"❌ 連線發生錯誤：{str(e)}")
                    
        st.markdown("<br>", unsafe_allow_html=True)
        encoded_msg = urllib.parse.quote(issue_text.strip())
        st.markdown(f"<div style='text-align:center;'><a href='https://wa.me/85223646837?text={encoded_msg}' target='_blank' style='font-size:12px; color:gray; text-decoration:none;'>👉 WhatsApp Direct Link</a></div>", unsafe_allow_html=True)

    if st.button(T["btn_close_admin"], use_container_width=True):
        st.session_state.admin_mode = False
        st.session_state.admin_text = ""
        st.rerun()
    st.markdown("---")

# -----------------------------------------------------------------------------
# 11. 🎤 一般語音輸入搜尋 (非 Admin 模式才顯示)
# -----------------------------------------------------------------------------
voice_prompt = None
if not st.session_state.admin_mode:
    st.markdown("---")
    audio_input = st.audio_input(T["voice_search_label"])
    if audio_input is not None:
        with st.spinner("🎙️ Transcribing..."):
            try:
                transcription = client.audio.transcriptions.create(
                    model="openai/whisper-1",
                    file=audio_input
                )
                voice_prompt = transcription.text
                st.success(f"🗣️ {voice_prompt}")
            except Exception as e:
                st.warning("⚠️ Voice search error.")

# -----------------------------------------------------------------------------
# 12. 顯示歷史聊天紀錄
# -----------------------------------------------------------------------------
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# -----------------------------------------------------------------------------
# 13. 處理輸入與發送 API 請求
# -----------------------------------------------------------------------------
user_text = st.chat_input(T["chat_placeholder"])

final_prompt = user_text or shortcut_prompt or voice_prompt

if final_prompt:
    st.session_state.messages.append({"role": "user", "content": final_prompt})
    with st.chat_message("user"):
        st.markdown(final_prompt)

    with st.chat_message("assistant"):
        with st.spinner("AI 正在處理中..."):
            try:
                api_messages = [{"role": "system", "content": SYSTEM_PROMPT}] + [
                    {"role": m["role"], "content": m["content"]}
                    for m in st.session_state.messages
                ]

                response = client.chat.completions.create(
                    model="deepseek/deepseek-chat",
                    messages=api_messages,
                    temperature=0.1
                )

                ai_reply = response.choices[0].message.content.strip()
                st.markdown(ai_reply)

                st.session_state.messages.append({"role": "assistant", "content": ai_reply})

            except Exception as e:
                st.error(f"❌ API 呼叫失敗：{str(e)}")
