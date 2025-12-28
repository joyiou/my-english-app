import streamlit as st
import google.generativeai as genai

# --- 1. 頁面設定 ---
st.set_page_config(page_title="英文學習工具", page_icon="📚")

# --- 2. API 設定區域 ---
# ⚠️ 請填入你的 Key
try:
    api_key = st.secrets["GEMINI_API_KEY"]
except:
    # 這裡是給你在本地端測試時用的 (如果不想設 secrets 檔)
    # 但上傳到 GitHub 前，請確保這一行被註解掉，或改為空字串
    api_key = "你的金鑰暫時貼這裡_但在上傳前請刪掉" 
genai.configure(api_key=api_key)

# --- 3. 側邊欄：模型診斷與選擇 (解決 404 問題) ---
st.sidebar.header("🛠️ 系統設定")
valid_model_name = ""

try:
    # 自動抓取帳號支援的所有模型
    available_models = []
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            name = m.name.replace("models/", "")
            available_models.append(name)
    
    if available_models:
        st.sidebar.success(f"已連線！找到 {len(available_models)} 個可用模型")
        # 讓使用者選模型，預設選第一個通常是最新的
        valid_model_name = st.sidebar.selectbox("使用模型：", available_models)
    else:
        st.sidebar.error("❌ 找不到可用模型，請檢查 Key。")
        st.stop()

except Exception as e:
    st.sidebar.error(f"連線錯誤：{e}")
    st.stop()

# 設定模型
model = genai.GenerativeModel(valid_model_name)

# ==========================================
#   主程式開始
# ==========================================
st.title("📚 期末專題：英文學習工具")
st.caption(f"目前使用模型：{valid_model_name}")
st.write("---")

function_option = st.sidebar.selectbox(
    "選擇功能",
    ("功能 A: 自動生成句子", "功能 B: 語法檢查與修正")
)

# --- 功能 A ---
if function_option == "功能 A: 自動生成句子":
    st.header("✨ 自動生成英文句子")
    
    col1, col2 = st.columns(2)
    with col1:
        difficulty = st.selectbox("選擇難度", ["國小 (Basic)", "國中 (Intermediate)", "高中/大學 (Advanced)"])
    with col2:
        scenario = st.text_input("輸入情境", value="旅遊")
    
    keywords = st.text_input("必須包含的單字", value="ticket, train")

    if st.button("生成句子"):
        with st.spinner("AI 正在造句中..."):
            # 修正點：這裡改回詳細的 Prompt，強制要求英文
            prompt = f"""
            你是一個專業的英文老師。請依照以下條件造一個「英文句子」：
            1. 難度等級：{difficulty}
            2. 情境主題：{scenario}
            3. 必須包含單字：{keywords}
            
            請直接提供句子即可，並附上中文翻譯。
            格式如下：
            🇬🇧 [英文句子]
            🇹🇼 [中文翻譯]
            """
            try:
                response = model.generate_content(prompt)
                st.success("生成結果：")
                st.markdown(response.text)
            except Exception as e:
                st.error(f"生成失敗：{e}")

# --- 功能 B ---
elif function_option == "功能 B: 語法檢查與修正":
    st.header("🔍 語法檢查與修正")
    
    user_sentence = st.text_area("請輸入英文句子", height=100, 
                                 placeholder="例如：He go to school yesterday.")

    if st.button("開始檢查"):
        if not user_sentence:
            st.warning("請先輸入句子！")
        else:
            with st.spinner("AI 老師正在改考卷..."):
                # 修正點：這裡改回詳細的 Prompt
                prompt = f"""
                請檢查以下英文句子的文法是否正確：
                句子："{user_sentence}"

                如果不正確，請依照以下格式回答：
                1. ❌ **錯誤原因**：(請用繁體中文詳細解釋)
                2. ✅ **正確寫法**：(提供修正後的句子)
                
                如果句子完全正確，請回答：「🎉 這個句子是正確的！」並給予稱讚。
                """
                try:
                    response = model.generate_content(prompt)
                    st.write("### 分析報告")
                    st.markdown(response.text)
                except Exception as e:
                    st.error(f"發生錯誤：{e}")
