import streamlit as st
import requests
import json
import time

# ── Page Config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="LexiMini AI — Indian Legal Assistant",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;700;900&family=DM+Sans:wght@300;400;500&display=swap');

:root {
    --ink:      #0d0d0d;
    --parchment:#f5f0e8;
    --gold:     #c9a84c;
    --deep:     #1a1a2e;
    --rust:     #8b3a3a;
    --cream:    #faf7f2;
    --border:   #d4c9b0;
}

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    background-color: var(--cream);
    color: var(--ink);
}

/* Hide default streamlit elements */
#MainMenu, footer, header {visibility: hidden;}
.block-container {padding-top: 1rem; max-width: 1200px;}

/* ── Header ── */
.lexi-header {
    text-align: center;
    padding: 2.5rem 1rem 1.5rem;
    border-bottom: 2px solid var(--gold);
    margin-bottom: 2rem;
    position: relative;
}
.lexi-header::before {
    content: "⚖";
    font-size: 3rem;
    display: block;
    margin-bottom: 0.5rem;
    filter: sepia(1);
}
.lexi-title {
    font-family: 'Playfair Display', serif;
    font-size: 2.8rem;
    font-weight: 900;
    color: var(--deep);
    letter-spacing: -1px;
    line-height: 1;
    margin: 0;
}
.lexi-subtitle {
    font-size: 0.95rem;
    color: #666;
    margin-top: 0.5rem;
    font-weight: 300;
    letter-spacing: 2px;
    text-transform: uppercase;
}
.lexi-badge {
    display: inline-block;
    background: var(--gold);
    color: white;
    font-size: 0.7rem;
    padding: 3px 10px;
    border-radius: 20px;
    margin-top: 0.5rem;
    letter-spacing: 1px;
    font-weight: 500;
}

/* ── Chat messages ── */
.user-msg {
    background: var(--deep);
    color: white;
    padding: 1rem 1.25rem;
    border-radius: 16px 16px 4px 16px;
    margin: 0.75rem 0 0.75rem 3rem;
    font-size: 0.95rem;
    line-height: 1.6;
    box-shadow: 0 2px 8px rgba(0,0,0,0.15);
}
.bot-msg {
    background: white;
    color: var(--ink);
    padding: 1.25rem 1.5rem;
    border-radius: 16px 16px 16px 4px;
    margin: 0.75rem 3rem 0.75rem 0;
    font-size: 0.95rem;
    line-height: 1.7;
    border-left: 3px solid var(--gold);
    box-shadow: 0 2px 12px rgba(0,0,0,0.08);
}
.msg-label {
    font-size: 0.7rem;
    font-weight: 500;
    letter-spacing: 1px;
    text-transform: uppercase;
    margin-bottom: 0.4rem;
    opacity: 0.6;
}
.bot-label { color: var(--gold); }
.user-label { color: rgba(255,255,255,0.7); }

/* ── Sidebar ── */
section[data-testid="stSidebar"] {
    background: var(--deep) !important;
    border-right: 1px solid rgba(201,168,76,0.3);
}
section[data-testid="stSidebar"] * {
    color: var(--parchment) !important;
}
section[data-testid="stSidebar"] .stButton>button {
    background: rgba(201,168,76,0.15) !important;
    border: 1px solid var(--gold) !important;
    color: var(--gold) !important;
    width: 100%;
    border-radius: 8px;
    font-size: 0.85rem;
    margin-bottom: 0.3rem;
    transition: all 0.2s;
}
section[data-testid="stSidebar"] .stButton>button:hover {
    background: var(--gold) !important;
    color: var(--deep) !important;
}

/* ── Input ── */
.stTextArea textarea {
    background: white !important;
    border: 1.5px solid var(--border) !important;
    border-radius: 12px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.95rem !important;
    color: var(--ink) !important;
    padding: 0.75rem 1rem !important;
}
.stTextArea textarea:focus {
    border-color: var(--gold) !important;
    box-shadow: 0 0 0 3px rgba(201,168,76,0.15) !important;
}

/* ── Send button ── */
.stButton>button[kind="primary"] {
    background: var(--deep) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 0.6rem 2rem !important;
    font-weight: 500 !important;
    font-size: 0.95rem !important;
    letter-spacing: 0.5px !important;
    transition: all 0.2s !important;
}
.stButton>button[kind="primary"]:hover {
    background: var(--gold) !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 12px rgba(201,168,76,0.4) !important;
}

/* ── Info cards ── */
.info-card {
    background: white;
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1rem 1.25rem;
    margin-bottom: 0.75rem;
    font-size: 0.85rem;
    line-height: 1.6;
}
.info-card strong {
    color: var(--rust);
    display: block;
    margin-bottom: 0.25rem;
    font-size: 0.8rem;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

/* ── Disclaimer ── */
.disclaimer {
    background: #fff8e7;
    border: 1px solid var(--gold);
    border-radius: 10px;
    padding: 0.75rem 1rem;
    font-size: 0.8rem;
    color: #7a6030;
    margin-top: 1.5rem;
    text-align: center;
}

/* ── Spinner ── */
.stSpinner > div { border-top-color: var(--gold) !important; }

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: var(--cream); }
::-webkit-scrollbar-thumb { background: var(--border); border-radius: 3px; }
</style>
""", unsafe_allow_html=True)

# ── Config ────────────────────────────────────────────────────────────────────
# Ollama ya vLLM endpoint — model serve hone ke baad yahan set karo
OLLAMA_URL  = "http://localhost:11434/api/generate"
MODEL_NAME  = "leximini"   # ollama run leximini

SYSTEM_PROMPT = """You are LexiMini — a precise and helpful AI legal assistant specialized in Indian law.
You are trained on Indian legal codes including BNS (Bharatiya Nyaya Sanhita), BNSS (Bharatiya Nagarik Suraksha Sanhita), BSA (Bharatiya Sakshya Adhiniyam), IPC, CrPC, family law, labour law, property law, and constitutional law.

Guidelines:
- Give specific section numbers and act names when relevant
- Answer in the same language as the question (Hindi or English)
- Be clear, accurate, and practical
- Always mention enforcement authority when applicable
- Add a note that this is for informational purposes and not legal advice for complex cases"""

SAMPLE_QUESTIONS = {
    "🏛️ Criminal Law": "What are my rights if arrested without a warrant under BNSS?",
    "👨‍👩‍👧 Family Law": "Divorce procedure under Hindu Marriage Act — what are the grounds?",
    "💼 Labour Rights": "What are my rights if fired without notice under labour law?",
    "🏠 Property Law": "How to register a property sale deed in India?",
    "📜 Will & Succession": "How to make a valid Will under Indian Succession Act?",
    "⚖️ Constitutional": "What are Fundamental Rights under Article 19 of the Constitution?",
}

# ── Session State ─────────────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []
if "model_mode" not in st.session_state:
    st.session_state.model_mode = "ollama"

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### ⚖️ LexiMini AI")
    st.markdown("---")

    st.markdown("**Model Settings**")
    model_mode = st.radio(
        "Backend",
        ["Ollama (Local)", "vLLM (Server)", "Demo Mode"],
        index=2,
        label_visibility="collapsed"
    )

    if model_mode == "Ollama (Local)":
        ollama_url = st.text_input("Ollama URL", value="http://localhost:11434")
        model_name = st.text_input("Model Name", value="leximini")
    elif model_mode == "vLLM (Server)":
        vllm_url = st.text_input("vLLM URL", value="http://localhost:8000")
        model_name = st.text_input("Model Name", value="leximini-1b")

    st.markdown("---")
    st.markdown("**Sample Questions**")
    for label, question in SAMPLE_QUESTIONS.items():
        if st.button(label, key=label):
            st.session_state.pending_question = question

    st.markdown("---")
    if st.button("🗑️ Clear Chat"):
        st.session_state.messages = []
        st.rerun()

    st.markdown("""
    <div style='margin-top:2rem; opacity:0.5; font-size:0.75rem;'>
    <strong>Model:</strong> Gemma 3 1B (Distilled)<br>
    <strong>Trained on:</strong> Indian Laws 2026<br>
    <strong>Framework:</strong> Google Tunix
    </div>
    """, unsafe_allow_html=True)

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="lexi-header">
    <div class="lexi-title">LexiMini AI</div>
    <div class="lexi-subtitle">Indian Legal Intelligence</div>
    <span class="lexi-badge">Powered by Gemma · Fine-tuned on Indian Law</span>
</div>
""", unsafe_allow_html=True)

# ── Chat History ──────────────────────────────────────────────────────────────
chat_container = st.container()

with chat_container:
    if not st.session_state.messages:
        st.markdown("""
        <div class="info-card">
            <strong>Welcome to LexiMini</strong>
            Ask any question about Indian law — criminal, civil, family, labour, property, or constitutional.
            I can answer in Hindi or English.
        </div>
        <div class="info-card">
            <strong>Example Questions</strong>
            • Bina warrant ke giraftaar kiya jaye toh kya karein?<br>
            • What is the punishment under BNS Section 103?<br>
            • How to file for divorce under Hindu Marriage Act?
        </div>
        """, unsafe_allow_html=True)
    else:
        for msg in st.session_state.messages:
            if msg["role"] == "user":
                st.markdown(f"""
                <div class="user-msg">
                    <div class="msg-label user-label">You</div>
                    {msg["content"]}
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="bot-msg">
                    <div class="msg-label bot-label">LexiMini</div>
                    {msg["content"]}
                </div>
                """, unsafe_allow_html=True)

# ── Input ─────────────────────────────────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)

# Sample question se auto-fill
default_val = ""
if "pending_question" in st.session_state:
    default_val = st.session_state.pending_question
    del st.session_state.pending_question

col1, col2 = st.columns([5, 1])
with col1:
    user_input = st.text_area(
        "Ask your legal question...",
        value=default_val,
        placeholder="e.g. What are my rights under BNSS Section 47?",
        height=80,
        label_visibility="collapsed",
        key="user_input"
    )
with col2:
    st.markdown("<br>", unsafe_allow_html=True)
    send = st.button("Send ⚖️", type="primary", use_container_width=True)

# ── Response Logic ────────────────────────────────────────────────────────────
def get_demo_response(question):
    """Demo mode — actual model load hone tak placeholder response"""
    q = question.lower()
    if "arrest" in q or "giraftaar" in q or "warrant" in q:
        return """Under BNSS Section 47-60 (Bharatiya Nagarik Suraksha Sanhita):

**Your Rights on Arrest:**
• Police must inform you of the reason for arrest
• Right to inform a family member or friend immediately
• Right to consult a lawyer of your choice
• Must be produced before Magistrate within 24 hours

**Enforcement Authority:** Magistrate Court

*Note: This is informational. For specific legal advice, consult a qualified advocate.*"""
    elif "bns" in q or "section 103" in q:
        return """Under BNS Section 103 (Bharatiya Nyaya Sanhita — Murder):

**Key Provisions:**
• Punishment for murder: Death penalty or life imprisonment + fine
• Applies to: Any person who commits murder as defined under BNS

**Enforcement Authority:** Sessions Court

*Note: This is informational. Consult a criminal lawyer for case-specific advice.*"""
    elif "divorce" in q or "talaq" in q:
        return """Under Hindu Marriage Act, 1955 — Grounds for Divorce (Section 13):

**Grounds include:**
• Adultery
• Cruelty (mental or physical)
• Desertion for 2+ years
• Conversion to another religion
• Mental disorder
• Mutual consent (Section 13B) — 1 year separation required

**Enforcement Authority:** Family Court / District Court

*Note: Consult a family lawyer for your specific situation.*"""
    else:
        return f"""I understand your question about Indian law. 

⚠️ **Demo Mode Active** — Connect Ollama or vLLM with the fine-tuned LexiMini model for accurate legal responses.

To use the actual model:
1. Install Ollama: `curl -fsSL https://ollama.ai/install.sh | sh`
2. Run: `ollama run leximini`
3. Select "Ollama (Local)" in sidebar

*This is informational content only, not legal advice.*"""

def get_ollama_response(question, url, model):
    try:
        prompt = f"<start_of_turn>user\n{SYSTEM_PROMPT}\n\n{question}<end_of_turn>\n<start_of_turn>model\n"
        response = requests.post(
            f"{url}/api/generate",
            json={"model": model, "prompt": prompt, "stream": False},
            timeout=60
        )
        if response.status_code == 200:
            return response.json().get("response", "Error: No response")
        return f"Error: {response.status_code}"
    except Exception as e:
        return f"Connection error: {e}\n\nMake sure Ollama is running with: `ollama run {model}`"

def get_vllm_response(question, url, model):
    try:
        prompt = f"<start_of_turn>user\n{SYSTEM_PROMPT}\n\n{question}<end_of_turn>\n<start_of_turn>model\n"
        response = requests.post(
            f"{url}/v1/completions",
            json={"model": model, "prompt": prompt, "max_tokens": 400, "temperature": 0.7},
            timeout=60
        )
        if response.status_code == 200:
            return response.json()["choices"][0]["text"]
        return f"Error: {response.status_code}"
    except Exception as e:
        return f"Connection error: {e}"

if send and user_input.strip():
    st.session_state.messages.append({"role": "user", "content": user_input})

    with st.spinner("Consulting legal database..."):
        time.sleep(0.3)
        if model_mode == "Demo Mode":
            reply = get_demo_response(user_input)
        elif model_mode == "Ollama (Local)":
            reply = get_ollama_response(user_input, ollama_url, model_name)
        else:
            reply = get_vllm_response(user_input, vllm_url, model_name)

    st.session_state.messages.append({"role": "assistant", "content": reply})
    st.rerun()

# ── Disclaimer ────────────────────────────────────────────────────────────────
st.markdown("""
<div class="disclaimer">
    ⚠️ LexiMini AI is for informational purposes only. It is not a substitute for professional legal advice.
    Always consult a qualified advocate for your specific legal situation.
</div>
""", unsafe_allow_html=True)