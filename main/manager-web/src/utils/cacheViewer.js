/**
 * Cache viewer tool - for checking if CDN resources are cached by Service Worker
 */

/**
 * Get names of all Service Worker caches
 * @returns {Promise<string[]>} Cache name list
 */
export const getCacheNames = async () => {
  if (!('caches' in window)) {
    return [];
  }
  
  try {
    return await caches.keys();
  } catch (error) {
    console.error('Failed to get cache names:', error);
    return [];
  }
};

/**
 * Get all URLs in specified cache
 * @param {string} cacheName Cache name
 * @returns {Promise<string[]>} Cached URL list
 */
export const getCacheUrls = async (cacheName) => {
  if (!('caches' in window)) {
    return [];
  }
  
  try {
    const cache = await caches.open(cacheName);
    const requests = await cache.keys();
    return requests.map(request => request.url);
  } catch (error) {
    console.error(`Failed to get URLs for cache ${cacheName}:`, error);
    return [];
  }
};

/**
 * Check if specific URL is cached
 * @param {string} url URL to check
 * @returns {Promise<boolean>} Whether it is cached
 */
export const isUrlCached = async (url) => {
  if (!('caches' in window)) {
    return false;
  }
  
  try {
    const cacheNames = await getCacheNames();
    for (const cacheName of cacheNames) {
      const cache = await caches.open(cacheName);
      const match = await cache.match(url);
      if (match) {
        return true;
      }
    }
    return false;
  } catch (error) {
    console.error(`Failed to check if URL ${url} is cached:`, error);
    return false;
  }
};

/**
 * Get cache status of all CDN resources on current page
 * @returns {Promise<Object>} Cache status object
 */
export const checkCdnCacheStatus = async () => {
  // Find resources from CDN cache
  const cdnCaches = ['cdn-stylesheets', 'cdn-scripts'];
  const results = {
    css: [],
    js: [],
    totalCached: 0,
    totalNotCached: 0
  };
  
  for (const cacheName of cdnCaches) {
    try {
      const urls = await getCacheUrls(cacheName);
      
      // Distinguish CSS and JS resources
      for (const url of urls) {
        if (url.endsWith('.css')) {
          results.css.push({ url, cached: true });
        } else if (url.endsWith('.js')) {
          results.js.push({ url, cached: true });
        }
        results.totalCached++;
      }
    } catch (error) {
      console.error(`Failed to get ${cacheName} cache info:`, error);
    }
  }
  
  return results;
};

/**
 * Clear all Service Worker caches
 * @returns {Promise<boolean>} Whether successfully cleared
 */
export const clearAllCaches = async () => {
  if (!('caches' in window)) {
    return false;
  }
  
  try {
    const cacheNames = await getCacheNames();
    for (const cacheName of cacheNames) {
      await caches.delete(cacheName);
    }
    return true;
  } catch (error) {
    console.error('Failed to clear all caches:', error);
    return false;
  }
};

/**
 * Output cache status to console
 */
export const logCacheStatus = async () => {
  console.group('Service Worker Cache Status');
  
  const cacheNames = await getCacheNames();
  console.log('Discovered caches:', cacheNames);
  
  for (const cacheName of cacheNames) {
    const urls = await getCacheUrls(cacheName);
    console.group(`Cache: ${cacheName} (${urls.length} items)`);
    urls.forEach(url => console.log(url));
    console.groupEnd();
  }
  
  console.groupEnd();
  return cacheNames.length > 0;
}; 