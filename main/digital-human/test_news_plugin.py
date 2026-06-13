import unittest
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from plugins_func.functions.get_news import (
    fetch_news_from_rss,
    fetch_news_detail,
    get_news_sources,
    map_category,
    get_news
)


class TestNewsPlugin(unittest.TestCase):
    """Test cases for the news plugin functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_conn = Mock()
        self.mock_conn.config = {
            "plugins": {
                "get_news": {
                    "default_rss_url": "https://feeds.reuters.com/reuters/worldNews"
                }
            }
        }
        self.mock_conn.client_ip = "192.168.1.1"

    def test_get_news_sources(self):
        """Test news sources configuration."""
        sources = get_news_sources()
        
        self.assertIn("world", sources)
        self.assertIn("technology", sources)
        self.assertIn("business", sources)
        self.assertIn("sports", sources)
        self.assertIn("health", sources)
        self.assertIn("politics", sources)
        self.assertIn("science", sources)
        
        # Check that each category has multiple sources
        for category, urls in sources.items():
            self.assertGreater(len(urls), 1)
            for url in urls:
                self.assertTrue(url.startswith("http"))

    def test_map_category(self):
        """Test category mapping functionality."""
        # Test world news mappings
        self.assertEqual(map_category("world"), "world")
        self.assertEqual(map_category("world news"), "world")
        self.assertEqual(map_category("international"), "world")
        self.assertEqual(map_category("global"), "world")
        
        # Test technology mappings
        self.assertEqual(map_category("technology"), "technology")
        self.assertEqual(map_category("tech"), "technology")
        self.assertEqual(map_category("ai"), "technology")
        self.assertEqual(map_category("artificial intelligence"), "technology")
        
        # Test business mappings
        self.assertEqual(map_category("business"), "business")
        self.assertEqual(map_category("finance"), "business")
        self.assertEqual(map_category("economy"), "business")
        self.assertEqual(map_category("markets"), "business")
        
        # Test sports mappings
        self.assertEqual(map_category("sports"), "sports")
        self.assertEqual(map_category("football"), "sports")
        self.assertEqual(map_category("soccer"), "sports")
        
        # Test health mappings
        self.assertEqual(map_category("health"), "health")
        self.assertEqual(map_category("medical"), "health")
        self.assertEqual(map_category("healthcare"), "health")
        
        # Test politics mappings
        self.assertEqual(map_category("politics"), "politics")
        self.assertEqual(map_category("election"), "politics")
        self.assertEqual(map_category("government"), "politics")
        
        # Test science mappings
        self.assertEqual(map_category("science"), "science")
        self.assertEqual(map_category("climate"), "science")
        self.assertEqual(map_category("environment"), "science")
        
        # Test unknown category
        self.assertEqual(map_category("unknown category"), "unknown category")
        self.assertIsNone(map_category(None))

    @patch('plugins_func.functions.get_news.requests.get')
    def test_fetch_news_from_rss_success(self, mock_get):
        """Test successful RSS news fetching."""
        # Mock successful RSS response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = b'''<?xml version="1.0" encoding="UTF-8"?>
        <rss version="2.0">
            <channel>
                <title>Test News</title>
                <item>
                    <title>Test News Title</title>
                    <link>https://example.com/news1</link>
                    <description>Test news description</description>
                    <pubDate>Mon, 01 Jan 2024 12:00:00 GMT</pubDate>
                </item>
                <item>
                    <title>Another News Title</title>
                    <link>https://example.com/news2</link>
                    <description>Another news description</description>
                    <pubDate>Tue, 02 Jan 2024 12:00:00 GMT</pubDate>
                </item>
            </channel>
        </rss>'''
        mock_get.return_value = mock_response
        
        news_items = fetch_news_from_rss("https://example.com/rss")
        
        self.assertEqual(len(news_items), 2)
        self.assertEqual(news_items[0]["title"], "Test News Title")
        self.assertEqual(news_items[0]["link"], "https://example.com/news1")
        self.assertEqual(news_items[0]["description"], "Test news description")
        self.assertEqual(news_items[1]["title"], "Another News Title")

    @patch('plugins_func.functions.get_news.requests.get')
    def test_fetch_news_from_rss_failure(self, mock_get):
        """Test RSS news fetching failure."""
        # Mock failed response
        mock_get.side_effect = Exception("Network error")
        
        news_items = fetch_news_from_rss("https://invalid-url.com/rss")
        
        self.assertEqual(news_items, [])

    @patch('plugins_func.functions.get_news.requests.get')
    def test_fetch_news_detail_success(self, mock_get):
        """Test successful news detail fetching."""
        # Mock successful HTML response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = b'''
        <html>
            <body>
                <div class="article-content">
                    <p>First paragraph of the article.</p>
                    <p>Second paragraph with more content.</p>
                </div>
            </body>
        </html>'''
        mock_get.return_value = mock_response
        
        content = fetch_news_detail("https://example.com/article")
        
        self.assertIn("First paragraph of the article.", content)
        self.assertIn("Second paragraph with more content.", content)

    @patch('plugins_func.functions.get_news.requests.get')
    def test_fetch_news_detail_failure(self, mock_get):
        """Test news detail fetching failure."""
        # Mock failed response
        mock_get.side_effect = Exception("Network error")
        
        content = fetch_news_detail("https://invalid-url.com/article")
        
        self.assertEqual(content, "Unable to fetch detailed content")

    @patch('plugins_func.functions.get_news.fetch_news_from_rss')
    @patch('core.utils.cache.manager.cache_manager')
    def test_get_news_success(self, mock_cache_manager, mock_fetch_rss):
        """Test successful news plugin execution."""
        # Mock cache miss
        mock_cache_manager.get.return_value = None
        
        # Mock news data
        news_items = [
            {
                "title": "Breaking News Title",
                "link": "https://example.com/news1",
                "description": "This is breaking news content",
                "pubDate": "Mon, 01 Jan 2024 12:00:00 GMT"
            },
            {
                "title": "Another News Title",
                "link": "https://example.com/news2", 
                "description": "This is another news content",
                "pubDate": "Tue, 02 Jan 2024 12:00:00 GMT"
            }
        ]
        mock_fetch_rss.return_value = news_items
        
        from plugins_func.register import ActionResponse, Action
        
        result = get_news(self.mock_conn, "world", False, "en_US")
        
        self.assertIsInstance(result, ActionResponse)
        self.assertEqual(result.action, Action.REQLLM)
        self.assertIsNotNone(result.result)
        self.assertIn("Breaking News Title", result.result)
        
        # Verify cache was set
        mock_cache_manager.set.assert_called_once()

    @patch('core.utils.cache.manager.cache_manager')
    def test_get_news_cache_hit(self, mock_cache_manager):
        """Test news plugin with cache hit."""
        # Mock cache hit
        cached_report = "Cached news report"
        mock_cache_manager.get.return_value = cached_report
        
        from plugins_func.register import ActionResponse, Action
        
        result = get_news(self.mock_conn, "world", False, "en_US")
        
        self.assertIsInstance(result, ActionResponse)
        self.assertEqual(result.action, Action.REQLLM)
        self.assertEqual(result.result, cached_report)

    @patch('plugins_func.functions.get_news.fetch_news_detail')
    def test_get_news_detail_success(self, mock_fetch_detail):
        """Test news plugin detail mode."""
        # Mock last news link
        self.mock_conn.last_news_link = {
            "link": "https://example.com/article",
            "title": "Test Article Title"
        }
        
        # Mock detail content
        mock_fetch_detail.return_value = "Detailed article content with full text."
        
        from plugins_func.register import ActionResponse, Action
        
        result = get_news(self.mock_conn, None, True, "en_US")
        
        self.assertIsInstance(result, ActionResponse)
        self.assertEqual(result.action, Action.REQLLM)
        self.assertIn("Test Article Title", result.result)
        self.assertIn("Detailed article content", result.result)

    def test_get_news_detail_no_previous_news(self):
        """Test news plugin detail mode without previous news."""
        # No last_news_link attribute
        from plugins_func.register import ActionResponse, Action
        
        result = get_news(self.mock_conn, None, True, "en_US")
        
        self.assertIsInstance(result, ActionResponse)
        self.assertEqual(result.action, Action.REQLLM)
        self.assertIn("no recently queried news", result.result)

    @patch('plugins_func.functions.get_news.fetch_news_from_rss')
    @patch('core.utils.cache.manager.cache_manager')
    def test_get_news_no_items(self, mock_cache_manager, mock_fetch_rss):
        """Test news plugin with no news items."""
        # Mock cache miss
        mock_cache_manager.get.return_value = None
        
        # Mock empty news data
        mock_fetch_rss.return_value = []
        
        from plugins_func.register import ActionResponse, Action
        
        result = get_news(self.mock_conn, "world", False, "en_US")
        
        self.assertIsInstance(result, ActionResponse)
        self.assertEqual(result.action, Action.REQLLM)
        self.assertIn("no news information could be retrieved", result.result)

    @patch('plugins_func.functions.get_news.fetch_news_from_rss')
    @patch('core.utils.cache.manager.cache_manager')
    def test_get_news_category_mapping(self, mock_cache_manager, mock_fetch_rss):
        """Test news plugin with different categories."""
        # Mock cache miss
        mock_cache_manager.get.return_value = None
        
        # Mock news data
        news_items = [{"title": "Tech News", "link": "#", "description": "Tech content", "pubDate": "Now"}]
        mock_fetch_rss.return_value = news_items
        
        from plugins_func.register import ActionResponse, Action
        
        # Test technology category
        result = get_news(self.mock_conn, "technology", False, "en_US")
        self.assertIsInstance(result, ActionResponse)
        
        # Test business category
        result = get_news(self.mock_conn, "business", False, "en_US")
        self.assertIsInstance(result, ActionResponse)
        
        # Test sports category
        result = get_news(self.mock_conn, "sports", False, "en_US")
        self.assertIsInstance(result, ActionResponse)

    @patch('plugins_func.functions.get_news.fetch_news_from_rss')
    @patch('core.utils.cache.manager.cache_manager')
    def test_get_news_source_rotation(self, mock_cache_manager, mock_fetch_rss):
        """Test news plugin source rotation functionality."""
        # Mock cache miss
        mock_cache_manager.get.return_value = None
        
        # Mock first source failure, second source success
        mock_fetch_rss.side_effect = [[], [{"title": "News from second source", "link": "#", "description": "Content", "pubDate": "Now"}]]
        
        from plugins_func.register import ActionResponse, Action
        
        result = get_news(self.mock_conn, "world", False, "en_US")
        
        self.assertIsInstance(result, ActionResponse)
        self.assertEqual(result.action, Action.REQLLM)
        self.assertIn("News from second source", result.result)
        
        # Verify multiple sources were tried
        self.assertGreaterEqual(mock_fetch_rss.call_count, 2)


if __name__ == '__main__':
    unittest.main()
