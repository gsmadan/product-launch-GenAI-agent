import os
from pathlib import Path
import google.generativeai as genai
from dotenv import load_dotenv

# ─── Setup ────────────────────────────────────────────────────────────────────
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# ─── Load Comparison ──────────────────────────────────────────────────────────
def load_comparison_report(product_category: str) -> str:
    path = f"data/feature_comparison_{product_category.replace(' ', '_')}.md"
    if not os.path.exists(path):
        raise FileNotFoundError(f"Comparison report not found at {path}")
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

# ─── Generate GTM Brief ───────────────────────────────────────────────────────
def generate_launch_brief(report_text: str) -> str:
    model = genai.GenerativeModel("models/gemini-2.0-flash")

    prompt = f"""
You are a senior product marketing manager.

Based on the following competitive feature comparison, write a go-to-market (GTM) launch brief for a new product entering this market.

The brief should include:
- Suggested product positioning
- Pricing strategy
- Key differentiators to emphasize
- Ideal customer persona
- Go-to-market messaging pillars
- Launch campaign themes

Feature comparison:
{report_text}
"""

    response = model.generate_content(prompt)
    return response.text.strip()

# ─── Save GTM Brief ───────────────────────────────────────────────────────────
def save_launch_brief(text: str, product_category: str):
    Path("data").mkdir(parents=True, exist_ok=True)
    path = f"data/launch_brief_{product_category.replace(' ', '_')}.md"
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)
    print(f"\n💾 GTM Launch Brief saved to {path}")

# ─── Run CLI ──────────────────────────────────────────────────────────────────
def run_brief_writer(product_category="wireless earbuds"):
    if "=" in product_category:
        product_category = product_category.split("=", 1)[1].strip()
    product_category = product_category.strip("\"'")
        
    print(f"\n🚀 Generating GTM brief for: {product_category}")
    comparison = load_comparison_report(product_category)
    brief = generate_launch_brief(comparison)
    print("\n📣 Launch Brief:\n")
    # print(brief)
    save_launch_brief(brief, product_category)
    return(brief)
    

if __name__ == "__main__":
    run_brief_writer("wireless earbuds")
