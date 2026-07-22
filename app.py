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

# 💡【你在這裡修改你的專屬要求】
SYSTEM_PROMPT = """你是一個親切、專業且非常有條理的 AI 智能管家。
請用繁體中文回答使用者的問題，並根據使用者的指令給出最精確的解答。"""

# -----------------------------------------------------------------------------
# 3. 初始化對話紀錄與快捷鍵狀態
# -----------------------------------------------------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

# -----------------------------------------------------------------------------
# 4. 側邊欄：控制項與清空對話
# -----------------------------------------------------------------------------
with st.sidebar:
    st.header("⚙️ 控制面板")
    
    # 清空聊天紀錄按鈕
    if st.button("🗑️ 清空所有對話紀錄", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    st.markdown("---")
    st.markdown("### 💡 側邊欄快捷功能")
    sidebar_shortcut = None
    if st.button("📌 摘要總結", use_container_width=True):
        sidebar_shortcut = "請幫我摘要以下文字的重點內容："
    if st.button("✍️ 文章潤飾", use_container_width=True):
        sidebar_shortcut = "請幫我優化潤飾以下文字，使其口吻更專業通順："

# -----------------------------------------------------------------------------
# 5. 畫面快捷鍵按鈕區 (Shortcut Buttons)
# -----------------------------------------------------------------------------
st.markdown("##### ⚡ 常用快捷鍵：")
col1, col2, col3, col4 = st.columns(4)

button_prompt = None

with col1:
    if st.button("📝 整理重點"):
        button_prompt = "請幫我將以下內容整理成清晰的條列重點："
with col2:
    if st.button("💡 提供靈感"):
        button_prompt = "請針對我接下來提出的主題，提供 5 個創意的 Idea："
with col3:
    if st.button("🔍 檢查錯別字"):
        button_prompt = "請幫我檢查並修正以下文字中的錯別字與文法錯誤："
with col4:
    if st.button("🌐 翻譯成英文"):
        button_prompt = "請幫我將以下文字翻譯成地道的英文："

# -----------------------------------------------------------------------------
# 6. 渲染歷史聊天紀錄
# -----------------------------------------------------------------------------
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# -----------------------------------------------------------------------------
# 7. 接收與處理輸入 (結合聊天框與快捷鍵)
# -----------------------------------------------------------------------------
user_input = st.chat_input("請輸入你想查詢的內容，或點擊上方快捷鍵...")

# 判斷觸發來源（聊天框輸入 / 頂部快捷按鈕 / 側邊欄按鈕）
prompt_to_send = user_input or button_prompt or sidebar_shortcut

if prompt_to_send:
    # 顯示使用者訊息
    st.session_state.messages.append({"role": "user", "content": prompt_to_send})
    with st.chat_message("user"):
        st.markdown(prompt_to_send)

    # 發送請求至 DeepSeek
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
