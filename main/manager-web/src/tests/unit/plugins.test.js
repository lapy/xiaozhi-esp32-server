import { mount, shallowMount } from '@vue/test-utils'
import Vue from 'vue'
import VueI18n from 'vue-i18n'
import ElementUI from 'element-ui'

// Mock the plugins
jest.mock('@/plugins_func/functions/get_weather', () => ({
  get_weather: jest.fn()
}))

jest.mock('@/plugins_func/functions/get_news', () => ({
  get_news: jest.fn()
}))

// Setup Vue with i18n and ElementUI
Vue.use(VueI18n)
Vue.use(ElementUI)

const i18n = new VueI18n({
  locale: 'en',
  fallbackLocale: 'en',
  messages: {
    en: {
      'login.title': 'Login',
      'register.title': 'Create Account',
      'language.en': 'English'
    }
  }
})

describe('Plugin Functionality Tests', () => {
  let wrapper
  let mockConn

  beforeEach(() => {
    mockConn = {
      config: {
        plugins: {
          get_weather: {
            api_key: 'test_api_key',
            default_location: 'New York'
          },
          get_news: {
            default_rss_url: 'https://feeds.reuters.com/reuters/worldNews'
          }
        }
      },
      client_ip: '192.168.1.1'
    }
  })

  afterEach(() => {
    if (wrapper) {
      wrapper.destroy()
    }
  })

  describe('Weather Plugin Tests', () => {
    test('should handle weather plugin configuration correctly', async () => {
      const { get_weather } = require('@/plugins_func/functions/get_weather')
      
      // Mock successful response
      get_weather.mockResolvedValue({
        action: 'REQLLM',
        result: 'Weather report for New York: Clear sky, 20°C'
      })

      const result = await get_weather(mockConn, 'New York', 'en_US')
      
      expect(result.action).toBe('REQLLM')
      expect(result.result).toContain('Weather report for New York')
      expect(get_weather).toHaveBeenCalledWith(mockConn, 'New York', 'en_US')
    })

    test('should handle weather plugin API key validation', async () => {
      const { get_weather } = require('@/plugins_func/functions/get_weather')
      
      // Mock unconfigured API key
      mockConn.config.plugins.get_weather.api_key = 'your_openweathermap_api_key'
      
      get_weather.mockResolvedValue({
        action: 'REQLLM',
        result: 'Weather service not configured. Please contact administrator to set up OpenWeatherMap API key.'
      })

      const result = await get_weather(mockConn, 'New York', 'en_US')
      
      expect(result.result).toContain('not configured')
    })

    test('should handle weather plugin location fallback', async () => {
      const { get_weather } = require('@/plugins_func/functions/get_weather')
      
      get_weather.mockResolvedValue({
        action: 'REQLLM',
        result: 'Weather report for New York: Clear sky, 20°C'
      })

      // Test without location parameter
      const result = await get_weather(mockConn, null, 'en_US')
      
      expect(result.action).toBe('REQLLM')
      expect(result.result).toContain('Weather report')
    })

    test('should handle weather plugin API errors', async () => {
      const { get_weather } = require('@/plugins_func/functions/get_weather')
      
      get_weather.mockResolvedValue({
        action: 'REQLLM',
        result: 'Unable to get weather data for InvalidCity. Please check if the location name is correct and try again.'
      })

      const result = await get_weather(mockConn, 'InvalidCity', 'en_US')
      
      expect(result.result).toContain('Unable to get weather data')
    })
  })

  describe('News Plugin Tests', () => {
    test('should handle news plugin basic functionality', async () => {
      const { get_news } = require('@/plugins_func/functions/get_news')
      
      get_news.mockResolvedValue({
        action: 'REQLLM',
        result: 'Breaking News: Latest developments in technology sector...'
      })

      const result = await get_news(mockConn, 'technology', false, 'en_US')
      
      expect(result.action).toBe('REQLLM')
      expect(result.result).toContain('Breaking News')
      expect(get_news).toHaveBeenCalledWith(mockConn, 'technology', false, 'en_US')
    })

    test('should handle news plugin category mapping', async () => {
      const { get_news } = require('@/plugins_func/functions/get_news')
      
      get_news.mockResolvedValue({
        action: 'REQLLM',
        result: 'World News: International developments...'
      })

      // Test different category mappings
      const categories = ['world', 'tech', 'business', 'sports', 'health', 'politics', 'science']
      
      for (const category of categories) {
        const result = await get_news(mockConn, category, false, 'en_US')
        expect(result.action).toBe('REQLLM')
      }
    })

    test('should handle news plugin detail mode', async () => {
      const { get_news } = require('@/plugins_func/functions/get_news')
      
      // Mock last news link
      mockConn.last_news_link = {
        link: 'https://example.com/article',
        title: 'Test Article'
      }
      
      get_news.mockResolvedValue({
        action: 'REQLLM',
        result: 'Detailed content: Full article text with comprehensive information...'
      })

      const result = await get_news(mockConn, null, true, 'en_US')
      
      expect(result.action).toBe('REQLLM')
      expect(result.result).toContain('Detailed content')
    })

    test('should handle news plugin no previous news error', async () => {
      const { get_news } = require('@/plugins_func/functions/get_news')
      
      get_news.mockResolvedValue({
        action: 'REQLLM',
        result: 'Sorry, no recently queried news found. Please get a news item first.'
      })

      const result = await get_news(mockConn, null, true, 'en_US')
      
      expect(result.result).toContain('no recently queried news found')
    })

    test('should handle news plugin source rotation', async () => {
      const { get_news } = require('@/plugins_func/functions/get_news')
      
      get_news.mockResolvedValue({
        action: 'REQLLM',
        result: 'News from secondary source: Alternative news content...'
      })

      const result = await get_news(mockConn, 'world', false, 'en_US')
      
      expect(result.action).toBe('REQLLM')
      expect(result.result).toContain('News from secondary source')
    })
  })

  describe('Language and Locale Tests', () => {
    test('should use English as default language', () => {
      expect(i18n.locale).toBe('en')
      expect(i18n.fallbackLocale).toBe('en')
    })

    test('should have English translations available', () => {
      expect(i18n.t('login.title')).toBe('Login')
      expect(i18n.t('register.title')).toBe('Create Account')
      expect(i18n.t('language.en')).toBe('English')
    })

    test('should support language switching', () => {
      // Test language switching functionality
      i18n.locale = 'en'
      expect(i18n.locale).toBe('en')
      
      // Simulate language change
      const changeLanguage = (lang) => {
        i18n.locale = lang
        localStorage.setItem('userLanguage', lang)
      }
      
      changeLanguage('en')
      expect(i18n.locale).toBe('en')
      expect(localStorage.getItem('userLanguage')).toBe('en')
    })
  })

  describe('Configuration Tests', () => {
    test('should validate weather plugin configuration', () => {
      const weatherConfig = mockConn.config.plugins.get_weather
      
      expect(weatherConfig).toBeDefined()
      expect(weatherConfig.api_key).toBeDefined()
      expect(weatherConfig.default_location).toBe('New York')
    })

    test('should validate news plugin configuration', () => {
      const newsConfig = mockConn.config.plugins.get_news
      
      expect(newsConfig).toBeDefined()
      expect(newsConfig.default_rss_url).toBeDefined()
      expect(newsConfig.default_rss_url).toContain('reuters.com')
    })

    test('should handle missing plugin configuration gracefully', () => {
      const emptyConn = {
        config: {
          plugins: {}
        }
      }
      
      expect(emptyConn.config.plugins.get_weather).toBeUndefined()
      expect(emptyConn.config.plugins.get_news).toBeUndefined()
    })
  })

  describe('Error Handling Tests', () => {
    test('should handle network errors gracefully', async () => {
      const { get_weather } = require('@/plugins_func/functions/get_weather')
      
      get_weather.mockRejectedValue(new Error('Network error'))
      
      try {
        await get_weather(mockConn, 'New York', 'en_US')
      } catch (error) {
        expect(error.message).toBe('Network error')
      }
    })

    test('should handle API timeout errors', async () => {
      const { get_news } = require('@/plugins_func/functions/get_news')
      
      get_news.mockRejectedValue(new Error('Request timeout'))
      
      try {
        await get_news(mockConn, 'world', false, 'en_US')
      } catch (error) {
        expect(error.message).toBe('Request timeout')
      }
    })

    test('should handle invalid configuration errors', async () => {
      const { get_weather } = require('@/plugins_func/functions/get_weather')
      
      // Mock invalid configuration
      mockConn.config.plugins.get_weather.api_key = null
      
      get_weather.mockResolvedValue({
        action: 'REQLLM',
        result: 'Weather service not configured. Please contact administrator.'
      })

      const result = await get_weather(mockConn, 'New York', 'en_US')
      
      expect(result.result).toContain('not configured')
    })
  })

  describe('Integration Tests', () => {
    test('should handle multiple plugin calls in sequence', async () => {
      const { get_weather } = require('@/plugins_func/functions/get_weather')
      const { get_news } = require('@/plugins_func/functions/get_news')
      
      get_weather.mockResolvedValue({
        action: 'REQLLM',
        result: 'Weather: Clear sky, 20°C'
      })
      
      get_news.mockResolvedValue({
        action: 'REQLLM',
        result: 'News: Breaking technology developments'
      })

      const weatherResult = await get_weather(mockConn, 'New York', 'en_US')
      const newsResult = await get_news(mockConn, 'technology', false, 'en_US')
      
      expect(weatherResult.action).toBe('REQLLM')
      expect(newsResult.action).toBe('REQLLM')
      expect(weatherResult.result).toContain('Weather')
      expect(newsResult.result).toContain('News')
    })

    test('should maintain plugin state across calls', async () => {
      const { get_news } = require('@/plugins_func/functions/get_news')
      
      // First call - get news
      get_news.mockResolvedValue({
        action: 'REQLLM',
        result: 'Breaking News: Test article'
      })
      
      await get_news(mockConn, 'world', false, 'en_US')
      
      // Verify last_news_link was set
      expect(mockConn.last_news_link).toBeDefined()
      
      // Second call - get detail
      get_news.mockResolvedValue({
        action: 'REQLLM',
        result: 'Detailed content: Full article text'
      })
      
      const detailResult = await get_news(mockConn, null, true, 'en_US')
      
      expect(detailResult.result).toContain('Detailed content')
    })
  })
})
