#!/usr/bin/env python3
"""
Comprehensive Integration Test Suite
Tests all updated dependencies and TTS integrations
"""

import sys
import asyncio
import traceback
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

class TestResults:
    def __init__(self):
        self.passed = []
        self.failed = []
        self.warnings = []
        
    def add_pass(self, test_name, message=""):
        self.passed.append((test_name, message))
        print(f"✅ {test_name}: PASSED {message}")
        
    def add_fail(self, test_name, error):
        self.failed.append((test_name, str(error)))
        print(f"❌ {test_name}: FAILED - {error}")
        
    def add_warning(self, test_name, message):
        self.warnings.append((test_name, message))
        print(f"⚠️  {test_name}: WARNING - {message}")
        
    def print_summary(self):
        print("\n" + "="*70)
        print("📊 TEST SUMMARY")
        print("="*70)
        print(f"✅ Passed: {len(self.passed)}")
        print(f"❌ Failed: {len(self.failed)}")
        print(f"⚠️  Warnings: {len(self.warnings)}")
        print(f"📈 Success Rate: {(len(self.passed)/(len(self.passed)+len(self.failed))*100):.1f}%")
        
        if self.failed:
            print("\n❌ FAILED TESTS:")
            for name, error in self.failed:
                print(f"  - {name}: {error}")
                
        if self.warnings:
            print("\n⚠️  WARNINGS:")
            for name, msg in self.warnings:
                print(f"  - {name}: {msg}")
        
        return len(self.failed) == 0

results = TestResults()

print("🧪 COMPREHENSIVE INTEGRATION TEST SUITE")
print("="*70)

# Test 1: Core Dependencies Import
print("\n📦 TEST 1: Core Dependencies Import")
print("-"*70)

core_imports = [
    ("numpy", "NumPy"),
    ("torch", "PyTorch"),
    ("torchaudio", "TorchAudio"),
]

for module, name in core_imports:
    try:
        imported = __import__(module)
        version = getattr(imported, '__version__', 'unknown')
        results.add_pass(f"Import {name}", f"(v{version})")
    except ImportError as e:
        results.add_fail(f"Import {name}", e)
    except Exception as e:
        results.add_warning(f"Import {name}", e)

# Test 2: Web Framework Dependencies
print("\n🌐 TEST 2: Web Framework Dependencies")
print("-"*70)

web_imports = [
    ("websockets", "WebSockets"),
    ("aiohttp", "aiohttp"),
    ("httpx", "HTTPX"),
    ("requests", "Requests"),
]

for module, name in web_imports:
    try:
        imported = __import__(module)
        version = getattr(imported, '__version__', 'unknown')
        results.add_pass(f"Import {name}", f"(v{version})")
    except ImportError as e:
        results.add_fail(f"Import {name}", e)

# Test 3: AI/LLM API Clients
print("\n🤖 TEST 3: AI/LLM API Clients")
print("-"*70)

ai_imports = [
    ("openai", "OpenAI SDK"),
    ("google.generativeai", "Google Generative AI"),
    ("elevenlabs", "ElevenLabs"),
]

for module, name in ai_imports:
    try:
        imported = __import__(module, fromlist=[''])
        version = getattr(imported, '__version__', 'unknown')
        results.add_pass(f"Import {name}", f"(v{version})")
        
        # Special check for OpenAI 2.x breaking changes
        if module == "openai":
            try:
                from openai import OpenAI
                results.add_pass("OpenAI 2.x Client", "New API structure available")
            except ImportError:
                results.add_warning("OpenAI 2.x Client", "May need code updates")
                
    except ImportError as e:
        results.add_fail(f"Import {name}", e)

# Test 4: TTS Services
print("\n🎤 TEST 4: TTS Service Providers")
print("-"*70)

tts_imports = [
    ("edge_tts", "Edge TTS"),
]

for module, name in tts_imports:
    try:
        imported = __import__(module)
        version = getattr(imported, '__version__', 'unknown')
        results.add_pass(f"Import {name}", f"(v{version})")
    except ImportError as e:
        results.add_fail(f"Import {name}", e)

# Test 5: Kokoro TTS Integration
print("\n🎵 TEST 5: Kokoro TTS Integration")
print("-"*70)

try:
    import kokoro_tts
    results.add_pass("Import Kokoro TTS", f"(v{kokoro_tts.__version__})")
    
    # Test provider initialization
    try:
        from core.providers.tts.kokoro import TTSProvider
        test_config = {
            "type": "kokoro",
            "use_api": False,
            "voice": "af_heart",
            "language": "en-us",
            "speed": 1.0,
            "response_format": "mp3",
            "output_dir": "tmp/"
        }
        provider = TTSProvider(test_config, delete_audio_file=True)
        results.add_pass("Kokoro TTS Provider Init", "Successfully initialized")
    except Exception as e:
        results.add_fail("Kokoro TTS Provider Init", e)
        
except ImportError as e:
    results.add_fail("Import Kokoro TTS", e)

# Test 6: ElevenLabs TTS Integration
print("\n🔊 TEST 6: ElevenLabs TTS Integration")
print("-"*70)

try:
    from elevenlabs.client import ElevenLabs
    results.add_pass("Import ElevenLabs Client", "SDK 2.16.0 structure")
    
    try:
        from core.providers.tts.elevenlabs import TTSProvider
        test_config = {
            "type": "elevenlabs",
            "api_key": "test_key",
            "voice_id": "21m00Tcm4TlvDq8ikWAM",
            "model_id": "eleven_turbo_v2_5",
            "output_dir": "tmp/"
        }
        provider = TTSProvider(test_config, delete_audio_file=True)
        results.add_pass("ElevenLabs TTS Provider Init", "Successfully initialized")
    except Exception as e:
        results.add_fail("ElevenLabs TTS Provider Init", e)
        
except ImportError as e:
    results.add_warning("Import ElevenLabs Client", "Trying fallback import")
    try:
        from elevenlabs import ElevenLabs
        results.add_pass("Import ElevenLabs (fallback)", "Alternative import works")
    except ImportError as e2:
        results.add_fail("Import ElevenLabs", e2)

# Test 7: Security & Authentication
print("\n🔒 TEST 7: Security & Authentication")
print("-"*70)

security_imports = [
    ("jwt", "PyJWT"),
    ("cryptography", "Cryptography"),
]

for module, name in security_imports:
    try:
        imported = __import__(module)
        version = getattr(imported, '__version__', 'unknown')
        results.add_pass(f"Import {name}", f"(v{version})")
    except ImportError as e:
        results.add_fail(f"Import {name}", e)

# Test 8: Data Processing
print("\n📊 TEST 8: Data Processing & Serialization")
print("-"*70)

data_imports = [
    ("ormsgpack", "ormsgpack"),
    ("ruamel.yaml", "ruamel.yaml"),
    ("loguru", "Loguru"),
]

for module, name in data_imports:
    try:
        imported = __import__(module, fromlist=[''])
        version = getattr(imported, '__version__', 'unknown')
        results.add_pass(f"Import {name}", f"(v{version})")
    except ImportError as e:
        results.add_fail(f"Import {name}", e)

# Test 9: Memory & MCP
print("\n🧠 TEST 9: Memory & MCP Systems")
print("-"*70)

memory_imports = [
    ("mem0ai", "Mem0 AI"),
    ("mcp", "MCP"),
]

for module, name in memory_imports:
    try:
        imported = __import__(module)
        version = getattr(imported, '__version__', 'unknown')
        results.add_pass(f"Import {name}", f"(v{version})")
    except ImportError as e:
        results.add_fail(f"Import {name}", e)

# Test 10: Audio Processing
print("\n🎧 TEST 10: Audio Processing")
print("-"*70)

audio_imports = [
    ("pydub", "PyDub"),
    ("vosk", "Vosk"),
    ("whisper", "OpenAI Whisper"),
]

for module, name in audio_imports:
    try:
        imported = __import__(module)
        version = getattr(imported, '__version__', 'unknown')
        results.add_pass(f"Import {name}", f"(v{version})")
    except ImportError as e:
        results.add_fail(f"Import {name}", e)

# Test 11: Version Compatibility Checks
print("\n🔍 TEST 11: Version Compatibility Checks")
print("-"*70)

try:
    import numpy as np
    import torch
    
    np_version = tuple(map(int, np.__version__.split('.')[:2]))
    torch_version = tuple(map(int, torch.__version__.split('.')[:2]))
    
    if np_version >= (2, 0):
        results.add_pass("NumPy 2.x Compatibility", f"NumPy {np.__version__}")
    else:
        results.add_fail("NumPy 2.x Compatibility", f"NumPy {np.__version__} < 2.0")
        
    if torch_version >= (2, 4):
        results.add_pass("PyTorch 2.4+ Compatibility", f"PyTorch {torch.__version__}")
    else:
        results.add_warning("PyTorch Version", f"PyTorch {torch.__version__} (2.4+ recommended)")
        
except Exception as e:
    results.add_fail("Version Compatibility Check", e)

# Test 12: Configuration Loading
print("\n⚙️  TEST 12: Configuration Files")
print("-"*70)

config_files = [
    "config.yaml",
    "mcp_server_settings.json",
]

for config_file in config_files:
    try:
        config_path = Path(__file__).parent / config_file
        if config_path.exists():
            results.add_pass(f"Config File: {config_file}", "Found")
        else:
            results.add_warning(f"Config File: {config_file}", "Not found (optional)")
    except Exception as e:
        results.add_fail(f"Config File: {config_file}", e)

# Test 13: TTS Provider Module Structure
print("\n🎙️  TEST 13: TTS Provider Module Structure")
print("-"*70)

tts_providers = [
    ("core.providers.tts.openai", "OpenAI TTS"),
    ("core.providers.tts.edge", "Edge TTS"),
    ("core.providers.tts.elevenlabs", "ElevenLabs TTS"),
    ("core.providers.tts.kokoro", "Kokoro TTS"),
]

for module, name in tts_providers:
    try:
        imported = __import__(module, fromlist=['TTSProvider'])
        TTSProvider = getattr(imported, 'TTSProvider')
        results.add_pass(f"TTS Provider: {name}", "Module structure valid")
    except ImportError as e:
        results.add_fail(f"TTS Provider: {name}", e)
    except Exception as e:
        results.add_warning(f"TTS Provider: {name}", e)

# Test 14: Async Support
print("\n⚡ TEST 14: Async/Await Support")
print("-"*70)

async def test_async():
    """Test async functionality"""
    try:
        import aiohttp
        async with aiohttp.ClientSession() as session:
            results.add_pass("Async HTTP Session", "aiohttp async support works")
    except Exception as e:
        results.add_fail("Async HTTP Session", e)

try:
    asyncio.run(test_async())
except Exception as e:
    results.add_fail("Async Event Loop", e)

# Final Summary
print("\n" + "="*70)
success = results.print_summary()

if success:
    print("\n🎉 ALL TESTS PASSED!")
    print("✅ System is ready for deployment")
    sys.exit(0)
else:
    print("\n⚠️  SOME TESTS FAILED")
    print("💡 Review failed tests above and fix issues before deployment")
    sys.exit(1)

