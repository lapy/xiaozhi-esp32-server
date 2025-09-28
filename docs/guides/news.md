# News Plugin Integration

This document describes how to use and configure the News plugin for getting news from major news sources worldwide.

## Overview

The News plugin (`get_news`) allows users to get the latest news from major news sources through RSS feeds. It features automatic source rotation, enhanced content parsing, and robust fallback mechanisms for maximum reliability.

## Features

- **Major News Sources**: Reuters, CNN, BBC, Guardian, TechCrunch, and more
- **Multiple News Categories**: World, Technology, Business, Sports, Health, Politics, Science
- **Source Rotation**: Automatically tries multiple sources for reliability and variety
- **Enhanced Content Parsing**: Optimized for major news site structures
- **Random News Selection**: Randomly selects news items for variety
- **Detailed Content**: Can fetch full article content when requested
- **Multi-language Support**: Supports responses in different languages
- **Robust Error Handling**: Multiple fallback options and timeout management
- **Smart Content Extraction**: Advanced parsing for Reuters, CNN, BBC, Guardian, NYT, and more

## Configuration

### 1. Plugin Configuration (config.yaml)

```yaml
plugins:
  get_news:
    default_rss_url: "https://feeds.reuters.com/reuters/worldNews"
    # Built-in sources include: Reuters, CNN, BBC, Guardian, TechCrunch, and more
    # These are automatically rotated for variety and reliability
    # Custom sources can be added here if needed
```

### 2. Enable Plugin

Add the plugin to the functions list in `config.yaml`:

```yaml
Intent:
  function_call:
    functions:
      - get_news
      # ... other plugins
```

## Supported News Categories

| Category | Keywords | Description |
|----------|----------|-------------|
| **World News** | `world`, `world news`, `international`, `international news`, `global`, `global news` | Global news and international affairs |
| **Technology** | `technology`, `tech`, `tech news`, `technology news`, `innovation`, `ai`, `artificial intelligence` | Technology and innovation news |
| **Business** | `business`, `business news`, `finance`, `financial`, `economy`, `economic`, `market`, `markets`, `stocks` | Business and economic news |
| **Sports** | `sports`, `sport`, `sports news`, `football`, `soccer`, `basketball`, `baseball` | Sports news and updates |
| **Health** | `health`, `health news`, `medical`, `medicine`, `healthcare` | Health and medical news |
| **Politics** | `politics`, `political`, `election`, `government` | Political news and government affairs |
| **Science** | `science`, `scientific`, `research`, `climate`, `environment` | Science news and research |

## Usage Examples

### Basic News Query
```
User: "What's the latest news?"
Response: [Random world news item]
```

### Category-Specific News
```
User: "Get me some technology news"
Response: [Random technology news item]
```

### Detailed News Content
```
User: "Please provide more details about this news"
Response: [Full article content with summary]
```

## Function Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `category` | string | No | News category (world, technology, business, sports, health) |
| `detail` | boolean | No | Whether to get detailed content (default: false) |
| `lang` | string | Yes | Language code for response (e.g., en_US, zh_CN) |

## News Sources

The plugin automatically uses multiple RSS feeds from major news sources:

### Built-in Sources by Category

**World News:**
- Reuters World News
- CNN International Edition
- BBC World News
- Reuters Global News

**Technology:**
- Reuters Technology News
- CNN Technology
- TechCrunch
- O'Reilly Radar

**Business:**
- Reuters Business News
- CNN Money
- Reuters Wealth
- CNN Business

**Sports:**
- Reuters Sports News
- CNN Sports
- CNN Football

**Health:**
- Reuters Health News
- CNN Health

**Politics:**
- CNN Politics
- BBC Politics
- Reuters Politics

**Science:**
- BBC Science & Environment
- Reuters Science News

### Source Rotation & Reliability

The plugin automatically:
- **Tries multiple sources** in order until news is found
- **Falls back to configuration** if built-in sources fail
- **Logs source usage** for monitoring and debugging
- **Handles timeouts and errors** gracefully

## Technical Details

### RSS Parsing
- Uses `xml.etree.ElementTree` for XML parsing
- Extracts title, link, description, and publication date
- Handles various RSS formats and structures

### Content Fetching
- Uses `requests` with proper headers for web scraping
- Implements multiple content selectors for different website structures
- Limits content length to prevent excessive responses

### Error Handling
- Network timeout handling (10s for RSS, 15s for content)
- Fallback to default category if specified category fails
- Graceful degradation when content cannot be fetched

## Troubleshooting

### Common Issues

1. **No News Retrieved**
   - Check internet connectivity
   - Verify RSS URLs are accessible
   - Check logs for specific error messages

2. **Content Fetching Failures**
   - Some websites may block automated requests
   - Content selectors may need updating for site changes
   - Consider using alternative RSS sources

3. **Category Not Found**
   - Ensure category keywords match supported values
   - Check configuration for correct RSS URL mapping

### Logging

Enable debug logging to troubleshoot issues:

```python
# Check logs for:
# - RSS fetch attempts and results
# - Content parsing errors
# - Category mapping issues
```

## Security Considerations

- Uses proper User-Agent headers to avoid blocking
- Implements request timeouts to prevent hanging
- Validates RSS feed responses before parsing
- Limits content extraction to prevent abuse

## Performance

- RSS feeds are fetched on-demand (not cached)
- Content fetching is only performed when detailed content is requested
- Random selection ensures variety without performance impact
- Timeout settings prevent long waits

## Future Enhancements

Potential improvements for future versions:

1. **Caching**: Implement RSS feed caching for better performance
2. **More Sources**: Add support for additional news sources
3. **Custom Categories**: Allow user-defined category mappings
4. **Content Filtering**: Add content filtering and summarization
5. **Multi-language**: Enhanced multi-language content support

## API Reference

### Function Signature
```python
def get_news_from_western_sources(
    conn, 
    category: str = None, 
    detail: bool = False, 
    lang: str = "en_US"
) -> ActionResponse
```

### Return Types
- `ActionResponse(Action.REQLLM, message, None)`: Success with news content
- `ActionResponse(Action.REQLLM, error_message, None)`: Error or no content found

## Support

For issues or questions regarding the Western News plugin:

1. Check the logs for error messages
2. Verify configuration settings
3. Test RSS URLs manually
4. Review this documentation for troubleshooting steps

The plugin is designed to be robust and handle various edge cases, but may require configuration adjustments for specific use cases or news sources.
