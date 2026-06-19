# 🧠 Multi-Agent AI Research System

An **agentic AI research assistant** that automates the entire research workflow.
Give it any topic and **four specialized AI agents collaborate** to search the web,
read the best sources, write a structured report, and critique their own work — all
through a clean, modern Streamlit interface.

> Built with LangChain + LangGraph, Mistral AI, Tavily, and Streamlit.

---

## ✨ Features

- 🤖 **Multi-agent architecture** — four cooperating agents, each with a single responsibility
- 🔎 **Live web search** — real, up-to-date sources via the Tavily Search API
- 🕸️ **Autonomous web scraping** — the reader agent picks and reads the best source
- ✍️ **Structured report generation** — introduction, key findings, conclusion, and sources
- 🧐 **Self-critique** — a critic agent scores the report and suggests improvements
- 🎨 **Modern UI** — gradient hero, live progress, tabbed results, and one-click report download
- 💻 **CLI mode** — run the whole pipeline from the terminal too

---

## 🏗️ Architecture

```
              ┌──────────────┐
   Topic ───► │ Search Agent │  finds reliable sources (Tavily)
              └──────┬───────┘
                     ▼
              ┌──────────────┐
              │ Reader Agent │  scrapes the most relevant URL (BeautifulSoup)
              └──────┬───────┘
                     ▼
              ┌──────────────┐
              │ Writer Chain │  drafts a structured research report
              └──────┬───────┘
                     ▼
              ┌──────────────┐
              │ Critic Chain │  scores & critiques the report
              └──────┬───────┘
                     ▼
              Final report + review
```

| Agent | Role | Tool |
|-------|------|------|
| **Search Agent** | Finds recent, reliable information | `web_search` (Tavily) |
| **Reader Agent** | Reads the best source in depth | `scrape_url` (requests + BeautifulSoup) |
| **Writer Agent** | Synthesizes research into a report | — (prompt chain) |
| **Critic Agent** | Evaluates and scores the report | — (prompt chain) |

---

## 📁 Project Structure

```
multi-agent-ai-research-system/
├── app.py             # Streamlit web UI
├── pipeline.py        # Orchestrates the 4-agent workflow
├── agents.py          # Agent + chain definitions (LLM, prompts)
├── tools.py           # web_search & scrape_url tools
├── requirements.txt   # Python dependencies
├── .env.example       # Template for your API keys
├── .gitignore
└── README.md
```

---

## 🚀 Getting Started

### 1. Clone & enter the project
```bash
git clone <your-repo-url>
cd multi-agent-ai-research-system
```

### 2. Create a virtual environment & install dependencies
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS / Linux
source venv/bin/activate

pip install -r requirements.txt
```

### 3. Add your API keys
Copy the template and fill in your keys:
```bash
cp .env.example .env
```
You need (at minimum):
- **`MISTRAL_API_KEY`** — get one at https://console.mistral.ai
- **`TAVILY_API_KEY`** — get one at https://app.tavily.com

### 4. Run it

**Web UI (recommended):**
```bash
streamlit run app.py
```
Then open the URL shown in your terminal (usually http://localhost:8501).

**Command line:**
```bash
python pipeline.py
```

---

## 🧩 How It Works

1. The **Search Agent** queries Tavily for the top sources on your topic.
2. The **Reader Agent** picks the most relevant URL and scrapes its content.
3. The **Writer Agent** combines the search results and scraped text into a
   structured report (intro → key findings → conclusion → sources).
4. The **Critic Agent** independently reviews the report and returns a score
   out of 10, strengths, and areas to improve.

The Streamlit UI streams each step live and presents the final output in
clean tabs: **Report**, **Critic Review**, **Sources**, and **Raw Agent Output**.

---

## 🛠️ Tech Stack

- **LangChain / LangGraph** — agent orchestration & tool calling
- **Mistral AI** (`mistral-small-2506`) — LLM reasoning
- **Tavily** — real-time web search
- **BeautifulSoup + requests** — web scraping
- **Streamlit** — interactive web interface
- **python-dotenv** — environment/secret management

---

## 🔐 Security

API keys are loaded from a local `.env` file, which is **git-ignored** and never
committed. Use `.env.example` as a reference for the variables you need.

---

## 📈 Possible Extensions

- Add memory so agents can refine the report over multiple rounds
- Scrape multiple sources instead of one
- Swap the LLM provider (OpenAI / Anthropic / Groq) via `agents.py`
- Export reports as PDF
- Deploy to Streamlit Community Cloud

---

## 👤 Author

**Paresh Kumar Pradhan**

If you find this project useful, consider giving it a ⭐ on GitHub.
