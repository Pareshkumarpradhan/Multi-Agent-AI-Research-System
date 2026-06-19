"""
agents.py
---------
Defines the four "workers" of the multi-agent research system.

Two of them are tool-using AGENTS (they decide when to call a tool):
    1. Search Agent  -> uses `web_search` to find sources
    2. Reader Agent  -> uses `scrape_url` to read a source in depth

Two of them are prompt CHAINS (single LLM call, no tools):
    3. Writer Chain  -> turns raw research into a structured report
    4. Critic Chain  -> grades and critiques the report

All four share the same Mistral LLM instance.
"""

from langchain.agents import create_agent
from langchain_mistralai import ChatMistralAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from tools import web_search, scrape_url
import os

from dotenv import load_dotenv

load_dotenv()

# =====================================================
# LLM INITIALIZATION
# temperature=0 keeps outputs focused and factual
# =====================================================
llm = ChatMistralAI(model="mistral-small-2506", temperature=0)


# =====================================================
# AGENT 1 - SEARCH
# Given a topic, it calls web_search to gather sources.
# =====================================================
def build_search_agent():
    return create_agent(model=llm, tools=[web_search])


# =====================================================
# AGENT 2 - READER
# Picks the best URL from the search results and scrapes it.
# =====================================================
def build_reader_agent():
    return create_agent(model=llm, tools=[scrape_url])


# =====================================================
# CHAIN 3 - WRITER
# Synthesizes search + scraped content into a full report.
# =====================================================
writer_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are an expert research writer. Write clear, structured and insightful reports."),
    ("human", """Write a detailed research report on the topic below.

Topic: {topic}

Research Gathered:
{research}

Structure the report as:
- Introduction
- Key Findings (minimum 3 well-explained points)
- Conclusion
- Sources (list all URLs found in the research)

Be detailed, factual and professional."""),
])

# Prompt -> LLM -> plain string output
writer_chain = writer_prompt | llm | StrOutputParser()


# =====================================================
# CHAIN 4 - CRITIC
# Reviews the writer's report and returns a structured critique.
# =====================================================
critic_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a sharp and constructive research critic. Be honest and specific."),
    ("human", """Review the research report below and evaluate it strictly.

Report:
{report}

Respond in this exact format:

Score: X/10

Strengths:
- ...
- ...

Areas to Improve:
- ...
- ...

One line verdict:
..."""),
])

critic_chain = critic_prompt | llm | StrOutputParser()
