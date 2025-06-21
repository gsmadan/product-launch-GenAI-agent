# 🧠 Product Launch Research Assistant

A multi-agent Generative AI system that helps you:

- 🔍 Scrape and summarize competitor product pages
- 📊 Compare product features and positioning
- 🚀 Generate a go-to-market launch brief

### 🛠️ Tech Stack

- LangChain
- Gemini 2.0 Flash (via `langchain-google-genai`)
- Crawl4AI
- SerpAPI
- Python

### 🧩 Agents

1. **CompetitorScraperAgent** — gets top links via SerpAPI + summarizes with Gemini
2. **FeatureComparatorAgent** — compares product features from saved summaries
3. **LaunchBriefAgent** — generates a GTM launch plan from comparison insights

