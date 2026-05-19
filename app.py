import streamlit as st
import requests
import base64

st.set_page_config(page_title="无籽西瓜育种方案点评", page_icon="🍉")
st.title("🍉 无籽西瓜育种方案 · AI专家点评")
st.caption("学生拍照上传手绘方案，AI育种专家即时点评优点与改进方向")

API_KEY = "sk-TBFPttPpUlYeUfGKoCl3RBQxy5b9GumojZIyF0Cq2USplnvs"
API_URL = "https://api.moonshot.cn/v1/chat/completions"

SYSTEM_PROMPT = """你是一位拥有30年经验的西瓜育种专家，擅长无籽西瓜（三倍体育种）技术。
请对学生提交的无籽西瓜育种方案进行专业点评：
1. 先指出方案中科学合理的优点（如：是否正确利用秋水仙素/低温诱导、是否理解二倍体×四倍体杂交等）；
2. 再指出需要改进的方向或科学误区（如：染色体加倍环节遗漏、亲本选择不当等）；
3. 语言亲切、鼓励性强，但要体现高中生物"染色体变异"章节的知识点。
"""

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": SYSTEM_PROMPT}]

student_id = st.text_input("请输入学号或姓名", placeholder="如：01-张三")

uploaded_file = st.file_uploader(
    "📷 拍照或选择图片上传育种方案", 
    type=["jpg", "jpeg", "png"],
    help="点击后平板会自动打开相机，请确保方案文字清晰可见"
)

if uploaded_file is not None:
    st.image(uploaded_file, caption="方案预览", use_column_width=True)

if st.button("🚀 提交方案，获取专家点评") and uploaded_file and student_id:
    img_bytes = uploaded_file.getvalue()
    img_b64 = base64.b64encode(img_bytes).decode()
    mime = uploaded_file.type or "image/jpeg"
    img_url = f"data:{mime};base64,{img_b64}"
    
    user_content = [
        {"type": "image_url", "image_url": {"url": img_url}},
        {"type": "text", "text": f"我是学生{student_id}，这是我设计的无籽西瓜育种方案，请点评优点和改正方向。"}
    ]
    st.session_state.messages.append({"role": "user", "content": user_content})
    
    with st.spinner("⏳ 专家正在分析你的方案，请稍候..."):
        try:
            resp = requests.post(
                API_URL,
                headers={
                    "Authorization": f"Bearer {API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "kimi-k2.6",
                    "messages": st.session_state.messages,
                    "temperature": 0.6,
                    "max_tokens": 1500
                },
                timeout=60
            )
            resp.raise_for_status()
            data = resp.json()
            reply = data["choices"][0]["message"]["content"]
            st.session_state.messages.append({"role": "assistant", "content": reply})
            st.success("点评完成！")
        except Exception as e:
            st.error(f"AI请求失败，请检查网络或联系老师: {e}")

for msg in st.session_state.messages:
    if msg["role"] == "assistant":
        with st.chat_message("assistant"):
            st.markdown(msg["content"])

if len(st.session_state.messages) > 1:
    question = st.chat_input("💬 对点评有疑问？继续向专家提问...")
    if question:
        st.session_state.messages.append({"role": "user", "content": question})
        with st.spinner("思考中..."):
            try:
                resp = requests.post(
                    API_URL,
                    headers={
                        "Authorization": f"Bearer {API_KEY}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "kimi-k2.6",
                        "messages": st.session_state.messages,
                        "temperature": 0.6,
                        "max_tokens": 1500
                    },
                    timeout=60
                )
                data = resp.json()
                reply = data["choices"][0]["message"]["content"]
                st.session_state.messages.append({"role": "assistant", "content": reply})
                st.rerun()
            except Exception as e:
                st.error(f"请求失败: {e}")
