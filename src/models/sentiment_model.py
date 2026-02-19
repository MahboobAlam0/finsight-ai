import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import logging

logger = logging.getLogger(__name__)

_tokenizer = None
_model = None
_device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

def load_sentiment_model():
    global _tokenizer, _model, _device
    if _model is None:
        logger.info("Loading sentiment analysis model (manual)...")
        model_name = "ProsusAI/finbert"
        _tokenizer = AutoTokenizer.from_pretrained(model_name)
        _model = AutoModelForSequenceClassification.from_pretrained(model_name).to(_device)
        _model.eval()
        logger.info("FinBERT model loaded successfully.")

def analyze_sentiment(text: str) -> dict:
    if not text:
        return {
            "sentiment": "Neutral",
            "confidence": 0.0,
            "model": "finbert"
        }

    load_sentiment_model()
    
    try:
        inputs = _tokenizer(
            text, 
            return_tensors="pt", 
            truncation=True, 
            max_length=512
        ).to(_device)
        
        with torch.no_grad():
            outputs = _model(**inputs)
            probs = torch.nn.functional.softmax(outputs.logits, dim=-1)
            
        # Get highest probability class
        rating_idx = torch.argmax(probs).item()
        score = probs[0][rating_idx].item()
        
        # ProsusAI/finbert labels: 0: positive, 1: negative, 2: neutral
        # Wait, let's use the explicit model config labels to be safe
        label = _model.config.id2label[rating_idx]
        
        # Normalize label (capitalize)
        sentiment = label.capitalize()
        
        return {
            "sentiment": sentiment,
            "confidence": round(score, 3),
            "model": "finbert"
        }
    except Exception as e:
        logger.error(f"Sentiment analysis failed: {e}")
        return {
            "sentiment": "Neutral",
            "confidence": 0.0,
            "rating": None,
            "error": str(e)
        }