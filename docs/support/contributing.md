# 🤝 Contributing

This guide explains how to contribute to Xiaozhi ESP32 Server, including code contributions, documentation, testing, and community support.

## 🎯 Contributing Overview

We welcome contributions from everyone! Whether you're fixing bugs, adding features, improving documentation, or helping other users, your contributions make Xiaozhi ESP32 Server better for everyone.

## 🌟 Types of Contributions

### **Code Contributions**
- **Bug fixes** and improvements
- **New features** and enhancements
- **Performance optimizations**
- **Security improvements**
- **Code refactoring** and cleanup
- **Plugin development**
- **API improvements**

### **Documentation**
- **Writing guides** and tutorials
- **Improving existing** documentation
- **Translating content** to other languages
- **Creating examples** and code samples
- **Updating API** documentation
- **Adding troubleshooting** guides

### **Testing and Quality Assurance**
- **Testing new features** and bug fixes
- **Reporting bugs** and issues
- **Performance testing** and benchmarking
- **Security testing** and vulnerability assessment
- **User acceptance testing**
- **Cross-platform testing**

### **Community Support**
- **Helping other users** with questions
- **Answering questions** in discussions
- **Sharing knowledge** and experiences
- **Mentoring newcomers**
- **Organizing events** and meetups
- **Creating video tutorials**

## 🚀 Getting Started

### **Prerequisites**
- **Git** installed on your system
- **Python 3.8+** for development
- **Docker** for testing (optional)
- **ESP32 development board** for hardware testing (optional)
- **Basic understanding** of Python and web technologies

### **Development Environment Setup**

#### **Step 1: Fork and Clone**
```bash
# Fork the repository on GitHub
# Then clone your fork
git clone https://github.com/YOUR_USERNAME/xiaozhi-esp32-server.git
cd xiaozhi-esp32-server

# Add upstream remote
git remote add upstream https://github.com/lapy/xiaozhi-esp32-server.git
```

#### **Step 2: Create Virtual Environment**
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows
venv\Scripts\activate
# On macOS/Linux
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

#### **Step 3: Install Development Tools**
```bash
# Install pre-commit hooks
pre-commit install

# Install development dependencies
pip install pytest pytest-cov black flake8 mypy
```

#### **Step 4: Run Tests**
```bash
# Run all tests
pytest

# Run tests with coverage
pytest --cov=xiaozhi

# Run specific test file
pytest tests/test_core.py
```

## 📝 Development Workflow

### **Branch Strategy**
- **main**: Production-ready code
- **develop**: Integration branch for features
- **feature/**: New features and enhancements
- **bugfix/**: Bug fixes and improvements
- **hotfix/**: Critical bug fixes
- **docs/**: Documentation updates

### **Commit Message Format**
```
type(scope): description

[optional body]

[optional footer]
```

#### **Types**
- **feat**: New feature
- **fix**: Bug fix
- **docs**: Documentation changes
- **style**: Code style changes
- **refactor**: Code refactoring
- **test**: Test additions or changes
- **chore**: Maintenance tasks

#### **Examples**
```
feat(api): add new endpoint for device status
fix(websocket): resolve connection timeout issue
docs(readme): update installation instructions
test(core): add unit tests for audio processing
```

### **Pull Request Process**

#### **Step 1: Create Feature Branch**
```bash
# Create and switch to new branch
git checkout -b feature/your-feature-name

# Make your changes
# ... edit files ...

# Stage changes
git add .

# Commit changes
git commit -m "feat(scope): add your feature"
```

#### **Step 2: Push and Create PR**
```bash
# Push branch to your fork
git push origin feature/your-feature-name

# Create pull request on GitHub
# Fill out PR template with:
# - Description of changes
# - Testing instructions
# - Screenshots (if applicable)
# - Related issues
```

#### **Step 3: Code Review**
- **Address feedback** from reviewers
- **Update tests** if needed
- **Update documentation** if needed
- **Ensure all checks pass**

#### **Step 4: Merge**
- **Squash commits** if requested
- **Delete feature branch** after merge
- **Update local repository**

## 🧪 Testing Guidelines

### **Test Types**

#### **Unit Tests**
```python
# tests/test_core/test_audio.py
import pytest
from xiaozhi.core.audio import AudioProcessor

def test_audio_processing():
    processor = AudioProcessor()
    result = processor.process_audio("test_audio.wav")
    assert result is not None
    assert result.sample_rate == 16000
```

#### **Integration Tests**
```python
# tests/test_integration/test_websocket.py
import pytest
import asyncio
from xiaozhi.core.websocket import WebSocketServer

@pytest.mark.asyncio
async def test_websocket_connection():
    server = WebSocketServer()
    await server.start()
    
    # Test connection
    # ... test code ...
    
    await server.stop()
```

#### **End-to-End Tests**
```python
# tests/test_e2e/test_voice_interaction.py
import pytest
from xiaozhi.testing.e2e import VoiceInteractionTest

def test_voice_interaction():
    test = VoiceInteractionTest()
    result = test.test_voice_command("turn on the light")
    assert result.success
    assert "light" in result.response
```

### **Test Coverage**
- **Minimum coverage**: 80% for new code
- **Critical components**: 90% coverage
- **API endpoints**: 100% coverage
- **Core functionality**: 95% coverage

### **Running Tests**
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=xiaozhi --cov-report=html

# Run specific test category
pytest tests/test_unit/
pytest tests/test_integration/
pytest tests/test_e2e/

# Run with verbose output
pytest -v

# Run tests in parallel
pytest -n auto
```

## 📚 Documentation Guidelines

### **Documentation Types**

#### **Code Documentation**
```python
def process_audio(audio_data: bytes, format: str = "wav") -> AudioResult:
    """
    Process audio data for speech recognition.
    
    Args:
        audio_data: Raw audio data bytes
        format: Audio format (wav, mp3, ogg)
        
    Returns:
        AudioResult: Processed audio with metadata
        
    Raises:
        AudioProcessingError: If audio processing fails
        UnsupportedFormatError: If format is not supported
    """
    # Implementation here
    pass
```

#### **API Documentation**
```markdown
## POST /api/v1/audio/process

Process audio data and get response.

### Request
```json
{
    "audio_data": "base64_encoded_audio",
    "format": "wav",
    "device_id": "esp32_device_001"
}
```

### Response
```json
{
    "success": true,
    "transcription": "turn on the light",
    "response": "I'll turn on the light for you.",
    "processing_time": 1.5
}
```
```

#### **User Guides**
```markdown
# Getting Started Guide

This guide will help you get started with Xiaozhi ESP32 Server.

## Prerequisites

Before you begin, ensure you have:
- ESP32 development board
- USB cable
- Computer with Python 3.8+

## Installation

1. Clone the repository
2. Install dependencies
3. Configure settings
4. Start the server
```

### **Documentation Standards**
- **Clear and concise** language
- **Step-by-step** instructions
- **Code examples** for all features
- **Screenshots** for UI elements
- **Troubleshooting** sections
- **Regular updates** with code changes

## 🔌 Plugin Development

### **Plugin Structure**
```
plugins/my_plugin/
├── __init__.py
├── my_plugin.py
├── config.yaml
├── tests/
│   └── test_my_plugin.py
└── README.md
```

### **Plugin Template**
```python
# plugins/my_plugin/my_plugin.py
from plugins.base.plugin import BasePlugin
import logging

logger = logging.getLogger(__name__)

class MyPlugin(BasePlugin):
    """My custom plugin"""
    
    def __init__(self, config):
        super().__init__(config)
        self.api_key = config.get('api_key')
    
    def initialize(self):
        """Initialize the plugin"""
        if not self.api_key:
            raise ValueError("API key is required")
        self.logger.info("Plugin initialized")
    
    def process_command(self, command, context=None):
        """Process voice commands"""
        if "hello" in command.lower():
            return "Hello from my plugin!"
        return None
    
    def get_status(self):
        """Get plugin status"""
        return {
            "name": self.name,
            "version": self.version,
            "enabled": self.enabled,
            "status": "running"
        }
```

### **Plugin Testing**
```python
# plugins/my_plugin/tests/test_my_plugin.py
import pytest
from plugins.my_plugin import MyPlugin

def test_plugin_initialization():
    config = {"api_key": "test_key"}
    plugin = MyPlugin(config)
    plugin.initialize()
    assert plugin.enabled

def test_plugin_command():
    config = {"api_key": "test_key"}
    plugin = MyPlugin(config)
    plugin.initialize()
    
    response = plugin.process_command("hello")
    assert response == "Hello from my plugin!"
```

## 🐛 Bug Reports

### **Bug Report Template**
```markdown
## Bug Report

### Description
Brief description of the bug

### Steps to Reproduce
1. Go to '...'
2. Click on '....'
3. Scroll down to '....'
4. See error

### Expected Behavior
What you expected to happen

### Actual Behavior
What actually happened

### Environment
- OS: [e.g., Windows 10, macOS 12, Ubuntu 20.04]
- Python Version: [e.g., 3.8.10]
- Xiaozhi Version: [e.g., 1.0.0]
- ESP32 Board: [e.g., ESP32-S3-DevKitC-1]

### Additional Context
Any other context about the problem

### Logs
```
Paste relevant logs here
```
```

### **Bug Report Guidelines**
- **Search existing issues** before creating new ones
- **Provide clear steps** to reproduce the bug
- **Include environment** information
- **Attach logs** and error messages
- **Use descriptive titles**
- **Tag appropriately** with labels

## ✨ Feature Requests

### **Feature Request Template**
```markdown
## Feature Request

### Description
Brief description of the feature

### Use Case
Why would this feature be useful?

### Proposed Solution
How would you like this feature to work?

### Alternatives Considered
What other solutions have you considered?

### Additional Context
Any other context about the feature request
```

### **Feature Request Guidelines**
- **Search existing requests** before creating new ones
- **Provide clear use cases** and benefits
- **Include mockups** or examples if applicable
- **Consider implementation** complexity
- **Tag appropriately** with labels

## 🔍 Code Review Guidelines

### **For Contributors**
- **Write clear commit messages**
- **Include tests** for new features
- **Update documentation** as needed
- **Follow coding standards**
- **Address review feedback** promptly

### **For Reviewers**
- **Be constructive** and helpful
- **Test the changes** locally
- **Check for security** issues
- **Verify tests** pass
- **Ensure documentation** is updated

### **Review Checklist**
- [ ] **Code quality** and style
- [ ] **Test coverage** and quality
- [ ] **Documentation** updates
- [ ] **Security** considerations
- [ ] **Performance** impact
- [ ] **Backward compatibility**
- [ ] **Error handling** and logging

## 📊 Performance Guidelines

### **Performance Standards**
- **API response time**: < 200ms average
- **WebSocket latency**: < 50ms
- **Memory usage**: < 80% of available
- **CPU usage**: < 70% average
- **Audio processing**: < 100ms latency

### **Performance Testing**
```python
# tests/test_performance/test_api_performance.py
import pytest
import time
from xiaozhi.api import APIClient

def test_api_response_time():
    client = APIClient()
    
    start_time = time.time()
    response = client.get_status()
    end_time = time.time()
    
    response_time = end_time - start_time
    assert response_time < 0.2  # 200ms
```

### **Performance Optimization**
- **Use async/await** for I/O operations
- **Implement caching** for frequently accessed data
- **Optimize database** queries
- **Use connection pooling**
- **Profile and benchmark** regularly

## 🔐 Security Guidelines

### **Security Best Practices**
- **Validate all inputs** and sanitize data
- **Use parameterized queries** to prevent SQL injection
- **Implement rate limiting** to prevent abuse
- **Use HTTPS/WSS** for secure connections
- **Store secrets** securely (environment variables)
- **Regular security audits** and updates

### **Security Testing**
```python
# tests/test_security/test_input_validation.py
import pytest
from xiaozhi.api import APIClient

def test_sql_injection_prevention():
    client = APIClient()
    
    # Test SQL injection attempt
    malicious_input = "'; DROP TABLE users; --"
    response = client.process_command(malicious_input)
    
    # Should not cause database error
    assert response.success
    assert "error" not in response.data
```

### **Security Checklist**
- [ ] **Input validation** and sanitization
- [ ] **Authentication** and authorization
- [ ] **Rate limiting** implementation
- [ ] **Secure communication** (HTTPS/WSS)
- [ ] **Secret management** (API keys, passwords)
- [ ] **Error handling** (no sensitive data exposure)
- [ ] **Dependency updates** and vulnerability scanning

## 🎯 Release Process

### **Release Checklist**
- [ ] **All tests pass** (unit, integration, e2e)
- [ ] **Documentation updated** for new features
- [ ] **Changelog updated** with new changes
- [ ] **Version bumped** in all relevant files
- [ ] **Security scan** completed
- [ ] **Performance benchmarks** met
- [ ] **Backward compatibility** verified

### **Release Steps**
1. **Create release branch** from develop
2. **Update version numbers** and changelog
3. **Run full test suite** and security scan
4. **Create release notes** and documentation
5. **Tag release** and create GitHub release
6. **Deploy to production** and monitor
7. **Announce release** to community

## 🏆 Recognition and Rewards

### **Contributor Recognition**
- **Contributor badge** on GitHub profile
- **Recognition in README** for significant contributions
- **Featured contributor** profile on website
- **Community highlight** in newsletters
- **Conference speaking** opportunities

### **Contribution Levels**
- **Bronze**: 1-5 contributions
- **Silver**: 6-20 contributions
- **Gold**: 21+ contributions
- **Platinum**: Exceptional contributions and leadership

## 🆘 Getting Help

### **Development Help**
- **Discord #development**: Real-time development discussions
- **GitHub Discussions**: Technical questions and discussions
- **Code review**: Get feedback on your contributions
- **Mentorship**: Connect with experienced contributors

### **Resources**
- **[Development Setup](#development-environment-setup)** - Get your environment ready
- **[Testing Guidelines](#testing-guidelines)** - Learn how to test your code
- **[Documentation Guidelines](#documentation-guidelines)** - Write great documentation
- **[Community Support](../support/community.md)** - Connect with the community

## 🎯 Next Steps

After reading this guide:

1. **[Set Up Development Environment](#development-environment-setup)** - Get ready to contribute
2. **[Join the Community](../support/community.md)** - Connect with other contributors
3. **[Find Your First Issue](https://github.com/lapy/xiaozhi-esp32-server/issues)** - Start contributing
4. **[Create Your First PR](#pull-request-process)** - Submit your contribution

## 🆘 Need Help?

- **Development Questions?** Join [Discord #development](https://discord.gg/xiaozhi-esp32)
- **Technical Issues?** Check [GitHub Discussions](https://github.com/lapy/xiaozhi-esp32-server/discussions)
- **General Questions?** Browse [FAQ](../support/faq.md)

---

## 🎯 Quick Reference

### **Development Setup**
```bash
git clone https://github.com/YOUR_USERNAME/xiaozhi-esp32-server.git
cd xiaozhi-esp32-server
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### **Testing**
```bash
pytest
pytest --cov=xiaozhi
pytest tests/test_unit/
```

### **Contributing**
1. Fork repository
2. Create feature branch
3. Make changes
4. Write tests
5. Submit PR

### **Code Standards**
- Follow PEP 8
- Write tests
- Update documentation
- Use type hints
- Write clear commit messages

---

**Thank you for contributing to Xiaozhi ESP32 Server! 🎉**

👉 **[Next: Community →](community.md)**
