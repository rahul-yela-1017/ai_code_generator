import streamlit as st
import requests
import json
import os
import re
from datetime import datetime
from pathlib import Path

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AI Code Generator",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&family=Syne:wght@400;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Syne', sans-serif;
    background-color: #0d0f14;
    color: #e2e8f0;
}

.stApp { background-color: #0d0f14; }

.main-title {
    font-family: 'Syne', sans-serif;
    font-weight: 800;
    font-size: 2.6rem;
    background: linear-gradient(135deg, #38bdf8, #818cf8);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 0.2rem;
}

.subtitle {
    color: #64748b;
    font-size: 0.95rem;
    margin-bottom: 1.5rem;
}

.section-label {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.75rem;
    color: #38bdf8;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    margin-bottom: 0.4rem;
}

.status-ok  { color: #34d399; font-size: 0.85rem; }
.status-err { color: #f87171; font-size: 0.85rem; }

textarea, .stTextArea textarea {
    font-family: 'JetBrains Mono', monospace !important;
    background: #141720 !important;
    color: #e2e8f0 !important;
    border: 1px solid #1e2535 !important;
    border-radius: 8px !important;
}

.stSelectbox > div > div {
    background: #141720 !important;
    color: #e2e8f0 !important;
    border: 1px solid #1e2535 !important;
    border-radius: 8px !important;
}

.stButton > button {
    background: linear-gradient(135deg, #0ea5e9, #6366f1);
    color: white;
    border: none;
    border-radius: 8px;
    font-family: 'Syne', sans-serif;
    font-weight: 700;
    padding: 0.55rem 1.6rem;
    font-size: 0.95rem;
    transition: opacity 0.2s;
}
.stButton > button:hover { opacity: 0.85; }

.code-block {
    background: #141720;
    border: 1px solid #1e2535;
    border-radius: 10px;
    padding: 1.2rem;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.82rem;
    color: #a5f3fc;
    white-space: pre-wrap;
    word-break: break-word;
    overflow-x: auto;
    max-height: 420px;
    overflow-y: auto;
}

.explain-block {
    background: #0f1621;
    border-left: 3px solid #6366f1;
    border-radius: 0 10px 10px 0;
    padding: 1.2rem;
    font-size: 0.9rem;
    line-height: 1.7;
    color: #cbd5e1;
    max-height: 420px;
    overflow-y: auto;
}

.debug-block {
    background: #0f1621;
    border-left: 3px solid #f59e0b;
    border-radius: 0 10px 10px 0;
    padding: 1.2rem;
    font-size: 0.9rem;
    line-height: 1.7;
    color: #fde68a;
    max-height: 300px;
    overflow-y: auto;
}

.saved-badge {
    display: inline-block;
    background: #052e16;
    color: #34d399;
    border-radius: 6px;
    padding: 0.25rem 0.8rem;
    font-size: 0.8rem;
    font-family: 'JetBrains Mono', monospace;
    margin-top: 0.4rem;
}

.stTabs [data-baseweb="tab-list"] { gap: 6px; }
.stTabs [data-baseweb="tab"] {
    background: #141720;
    border-radius: 8px 8px 0 0;
    color: #64748b;
    font-family: 'Syne', sans-serif;
    font-weight: 700;
}
.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, #0ea5e9, #6366f1) !important;
    color: white !important;
}

.stSidebar { background: #0a0c10 !important; }
.stSidebar [data-testid="stMarkdownContainer"] { color: #94a3b8; }
hr { border-color: #1e2535; }
</style>
""", unsafe_allow_html=True)

# ── Constants ─────────────────────────────────────────────────────────────────
OLLAMA_URL   = "http://localhost:11434"
SAVED_DIR    = Path("saved_code")
SAVED_DIR.mkdir(exist_ok=True)

MODELS = {
    "deepseek-coder:1.3b  (fastest, ~800 MB)": "deepseek-coder:1.3b",
    "deepseek-coder:6.7b  (balanced, ~3.8 GB)": "deepseek-coder:6.7b",
    "codellama:7b          (general, ~3.8 GB)": "codellama:7b",
    "codellama:code        (instruct, ~3.8 GB)": "codellama:code",
    "phi3:mini             (tiny, ~2.3 GB)":     "phi3:mini",
}

LANGUAGES = ["Python", "Java", "C++", "JavaScript", "Bash", "SQL"]

EXT_MAP = {
    "Python": "py", "Java": "java", "C++": "cpp",
    "JavaScript": "js", "Bash": "sh", "SQL": "sql",
}

# ── Helpers ───────────────────────────────────────────────────────────────────

def ollama_running() -> bool:
    try:
        r = requests.get(f"{OLLAMA_URL}/api/tags", timeout=3)
        return r.status_code == 200
    except Exception:
        return False


def list_local_models() -> list[str]:
    try:
        r = requests.get(f"{OLLAMA_URL}/api/tags", timeout=5)
        data = r.json()
        return [m["name"] for m in data.get("models", [])]
    except Exception:
        return []


def stream_ollama(model: str, prompt: str) -> str:
    payload = {"model": model, "prompt": prompt, "stream": True}
    full = ""
    try:
        with requests.post(f"{OLLAMA_URL}/api/generate",
                           json=payload, stream=True, timeout=180) as resp:
            placeholder = st.empty()
            for line in resp.iter_lines():
                if line:
                    chunk = json.loads(line)
                    full += chunk.get("response", "")
                    placeholder.markdown(
                        f'<div class="code-block">{full}</div>',
                        unsafe_allow_html=True,
                    )
                    if chunk.get("done"):
                        break
    except requests.exceptions.ConnectionError:
        st.error("Cannot reach Ollama. Make sure `ollama serve` is running.")
    return full


def build_code_prompt(user_prompt: str, language: str) -> str:
    return f"""You are an expert {language} programmer.
Task: {user_prompt}

Rules:
- Write ONLY clean, well-commented {language} code.
- Do NOT include any explanation outside the code block.
- Use a single ```{language.lower()} ... ``` fenced block.
- Keep the solution concise but complete.

```{language.lower()}"""


def build_explain_prompt(code: str, language: str) -> str:
    return f"""You are a senior {language} developer and teacher.
Explain the following {language} code step by step in simple English.
Be concise. Use numbered points. Focus on what each section does and why.

Code:
```{language.lower()}
{code}
```

Explanation (numbered steps):"""


def build_debug_prompt(code: str, language: str) -> str:
    return f"""You are a {language} code reviewer.
Analyse the following code and list:
1. Potential bugs or errors
2. Edge cases not handled
3. One concrete suggestion to improve robustness

Code:
```{language.lower()}
{code}
```

Review:"""


def extract_code(raw: str, language: str) -> str:
    """Pull the code block out of the model reply."""
    # Try fenced block first
    pattern = rf"```(?:{language.lower()}|{language}|)\n?(.*?)```"
    match = re.search(pattern, raw, re.DOTALL | re.IGNORECASE)
    if match:
        return match.group(1).strip()
    # Fallback: return everything
    return raw.strip()


def save_code(code: str, language: str, prompt: str) -> Path:
    ts   = datetime.now().strftime("%Y%m%d_%H%M%S")
    slug = re.sub(r"\W+", "_", prompt[:30]).strip("_")
    ext  = EXT_MAP.get(language, "txt")
    path = SAVED_DIR / f"{slug}_{ts}.{ext}"
    path.write_text(code, encoding="utf-8")
    return path


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("##  AI Code Generator")
    st.markdown("---")

    # Ollama status
    running = ollama_running()
    if running:
        st.markdown('<p class="status-ok">● Ollama running</p>', unsafe_allow_html=True)
    else:
        st.markdown('<p class="status-err">● Ollama offline</p>', unsafe_allow_html=True)
        st.info("Run `ollama serve` in a terminal to start Ollama.")

    st.markdown("---")

    # Model selector – show only models that are locally available
    local = list_local_models()
    model_options = list(MODELS.keys())

    if local:
        # highlight available models
        model_options_display = []
        for label, val in MODELS.items():
            tag = "✅ " if any(val in m for m in local) else "⬇ "
            model_options_display.append(tag + label)
    else:
        model_options_display = ["⬇ " + l for l in model_options]

    st.markdown('<p class="section-label">Model</p>', unsafe_allow_html=True)
    chosen_label_idx = st.selectbox(
        "", range(len(model_options_display)),
        format_func=lambda i: model_options_display[i],
        label_visibility="collapsed",
    )
    chosen_model = list(MODELS.values())[chosen_label_idx]

    st.markdown("---")
    st.markdown('<p class="section-label">Language</p>', unsafe_allow_html=True)
    language = st.selectbox("", LANGUAGES, label_visibility="collapsed")

    st.markdown("---")
    st.markdown("**Pull a model** (run in terminal):")
    st.code(f"ollama pull {chosen_model}", language="bash")

    st.markdown("---")
    # Saved files list
    saved_files = sorted(SAVED_DIR.glob("*"), reverse=True)
    if saved_files:
        st.markdown('<p class="section-label">Saved Files</p>', unsafe_allow_html=True)
        for f in saved_files[:8]:
            st.markdown(f"📄 `{f.name}`")


# ── Main Area ─────────────────────────────────────────────────────────────────
st.markdown('<p class="main-title">AI Code Generator & Explainer</p>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Describe what you need → get code, explanation & debug hints</p>', unsafe_allow_html=True)

col_left, col_right = st.columns([1, 1], gap="large")

with col_left:
    st.markdown('<p class="section-label">Your Prompt</p>', unsafe_allow_html=True)
    user_prompt = st.text_area(
        "",
        height=160,
        placeholder=f"e.g. Write a {language} function to sort a list of dictionaries by a key",
        label_visibility="collapsed",
    )

    btn_gen, btn_clr = st.columns([2, 1])
    with btn_gen:
        generate = st.button("⚡ Generate Code", use_container_width=True)
    with btn_clr:
        if st.button("🗑 Clear", use_container_width=True):
            for k in ("code", "explanation", "debug"):
                st.session_state.pop(k, None)
            st.rerun()

with col_right:
    st.markdown('<p class="section-label">Options</p>', unsafe_allow_html=True)
    auto_explain = st.toggle("Auto-explain after generation", value=True)
    auto_debug   = st.toggle("Auto-debug suggestions",        value=True)
    auto_save    = st.toggle("Auto-save generated code",      value=True)

st.markdown("---")

# ── Generation ────────────────────────────────────────────────────────────────
if generate:
    if not user_prompt.strip():
        st.warning("Please enter a prompt first.")
    elif not running:
        st.error("Ollama is not running. Start it with `ollama serve`.")
    else:
        with st.spinner(f"Generating {language} code with **{chosen_model}** …"):
            raw_code = stream_ollama(
                chosen_model,
                build_code_prompt(user_prompt, language),
            )
        code = extract_code(raw_code, language)
        st.session_state["code"]     = code
        st.session_state["language"] = language
        st.session_state["prompt"]   = user_prompt
        st.session_state.pop("explanation", None)
        st.session_state.pop("debug", None)

        if auto_save and code:
            path = save_code(code, language, user_prompt)
            st.session_state["saved_path"] = str(path)

# ── Output Tabs ───────────────────────────────────────────────────────────────
if "code" in st.session_state:
    code     = st.session_state["code"]
    lang_out = st.session_state.get("language", language)

    tab_code, tab_explain, tab_debug = st.tabs(["📄 Code", "📚 Explanation", "🐛 Debug Hints"])

    # ── Code Tab ──────────────────────────────────────────────────────────────
    with tab_code:
        st.markdown('<p class="section-label">Generated Code</p>', unsafe_allow_html=True)
        st.markdown(f'<div class="code-block">{code}</div>', unsafe_allow_html=True)

        dl_col, copy_col = st.columns([1, 1])
        with dl_col:
            st.download_button(
                "⬇ Download",
                data=code,
                file_name=f"generated.{EXT_MAP.get(lang_out,'txt')}",
                mime="text/plain",
                use_container_width=True,
            )

        if "saved_path" in st.session_state:
            st.markdown(
                f'<span class="saved-badge">💾 Saved → {st.session_state["saved_path"]}</span>',
                unsafe_allow_html=True,
            )

    # ── Explanation Tab ───────────────────────────────────────────────────────
    with tab_explain:
        if "explanation" not in st.session_state:
            if auto_explain or st.button("Generate Explanation"):
                with st.spinner("Explaining code …"):
                    expl = stream_ollama(
                        chosen_model,
                        build_explain_prompt(code, lang_out),
                    )
                st.session_state["explanation"] = expl
        else:
            st.markdown('<p class="section-label">Step-by-Step Explanation</p>', unsafe_allow_html=True)
            st.markdown(
                f'<div class="explain-block">{st.session_state["explanation"]}</div>',
                unsafe_allow_html=True,
            )

        if "explanation" in st.session_state and not auto_explain:
            st.markdown('<p class="section-label">Step-by-Step Explanation</p>', unsafe_allow_html=True)
            st.markdown(
                f'<div class="explain-block">{st.session_state["explanation"]}</div>',
                unsafe_allow_html=True,
            )

    # ── Debug Tab ─────────────────────────────────────────────────────────────
    with tab_debug:
        if "debug" not in st.session_state:
            if auto_debug or st.button("Run Debug Analysis"):
                with st.spinner("Analysing for potential issues …"):
                    dbg = stream_ollama(
                        chosen_model,
                        build_debug_prompt(code, lang_out),
                    )
                st.session_state["debug"] = dbg
        else:
            st.markdown('<p class="section-label">Debug & Review Suggestions</p>', unsafe_allow_html=True)
            st.markdown(
                f'<div class="debug-block">{st.session_state["debug"]}</div>',
                unsafe_allow_html=True,
            )

        if "debug" in st.session_state and not auto_debug:
            st.markdown('<p class="section-label">Debug & Review Suggestions</p>', unsafe_allow_html=True)
            st.markdown(
                f'<div class="debug-block">{st.session_state["debug"]}</div>',
                unsafe_allow_html=True,
            )
