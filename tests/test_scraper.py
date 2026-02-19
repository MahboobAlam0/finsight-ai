def test_news_scraper(mocker):
    # Mock the requests.get method to simulate a response
    mock_response = mocker.Mock()
    mock_response.content = b'<html><head><title>Test News</title></head><body><h1>News Title</h1><p>News summary goes here.</p></body></html>'
    mocker.patch('requests.get', return_value=mock_response)

    from src.scraper.news_scraper import scrape_news

    # Call the function to test
    articles = scrape_news('http://test-url.com')

    # Assert that the scraped articles contain the expected title and summary
    assert len(articles) == 1
    assert articles[0]['title'] == 'News Title'
    assert articles[0]['summary'] == 'News summary goes here.'

def test_news_scraper_empty_response(mocker):
    # Mock the requests.get method to simulate an empty response
    mock_response = mocker.Mock()
    mock_response.content = b'<html></html>'
    mocker.patch('requests.get', return_value=mock_response)

    from src.scraper.news_scraper import scrape_news

    # Call the function to test
    articles = scrape_news('http://test-url.com')

    # Assert that no articles are returned
    assert len(articles) == 0