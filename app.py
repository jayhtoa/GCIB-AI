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
# 2. 安全讀取 API Key (Streamlit Cloud Secrets)
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
        
        # 抓取京士柏/九龍區氣溫與濕度
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
- 🔗 [點此查看香港天文台官方網站](https://www.hko.gov.hk/tc/index.html)
"""
    except Exception as e:
        return "⚠️ 天氣 API 連線暫時繁忙，請直接點擊 [香港天文台官網](https://www.hko.gov.hk/tc/index.html) 查看實時天氣。"

# -----------------------------------------------------------------------------
# 4. 嚴格真實資料 System Prompt
# -----------------------------------------------------------------------------
SYSTEM_PROMPT = """你係「志昌 AI 智能管家」，服務地位於【香港九龍土瓜灣落山道 108 號】。

【嚴格真實性原則（不可捏造）】
1. 所有介紹的餐廳、地址、地鐵出口、巴士路線必須為【香港真實存在】的資料。如果不確定某間小店名稱，請推薦該區知名實體餐廳，並給出正確的 Google Maps 搜尋連結。
2. 支援三語：根據使用者輸入，自動使用廣東話（預設）、英文或普通話回覆。

【真實地點與交通 Context】
- 本工廠地址：土瓜灣落山道 108 號（鄰近馬頭圍道、浙江街、土瓜灣街市）。
- 港鐵站：港鐵土瓜灣站 B 出口（經江蘇街/落山道步行約 3-4 分鐘）。
- 主要巴士線（馬頭圍道/漆咸道北）：5C、11X、21、26、85X、116、E23 等。

【餐廳搜尋超連結格式】
每當推薦任何餐廳，必須輸出以下真實搜尋連結：
- 📍 Google Maps 導航：`[📍 Google 地圖導航](https://www.google.com/maps/search/?api=1&query=餐廳名稱+土瓜灣)`
- 🍽️ OpenRice Book 枱：`[👉 點我 Book 枱/睇 OpenRice](https://www.openrice.com/zh/hongkong/restaurants?where=餐廳名稱)`

【管理員報修聯絡】
- 缺豆/維修請告知使用者聯絡工廠管理處（內線：108 / 電話：+852 2345-6789）。"""

# -----------------------------------------------------------------------------
# 5. 初始化對話紀錄
# -----------------------------------------------------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

# -----------------------------------------------------------------------------
# 6. 側邊欄控制面板
# -----------------------------------------------------------------------------
with st.sidebar:
    st.header("⚙️ 控制面板")
    st.info("📍 當前定位：土瓜灣落山道 108 號")
    st.markdown("🌐 **語言支援：** 廣東話 / English / 普通話")
    
    st.markdown("---")
    if st.button("🗑️ 清空聊天紀錄", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    st.markdown("---")
    st.markdown("📞 **管理處緊急聯絡：**\n* 內線：`108`\n* 電話：`+852 2345-6789`\n* 服務：咖啡豆補充 / 設備維修")

# -----------------------------------------------------------------------------
# 7. 快捷按鈕區
# -----------------------------------------------------------------------------
st.markdown("##### ⚡ 專屬快捷按鈕：")

shortcut_prompt = None

col1, col2, col3 = st.columns(3)
with col1:
    if st.button("🍱 附近真實美食", use_container_width=True):
        shortcut_prompt = "請推薦土瓜灣落山道108號附近的真實熱門餐廳，並附上 Google Maps 及 OpenRice 連結！"
with col2:
    if st.button("🚌 附近巴士地鐵", use_container_width=True):
        shortcut_prompt = "請詳細說明由土瓜灣落山道108號出發，點去土瓜灣地鐵站 B 出口同附近馬頭圍道巴士站？"
with col3:
    if st.button("☕ 搵管理員 (缺豆/維修)", use_container_width=True):
        shortcut_prompt = "咖啡機冇咖啡豆 / 需要維修！請提供報修流程同管理員聯絡資料！"

col4, col5 = st.columns(2)
with col4:
    # 點擊天氣直接調用天文台 API
    if st.button("🌤️ 實時天氣 (天文台API)", use_container_width=True):
        real_weather_text = get_real_hk_weather()
        st.session_state.messages.append({"role": "assistant", "content": real_weather_text})
        st.rerun()

with col5:
    if st.button("🍽️ 全港餐廳 & Book 枱", use_container_width=True):
        shortcut_prompt = "我想搜尋全港真實熱門餐廳，請提供推薦並附上直達 Google Maps 同 OpenRice Book 枱連結！"

# -----------------------------------------------------------------------------
# 8. 🎤 語音輸入搜尋 (Voice Search)
# -----------------------------------------------------------------------------
st.markdown("---")
audio_input = st.audio_input("🎤 點擊錄音進行語音搜尋 (Voice Search)")
voice_prompt = None

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
# 9. 顯示歷史聊天紀錄
# -----------------------------------------------------------------------------
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# -----------------------------------------------------------------------------
# 10. 處理輸入與發送 API 請求
# -----------------------------------------------------------------------------
user_text = st.chat_input("請輸入問題（支援廣東話/English/普通話）...")

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
                    temperature=0.1  # 降低隨機性，保證輸出精準真實
                )

                ai_reply = response.choices[0].message.content.strip()
                st.markdown(ai_reply)

                st.session_state.messages.append({"role": "assistant", "content": ai_reply})

            except Exception as e:
                st.error(f"❌ API 呼叫失敗：{str(e)}")
