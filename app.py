import os
import streamlit as st
from openai import OpenAI

# -----------------------------------------------------------------------------
# 1. 頁面基本配置
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="志昌 AI 智能管家",
    page_icon="🤖",
    layout="centered"
)

st.title("🤖 志昌 AI 智能管家")
st.caption("🚀 由 Streamlit & OpenRouter (DeepSeek) 強力驅動")

# -----------------------------------------------------------------------------
# 2. 安全讀取 API Key (優先讀取 Streamlit Cloud Secrets)
# -----------------------------------------------------------------------------
api_key = st.secrets.get("OPENROUTER_API_KEY", os.environ.get("OPENROUTER_API_KEY", ""))

if not api_key:
    st.error("⚠️ 找不到 API Key！請前往 Streamlit Cloud Settings 內的 Secrets 設定 `OPENROUTER_API_KEY`。")
    st.stop()

# 初始化 OpenAI 客戶端（連接至 OpenRouter API）
client = OpenAI(
    api_key=api_key,
    base_url="https://openrouter.ai/api/v1"
)

# 系統人設提示詞 (System Prompt)
SYSTEM_PROMPT = """你是一個親切、專業且很有條理的 AI 智能管家。
請用繁體中文（可帶點親切的口吻）回答使用者的問題，並盡量給出清晰簡潔的建議。"""

# -----------------------------------------------------------------------------
# 3. 初始化對話紀錄 (Session State)
# -----------------------------------------------------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

# -----------------------------------------------------------------------------
# 4. 渲染歷史聊天畫面
# -----------------------------------------------------------------------------
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# -----------------------------------------------------------------------------
# 5. 處理使用者輸入與 API 呼叫
# -----------------------------------------------------------------------------
if user_input := st.chat_input("請輸入你想查詢或聊天的內容..."):
    # 顯示使用者發送的訊息
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # 呼叫 AI 產生回覆
    with st.chat_message("assistant"):
        with st.spinner("AI 管家正在思考中..."):
            try:
                # 組合 Prompt 與對話歷史
                api_messages = [{"role": "system", "content": SYSTEM_PROMPT}] + [
                    {"role": m["role"], "content": m["content"]}
                    for m in st.session_state.messages
                ]

                # 發送請求至 OpenRouter (使用 deepseek/deepseek-chat 模型)
                response = client.chat.completions.create(
                    model="deepseek/deepseek-chat",
                    messages=api_messages,
                    temperature=0.3
                )

                ai_reply = response.choices[0].message.content.strip()
                st.markdown(ai_reply)

                # 儲存 AI 的回覆至歷史紀錄
                st.session_state.messages.append({"role": "assistant", "content": ai_reply})

            except Exception as e:
                st.error(f"❌ API 呼叫失敗：{str(e)}")
