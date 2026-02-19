from fastapi.testclient import TestClient
from src.api.api import app
from unittest.mock import patch, MagicMock

client = TestClient(app)

def test_read_main():
    response = client.get("/docs")
    assert response.status_code == 200

@patch("src.api.api.scrape_news_from_sources")
def test_scrape_endpoint(mock_scrape):
    # Mock return value
    mock_scrape.return_value = [
        {
            "title": "Test Article",
            "summary": "This is a test summary.",
            "source": "Test Source",
            "url": "http://test.com",
            "sentiment": "neutral"
        }
    ]

    response = client.post(
        "/scrape",
        json={"company": "Tesla", "num_articles": 1}
    )

    assert response.status_code == 200
    data = response.json()
    assert "articles" in data
    assert len(data["articles"]) == 1
    assert data["articles"][0]["title"] == "Test Article"

def test_analyze_endpoint():
    # Test sentiment analysis integration
    articles = [
        {"summary": "Tesla is doing amazingly well! Profits are up.", "title": "Good News"}
    ]
    
    response = client.post(
        "/analyze",
        json={"articles": articles}
    )
    
    assert response.status_code == 200
    data = response.json()
    print("\nAPI Response:", data)
    analyzed_article = data["articles"][0]
    
    # Check if sentiment keys were added
    assert "sentiment" in analyzed_article
    assert "confidence" in analyzed_article
    # Verify sentiment is present and valid
    assert isinstance(analyzed_article["sentiment"], str)
    assert len(analyzed_article["sentiment"]) > 0
