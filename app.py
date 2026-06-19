"""
app.py
------
Modern Streamlit UI for the Multi-Agent AI Research System.

Run with:   streamlit run app.py

The UI lets a user type any topic and watch four AI agents collaborate
in real time (Search -> Read -> Write -> Critic), then displays the final
report and the critic's score in a clean, shareable layout.
"""

import os
import streamlit as st

# ============================================================
# SECRET MANAGEMENT
# Works in BOTH environments without code changes:
#   - Local:           keys come from the git-ignored .env file (via dotenv)
#   - Streamlit Cloud: keys come from st.secrets (set in the app's Secrets UI)
# We copy any st.secrets into os.environ *before* importing the pipeline,
# because agents.py / tools.py read their keys with os.getenv() at import time.
# ============================================================
try:
    for _key, _val in st.secrets.items():
        os.environ.setdefault(_key, str(_val))
except Exception:
    # No secrets.toml present (e.g. running locally) -> fall back to .env
    pass

from pipeline import run_research_pipeline

# Fail fast with a clear message if required keys are missing
_REQUIRED_KEYS = ["MISTRAL_API_KEY", "TAVILY_API_KEY"]
_missing = [k for k in _REQUIRED_KEYS if not os.getenv(k)]
if _missing:
    st.error(
        "Missing required API key(s): "
        + ", ".join(_missing)
        + ".\n\nSet them locally in a `.env` file, or on Streamlit Cloud "
        "under **Settings → Secrets**."
    )
    st.stop()

# ============================================================
# PAGE CONFIG
# ============================================================
st.set_page_config(
    page_title="Multi-Agent AI Research System",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============================================================
# CUSTOM STYLING (modern gradient + card look)
# ============================================================
st.markdown(
    """
    <style>
        /* Hide Streamlit chrome for a cleaner demo */
        #MainMenu, footer {visibility: hidden;}

        .hero {
            background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 50%, #ec4899 100%);
            padding: 2.2rem 2rem;
            border-radius: 18px;
            color: white;
            margin-bottom: 1.5rem;
            box-shadow: 0 10px 30px rgba(99,102,241,0.35);
        }
        .hero h1 { font-size: 2.2rem; margin: 0; font-weight: 800; }
        .hero p  { font-size: 1.05rem; margin-top: .5rem; opacity: .95; }

        .agent-card {
            background: rgba(255,255,255,0.04);
            border: 1px solid rgba(255,255,255,0.12);
            border-radius: 14px;
            padding: 1rem 1.2rem;
            margin-bottom: .8rem;
        }
        .pill {
            display:inline-block; padding: 3px 12px; border-radius: 999px;
            font-size: .75rem; font-weight: 600; margin-right:6px;
        }
        .pill-blue  { background:#dbeafe; color:#1e40af; }
        .pill-green { background:#dcfce7; color:#166534; }
        .pill-amber { background:#fef3c7; color:#92400e; }
        .pill-pink  { background:#fce7f3; color:#9d174d; }
        .stButton>button {
            background: linear-gradient(135deg,#6366f1,#8b5cf6);
            color:white; border:none; border-radius:10px;
            padding:.6rem 1.4rem; font-weight:700; width:100%;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# ============================================================
# SIDEBAR - project info (great for a portfolio / demo)
# ============================================================
with st.sidebar:
    st.markdown("## 🧠 About this project")
    st.markdown(
        """
        An **agentic AI research assistant** that automates the full
        research workflow using four specialized agents.

        **Tech stack**
        - 🦜 LangChain + LangGraph (agents)
        - 🧩 Mistral AI (LLM reasoning)
        - 🔎 Tavily (live web search)
        - 🕸️ BeautifulSoup (web scraping)
        - 🎨 Streamlit (this UI)
        """
    )
    st.divider()
    st.markdown("### 🤖 The Agent Pipeline")
    st.markdown(
        """
        1. **Search Agent** — finds reliable sources
        2. **Reader Agent** — scrapes the best source
        3. **Writer Agent** — drafts a structured report
        4. **Critic Agent** — scores & critiques it
        """
    )
    st.divider()
    st.caption("Built by Paresh Kumar Pradhan")

# ============================================================
# HERO HEADER
# ============================================================
st.markdown(
    """
    <div class="hero">
        <h1>🧠 Multi-Agent AI Research System</h1>
        <p>Four autonomous AI agents collaborate to search, read, write, and critique
        a complete research report — on any topic, in minutes.</p>
        <span class="pill pill-blue">Search</span>
        <span class="pill pill-green">Read</span>
        <span class="pill pill-amber">Write</span>
        <span class="pill pill-pink">Critique</span>
    </div>
    """,
    unsafe_allow_html=True,
)

# ============================================================
# INPUT
# ============================================================
col_in, col_btn = st.columns([4, 1])
with col_in:
    topic = st.text_input(
        "Research topic",
        placeholder="e.g. The impact of AI agents on software engineering in 2026",
        label_visibility="collapsed",
    )
with col_btn:
    run = st.button("🚀 Research")

# ============================================================
# RUN PIPELINE
# ============================================================
if run:
    if not topic.strip():
        st.warning("Please enter a research topic first.")
        st.stop()

    # We drive the UI with a single status box that updates per step
    progress = st.status("Running the multi-agent pipeline...", expanded=True)
    captured = {}

    # Friendly labels for each pipeline step
    labels = {
        "search": "🔎 Search Agent gathered sources",
        "read": "📖 Reader Agent scraped the best source",
        "write": "✍️ Writer Agent drafted the report",
        "critic": "🧐 Critic Agent reviewed the report",
    }

    def on_step(step, content):
        # Called after each agent finishes; store result and update the status log
        captured[step] = content
        progress.write(f"**{labels.get(step, step)}** ✅")

    try:
        with progress:
            state = run_research_pipeline(topic, on_step=on_step)
        progress.update(label="✅ Research complete!", state="complete", expanded=False)
    except Exception as e:
        progress.update(label="❌ Pipeline failed", state="error")
        st.error(f"Something went wrong: {e}")
        st.stop()

    # ========================================================
    # RESULTS
    # ========================================================
    st.success("Your research report is ready 🎉")

    tab_report, tab_critic, tab_sources, tab_raw = st.tabs(
        ["📄 Report", "🧐 Critic Review", "🔎 Sources", "🧩 Raw Agent Output"]
    )

    with tab_report:
        st.markdown(state["report"])
        st.download_button(
            "⬇️ Download report (.md)",
            data=state["report"],
            file_name=f"research_report_{topic[:30].replace(' ', '_')}.md",
            mime="text/markdown",
        )

    with tab_critic:
        st.markdown("### Critic Agent Evaluation")
        st.markdown(state["feedback"])

    with tab_sources:
        st.markdown("### Sources found by the Search Agent")
        st.markdown(state["search_results"])

    with tab_raw:
        with st.expander("Search Agent output"):
            st.text(state["search_results"])
        with st.expander("Reader Agent (scraped content)"):
            st.text(state["scraped_content"])

else:
    # Default landing state - explain the system
    st.info(
        "👆 Enter a topic above and click **Research** to watch four AI agents "
        "collaborate on a full research report."
    )

    c1, c2, c3, c4 = st.columns(4)
    for col, (emoji, title, desc) in zip(
        [c1, c2, c3, c4],
        [
            ("🔎", "Search", "Finds recent, reliable sources via live web search."),
            ("📖", "Read", "Scrapes the most relevant page for deep content."),
            ("✍️", "Write", "Synthesizes everything into a structured report."),
            ("🧐", "Critique", "Scores the report and suggests improvements."),
        ],
    ):
        with col:
            st.markdown(
                f"""<div class="agent-card">
                <div style="font-size:1.8rem">{emoji}</div>
                <b>{title} Agent</b><br>
                <span style="opacity:.8;font-size:.85rem">{desc}</span>
                </div>""",
                unsafe_allow_html=True,
            )
