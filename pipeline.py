"""
pipeline.py
-----------
Orchestrates the four agents into a single research workflow:

    Topic
      |
      v
   [1] Search Agent   -> finds reliable sources on the web
      |
      v
   [2] Reader Agent   -> scrapes the most relevant source for depth
      |
      v
   [3] Writer Chain   -> drafts a structured report
      |
      v
   [4] Critic Chain   -> reviews and scores the report
      |
      v
   Final state (dict)

Run from the terminal:   python pipeline.py
Or import `run_research_pipeline` from the Streamlit UI (app.py).
"""

from agents import build_reader_agent, build_search_agent, writer_chain, critic_chain


def run_research_pipeline(topic: str, on_step=None) -> dict:
    """
    Execute the full research pipeline for a given topic.

    Args:
        topic:   The research subject entered by the user.
        on_step: Optional callback(step_name, content) invoked after each stage.
                 The Streamlit UI uses this to stream live progress; the CLI
                 leaves it as None and just prints to the console.

    Returns:
        dict with keys: search_results, scraped_content, report, feedback.
    """
    state = {}

    def notify(step, content):
        # Forward progress to the UI callback if one was provided
        if on_step:
            on_step(step, content)

    # ---- Step 1: Search agent gathers sources --------------------------
    # print("\n" + "= " * 50)
    # print("step 1 - search agent is working ...")
    # print("=" * 50)

    search_agent = build_search_agent()
    search_result = search_agent.invoke({
        "messages": [("user", f"Find recent, reliable and detailed information about: {topic}")]
    })
    # The agent's final message holds the gathered search results
    state["search_results"] = search_result["messages"][-1].content
    # print("\n search result", state["search_results"])
    notify("search", state["search_results"])

    # ---- Step 2: Reader agent scrapes the best source ------------------
    # print("\n" + "= " * 50)
    # print("step 2 - Reader agent is scraping top resources working ...")
    # print("=" * 50)

    reader_agent = build_reader_agent()
    reader_result = reader_agent.invoke({
        "messages": [("user",
            f"Based on the following search results about '{topic}', "
            f"pick the most relevent URL and scrape it for deeper content.\n\n"
            f"Search Results:\n{state['search_results'][:800]}"
        )]
    })
    state["scraped_content"] = reader_result["messages"][-1].content
    # print("\nScraped content\n", state["scraped_content"])
    notify("read", state["scraped_content"])

    # ---- Step 3: Writer chain drafts the report -----------------------
    # print("\n" + "= " * 50)
    # print("step 3 - writer is drafting the report..")
    # print("=" * 50)

    # Combine both research sources into one block for the writer
    research_combine = (
        f"SEARCH RESULTS : \n {state['search_results']} \n\n"
        f"DETAILED SCRAPED CONTENT :\n {state['scraped_content']} "
    )
    state["report"] = writer_chain.invoke({
        "topic": topic,
        "research": research_combine,
    })
    # print("\n Final report\n", state["report"])
    notify("write", state["report"])

    # ---- Step 4: Critic chain reviews the report ----------------------
    # print("\n" + "= " * 50)
    # print("step 4 - critic is reviewing the report..")
    # print("=" * 50)

    state["feedback"] = critic_chain.invoke({"report": state["report"]})
    # print("\n critic report \n", state["feedback"])
    notify("critic", state["feedback"])

    return state


if __name__ == "__main__":
    # Simple command-line entry point
    topic = input("\n Enter a research topic : ")
    run_research_pipeline(topic)
