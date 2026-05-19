import streamlit as st
import requests
import base64
from PIL import Image
import io

# ========== 页面设置 ==========
st.set_page_config(page_title="无籽西瓜育种方案点评", page_icon="🍉", layout="centered")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@300;400;500;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Noto Sans SC', sans-serif;
    background: #f8fafc;
    color: #0f172a;
}

.stApp {
    background: linear-gradient(180deg, #f0f9ff 0%, #f8fafc 40%, #ffffff 100%);
}

/* 标题 */
h1 {
    font-family: 'Noto Sans SC', sans-serif !important;
    color: #0f172a !important;
    text-align: center;
    font-size: 1.7rem !important;
    font-weight: 700 !important;
    margin: 0 !important;
    letter-spacing: 0.5px;
}

.subtitle {
    text-align: center;
    color: #64748b;
    font-size: 0.85rem;
    margin-top: 4px;
    margin-bottom: 24px;
}

/* 主卡片 - 简洁白底 */
.glass-card {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 16px;
    padding: 24px;
    margin-bottom: 16px;
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.06);
}

/* 上传区 */
.stFileUploader {
    background: #f8fafc !important;
    border: 2px dashed #06b6d4 !important;
    border-radius: 12px !important;
    padding: 24px !important;
}

.stFileUploader:hover {
    border-color: #0891b2 !important;
    background: #f0f9ff !important;
}

.stFileUploader span, .stFileUploader small, .stFileUploader div {
    color: #475569 !important;
}

/* 按钮 */
.stButton button {
    background: linear-gradient(90deg, #0891b2, #2563eb) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 14px 24px !important;
    font-weight: 700 !important;
    font-size: 1rem !important;
    width: 100% !important;
    box-shadow: 0 4px 12px rgba(8, 145, 178, 0.25) !important;
    transition: all 0.2s ease !important;
}

.stButton button:hover {
    transform: translateY(-1px);
    box-shadow: 0 6px 20px rgba(8, 145, 178, 0.35) !important;
}

/* 聊天消息 */
.stChatMessage {
    background: #ffffff !important;
    border-radius: 12px !important;
    border: 1px solid #e2e8f0 !important;
    box-shadow: 0 2px 8px rgba(0,0,0,0.04) !important;
}

[data-testid="stChatMessageAvatar"] {
    background: linear-gradient(135deg, #06b6d4, #2563eb) !important;
}

/* 成功提示 */
.success-box {
    background: #ecfdf5;
    border-left: 4px solid #10b981;
    border-radius: 8px;
    padding: 14px 16px;
    margin: 12px 0;
    color: #064e3b;
}

/* 分隔线 */
.divider {
    height: 1px;
    background: linear-gradient(90deg, transparent, #cbd5e1, transparent);
    margin: 20px 0;
}

/* 输入框 */
.stChatInput input {
    background: #ffffff !important;
    border: 1px solid #cbd5e1 !important;
    color: #0f172a !important;
    border-radius: 10px !important;
}

.stSpinner > div {
    color: #0891b2 !important;
}

/* 隐藏多余上下padding */
.block-container {
    padding-top: 1rem !important;
    padding-bottom: 1rem !important;
}

/* 西瓜装饰 */
.watermelon-deco {
    font-size: 3rem;
    line-height: 1;
    filter: drop-shadow(0 4px 6px rgba(0,0,0,0.1));
}
</style>
""", unsafe_allow_html=True)

# ========== 豆包（火山引擎方舟）配置 ==========
API_KEY = "ark-56337a36-0306-47f2-b77e-fc67e7c8dd49-adebf"
API_URL = "https://ark.cn-beijing.volces.com/api/v3/chat/completions"

# ========== 专家提示词（合并错误与改进建议） ==========
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
- 如果 4 个步骤全部正确且无明显错误，必须明确写出："你的方案完整正确，按照此流程可以成功培育出无籽西瓜！"

## 💡 诊断与改进建议
- 请对比**标准育种流程**（二倍体母本→秋水仙素加倍→四倍体母本×二倍体父本→三倍体种子→播种得三倍体植株→二倍体花粉刺激→无籽西瓜）与学生**当前方案的差距**。
- 如果学生在流程图中存在**具体的科学性错误**，请先明确指出错误所在，再给出改进方向。例如：
  - "你写的是'二倍体（2n）经减数分裂产生2n的配子'，这里有个小bug：减数分裂后染色体数目应该减半，所以配子应该是n而不是2n。如何修正这个数目，才能让后续杂交得到正确的后代呢？"
  - "你的流程里两个n的配子结合直接产生了3n个体，但n+n=2n。如何设计杂交组合，才能得到3n的三倍体呢？"
  - "你把秋水仙素处理的对象标成了父本，但父本不需要加倍。如何调整处理对象，才能正确得到四倍体母本？"
  - "你的三倍体植株没有接受花粉刺激就结果了，但三倍体自己不能产生正常花粉。如何让它结出无籽西瓜呢？花粉应该来自几倍体植株？"
- 如果学生只是**遗漏了某个关键环节**（没有画出来，但没有写错），请用**"如何做到……"**的启发式问句引导补全。例如：
  - "你的流程直接从'三倍体种子'跳到了'三倍体西瓜'，中间缺少了播种栽培的环节。如何体现从种子到植株再到果实的过程呢？"
  - "你的方案里没有体现花粉刺激这一步。如何让三倍体植株的子房发育成果实呢？"
- 语气亲切，像老师拿着学生的流程图，一边指着具体位置一边启发他思考。

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

# ========== 会话隔离 ==========
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": SYSTEM_PROMPT}]

# ========== 顶部标题（无多余框，西瓜装饰） ==========
st.markdown("""
<div style="display:flex;align-items:center;justify-content:center;gap:12px;margin-bottom:2px;">
    <div class="watermelon-deco">🍉</div>
    <h1 style="margin:0;">无籽西瓜育种方案 · AI实验室</h1>
    <div class="watermelon-deco">🍉</div>
</div>
""", unsafe_allow_html=True)
st.markdown('<div class="subtitle">上传手绘育种流程图，AI育种专家即时诊断</div>', unsafe_allow_html=True)

# ========== 上传与提交合并为一张卡片 ==========
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
            st.markdown(f'<div style="color:#64748b;font-size:0.8rem;">原始大小</div>', unsafe_allow_html=True)
            st.markdown(f'<div style="color:#0891b2;font-size:1.1rem;font-weight:700;">{raw_size:.0f} KB</div>', unsafe_allow_html=True)
            st.markdown('<div style="color:#94a3b8;font-size:0.7rem;margin-top:4px;">✓ 已自动压缩</div>', unsafe_allow_html=True)
    
    st.markdown('<div style="margin-top:12px;">', unsafe_allow_html=True)
    submit_btn = st.button("🚀 启动 AI 诊断系统")
    st.markdown('</div>', unsafe_allow_html=True)
    
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

# ========== 提交处理 ==========
if submit_btn:
    if not uploaded_file:
        st.error("⚠️ 请先拍照或选择图片上传育种方案")
    else:
        raw_bytes = uploaded_file.getvalue()
        compressed_bytes = compress_image(raw_bytes, max_size=1200, quality=85)
        compressed_size = len(compressed_bytes) / 1024
        
        img_b64 = base64.b64encode(compressed_bytes).decode()
        img_url = f"data:image/jpeg;base64,{img_b64}"
        
        user_content = [
            {"type": "image_url", "image_url": {"url": img_url}},
            {"type": "text", "text": "这是我设计的无籽西瓜育种方案手绘图/流程图。请严格按照系统提示的4个关键检查点和输出框架进行点评。"}
        ]
        st.session_state.messages.append({"role": "user", "content": user_content})
        
        with st.spinner("⏳ AI 专家正在分析你的育种方案，请稍候..."):
            try:
                resp = requests.post(
                    API_URL,
                    headers={
                        "Authorization": f"Bearer {API_KEY}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "doubao-seed-2-0-pro-260215",
                        "messages": st.session_state.messages,
                        "temperature": 0.4,
                        "max_tokens": 4000
                    },
                    timeout=120
                )
                resp.raise_for_status()
                data = resp.json()
                reply = data["choices"][0]["message"]["content"]
                st.session_state.messages.append({"role": "assistant", "content": reply})
                
                st.markdown(f"""
                <div class="success-box">
                    <div style="font-weight:700;color:#047857;margin-bottom:4px;">✅ 诊断完成</div>
                    <div style="font-size:0.8rem;color:#065f46;">图片压缩后 {compressed_size:.0f} KB · 分析完毕</div>
                </div>
                """, unsafe_allow_html=True)
                
            except requests.exceptions.Timeout:
                st.error("⏱️ 请求超时：网络较慢或图片过大。建议靠近 WiFi 路由器后重试。")
            except Exception as e:
                st.error(f"❌ AI 请求失败: {e}")

# ========== 显示专家点评 ==========
if len(st.session_state.messages) > 1:
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

for msg in st.session_state.messages:
    if msg["role"] == "assistant":
        with st.chat_message("assistant", avatar="🧑‍🔬"):
            st.markdown(msg["content"])

# ========== 继续追问 ==========
if len(st.session_state.messages) > 1:
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    st.markdown('<div style="color:#475569;font-size:0.85rem;margin-bottom:8px;text-align:center;">💬 对诊断有疑问？继续向专家提问</div>', unsafe_allow_html=True)
    
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
                        "model": "doubao-seed-2-0-pro-260215",
                        "messages": st.session_state.messages,
                        "temperature": 0.4,
                        "max_tokens": 4000
                    },
                    timeout=120
                )
                data = resp.json()
                reply = data["choices"][0]["message"]["content"]
                st.session_state.messages.append({"role": "assistant", "content": reply})
                st.rerun()
            except Exception as e:
                st.error(f"❌ 请求失败: {e}")
