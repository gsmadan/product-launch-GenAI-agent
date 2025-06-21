import os
import asyncio
import requests
from dotenv import load_dotenv
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode
import google.generativeai as genai
import json
from pathlib import Path


# ────── Config ───────────────────────────────────────────────────────────────

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
SERPAPI_KEY = os.getenv("SERPAPI_KEY")

# ────── Summarizer ───────────────────────────────────────────────────────────

async def fetch_article_summary(url: str) -> str:
    try:
        async with AsyncWebCrawler(config=BrowserConfig(headless=True)) as crawler:
            result = await crawler.arun(url=url, config=CrawlerRunConfig(cache_mode=CacheMode.BYPASS))
            soup = BeautifulSoup(result.cleaned_html, "html.parser")
            text = " ".join(p.get_text(strip=True) for p in soup.find_all("p"))
            if not text:
                return ""

        model = genai.GenerativeModel("models/gemini-2.0-flash")
        prompt = f"""
You are a product strategist. Analyze the following article and summarize:
- Common features in competing products
- Unique selling points (USPs)
- Pricing trends
- Product positioning insights

Article:
{text[:5000]}
"""
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print(f"❌ Error summarizing {url}: {e}")
        return ""

# ────── SerpAPI Fetcher ──────────────────────────────────────────────────────

def fetch_serpapi_links(product_category: str, max_links: int = 3) -> list:
    query = f"best {product_category} 2025"
    url = "https://serpapi.com/search"
    params = {
        "engine": "google",
        "q": query,
        "api_key": SERPAPI_KEY,
        "num": max_links
    }

    try:
        response = requests.get(url, params=params)
        results = response.json().get("organic_results", [])
        links = [(res.get("title", "Untitled"), res.get("link")) for res in results if res.get("link")]
        return links[:max_links]
    except Exception as e:
        print(f"❌ SerpAPI failed: {e}")
        return []

# ────── Orchestration ────────────────────────────────────────────────────────

async def crawl_and_summarize(product_category: str, top_k: int = 3):
    urls = fetch_serpapi_links(product_category, max_links=top_k)
    results = []

    for title, url in urls:
        print(f"\n🔗 {title}\n{url}")
        summary = await fetch_article_summary(url)
        results.append({
            "title": title,
            "url": url,
            "summary": summary
        })

    return results

def run_scraper(product_category="wireless earbuds"):
    if "=" in product_category:
        product_category = product_category.split("=", 1)[1].strip()
    product_category = product_category.strip("\"'")
        
    print(f"\n🧠 Researching competitors for: {product_category}")
    summaries = asyncio.run(crawl_and_summarize(product_category))

    if not summaries:
        print("❌ No summaries generated.")
        return

    print("\n📋 Product Competitor Insights:\n")
    # for i, res in enumerate(summaries, start=1):
    #     print(f"#{i}: {res['title']}\n{res['url']}\nSummary:\n{res['summary']}\n{'-'*80}")
    save_summaries_to_json(summaries, product_category)
    return "\n\n".join(f"#{i}. {r['title']}\n{r['summary']}" for i, r in enumerate(summaries, 1))
   


def save_summaries_to_json(summaries, product_category: str):
    Path("data").mkdir(parents=True, exist_ok=True)
    filename = f"data/competitor_summaries_{product_category.replace(' ', '_')}.json"
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(summaries, f, indent=2, ensure_ascii=False)
    print(f"\n💾 Saved summaries to {filename}")



# ────── CLI ───────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    run_scraper("wireless earbuds")
