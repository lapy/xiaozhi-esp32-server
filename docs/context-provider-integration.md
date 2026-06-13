# Context Provider Guide

## Overview

A context provider adds external data sources to Xiaozhi's system prompt context.

At wake time, Xiaozhi can fetch data from external systems and inject it into the large language model's system prompt. This lets the assistant start each interaction with fresh awareness of device state, environment data, or business status.

Context providers are different from MCP and memory:

- `Context providers` inject wake-time context proactively.
- `Memory` helps Xiaozhi remember prior conversations.
- `MCP` is used when the assistant needs to actively call a tool or query a capability during the conversation.

Typical use cases include:

- health or wellness sensor summaries
- live business metrics such as server load, queue length, or market data
- any text payload available from an HTTP API

This feature is best for preload context. If you need Xiaozhi to fetch live data after wake-up on demand, pair it with MCP tool calls.

## How It Works

1. Configure one or more HTTP API endpoints.
2. When the prompt template includes `{{ dynamic_context }}`, Xiaozhi requests those endpoints.
3. Returned data is formatted into Markdown and injected into the prompt.

## API Requirements

To work reliably, your API should follow these rules:

- Method: `GET`
- Headers: Xiaozhi automatically sends `device-id` in the request headers
- Response format: JSON with `code` and `data`

### Response Examples

**Example 1: key/value payload**

```json
{
  "code": 0,
  "msg": "success",
  "data": {
    "Living room temperature": "26 C",
    "Living room humidity": "45%",
    "Front door": "Closed"
  }
}
```

Injected result:

```markdown
<context>
- **Living room temperature:** 26 C
- **Living room humidity:** 45%
- **Front door:** Closed
</context>
```

**Example 2: list payload**

```json
{
  "code": 0,
  "data": [
    "You have 10 open tasks",
    "The current vehicle speed is 100 km/h"
  ]
}
```

Injected result:

```markdown
<context>
- You have 10 open tasks
- The current vehicle speed is 100 km/h
</context>
```

## Configuration

### Option 1: Admin Console configuration

1. Sign in to the Admin Console.
2. Open the role or agent configuration page.
3. Find the context provider setting and select `Edit Sources`.
4. Add one or more API URLs.
5. If your API requires authentication, add the necessary request headers.
6. Save the configuration.

### Option 2: Config file configuration

Edit `xiaozhi-server/data/.config.yaml` and add a `context_providers` section:

```yaml
# Context provider configuration
context_providers:
  - url: "http://api.example.com/data"
    headers:
      Authorization: "Bearer your-token"
  - url: "http://another-api.example.com/data"
```

## Enabling Prompt Injection

By default, the prompt template in `data/.agent-base-prompt.txt` already contains the `{{ dynamic_context }}` placeholder, so most deployments do not need to add it manually.

Example:

```markdown
<context>
[Important: the following information has already been provided in real time. Use it directly instead of calling tools.]
- **Device ID:** {{device_id}}
- **Current time:** {{current_time}}
...
{{ dynamic_context }}
</context>
```

If you do not want to use context providers, either leave `context_providers` unset or remove `{{ dynamic_context }}` from the prompt template.

## Appendix: Mock Test Service

The following local mock server is useful for testing and development.

**mock_api_server.py**

```python
import http.server
import json
import socketserver
from urllib.parse import parse_qs, urlparse

PORT = 8081


class MockRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        query = parse_qs(parsed_path.query)

        response_data = {}
        status_code = 200

        print(f"Received request: {path}, query: {query}")

        if path == "/health":
            device_id = self.headers.get("device-id", "unknown_device")
            print(f"device_id: {device_id}")
            response_data = {
                "code": 0,
                "msg": "success",
                "data": {
                    "Device under test": device_id,
                    "Heart rate": "80 bpm",
                    "Blood pressure": "120/80 mmHg",
                    "Status": "Good"
                }
            }
        elif path == "/news/list":
            response_data = {
                "code": 0,
                "msg": "success",
                "data": [
                    "Headline: Python 3.14 released",
                    "Tech news: AI assistants reshape daily life",
                    "Local alert: heavy rain expected tomorrow"
                ]
            }
        elif path == "/weather/simple":
            response_data = {
                "code": 0,
                "msg": "success",
                "data": "Sunny turning partly cloudy today, 20-25 C, good air quality."
            }
        elif path == "/device/info":
            device_id = self.headers.get("device-id", "unknown_device")
            response_data = {
                "code": 0,
                "msg": "success",
                "data": {
                    "Lookup mode": "Header parameter",
                    "Device ID": device_id,
                    "Battery": "85%",
                    "Firmware": "v2.0.1"
                }
            }
        else:
            status_code = 404
            response_data = {"error": "Endpoint not found"}

        self.send_response(status_code)
        self.send_header("Content-type", "application/json; charset=utf-8")
        self.end_headers()
        self.wfile.write(json.dumps(response_data, ensure_ascii=False).encode("utf-8"))


socketserver.TCPServer.allow_reuse_address = True
with socketserver.TCPServer(("", PORT), MockRequestHandler) as httpd:
    print("==================================================")
    print(f"Mock API server started: http://localhost:{PORT}")
    print("Available endpoints:")
    print(f"1. [Dict]   http://localhost:{PORT}/health")
    print(f"2. [List]   http://localhost:{PORT}/news/list")
    print(f"3. [Text]   http://localhost:{PORT}/weather/simple")
    print(f"4. [Query]  http://localhost:{PORT}/device/info")
    print("==================================================")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\\nServer stopped")
```
