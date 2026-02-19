import os
import logging
from typing import List, Dict
import json

from groq import Groq

from dotenv import load_dotenv

logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    logger.warning("GROQ_API_KEY not found in environment variables. LLM features may fail.")

_client = None

def load_llm():
    global _client
    if _client is None:
        logger.info("Loading Groq Client...")
        _client = Groq(api_key=GROQ_API_KEY)

def build_prompt(articles: List[Dict]) -> str:
    context = ""
    for a in articles:
        context += (
            f"Title: {a.get('title', 'N/A')}\n"
            f"Source: {a.get('source', 'N/A')}\n"
            f"Summary: {a.get('summary', 'N/A')}\n"
            f"Sentiment: {a.get('sentiment', 'N/A')}\n\n"
        )

    return f"""
You are a business news analyst.

Analyze the following news coverage and respond STRICTLY in JSON.

Required JSON schema:
{{
  "dominant_narrative": string,
  "conflicting_viewpoints": [string],
  "risk_signals": [string],
  "business_takeaway": string
}}

News Articles:
{context}

Response (JSON only):
"""

def run_insight_agent(articles: List[Dict]) -> Dict:
    try:
        load_llm()

        prompt = build_prompt(articles)
        
        completion = _client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that outputs JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,
            max_tokens=1024,
            response_format={"type": "json_object"}
        )

        output = completion.choices[0].message.content
        logger.info("Groq response received")

        # Parse JSON
        return {
            "analysis": json.loads(output)
        }

    except Exception as e:
        logger.error(f"Groq LLM analysis failed: {e}")
        return {
            "analysis": {
                "error": str(e),
                "business_takeaway": "Failed to generate insights due to API error.",
                "risk_signals": []
            }
        }