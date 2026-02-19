# src/scraper/news_scraper.py

import requests
from bs4 import BeautifulSoup
from urllib.parse import quote, unquote
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Optional
import logging

import torch
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ===================== SUMMARIZER =====================

_tokenizer = None
_model = None

def load_summarizer():
    global _tokenizer, _model
    if _tokenizer is None or _model is None:
        logger.info("Loading summarization model (manual Bart)...")

        _tokenizer = AutoTokenizer.from_pretrained(
            "sshleifer/distilbart-cnn-12-6"
        )
        _model = AutoModelForSeq2SeqLM.from_pretrained(
            "sshleifer/distilbart-cnn-12-6"
        )

        _model.eval()
        logger.info("Summarization model loaded successfully.")

def summarize_text(text: str) -> Dict:
    if not text or len(text) < 150:
        return {
            "summary": text.strip(),
            "summary_meta": {"method": "too_short"}
        }

    try:
        load_summarizer()

        text = text[:4000]
        inputs = _tokenizer(
            text,
            return_tensors="pt",
            truncation=True
        )

        with torch.no_grad():
            summary_ids = _model.generate(
                inputs["input_ids"],
                max_length=200,
                min_length=80,
                num_beams=4,
                length_penalty=2.0,
                early_stopping=True
            )

        summary = _tokenizer.decode(
            summary_ids[0],
            skip_special_tokens=True
        )

        ratio = len(summary) / max(len(text), 1)
        logger.info(
            f"Summary generated | orig_len={len(text)} "
            f"summary_len={len(summary)} ratio={ratio:.2f}"
        )

        return {
            "summary": summary.strip(),
            "summary_meta": {
                "method": "distilbart-cnn",
                "compression_ratio": round(ratio, 2)
            }
        }

    except Exception as e:
        logger.warning(f"Summarization failed: {e}")
        return {
            "summary": text[:300] + "...",
            "summary_meta": {"method": "fallback"}
        }

# ===================== SEARCH =====================

def yahoo_search_urls(query: str, limit: int) -> List[str]:
    # Enforce financial context
    search_query = f"{query} finance news"
    url = f"https://news.search.yahoo.com/search?p={quote(search_query)}"
    headers = {"User-Agent": "Mozilla/5.0"}

    resp = requests.get(url, headers=headers, timeout=15)
    resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "html.parser")
    
    # Try specific NewsArticle containers first
    anchors = soup.select("div.NewsArticle h4 a, div.NewsArticle h3 a, li div.dd h4 a, li div.dd h3 a, div.NewsArticle a")
    
    if not anchors:
        # Fallback to generic headings
        anchors = soup.select("h3 a, h4 a")
        
    logger.info(f"Yahoo Search: Found {len(anchors)} potential links.")

    urls = []
    seen_urls = set()
    
    for a in anchors:
        href = a.get("href")
        if not href:
            continue

        if "r.search.yahoo.com" in href:
            try:
                start = href.find("/RU=") + 4
                end = href.find("/R", start)
                clean = unquote(href[start:end])
                
                if clean not in seen_urls:
                    urls.append(clean)
                    seen_urls.add(clean)
            except Exception:
                continue

        if len(urls) >= limit:
            break

    logger.info(f"Yahoo search returned {len(urls)} unique URLs")
    return urls

# ===================== FETCH =====================

def fetch_article(url: str) -> Optional[Dict]:
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        resp = requests.get(url, headers=headers, timeout=15)
        resp.raise_for_status()

        soup = BeautifulSoup(resp.text, "html.parser")

        for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
            tag.decompose()

        title = soup.title.string.strip() if soup.title else "Untitled"

        paragraphs = [
            p.get_text(" ", strip=True)
            for p in soup.find_all("p")
            if len(p.get_text(strip=True)) > 40
        ]

        content = " ".join(paragraphs)

        if len(content) < 300:
            logger.warning(f"Discarded short article: {url}")
            return None

        summary_data = summarize_text(content)

        return {
            "title": title,
            "content": content,
            "summary": summary_data["summary"],
            "summary_meta": summary_data["summary_meta"],
            "source": url.split("/")[2],
            "url": url
        }

    except Exception as e:
        logger.warning(f"Failed to fetch article {url}: {e}")
        return None

# ===================== PUBLIC API =====================

def scrape_news_from_sources(company: str, num_articles: int = 10) -> List[Dict]:
    logger.info(f"Scraping news for company: {company}")

    urls = yahoo_search_urls(company, num_articles * 3)
    articles: List[Dict] = []
    seen_titles = set()

    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(fetch_article, u) for u in urls]

        for future in as_completed(futures):
            article = future.result()
            if article:
                # Deduplicate by title
                title_lower = article["title"].lower()
                if title_lower not in seen_titles:
                    articles.append(article)
                    seen_titles.add(title_lower)
            
            if len(articles) >= num_articles:
                break

    logger.info(f"Scraper returned {len(articles)} unique articles")
    return articles