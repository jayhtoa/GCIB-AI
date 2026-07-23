import os
import urllib.parse
import requests
import streamlit as st
from openai import OpenAI

# -----------------------------------------------------------------------------
# 1. 頁面基本設定
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="志昌 AI 智能管家 | 108 Lok Shan Road",
    page_icon="🤖",
    layout="centered"
)

st.title("🤖 志昌 AI 智能管家")
st.caption("📍 服務地點：九龍土瓜灣落山道 108 號 (108 Lok Shan Road, To Kwa Wan)")

# -----------------------------------------------------------------------------
# 2. 安全讀取 API Key
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
# 3. 抓取 100% 真實香港天文台 API 即時天氣
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
# 4. 初始化對話紀錄與狀態
# -----------------------------------------------------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []
if "admin_mode" not in st.session_state:
    st.session_state.admin_mode = False
if "admin_text" not in st.session_state:
    st.session_state.admin_text = ""

# -----------------------------------------------------------------------------
# 5. 側邊欄控制面板 (加入語言選項)
# -----------------------------------------------------------------------------
with st.sidebar:
    st.header("⚙️ 控制面板")
    st.info("📍 當前定位：土瓜灣落山道 108 號")
    
    st.markdown("🌐 **語言設定 / Language**")
    selected_language = st.radio(
        "請選擇 AI 回覆語言：",
        options=["廣東話 (Cantonese)", "繁體中文 (Traditional Chinese)", "简体中文 (Simplified Chinese)", "English"],
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    if st.button("🗑️ 清空聊天紀錄", use_container_width=True):
        st.session_state.messages = []
        st.session_state.admin_mode = False
        st.session_state.admin_text = ""
        st.rerun()

    st.markdown("---")
    st.markdown("📞 **管業處緊急聯絡：**\n* 電話：`23646837`\n* 服務：報修 / 設備協助")

# -----------------------------------------------------------------------------
# 6. 動態 System Prompt (包含跨區搜尋邏輯與語言)
# -----------------------------------------------------------------------------
SYSTEM_PROMPT = f"""你係「志昌 AI 智能管家」，服務地位於【香港九龍土瓜灣落山道 108 號】。

【嚴格真實性原則】
1. 所有介紹的餐廳、地址、地鐵出口必須為真實存在資料。
2. 語言規定：請嚴格使用【{selected_language}】來回覆使用者。

【跨區搜尋與交通規則（重要！）】
- 如果使用者尋找「土瓜灣以外」的其他地區（例如 Soho、中環、旺角等）的餐廳或設施，你必須「只推薦該目標地區」的真實地點，**絕對不要**再混入土瓜灣區的餐廳。
- 在介紹完其他地區的餐廳後，請務必在結尾提供「由土瓜灣落山道 108 號出發，前往該地區的建議交通路線」（例如搭乘哪一架巴士、或者去土瓜灣站搭港鐵等）。

【真實地點與交通 (出發地 Context)】
- 本工廠地址：土瓜灣落山道 108 號。
- 港鐵站：港鐵土瓜灣站 B 出口。
- 巴士線：5C、11X、21、26、85X、116 等。

【餐廳搜尋超連結格式】
每當推薦任何餐廳，必須輸出以下真實搜尋連結：
- 📍 Google Maps 導航：`[📍 Google 地圖導航](https://www.google.com/maps/search/?api=1&query=餐廳名稱+地區)`
- 🍽️ OpenRice Book 枱：`[👉 點我 Book 枱/睇 OpenRice](https://www.openrice.com/zh/hongkong/restaurants?where=餐廳名稱)`
"""

# -----------------------------------------------------------------------------
# 7. 快捷按鈕區 (4 個按鈕)
# -----------------------------------------------------------------------------
st.markdown("##### ⚡ 快捷按鈕：")

shortcut_prompt = None

col1, col2, col3, col4 = st.columns(4)
with col1:
    if st.button("🍱 附近美食", use_container_width=True):
        shortcut_prompt = "請推薦土瓜灣落山道108號附近的真實熱門餐廳，並附上 Google Maps 及 OpenRice 連結！"
        st.session_state.admin_mode = False
with col2:
    if st.button("🚌 附近交通", use_container_width=True):
        shortcut_prompt = "請詳細說明由土瓜灣落山道108號出發，點去土瓜灣地鐵站 B 出口同附近馬頭圍道巴士站？"
        st.session_state.admin_mode = False
with col3:
    if st.button("🌤️ 實時天氣", use_container_width=True):
        real_weather_text = get_real_hk_weather()
        st.session_state.messages.append({"role": "assistant", "content": real_weather_text})
        st.session_state.admin_mode = False
        st.rerun()
with col4:
    if st.button("🛠️ 管理員協助", use_container_width=True):
        st.session_state.admin_mode = True
        st.rerun()

# -----------------------------------------------------------------------------
# 8. 專屬「管理員協助」版面 (後台直飛 WhatsApp API)
# -----------------------------------------------------------------------------
if st.session_state.admin_mode:
    st.markdown("---")
    st.error("#### 🛠️ 管理員協助版面 (直接發送系統訊息)")
    st.info("📞 **管業處電話：** `23646837`")
    
    admin_audio = st.audio_input("🎤 點擊錄音講出問題 (會自動轉換為文字)")
    if admin_audio is not None:
        with st.spinner("🎙️ 正在辨識語音中..."):
            try:
                transcription = client.audio.transcriptions.create(
                    model="openai/whisper-1",
                    file=admin_audio
                )
                st.session_state.admin_text = transcription.text
                st.rerun()
            except Exception as e:
                st.warning("⚠️ 語音辨識失敗，請直接在下方輸入文字。")
    
    issue_text = st.text_area("✍️ 請文字輸入需要協助的事項：", key="admin_text", placeholder="例如：茶水間咖啡機冇豆 / 冷氣唔凍...")
    
    if issue_text.strip():
        # 【修改重點】改為直接執行發送的按鈕，而不再是網頁連結
        if st.button("🚀 確認直接發送通知畀管業處", type="primary", use_container_width=True):
            with st.spinner("⏳ 系統正在後台發送 WhatsApp..."):
                try:
                    # 讀取 Webhook URL (你需要喺 Streamlit Secrets 加入 WHATSAPP_WEBHOOK_URL)
                    webhook_url = st.secrets.get("WHATSAPP_WEBHOOK_URL", "")
                    
                    if webhook_url:
                        # 真正發送 API Request (傳送至你的 Zapier / Make.com / Meta API)
                        payload = {
                            "phone": "85223646837",
                            "message": f"🤖【志昌智能管家 - 報修通知】\n📍 地點：土瓜灣落山道 108 號\n⚠️ 事項：{issue_text.strip()}"
                        }
                        response = requests.post(webhook_url, json=payload, timeout=10)
                        
                        if response.status_code in [200, 201]:
                            st.success("✅ 發送成功！已經直接喺後台通知管業處。")
                            st.session_state.admin_text = "" # 發送完自動清空文字
                        else:
                            st.error(f"❌ API 發送失敗 (Status Code: {response.status_code})")
                    else:
                        # 如果未設定 Webhook，顯示模擬成功畫面
                        st.success("✅ (系統模擬發送) 已經紀錄並通知管業處！")
                        st.caption("⚙️ **開發者提示**：如果要真實發送，請前往 Streamlit Settings > Secrets 加入 `WHATSAPP_WEBHOOK_URL` 連結至 Zapier 或 Make.com。")
                        
                except Exception as e:
                    st.error(f"❌ 系統連線發生錯誤：{str(e)}")
                    
        # 後備方案（萬一系統死咗，仍然可以自己手動 Send）
        st.markdown("<br>", unsafe_allow_html=True)
        encoded_msg = urllib.parse.quote(issue_text.strip())
        st.markdown(f"<div style='text-align:center;'><a href='https://wa.me/85223646837?text={encoded_msg}' target='_blank' style='font-size:12px; color:gray; text-decoration:none;'>👉 (後備方案) 點擊此處打開手機 WhatsApp App 手動發送</a></div>", unsafe_allow_html=True)

    else:
        st.warning("💡 請輸入或錄音講出問題，系統就會顯示「發送」掣。")
        
    if st.button("❌ 關閉協助版面", use_container_width=True):
        st.session_state.admin_mode = False
        st.rerun()
    st.markdown("---")

# -----------------------------------------------------------------------------
# 9. 🎤 一般語音輸入搜尋 (非 Admin 模式才顯示)
# -----------------------------------------------------------------------------
voice_prompt = None
if not st.session_state.admin_mode:
    st.markdown("---")
    audio_input = st.audio_input("🎤 點擊錄音進行語音搜尋 (Voice Search)")
    if audio_input is not None:
        with st.spinner("🎙️ 正在辨識語音中..."):
            try:
                transcription = client.audio.transcriptions.create(
                    model="openai/whisper-1",
                    file=audio_input
                )
                voice_prompt = transcription.text
                st.success(f"🗣️ 語音辨識結果：{voice_prompt}")
            except Exception as e:
                st.warning("⚠️ 語音輸入轉文字暫時繁忙，請直接使用文字輸入框。")

# -----------------------------------------------------------------------------
# 10. 顯示歷史聊天紀錄
# -----------------------------------------------------------------------------
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# -----------------------------------------------------------------------------
# 11. 處理輸入與發送 API 請求
# -----------------------------------------------------------------------------
user_text = st.chat_input("請輸入問題...")

final_prompt = user_text or shortcut_prompt or voice_prompt

if final_prompt:
    st.session_state.messages.append({"role": "user", "content": final_prompt})
    with st.chat_message("user"):
        st.markdown(final_prompt)

    with st.chat_message("assistant"):
        with st.spinner("AI 管家驗證資料並搜尋中..."):
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
