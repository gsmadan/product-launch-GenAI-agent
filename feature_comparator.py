import json
import os
from pathlib import Path
import google.generativeai as genai
from dotenv import load_dotenv

# ─── Setup ────────────────────────────────────────────────────────────────────
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# ─── Load Summaries ───────────────────────────────────────────────────────────
def load_summaries(product_category: str):
    path = f"data/competitor_summaries_{product_category.replace(' ', '_')}.json"
    if not os.path.exists(path):
        raise FileNotFoundError(f"No summary file found at {path}")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

# ─── Gemini Comparison Agent ──────────────────────────────────────────────────
def generate_comparison_report(summaries: list) -> str:
    model = genai.GenerativeModel("models/gemini-2.0-flash")
    combined = "\n\n".join(
        f"Title: {s['title']}\nURL: {s['url']}\nSummary:\n{s['summary']}" for s in summaries
    )

    prompt = f"""
You're a product strategist.

Given these product review summaries, generate a comparison table or bullet list that highlights:
- Common product features
- Key differences (USPs)
- Pricing insights
- Positioning strategies
- Any gaps/opportunities across competitors

Summaries:
{combined}
"""

    response = model.generate_content(prompt)
    return response.text.strip()

# ─── Save Report ──────────────────────────────────────────────────────────────
def save_report(text: str, product_category: str):
    Path("data").mkdir(parents=True, exist_ok=True)
    path = f"data/feature_comparison_{product_category.replace(' ', '_')}.md"
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)
    print(f"\n💾 Comparison report saved to {path}")

# ─── Run CLI ──────────────────────────────────────────────────────────────────
def run_comparator(product_category="wireless earbuds"):
    if "=" in product_category:
        product_category = product_category.split("=", 1)[1].strip()
    product_category = product_category.strip("\"'")

    print(f"\n🔍 Comparing competitors for: {product_category}")
    summaries = load_summaries(product_category)
    report = generate_comparison_report(summaries)
    print("\n🧾 Feature Comparison Report:\n")
    # print(report)
    save_report(report, product_category)
    return (report)
    

if __name__ == "__main__":
    run_comparator("wireless earbuds")
