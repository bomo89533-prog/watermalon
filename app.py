import streamlit as st
import requests
import base64
from PIL import Image
import io

# ========== 页面设置 ==========
st.set_page_config(page_title="无籽西瓜育种方案点评", page_icon="🍉")
st.title("🍉 无籽西瓜育种方案 · AI专家点评")
st.caption("学生拍照上传手绘方案，AI育种专家即时点评优点与改进方向")

# ========== 阿里云百炼配置 ==========
API_KEY = "sk-3ca6530b7354447cac3327e5cf56aee8"  # ← 把这里换成你的阿里云百炼 API Key
API_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"

SYSTEM_PROMPT = """你是一位拥有30年经验的西瓜育种专家，擅长无籽西瓜（三倍体育种）技术。
请对学生提交的无籽西瓜育种方案进行专业点评：
1. 先指出方案中科学合理的优点（如：是否正确利用秋水仙素/低温诱导、是否理解二倍体×四倍体杂交等）；
2. 再指出需要改进的方向或科学误区（如：染色体加倍环节遗漏、亲本选择不当等）；
3. 语言亲切、鼓励性强，但要体现高中生物"染色体变异"章节的知识点。
"""

# ========== 每个浏览器会话独立的历史记录（天然隔离30人） ==========
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": SYSTEM_PROMPT}]

# ========== 学生身份输入 ==========
student_id = st.text_input("请输入学号或姓名", placeholder="如：01-张三")

# ========== 图片上传（平板会自动唤起相机） ==========
uploaded_file = st.file_uploader(
    "📷 拍照或选择图片上传育种方案", 
    type=["jpg", "jpeg", "png"],
    help="点击后平板会自动打开相机，请确保方案文字清晰可见"
)

def compress_image(file_bytes, max_size=1024, quality=85):
    """压缩图片：最长边不超过max_size，JPEG质量85%，返回bytes"""
    img = Image.open(io.BytesIO(file_bytes))
    
    # 如果是RGBA模式，转成RGB（JPEG不支持透明）
    if img.mode in ('RGBA', 'P'):
        img = img.convert('RGB')
    
    # 等比例缩放
    img.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
    
    # 保存为JPEG
    buf = io.BytesIO()
    img.save(buf, format='JPEG', quality=quality, optimize=True)
    buf.seek(0)
    return buf.read()

if uploaded_file is not None:
    # 显示原始预览
    st.image(uploaded_file, caption="方案预览", use_column_width=True)
    
    # 显示压缩信息
    original_size = len(uploaded_file.getvalue()) / 1024
    st.info(f"原始图片 {original_size:.0f} KB，已自动压缩后上传")

# ========== 提交并获取点评 ==========
if st.button("🚀 提交方案，获取专家点评") and uploaded_file and student_id:
    # 压缩图片
    raw_bytes = uploaded_file.getvalue()
    compressed_bytes = compress_image(raw_bytes, max_size=1024, quality=85)
    
    # 转Base64
    img_b64 = base64.b64encode(compressed_bytes).decode()
    img_url = f"data:image/jpeg;base64,{img_b64}"
    
    # 构建用户消息
    user_content = [
        {"type": "image_url", "image_url": {"url": img_url}},
        {"type": "text", "text": f"我是学生{student_id}，这是我设计的无籽西瓜育种方案，请点评优点和改正方向。"}
    ]
    st.session_state.messages.append({"role": "user", "content": user_content})
    
    # 调用阿里云百炼 API（超时延长到120秒）
    with st.spinner("⏳ 专家正在分析你的方案，请稍候..."):
        try:
            resp = requests.post(
                API_URL,
                headers={
                    "Authorization": f"Bearer {API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "qwen-vl-plus",
                    "messages": st.session_state.messages,
                    "temperature": 0.6,
                    "max_tokens": 1500
                },
                timeout=120  # 超时延长到120秒
            )
            resp.raise_for_status()
            data = resp.json()
            reply = data["choices"][0]["message"]["content"]
            st.session_state.messages.append({"role": "assistant", "content": reply})
            st.success("点评完成！")
        except requests.exceptions.Timeout:
            st.error("⏱️ 请求超时：图片太大或网络较慢。建议：重新拍摄时让画面更简洁，或靠近WiFi路由器后重试。")
        except Exception as e:
            st.error(f"AI请求失败，请检查网络或联系老师: {e}")

# ========== 显示对话历史 ==========
for msg in st.session_state.messages:
    if msg["role"] == "assistant":
        with st.chat_message("assistant"):
            st.markdown(msg["content"])

# ========== 继续追问（同一轮对话上下文） ==========
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
                        "model": "qwen-vl-plus",
                        "messages": st.session_state.messages,
                        "temperature": 0.6,
                        "max_tokens": 1500
                    },
                    timeout=120
                )
                data = resp.json()
                reply = data["choices"][0]["message"]["content"]
                st.session_state.messages.append({"role": "assistant", "content": reply})
                st.rerun()
            except Exception as e:
                st.error(f"请求失败: {e}")
