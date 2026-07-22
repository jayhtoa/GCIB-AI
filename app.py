import os
import json
import time
import urllib.parse
import requests
import httpx
import urllib3
import streamlit as st
import streamlit.components.v1 as components
from openai import OpenAI

# -----------------------------------------------------------------------------
# 0. 強制清空電腦殘留的系統 Proxy/代理設定 (解決 Connection error 的關鍵)
# -----------------------------------------------------------------------------
os.environ["NO_PROXY"] = "*"
os.environ.pop("HTTP_PROXY", None)
os.environ.pop("HTTPS_PROXY", None)
os.environ.pop("http_proxy", None)
os.environ.pop("https_proxy", None)

# 關閉 SSL 不安全警告訊息
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# -----------------------------------------------------------------------------
# 1. 頁面配置與 CSS 樣式美化
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="志昌 AI 智能管家", 
    layout="wide", 
    initial_sidebar_state="collapsed"
)

st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: #ffffff; }
    
    div.stButton > button {
        width: 100%;
        height: 65px;
        font-size: 18px !important;
        font-weight: bold;
        border-radius: 12px;
        background-color: #1f2937;
        color: #ffffff;
        border: 1px solid #374151;
        transition: 0.3s;
    }
    div.stButton > button:hover {
        background-color: #2563eb;
        color: white;
        border-color: #60a5fa;
    }
    
    .restaurant-card {
        background-color: #1a2332;
        padding: 18px;
        border-radius: 12px;
        border: 1px solid #2d3748;
        margin-bottom: 15px;
    }
    </style>
""", unsafe_allow_html=True)

# 初始化 Session State
if "input_text" not in st.session_state:
    st.session_state["input_text"] = ""
if "auto_submit" not in st.session_state:
    st.session_state["auto_submit"] = False

# -----------------------------------------------------------------------------
# 2. 自動抓取香港天文台實時天氣與預報 (HKO API)
# -----------------------------------------------------------------------------
@st.cache_data(ttl=600)
def get_hko_weather():
    try:
        url = "https://data.weather.gov.hk/weatherAPI/opendata/weather.php?dataType=rhrread&lang=tc"
        res = requests.get(url, timeout=5).json()
        temp = res['temperature']['data'][0]['value']
        warnings = res.get('warningMessage', [])
        return f"{temp}°C", warnings
    except Exception:
        return "25°C", []

@st.cache_data(ttl=1800)
def get_hko_forecast():
    """抓取香港天文台預報"""
    try:
        url = "https://data.weather.gov.hk/weatherAPI/opendata/weather.php?dataType=fnd&lang=tc"
        res = requests.get(url, timeout=5).json()
        general_situation = res.get('generalSituation', '')
        forecast_list = res.get('weatherForecast', [])
        
        output = f"🌤️ **香港天文台天氣概況**：\n{general_situation}\n\n### 📅 未來預報：\n"
        for day in forecast_list[:5]: 
            date = day.get('forecastDate', '')
            week = day.get('week', '')
            forecast = day.get('forecastMaxtemp', {}).get('value', '')
            mintemp = day.get('forecastMintemp', {}).get('value', '')
            weather = day.get('forecastWeather', '')
            rh = day.get('forecastRh', {}).get('value', '')
            output += f"- **{date} ({week})**：{mintemp}°C - {forecast}°C | 濕度 {rh}% | {weather}\n"
        return output
    except Exception:
        return "暫時無法取得天文台詳細預報，請稍後再試。"

temp, warnings = get_hko_weather()

# -----------------------------------------------------------------------------
# 3. 頂部 Bar
# -----------------------------------------------------------------------------
col_title, col_weather = st.columns([3, 1])

with col_title:
    st.title("📍 志昌 AI 智能管家")
    st.caption("🏢 起點位置：土瓜灣落山道 108 號 志昌工業大廈 (支援全港地區查詢)")

with col_weather:
    st.metric("當前氣溫", temp)
    if warnings:
        for w in warnings:
            st.error(f"⚠️ {w}")

st.divider()

# -----------------------------------------------------------------------------
# 4. 快捷發問按鈕
# -----------------------------------------------------------------------------
st.subheader("💡 快捷服務 (點擊即時發問)")
btn_col1, btn_col2, btn_col3 = st.columns(3)

if btn_col1.button("🍽️ 落山道附近美食 (步行3分鐘內)"):
    st.session_state["input_text"] = "請推薦志昌（落山道108號）周圍步行 3 分鐘內的熱門午餐餐廳。"
    st.session_state["auto_submit"] = True
    st.rerun()

if btn_col2.button("🚌 地鐵/公車路線 (土瓜灣站)"):
    st.session_state["input_text"] = "請問由志昌點樣去土瓜灣地鐵站同附近主要巴士站？"
    st.session_state["auto_submit"] = True
    st.rerun()

if btn_col3.button("☕ 設施報修/通知管理員"):
    st.session_state["input_text"] = "如果咖啡豆用完、紙巾缺失或者冷氣不夠，我應該點樣通知管理員？"
    st.session_state["auto_submit"] = True
    st.rerun()

# -----------------------------------------------------------------------------
# 5. 語音輸入組件 (HTML5 Web Speech API)
# -----------------------------------------------------------------------------
st_html = """
<div style="background-color: #1f2937; padding: 12px; border-radius: 12px; border: 1px solid #374151; display: flex; align-items: center; gap: 15px; margin-bottom: 10px;">
    <button id="start-btn" onclick="startDictation()" style="background-color: #2563eb; color: white; border: none; padding: 10px 20px; font-size: 15px; font-weight: bold; border-radius: 8px; cursor: pointer;">
        🎤 語音發問 (Voice Input)
    </button>
    <span id="speech-status" style="color: #9ca3af; font-size: 15px;">按鈕後可直接講話</span>
</div>

<script>
function startDictation() {
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
        var SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        var recognition = new SpeechRecognition();
        recognition.continuous = false;
        recognition.interimResults = false;
        recognition.lang = 'zh-HK'; 
        
        document.getElementById('speech-status').innerText = '🎙️ 聆聽中... (Listening)';
        document.getElementById('speech-status').style.color = '#60a5fa';
        
        recognition.start();
        
        recognition.onresult = function(event) {
            var text = event.results[0][0].transcript;
            document.getElementById('speech-status').innerText = '✅ 辨識到："' + text + '"';
            document.getElementById('speech-status').style.color = '#34d399';
            
            var inputList = window.parent.document.querySelectorAll('input[type="text"]');
            if (inputList.length > 0) {
                var nativeInputValueSetter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, "value").set;
                nativeInputValueSetter.call(inputList[0], text);
                inputList[0].dispatchEvent(new Event('input', { bubbles: true }));
            }
        };
        
        recognition.onerror = function() {
            document.getElementById('speech-status').innerText = '❌ 請再試一次。';
            document.getElementById('speech-status').style.color = '#f87171';
        };
    }
}
</script>
"""
components.html(st_html, height=75)

# -----------------------------------------------------------------------------
# 6. AI 處理邏輯 (連線防護機制：trust_env=False + verify=False)
# -----------------------------------------------------------------------------
SYSTEM_PROMPT = """You are the AI Concierge for Chi Cheong Industrial Building (志昌工業大廈) located at 108 Lok Shan Road, To Kwa Wan, Hong Kong.

### LOCATION LOGIC:
1. Default Location: If the user query DOES NOT specify a location (e.g. "附近美食", "餐廳"), default to 108 Lok Shan Road, To Kwa Wan.
2. Global HK Location: If the user explicitly mentions another region or area in Hong Kong (e.g. "Soho", "中環", "尖沙咀", "灣仔"), YOU MUST PROVIDE RECOMMENDATIONS FOR THAT SPECIFIC AREA IN HONG KONG.

### STRICT SEARCH KEYWORD RULE FOR LINKS (CRITICAL):
- "booking_search": Must be ONLY the concise restaurant name + area, NO extra symbols or prices. (e.g., "Quinary Central", "Bar Leone Soho", "哥登堡餐廳 土瓜灣").
- "destination_address": Precise restaurant name and English/Chinese address for Google Maps. (e.g., "Bar Leone Bridges Street Central Hong Kong", "哥登堡餐廳 馬頭圍道").

### STRICT RESPONSE FORMAT:
1. RESTAURANTS / BARS / FOOD QUERIES:
   - Return ONLY a raw JSON array of 3-4 venue objects (no markdown code blocks ```json, no extra text).
   - Format:
     [
       {
         "name": "Bar Leone",
         "cuisine": "Cocktail Bar / HKD $150-$250",
         "distance": "Bridges Street, Soho, Central",
         "highlight": "Famous for Olive Oil Sour and Negroni",
         "booking_search": "Bar Leone Central",
         "destination_address": "Bar Leone Bridges Street Central Hong Kong"
       }
     ]

2. ALL OTHER GENERAL QUERIES:
   - Provide direct, concise, helpful answers in plain text.

Language Rule:
- Match the user's language (Cantonese / Traditional Chinese or English).
"""

# ⚠️ 請填入你的 API Key (若使用 OpenRouter 格式為 sk-or-v1-...) ⚠️
OPENROUTER_API_KEY = "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"

def fetch_ai_response(query, api_key):
    """使用 trust_env=False 與 verify=False 強制進行乾淨直接的連線"""
    clean_key = str(api_key).strip().encode('ascii', 'ignore').decode('ascii')
    
    # trust_env=False 忽略任何代理，verify=False 繞過 SSL 證書錯誤
    http_client = httpx.Client(
        timeout=25.0, 
        verify=False, 
        trust_env=False, 
        follow_redirects=True
    )
    
    try:
        client = OpenAI(
            api_key=clean_key,
            base_url="[https://openrouter.ai/api/v1](https://openrouter.ai/api/v1)",  # 亦可改回 "[https://api.deepseek.com](https://api.deepseek.com)" 測試
            http_client=http_client
        )
        
        response = client.chat.completions.create(
            model="deepseek/deepseek-chat",  # 若改用 DeepSeek 原廠 Base URL 則請改為 "deepseek-chat"
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": query}
            ],
            temperature=0.3
        )
        return response.choices[0].message.content.strip()

    except Exception as e:
        return f"ERROR: API 呼叫失敗 - {str(e)}"

# -----------------------------------------------------------------------------
# 7. 主程式 UI 互動與渲染
# -----------------------------------------------------------------------------
user_query = st.text_input("💬 請輸入查詢：", value=st.session_state["input_text"], key="main_input")

if user_query or st.session_state["auto_submit"]:
    st.session_state["auto_submit"] = False
    
    st.chat_message("user").write(user_query)
    
    weather_keywords = ["天氣", "weather", "預報", "forecast", "下雨", "氣溫", "溫度"]
    if any(kw in user_query.lower() for kw in weather_keywords):
        weather_info = get_hko_forecast()
        st.chat_message("assistant").markdown(weather_info)
    
    elif OPENROUTER_API_KEY == "YOUR_OPENROUTER_API_KEY_HERE" or not OPENROUTER_API_KEY.strip():
        st.warning("⚠️ 請在程式碼中第 163 行填入你的 API Key！")
    else:
        with st.spinner("AI 智能管家思考中..."):
            raw_text = fetch_ai_response(user_query, OPENROUTER_API_KEY)
            
            # 如果回傳錯誤訊息，直接顯示
            if raw_text.startswith("ERROR:"):
                st.error(raw_text)
            else:
                # 處理 JSON 清理
                clean_text = raw_text
                if clean_text.startswith("```json"):
                    clean_text = clean_text[7:]
                if clean_text.startswith("```"):
                    clean_text = clean_text[3:]
                if clean_text.endswith("```"):
                    clean_text = clean_text[:-3]
                clean_text = clean_text.strip()

                data = None
                try:
                    parsed = json.loads(clean_text)
                    if isinstance(parsed, list):
                        data = parsed
                except Exception:
                    data = None

                # 情況 A：餐廳/酒吧推薦列表 (JSON 格式)
                if data and isinstance(data, list):
                    st.write("### 🍸/🍽️ 為你精選的推薦項目：")
                    for item in data:
                        with st.container():
                            c1, c2 = st.columns([2.5, 1.5])
                            with c1:
                                st.markdown(f"### {item.get('name', '地點')}")
                                st.markdown(f"🏷️ **類別/價位**：{item.get('cuisine', 'N/A')}")
                                st.markdown(f"📍 **位置/交通**：{item.get('distance', 'N/A')}")
                                st.markdown(f"✨ **特色/招牌**：{item.get('highlight', 'N/A')}")
                            
                            with c2:
                                st.write("")
                                # OpenRice 搜尋連結生成
                                search_term = str(item.get('booking_search', item.get('name', ''))).strip()
                                clean_openrice_q = urllib.parse.quote_plus(search_term)
                                booking_url = f"https://www.openrice.com/zh/hongkong/restaurants?whatwhich={clean_openrice_q}"
                                st.link_button("📅 預約 / OpenRice", booking_url, use_container_width=True)
                                
                                # Google Maps 搜尋導航連結生成
                                dest_address = str(item.get('destination_address', item.get('name', ''))).strip()
                                clean_maps_q = urllib.parse.quote_plus(dest_address)
                                map_url = f"https://www.google.com/maps/search/?api=1&query={clean_maps_q}"
                                st.link_button("🗺️ 地圖導航 (Google Maps)", map_url, use_container_width=True)
                                
                            st.divider()

                # 情況 B：純文字回答
                else:
                    st.chat_message("assistant").write(raw_text)