import Vue from 'vue'
import VueI18n from 'vue-i18n'
import ElementUI from 'element-ui'
import { config } from '@vue/test-utils'

// Mock localStorage
const localStorageMock = {
  getItem: jest.fn(),
  setItem: jest.fn(),
  removeItem: jest.fn(),
  clear: jest.fn(),
}
global.localStorage = localStorageMock

// Mock console methods to reduce noise in tests
global.console = {
  ...console,
  log: jest.fn(),
  debug: jest.fn(),
  info: jest.fn(),
  warn: jest.fn(),
  error: jest.fn(),
}

// Mock fetch
global.fetch = jest.fn()

// Mock XMLHttpRequest
global.XMLHttpRequest = jest.fn(() => ({
  open: jest.fn(),
  send: jest.fn(),
  setRequestHeader: jest.fn(),
  readyState: 4,
  status: 200,
  responseText: '{}',
  response: '{}'
}))

// Mock ResizeObserver
global.ResizeObserver = jest.fn(() => ({
  observe: jest.fn(),
  unobserve: jest.fn(),
  disconnect: jest.fn(),
}))

// Mock IntersectionObserver
global.IntersectionObserver = jest.fn(() => ({
  observe: jest.fn(),
  unobserve: jest.fn(),
  disconnect: jest.fn(),
}))

// Setup Vue plugins
Vue.use(VueI18n)
Vue.use(ElementUI)

// Create i18n instance for tests
const i18n = new VueI18n({
  locale: 'en',
  fallbackLocale: 'en',
  messages: {
    en: {
      // Common translations
      'login.title': 'Login',
      'register.title': 'Create Account',
      'language.en': 'English',
      
      // Weather plugin translations
      'weather.current': 'Current Weather',
      'weather.forecast': 'Forecast',
      'weather.temperature': 'Temperature',
      'weather.humidity': 'Humidity',
      'weather.pressure': 'Pressure',
      'weather.wind': 'Wind',
      'weather.visibility': 'Visibility',
      
      // News plugin translations
      'news.title': 'Latest News',
      'news.category': 'Category',
      'news.source': 'Source',
      'news.published': 'Published',
      'news.read_more': 'Read More',
      
      // Error messages
      'error.network': 'Network error occurred',
      'error.api': 'API error occurred',
      'error.configuration': 'Configuration error',
      'error.not_found': 'Resource not found'
    }
  }
})

// Global test utilities
global.testUtils = {
  i18n,
  createMockConn: () => ({
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
    client_ip: '192.168.1.1',
    last_news_link: null
  }),
  
  createMockResponse: (data, status = 200) => ({
    status,
    ok: status >= 200 && status < 300,
    json: () => Promise.resolve(data),
    text: () => Promise.resolve(JSON.stringify(data))
  }),
  
  createMockError: (message = 'Test error') => new Error(message),
  
  waitFor: (ms = 100) => new Promise(resolve => setTimeout(resolve, ms))
}

// Vue Test Utils configuration
config.mocks = {
  $t: (key) => key,
  $tc: (key) => key,
  $te: (key) => true,
  $d: (date) => date.toString(),
  $n: (number) => number.toString()
}

config.stubs = {
  'router-link': true,
  'router-view': true,
  'transition': true,
  'transition-group': true
}

// Global test helpers
global.expectAsync = async (fn) => {
  try {
    const result = await fn()
    return { success: true, result }
  } catch (error) {
    return { success: false, error }
  }
}

// Mock plugin functions
jest.mock('@/plugins_func/functions/get_weather', () => ({
  get_weather: jest.fn()
}))

jest.mock('@/plugins_func/functions/get_news', () => ({
  get_news: jest.fn()
}))

// Setup cleanup after each test
afterEach(() => {
  jest.clearAllMocks()
  localStorageMock.clear()
})
