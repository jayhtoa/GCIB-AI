import os
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
st.caption("📍 服務地點：土瓜灣落山道 108 號 (108 Lok Shan Road, To Kwa Wan)")

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
# 3. 三語 + 專屬地點 System Prompt 提示詞
# -----------------------------------------------------------------------------
SYSTEM_PROMPT = """你係「志昌 AI 智能管家」，專門為位於【香港九龍土瓜灣落山道108號】（108 Lok Shan Road, To Kwa Wan, Hong Kong）嘅工廠團隊、員工同訪客服務。

【核心語言與態度】
1. 支援三語：請根據使用者輸入嘅語言，自動選擇廣東話（預設/首選）、英文 (English) 或普通話 (Mandarin) 回覆。
2. 態度親切、效率高、條理清晰。

【地標與交通 Context】
- 本工廠地址：土瓜灣落山道108號（鄰近馬頭圍道、浙江街、土瓜灣街市）。
- 鄰近港鐵：港鐵土瓜灣站（Tuen Ma Line）A 出口或 B 出口，步行約 3-5 分鐘。
- 附近巴士/小巴：馬頭圍道及漆咸道北一帶有多線巴士直達尖沙咀、旺角、中環、觀塘等。

【專屬功能指令】
1. 美食推薦：熟悉落山道、浙江街、馬頭圍道及土瓜灣一帶美食（車仔麵、茶餐廳、泰國菜、咖啡店等）。推薦時請附上步行距離、大概價位。
2. 全港餐廳 & 交通 & Book 枱：當使用者查詢全港各區餐廳時，請提供餐廳特色、前往交通路線（地鐵/巴士）及建議訂座方式（如 OpenRice / 官方電話 / 網上表格）。
3. 天氣查詢：提供最新香港天氣預報、氣溫、雨量提示及穿衣建議。
4. 咖啡豆/維修管理：當使用者提及「冇咖啡豆」、「缺豆」、「咖啡機壞咗」、「需要維修」時，請表達關心，並提供緊急管理員聯絡指引（例：工廠管理處電話：+852 2345-6789 / 內部內線：108，或聯絡現場負責人）。"""

# -----------------------------------------------------------------------------
# 4. 初始化 Session State (對話紀錄)
# -----------------------------------------------------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

# -----------------------------------------------------------------------------
# 5. 側邊欄：管理員設定與控制
# -----------------------------------------------------------------------------
with st.sidebar:
    st.header("⚙️ 控制面板")
    st.info("📍 當前定位：土瓜灣落山道 108 號")
    
    # 語言切換提示
    st.markdown("🌐 **語言支援 / Languages:**\n* 廣東話 (Cantonese)\n* English\n* 普通話 (Mandarin)")
    
    st.markdown("---")
    if st.button("🗑️ 清空聊天紀錄", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    st.markdown("---")
    st.markdown("📞 **工廠管理處緊急聯絡：**\n* 內線：`108`\n* 電話：`+852 2345-6789`\n* 服務：咖啡豆補充 / 設備維修")

# -----------------------------------------------------------------------------
# 6. 專屬快捷鍵按鈕區 (Top Shortcuts)
# -----------------------------------------------------------------------------
st.markdown("##### ⚡ 專屬快捷按鈕：")

shortcut_prompt = None

# 第一排快捷鍵：落山道 108 號核心需求
col1, col2, col3 = st.columns(3)
with col1:
    if st.button("🍱 附近美食推薦", use_container_width=True):
        shortcut_prompt = "請推薦土瓜灣落山道108號附近的熱門美食與餐廳，附帶步行時間同特色！"
with col2:
    if st.button("🚌 附近巴士地鐵", use_container_width=True):
        shortcut_prompt = "請詳細說明由土瓜灣落山道108號出發，點去附近嘅港鐵站、巴士站同小巴站？"
with col3:
    if st.button("☕ 搵管理員 (缺豆/維修)", use_container_width=True):
        shortcut_prompt = "咖啡機冇咖啡豆 / 需要維修！請提供報修流程同管理員聯絡資料！"

# 第二排快捷鍵：天氣與全港餐廳
col4, col5 = st.columns(2)
with col4:
    if st.button("🌤️ 查詢今日天氣", use_container_width=True):
        shortcut_prompt = "請提供香港今日最新天氣情況、氣溫同出門注意事項。"
with col5:
    if st.button("🍽️ 全港餐廳搜尋 & Book 枱", use_container_width=True):
        shortcut_prompt = "我想搵香港熱門餐廳，請教我點樣搜尋、睇交通路線同埋訂座 (Book 枱)？"

# -----------------------------------------------------------------------------
# 7. 🎤 語音輸入搜尋 (Voice Search)
# -----------------------------------------------------------------------------
st.markdown("---")
audio_input = st.audio_input("🎤 點擊錄音進行語音搜尋 (Voice Search)")
voice_prompt = None

if audio_input is not None:
    with st.spinner("🎙️ 正在辨識語音中..."):
        try:
            # 呼叫 Whisper 進行語音轉文字
            transcription = client.audio.transcriptions.create(
                model="openai/whisper-1",
                file=audio_input
            )
            voice_prompt = transcription.text
            st.success(f"🗣️ 語音辨識結果：{voice_prompt}")
        except Exception as e:
            st.warning("⚠️ 語音輸入轉文字暫時繁忙，請直接使用文字輸入框。")

# -----------------------------------------------------------------------------
# 8. 顯示歷史聊天畫面
# -----------------------------------------------------------------------------
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# -----------------------------------------------------------------------------
# 9. 處理使用者輸入 (文字 / 快捷鍵 / 語音)
# -----------------------------------------------------------------------------
user_text = st.chat_input("請輸入問題（支援廣東話 / English / 普通話）...")

# 判斷觸發來源優先順序：文字輸入 > 快捷鍵 > 語音辨識
final_prompt = user_text or shortcut_prompt or voice_prompt

if final_prompt:
    # 記錄使用者訊息
    st.session_state.messages.append({"role": "user", "content": final_prompt})
    with st.chat_message("user"):
        st.markdown(final_prompt)

    # 發送請求至 OpenRouter (DeepSeek)
    with st.chat_message("assistant"):
        with st.spinner("AI 管家思考中..."):
            try:
                api_messages = [{"role": "system", "content": SYSTEM_PROMPT}] + [
                    {"role": m["role"], "content": m["content"]}
                    for m in st.session_state.messages
                ]

                response = client.chat.completions.create(
                    model="deepseek/deepseek-chat",
                    messages=api_messages,
                    temperature=0.3
                )

                ai_reply = response.choices[0].message.content.strip()
                st.markdown(ai_reply)

                # 記錄 AI 回覆
                st.session_state.messages.append({"role": "assistant", "content": ai_reply})

            except Exception as e:
                st.error(f"❌ API 呼叫失敗：{str(e)}")
