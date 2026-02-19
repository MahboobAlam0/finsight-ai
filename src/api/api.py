# src/api/api.py

from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Dict

import logging

from src.scraper.news_scraper import scrape_news_from_sources, load_summarizer
from src.models.sentiment_model import load_sentiment_model, analyze_sentiment
from src.llm.insight_agent import run_insight_agent
from src.tts.hindi_tts import generate_hindi_tts


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="News Summarization API")

# -------------------- Models --------------------

class ScrapeRequest(BaseModel):
    company: str
    num_articles: int = 10

class AnalyzeRequest(BaseModel):
    articles: List[Dict]
    
class TTSRequest(BaseModel):
    text: str

# ... (startup event) ...

# ... (existing routes) ...

@app.post("/analyze_llm")
def analyze_llm(articles: List[Dict]):
    logger.info("Running AI Insight Agent")
    return run_insight_agent(articles)

@app.post("/tts")
def tts_endpoint(req: TTSRequest):
    logger.info("Generating Hindi TTS...")
    audio_path = generate_hindi_tts(req.text)
    return {"audio_path": audio_path}

@app.on_event("startup")
def startup_event():
    logger.info("🚀 Loading models at startup...")
    load_summarizer()          # now SAFE
    load_sentiment_model()
    logger.info("✅ All models loaded")

# -------------------- Routes --------------------

@app.post("/scrape")
def scrape(req: ScrapeRequest):
    articles = scrape_news_from_sources(req.company, req.num_articles)
    return {"articles": articles}

@app.post("/analyze")
def analyze(req: AnalyzeRequest):
    logger.info(f"Analyzing {len(req.articles)} articles")

    analyzed = []
    for article in req.articles:
        sentiment = analyze_sentiment(article.get("summary", ""))
        article.update(sentiment)
        analyzed.append(article)

    return {"articles": analyzed}


