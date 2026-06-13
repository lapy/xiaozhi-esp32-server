# Digital Human Test Module

This module provides the local digital-human test page, frontend assets, wakeword runtime, and event bridge used to exercise the full interaction flow.

For server deployment, see the root [README](../../README.md).

For all-in-one kiosk deployment and system setup, see [docs/all-in-one-digital-human-setup.md](../../docs/all-in-one-digital-human-setup.md).

For wakeword model download and runtime configuration, see [docs/digital-human-wakeword.md](../../docs/digital-human-wakeword.md).

## Quick Start

Install dependencies:

```bash
pip install -r wakeword_runtime/requirements.txt
```

Start the module:

```bash
python start.py
```

## Endpoints

- Page: http://127.0.0.1:8006/index.html
- Event bridge: ws://127.0.0.1:8006/wakeword-ws
- Health check: http://127.0.0.1:8006/health

## Layout

- `start.py`: module entrypoint
- `index.html`: digital-human test page
- `wakeword_runtime/`: local wakeword runtime and config
- `js/`, `css/`: frontend scripts and styles
- `images/`, `resources/`: page assets
- `test_runner.py`, `test_weather_plugin.py`, `test_news_plugin.py`: plugin test harnesses
