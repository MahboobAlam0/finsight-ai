def test_sentiment_analysis():
    from src.api.sentiment import analyze_sentiment

    # Test positive sentiment
    positive_text = "I love this product! It's amazing."
    assert analyze_sentiment(positive_text) == "positive"

    # Test negative sentiment
    negative_text = "I hate this service. It's terrible."
    assert analyze_sentiment(negative_text) == "negative"

    # Test neutral sentiment
    neutral_text = "The product is okay."
    assert analyze_sentiment(neutral_text) == "neutral"

    # Test empty text
    empty_text = ""
    assert analyze_sentiment(empty_text) == "neutral"  # Assuming neutral for empty input

    # Test mixed sentiment
    mixed_text = "I love the quality, but the price is too high."
    assert analyze_sentiment(mixed_text) == "neutral"  # Assuming neutral for mixed sentiments