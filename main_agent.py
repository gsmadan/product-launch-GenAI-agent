from agents.competitor_scraper import run_scraper
from agents.feature_comparator import run_comparator
from agents.launch_brief_writer import run_brief_writer

from langchain.agents import initialize_agent, AgentType
from langchain.tools import Tool
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
import os

# ─── Load environment variables ───────────────────────────────────────────────
load_dotenv()

# ─── Set up Gemini LLM ────────────────────────────────────────────────────────
llm = ChatGoogleGenerativeAI(
    model="models/gemini-2.0-flash",
    temperature=0.3,
    api_key=os.getenv("GEMINI_API_KEY")
)

# ─── Define tools (agents) ────────────────────────────────────────────────────
tools = [
    Tool.from_function(
        name="CompetitorScraperAgent",
        func=run_scraper,
        description="Fetch and summarize top 3 competitors for a product category like 'wireless earbuds'."
    ),
    Tool.from_function(
        name="FeatureComparatorAgent",
        func=run_comparator,
        description="Compare product features, USPs, and pricing based on saved summaries."
    ),
    Tool.from_function(
        name="LaunchBriefAgent",
        func=run_brief_writer,
        description="Generate a GTM launch brief using the competitor comparison insights."
    )
]

# ─── Initialize the agent with Gemini ─────────────────────────────────────────
agent = initialize_agent(
    tools=tools,
    llm=llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True
)

# ─── Run agent with a prompt ──────────────────────────────────────────────────
if __name__ == "__main__":
    print("\n🤖 Starting Gemini-Powered Product Research Agent\n")
    output = agent.run("Create a GTM launch brief for a new wireless earbuds product.")
    print("\n✅ Final Output:\n")
    print(output)
