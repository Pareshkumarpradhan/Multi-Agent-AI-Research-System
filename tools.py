"""
tools.py
--------
Tools the agents can call during the research pipeline.

- `web_search` : queries the live web via the Tavily Search API.
- `scrape_url` : downloads a single web page and extracts clean readable text.

Both functions are decorated with LangChain's `@tool`, which turns them into
callable tools that an LLM agent can invoke autonomously.
"""

from langchain.tools import tool
import requests
from bs4 import BeautifulSoup
from tavily import TavilyClient
import os
from rich import print

from dotenv import load_dotenv

# Load environment variables (API keys) from the local .env file
load_dotenv()

# Tavily provides fast, LLM-friendly web search results
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
tavily_client = TavilyClient(api_key=TAVILY_API_KEY)


@tool
def web_search(query: str) -> str:
    """Search the web for recent and reliable information on a topic. Return Titles, urls, and snippets"""
    # Ask Tavily for the top 5 most relevant results for the query
    results = tavily_client.search(query=query, max_results=5)

    # Format each result into a compact, readable block for the LLM to reason over
    out = []
    for r in results["results"]:
        out.append(
            f"Title: {r['title']}\nURL: {r['url']}\nSnippet: {r['content'][:300]}\n"
        )

    # Join all results with a visual separator
    return "\n-----\n".join(out)


@tool
def scrape_url(url: str) -> str:
    """Scrape and return clean text content from a given URL for deeper reading"""
    try:
        # Fetch the page (8s timeout, browser-like User-Agent to avoid simple blocks)
        resp = requests.get(url, timeout=8, headers={"User-Agent": "Mozilla/5.0"})

        # Parse the HTML
        soup = BeautifulSoup(resp.text, "html.parser")

        # Strip out non-content tags so we keep only the meaningful text
        for tag in soup(["script", "style", "nav", "footer"]):
            tag.decompose()

        # Return clean text, capped at 3000 chars to stay within the LLM context budget
        return soup.get_text(separator=" ", strip=True)[:3000]
    except Exception as e:
        # Never crash the pipeline on a bad URL - return a readable error instead
        return f"Could not scrape URL: {str(e)}"
