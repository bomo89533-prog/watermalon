import streamlit as st
import requests
import base64
from PIL import Image
import io

# ========== 科技感 CSS 注入 ==========
st.set_page_config(page_title="🧬 无籽西瓜育种方案 · AI实验室", page_icon="🍉", layout="centered")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&family=Noto+Sans+SC:wght@300;400;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Noto Sans SC', sans-serif;
    background: linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #0f172a 100%);
    color: #e2e8f0;
}

.stApp {
    background: linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #0f172a 100%);
}

h1 {
    font-family: 'Orbitron', 'Noto Sans SC', sans-serif !important;
    background: linear-gradient(90deg, #06b6d4, #8b5cf6, #ec4899);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    text-align: center;
    font-size: 2.2rem !important;
    font-weight: 700 !important;
    letter-spacing: 1px;
    margin-bottom: 0.5rem !important;
}

.subtitle {
    text-align: center;
    color: #94a3b8;
    font-size: 0.95rem;
    margin-bottom: 2rem;
}

.glass-card {
    background: rgba(30, 41, 59, 0.7);
    backdrop-filter: blur(12px);
    border: 1px solid rgba(148, 163, 184, 0.15);
    border-radius: 16px;
    padding: 24px;
    margin-bottom: 20px;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
}

.glow-border {
    border: 1px solid rgba(6, 182, 212, 0.4);
    box-shadow: 0 0 15px rgba(6, 182, 212, 0.15), inset 0 0 15px rgba(6, 182, 212, 0.05);
}

label, .stTextInput label, .stFileUploader label {
    color: #cbd5e1 !important;
    font-weight: 500 !important;
}

.stTextInput input {
    background: rgba(15, 23, 42, 0.8) !important;
    border: 1px solid rgba(148, 163, 184, 0.3) !important;
    border-radius: 10px !important;
    color: #f1f5f9 !important;
    padding: 12px 14px !important;
}

.stTextInput input:focus {
    border-color: #06b6d4 !important;
    box-shadow: 0 0 0 2px rgba(6, 182, 212, 0.2) !important;
}

.stButton button {
    background: linear-gradient(90deg, #06b6d4, #3b82f6) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 12px 24px !important;
    font-weight: 700 !important;
    font-size: 1rem !important;
    width: 100% !important;
    transition: all 0.3s ease !important;
    box-shadow: 0 4px 15px rgba(6, 182, 212, 0.3) !important;
}

.stButton button:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 25px rgba(6, 182, 212, 0.5) !important;
}

.stFileUploader {
    background: rgba(15, 23, 42, 0.6) !important;
    border: 2px dashed rgba(6, 182, 212, 0.4) !important;
    border-radius: 12px !important;
    padding: 20px !important;
}

.stFileUploader:hover {
    border-color: #06b6d4 !important;
    background: rgba(6, 182, 212, 0.08) !important;
}

.stChatMessage {
    background: rgba(30, 41, 59, 0.6) !important;
    border-radius: 12px !important;
    border: 1px solid rgba(148, 163, 184, 0.1) !important;
}

[data-testid="stChatMessageAvatar"] {
    background: linear-gradient(135deg, #06b6d4, #3b82f6) !important;
}

.success-box {
    background: linear-gradient(90deg, rgba(6,182,212,0.15), rgba(59,130,246,0.15));
    border-left: 4px solid #06b6d4;
    border-radius: 8px;
    padding: 16px;
    margin: 16px 0;
}

.info-tag {
    display: inline-block;
    background: rgba(6, 182, 212, 0.15);
    color: #22d3ee;
    border: 1px solid rgba(6, 182, 212, 0.3);
    border-radius: 6px;
    padding: 2px 10px;
    font-size: 0.8rem;
    margin-right: 8px;
}

.divider {
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(148,163,184,0.3), transparent);
    margin: 20px 0;
}
</style>
""", unsafe_allow_html=True)

# ========== API 配置（直接写死） ==========
API_KEY = "sk-3ca6530b7354447cac3327e5cf56aee8"
API_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"

# ========== 专家提示词（严格按用户要求的 4 个检查点和 3+1 框架） ==========
SYSTEM_PROMPT = """你是一位高中生物教学助手，以西瓜育种专家的身份点评学生设计的无籽西瓜（三倍体）育种方案。

【评判范围】
只判断该方案能否成功获得三倍体西瓜。不需要评价产量高低、抗病性强弱、果实甜度等性状。

【4 个关键检查点】
请逐条检查学生的方案是否体现以下内容：

1. 母本选择与染色体加倍：是否选择二倍体作为母本，并用秋水仙素（或低温）处理使其染色体加倍为四倍体植株？
2. 杂交组合：是否让四倍体母本与二倍体父本杂交？（注意：父本保持二倍体，不需要加倍）
3. 种子与植株的时间差：是否意识到杂交直接得到的是三倍体种子，需要播种、栽培后，第二年（或下一个生长周期）才能长成三倍体植株？不能当年直接结出三倍体西瓜。
4. 花粉刺激与无籽原理：三倍体植株开花后，是否需要接受二倍体花粉的刺激才能促使子房发育成果实？是否体现或暗示了"联会紊乱"导致无法形成正常种子，从而获得无籽西瓜？

【输出框架】（必须严格按以下结构输出，用 markdown 标题）

## 🌟 优点
- 结合上述 4 个检查点，逐条列出学生做对的步骤。
- 如果 4 个步骤全部正确且无明显错误，必须明确写出：**"你的方案完整正确，按照此流程可以成功培育出无籽西瓜！"**

## ⚠️ 错误
- 指出学生方案中的明确科学错误（例如：母本父本选择颠倒、秋水仙素处理后直接得到三倍体、当年直接结果、不需要花粉刺激等）。
- 如果未发现明显错误，写：**"未发现明显错误。"**

## 💡 改进建议
- 针对遗漏或模糊的步骤，用**启发式问句**引导学生思考，然后给出简洁的改进方向。例如：
  - "如果母本没有经秋水仙素处理变成四倍体，二倍体母本和二倍体父本杂交，后代是几倍体？"
  - "三倍体种子种下去，当年就能结出无籽西瓜吗？还需要经历什么阶段？"
  - "为什么三倍体植株自己不能产生正常花粉，却需要二倍体花粉'刺激'才能结果？这个'刺激'和'受精'是一回事吗？"
  - "你的方案里写了'花粉刺激'，那你知道花粉来自几倍体植株吗？"
- 语气亲切，像老师在课堂上启发学生。

## 📚 补充小知识（可选）
- 只有当学生方案基本正确、值得鼓励时，才添加 1 条简短有趣的拓展知识。例如：
  - "小知识：秋水仙素诱导染色体加倍的常用浓度约为 0.01%–0.2%，处理时间一般为几小时至一天。"
  - "小知识：三倍体西瓜并非绝对无籽，有时会出现少量白色软籽，但无法发育成硬籽。"
  - "小知识：低温（如 2–4℃）也能抑制纺锤体形成，起到和秋水仙素类似的效果。"
- 如果学生错误较多，先聚焦改错，此栏可省略。

【语气要求】
- 面向高中生，语言通俗易懂，亲切鼓励。
- 不要过度展开专业细节（如具体处理时长、温度、浓度），除非放在"补充小知识"栏目。
- 每个部分用简洁条目列出，方便学生快速阅读。
- 不要编造学生方案中没有的内容进行点评，只基于学生实际呈现的信息分析。
"""

# ========== 会话隔离（每个浏览器独立） ==========
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": SYSTEM_PROMPT}]

# ========== 页面标题 ==========
st.markdown('<h1>🧬 无籽西瓜育种方案 · AI实验室</h1>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">上传手绘育种流程图，AI育种专家即时诊断你的方案能否成功 🍉</div>', unsafe_allow_html=True)

# ========== 学生身份输入 ==========
with st.container():
    st.markdown('<div class="glass-card glow-border">', unsafe_allow_html=True)
    student_id = st.text_input("👤 请输入学号或姓名", placeholder="如：01-张三", key="sid")
    st.markdown('</div>', unsafe_allow_html=True)

# ========== 图片上传 ==========
with st.container():
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    uploaded_file = st.file_uploader(
        "📷 拍照或选择图片上传育种方案", 
        type=["jpg", "jpeg", "png"],
        help="平板点击此处会自动唤起相机，请确保手绘流程图文字清晰可见"
    )
    
    if uploaded_file is not None:
        col1, col2 = st.columns([3, 1])
        with col1:
            st.image(uploaded_file, caption="📋 方案预览", use_column_width=True)
        with col2:
            raw_size = len(uploaded_file.getvalue()) / 1024
            st.markdown(f'<div style="color:#94a3b8;font-size:0.85rem;">原始大小<br><span style="color:#22d3ee;font-size:1.2rem;font-weight:700;">{raw_size:.0f} KB</span></div>', unsafe_allow_html=True)
            st.markdown('<div style="color:#94a3b8;font-size:0.75rem;margin-top:8px;">已自动压缩<br>优化上传</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ========== 图片压缩函数 ==========
def compress_image(file_bytes, max_size=1200, quality=85):
    img = Image.open(io.BytesIO(file_bytes))
    if img.mode in ('RGBA', 'P'):
        img = img.convert('RGB')
    img.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
    buf = io.BytesIO()
    img.save(buf, format='JPEG', quality=quality, optimize=True)
    buf.seek(0)
    return buf.read()

# ========== 提交并获取点评 ==========
with st.container():
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    submit_btn = st.button("🚀 提交方案，启动 AI 诊断")
    st.markdown('</div>', unsafe_allow_html=True)

if submit_btn:
    if not student_id:
        st.error("⚠️ 请先输入学号或姓名")
    elif not uploaded_file:
        st.error("⚠️ 请先拍照或选择图片上传")
    else:
        # 压缩图片
        raw_bytes = uploaded_file.getvalue()
        compressed_bytes = compress_image(raw_bytes, max_size=1200, quality=85)
        compressed_size = len(compressed_bytes) / 1024
        
        # 转 Base64
        img_b64 = base64.b64encode(compressed_bytes).decode()
        img_url = f"data:image/jpeg;base64,{img_b64}"
        
        # 构建用户消息
        user_content = [
            {"type": "image_url", "image_url": {"url": img_url}},
            {"type": "text", "text": f"我是学生【{student_id}】，这是我设计的无籽西瓜育种方案手绘图/流程图。请严格按照系统提示的4个关键检查点和输出框架进行点评。"}
        ]
        st.session_state.messages.append({"role": "user", "content": user_content})
        
        # 调用阿里云百炼 API
        with st.spinner("⏳ AI 专家正在分析你的育种方案，请稍候..."):
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
                        "temperature": 0.4,
                        "max_tokens": 2000
                    },
                    timeout=120
                )
                resp.raise_for_status()
                data = resp.json()
                reply = data["choices"][0]["message"]["content"]
                st.session_state.messages.append({"role": "assistant", "content": reply})
                
                st.markdown(f"""
                <div class="success-box">
                    <div style="font-weight:700;color:#22d3ee;margin-bottom:4px;">✅ 诊断完成</div>
                    <div style="font-size:0.85rem;color:#94a3b8;">图片压缩后 {compressed_size:.0f} KB · 学号：{student_id}</div>
                </div>
                """, unsafe_allow_html=True)
                
            except requests.exceptions.Timeout:
                st.error("⏱️ 请求超时：网络较慢或图片过大。建议靠近 WiFi 路由器后重试。")
            except Exception as e:
                st.error(f"❌ AI 请求失败: {e}")

# ========== 显示对话历史（专家点评） ==========
st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

for msg in st.session_state.messages:
    if msg["role"] == "assistant":
        with st.chat_message("assistant", avatar="🧑‍🔬"):
            st.markdown(msg["content"])

# ========== 继续追问 ==========
if len(st.session_state.messages) > 1:
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    st.markdown('<div style="color:#94a3b8;font-size:0.9rem;margin-bottom:8px;">💬 对点评有疑问？继续向专家提问</div>', unsafe_allow_html=True)
    
    question = st.chat_input("输入你的问题...")
    if question:
        st.session_state.messages.append({"role": "user", "content": question})
        with st.spinner("🧠 专家思考中..."):
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
                        "temperature": 0.4,
                        "max_tokens": 2000
                    },
                    timeout=120
                )
                data = resp.json()
                reply = data["choices"][0]["message"]["content"]
                st.session_state.messages.append({"role": "assistant", "content": reply})
                st.rerun()
            except Exception as e:
                st.error(f"❌ 请求失败: {e}")

# ========== 底部装饰 ==========
st.markdown("""
<div style="text-align:center;color:#64748b;font-size:0.75rem;margin-top:40px;padding-bottom:20px;">
    🔬 高中生物 · 染色体变异 · 多倍体育种实验室<br>
    Powered by 通义千问 Qwen-VL
</div>
""", unsafe_allow_html=True)
