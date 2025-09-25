# Request Library

The current project uses Alova as the only HTTP request library:

## Usage

- **Alova HTTP**: Path (src/http/request/alova.ts)
- **Example code**: src/api/foo-alova.ts and src/api/foo.ts
- **API documentation**: https://alova.js.org/

## Configuration

Alova instance is configured:
- Automatic Token authentication and refresh
- Unified error handling and prompts
- Support dynamic domain switching
- Built-in request/response interceptors

## Usage Examples

```typescript
import { http } from '@/http/request/alova'

// GET request
http.Get<ResponseType>('/api/path', {
  params: { id: 1 },
  headers: { 'Custom-Header': 'value' },
  meta: { toast: false } // Disable error prompts
})

// POST request  
http.Post<ResponseType>('/api/path', data, {
  params: { query: 'param' },
  headers: { 'Content-Type': 'application/json' }
})
```