import streamlit as st
import requests
import base64
from PIL import Image
import io

# ========== 页面设置 ==========
st.set_page_config(page_title="🧬 无籽西瓜育种方案 · AI实验室", page_icon="🧬", layout="centered")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&family=Noto+Sans+SC:wght@300;400;500;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Noto Sans SC', sans-serif;
    background: #f8fafc;
    color: #0f172a;
}

.stApp {
    background: 
        radial-gradient(circle at 10% 20%, rgba(6, 182, 212, 0.04) 0%, transparent 20%),
        radial-gradient(circle at 90% 80%, rgba(139, 92, 246, 0.04) 0%, transparent 20%),
        linear-gradient(180deg, #f0f9ff 0%, #f8fafc 50%, #ffffff 100%);
    background-attachment: fixed;
}

/* 科技网格背景 */
.stApp::before {
    content: "";
    position: fixed;
    top: 0; left: 0; right: 0; bottom: 0;
    background-image: 
        linear-gradient(rgba(6, 182, 212, 0.03) 1px, transparent 1px),
        linear-gradient(90deg, rgba(6, 182, 212, 0.03) 1px, transparent 1px);
    background-size: 50px 50px;
    pointer-events: none;
    z-index: 0;
}

/* 标题样式 - 科技渐变 */
h1 {
    font-family: 'Orbitron', 'Noto Sans SC', sans-serif !important;
    background: linear-gradient(135deg, #0891b2, #7c3aed, #db2777);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    text-align: center;
    font-size: 2rem !important;
    font-weight: 700 !important;
    margin-bottom: 0.5rem !important;
    letter-spacing: 1px;
    text-shadow: none !important;
}

.subtitle {
    text-align: center;
    color: #64748b;
    font-size: 0.9rem;
    margin-bottom: 2rem;
    letter-spacing: 2px;
}

/* 玻璃卡片 - 科技感 */
.glass-card {
    background: rgba(255, 255, 255, 0.85);
    backdrop-filter: blur(12px);
    border: 1px solid rgba(226, 232, 240, 0.8);
    border-radius: 16px;
    padding: 28px;
    margin-bottom: 20px;
    box-shadow: 
        0 4px 20px rgba(0, 0, 0, 0.06),
        0 0 0 1px rgba(255, 255, 255, 0.5) inset;
    position: relative;
    overflow: hidden;
}

/* 卡片角落装饰 */
.glass-card::before {
    content: "";
    position: absolute;
    top: 0; left: 0;
    width: 40px; height: 40px;
    border-top: 2px solid #06b6d4;
    border-left: 2px solid #06b6d4;
    border-radius: 16px 0 0 0;
    opacity: 0.6;
}

.glass-card::after {
    content: "";
    position: absolute;
    bottom: 0; right: 0;
    width: 40px; height: 40px;
    border-bottom: 2px solid #8b5cf6;
    border-right: 2px solid #8b5cf6;
    border-radius: 0 0 16px 0;
    opacity: 0.6;
}

/* 发光边框卡片 */
.glow-border {
    border: 1px solid rgba(6, 182, 212, 0.4);
    box-shadow: 
        0 0 20px rgba(6, 182, 212, 0.1),
        0 4px 20px rgba(0, 0, 0, 0.06),
        inset 0 0 20px rgba(6, 182, 212, 0.03);
}

/* 扫描线动画 */
.scan-line {
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, transparent, #06b6d4, transparent);
    opacity: 0.6;
    animation: scan 3s linear infinite;
    pointer-events: none;
}

@keyframes scan {
    0% { top: 0; opacity: 0; }
    10% { opacity: 0.6; }
    90% { opacity: 0.6; }
    100% { top: 100%; opacity: 0; }
}

/* 按钮 - 科技发光 */
.stButton button {
    background: linear-gradient(135deg, #0891b2, #2563eb, #7c3aed) !important;
    background-size: 200% 200% !important;
    color: white !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 16px 28px !important;
    font-weight: 700 !important;
    font-size: 1.1rem !important;
    width: 100% !important;
    letter-spacing: 1px !important;
    transition: all 0.3s ease !important;
    box-shadow: 0 4px 20px rgba(37, 99, 235, 0.3) !important;
    position: relative;
    overflow: hidden;
}

.stButton button:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 30px rgba(37, 99, 235, 0.5) !important;
    background-position: right center !important;
}

/* 按钮闪光效果 */
.stButton button::after {
    content: "";
    position: absolute;
    top: -50%;
    left: -50%;
    width: 200%;
    height: 200%;
    background: linear-gradient(
        45deg,
        transparent 30%,
        rgba(255, 255, 255, 0.1) 50%,
        transparent 70%
    );
    transform: rotate(45deg);
    transition: all 0.5s;
}

.stButton button:hover::after {
    left: 100%;
}

/* 文件上传器 - 科技虚线框 */
.stFileUploader {
    background: rgba(248, 250, 252, 0.8) !important;
    border: 2px dashed rgba(6, 182, 212, 0.5) !important;
    border-radius: 14px !important;
    padding: 32px 24px !important;
    transition: all 0.3s ease !important;
}

.stFileUploader:hover {
    border-color: #0891b2 !important;
    background: rgba(240, 249, 255, 0.9) !important;
    box-shadow: 0 0 20px rgba(6, 182, 212, 0.15) !important;
}

/* 聊天消息 */
.stChatMessage {
    background: rgba(255, 255, 255, 0.9) !important;
    border-radius: 14px !important;
    border: 1px solid rgba(226, 232, 240, 0.8) !important;
    box-shadow: 0 4px 12px rgba(0,0,0,0.05) !important;
}

[data-testid="stChatMessageAvatar"] {
    background: linear-gradient(135deg, #0891b2, #7c3aed) !important;
    box-shadow: 0 2px 8px rgba(124, 58, 237, 0.3) !important;
}

/* 成功提示 */
.success-box {
    background: linear-gradient(135deg, #ecfdf5, #d1fae5);
    border-left: 4px solid #10b981;
    border-radius: 10px;
    padding: 16px 20px;
    margin: 16px 0;
    color: #064e3b;
    box-shadow: 0 4px 12px rgba(16, 185, 129, 0.1);
}

/* 分隔线 */
.divider {
    height: 1px;
    background: linear-gradient(90deg, transparent, #06b6d4, #8b5cf6, transparent);
    margin: 24px 0;
    opacity: 0.4;
}

/* 状态标签 */
.status-badge {
    display: inline-block;
    background: linear-gradient(135deg, #e0f2fe, #ddd6fe);
    color: #0369a1;
    border-radius: 20px;
    padding: 4px 14px;
    font-size: 0.8rem;
    font-weight: 600;
    border: 1px solid rgba(6, 182, 212, 0.2);
}

/* 修复文件上传器文字 */
.stFileUploader span, .stFileUploader small, .stFileUploader div {
    color: #475569 !important;
}

.stSpinner > div {
    color: #0891b2 !important;
}

.stChatInput input {
    background: #ffffff !important;
    border: 1px solid #cbd5e1 !important;
    color: #0f172a !important;
    border-radius: 10px !important;
}

/* 滚动条美化 */
::-webkit-scrollbar {
    width: 8px;
}
::-webkit-scrollbar-track {
    background: #f1f5f9;
    border-radius: 4px;
}
::-webkit-scrollbar-thumb {
    background: linear-gradient(180deg, #06b6d4, #8b5cf6);
    border-radius: 4px;
}
</style>
""", unsafe_allow_html=True)

# ========== 豆包（火山引擎方舟）配置 ==========
API_KEY = "ark-56337a36-0306-47f2-b77e-fc67e7c8dd49-adebf"
API_URL = "https://ark.cn-beijing.volces.com/api/v3/chat/completions"

# ========== 专家提示词 ==========
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

## ⚠️ 错误
- 请仔细审视学生**已经画出来的流程图或写出来的方案中**，是否存在**具体的科学性错误**。例如：
  - 是否把"二倍体（2n）经减数分裂"错误地写成了产生"2n的配子"？（减数分裂后配子应该是n）
  - 是否把"两个n的配子结合"错误地直接写成了产生"3n的个体"？（n+n=2n，不是3n）
  - 是否把"秋水仙素处理"的对象搞错了（比如处理了父本而不是母本）？
  - 是否把"四倍体母本 × 二倍体父本"写反了？
  - 是否出现了"三倍体植株自己能产生正常花粉"或"三倍体自交"这类错误？
  - 流程图中是否出现了箭头指向错误、染色体数目标注错误、阶段顺序颠倒等硬伤？
- **错误描述要具体**：指出"你在流程图的哪一步写了什么"，以及"这为什么不符合生物学事实"。
- 如果未发现明显错误，写："未发现明显错误。"

## 💡 改进建议
- 请对比**标准育种流程**（二倍体母本→秋水仙素加倍→四倍体母本×二倍体父本→三倍体种子→播种得三倍体植株→二倍体花粉刺激→无籽西瓜）与学生**当前方案的差距**。
- 针对学生遗漏或做错的环节，用**"如何做到……"**的启发式问句引导学生思考修正方向。例如：
  - "你的方案里母本还是二倍体，**如何**让它变成四倍体，才能与二倍体父本杂交出三倍体后代呢？"
  - "你写的是两个n配子结合得到了3n个体，但n+n=2n，**如何**才能得到3n的后代呢？"
  - "你的流程图里直接画出了'三倍体西瓜'，但杂交后先得到的是三倍体种子，**如何**才能从种子变成结西瓜的植株呢？"
  - "你的三倍体植株似乎没有接受花粉刺激就结果了，**如何**才能让子房发育成果实呢？这个花粉应该来自几倍体？"
  - "你标注的配子染色体数目是2n，但减数分裂后染色体数目应该减半，**如何**修正这个数目才能符合减数分裂的规律？"
- 语气亲切，像老师在课堂上拿着学生的流程图，一边指着具体位置一边启发他思考。

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

# ========== 科技标题 ==========
st.markdown("""
<div style="text-align:center;margin-bottom:8px;">
    <span style="font-size:2.5rem;">🧬</span>
</div>
""", unsafe_allow_html=True)
st.markdown('<h1>无籽西瓜育种方案 · AI实验室</h1>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">◆ 上传手绘育种流程图 · 启动智能诊断系统 ◆</div>', unsafe_allow_html=True)

# ========== 图片上传 ==========
with st.container():
    st.markdown('<div class="glass-card glow-border" style="position:relative;">', unsafe_allow_html=True)
    st.markdown('<div class="scan-line"></div>', unsafe_allow_html=True)
    
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
            st.markdown(f'<div style="color:#64748b;font-size:0.85rem;margin-top:10px;">原始大小</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="status-badge">{raw_size:.0f} KB</div>', unsafe_allow_html=True)
            st.markdown('<div style="color:#94a3b8;font-size:0.75rem;margin-top:12px;">✓ 已自动压缩优化</div>', unsafe_allow_html=True)
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

# ========== 提交按钮 ==========
with st.container():
    st.markdown('<div class="glass-card" style="text-align:center;">', unsafe_allow_html=True)
    submit_btn = st.button("🚀 启动 AI 诊断系统")
    st.markdown('</div>', unsafe_allow_html=True)

if submit_btn:
    if not uploaded_file:
        st.error("⚠️ 请先拍照或选择图片上传育种方案")
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
            {"type": "text", "text": "这是我设计的无籽西瓜育种方案手绘图/流程图。请严格按照系统提示的4个关键检查点和输出框架进行点评。"}
        ]
        st.session_state.messages.append({"role": "user", "content": user_content})
        
        # 调用豆包（火山引擎方舟）API
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
                    <div style="font-size:0.85rem;color:#065f46;">图片压缩后 {compressed_size:.0f} KB · 分析完毕</div>
                </div>
                """, unsafe_allow_html=True)
                
            except requests.exceptions.Timeout:
                st.error("⏱️ 请求超时：网络较慢或图片过大。建议靠近 WiFi 路由器后重试。")
            except Exception as e:
                st.error(f"❌ AI 请求失败: {e}")

# ========== 显示专家点评 ==========
st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

for msg in st.session_state.messages:
    if msg["role"] == "assistant":
        with st.chat_message("assistant", avatar="🧑‍🔬"):
            st.markdown(msg["content"])

# ========== 继续追问 ==========
if len(st.session_state.messages) > 1:
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    st.markdown('<div style="color:#475569;font-size:0.9rem;margin-bottom:8px;text-align:center;">💬 对点评有疑问？继续向专家提问</div>', unsafe_allow_html=True)
    
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
