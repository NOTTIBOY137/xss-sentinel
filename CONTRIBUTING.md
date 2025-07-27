# Contributing to XSS Sentinel

Thank you for your interest in contributing to XSS Sentinel! This document provides guidelines and information for contributors.

## 🚀 Getting Started

### Prerequisites
- Python 3.8 or higher
- Git
- Basic knowledge of web security and Python

### Development Setup
```bash
# Fork and clone the repository
git clone https://github.com/YOUR_USERNAME/xss-sentinel.git
cd xss-sentinel

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -e .

# Install development dependencies
pip install -e ".[dev]"
```

## 📝 How to Contribute

### 1. Reporting Issues
- Use the GitHub issue tracker
- Provide detailed information about the problem
- Include steps to reproduce the issue
- Mention your operating system and Python version

### 2. Feature Requests
- Describe the feature you'd like to see
- Explain why this feature would be useful
- Provide examples of how it would work

### 3. Code Contributions

#### Before You Start
- Check existing issues and pull requests
- Discuss major changes in an issue first
- Ensure your code follows the project's style guidelines

#### Development Process
1. **Fork the repository**
2. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. **Make your changes**
4. **Test your changes**
   ```bash
   # Run tests
   python -m pytest tests/
   
   # Run linting
   flake8 xss_sentinel/
   
   # Test the tool
   xss-sentinel --help
   ```
5. **Commit your changes**
   ```bash
   git add .
   git commit -m "Add: brief description of changes"
   ```
6. **Push to your fork**
   ```bash
   git push origin feature/your-feature-name
   ```
7. **Create a pull request**

### 4. Code Style Guidelines

#### Python Code
- Follow PEP 8 style guidelines
- Use meaningful variable and function names
- Add docstrings to all functions and classes
- Keep functions focused and concise
- Use type hints where appropriate

#### Example:
```python
def scan_url(url: str, depth: int = 2) -> List[str]:
    """
    Scan a URL for XSS vulnerabilities.
    
    Args:
        url: The target URL to scan
        depth: Crawling depth (default: 2)
        
    Returns:
        List of discovered URLs
        
    Raises:
        ValueError: If URL is invalid
    """
    if not url.startswith(('http://', 'https://')):
        raise ValueError("URL must start with http:// or https://")
    
    # Implementation here
    return discovered_urls
```

#### Commit Messages
- Use clear, descriptive commit messages
- Start with a verb (Add, Fix, Update, Remove, etc.)
- Keep the first line under 50 characters
- Add more details in the body if needed

Examples:
```
Add: support for custom payload files
Fix: handle timeout errors gracefully
Update: improve error messages
```

## 🧪 Testing

### Running Tests
```bash
# Run all tests
python -m pytest

# Run with coverage
python -m pytest --cov=xss_sentinel

# Run specific test file
python -m pytest tests/test_scanner.py
```

### Writing Tests
- Write tests for new features
- Ensure good test coverage
- Use descriptive test names
- Mock external dependencies

## 📚 Documentation

### Code Documentation
- Add docstrings to all public functions and classes
- Use Google or NumPy docstring format
- Include examples in docstrings

### User Documentation
- Update README.md for new features
- Add usage examples
- Document configuration options

## 🔒 Security

### Responsible Disclosure
- Report security vulnerabilities privately
- Do not disclose vulnerabilities publicly
- Follow responsible disclosure practices

### Testing Guidelines
- Only test systems you own or have permission to test
- Respect rate limits and robots.txt
- Use appropriate delays between requests
- Do not perform destructive testing

## 🎯 Areas for Contribution

### High Priority
- Bug fixes and improvements
- Performance optimizations
- Better error handling
- Additional payload types
- Enhanced reporting features

### Medium Priority
- New crawling methods
- Additional AI/ML features
- Integration with other tools
- Documentation improvements
- Test coverage improvements

### Low Priority
- UI/UX improvements
- Additional output formats
- Plugin system
- Configuration management

## 🤝 Community Guidelines

### Be Respectful
- Be kind and respectful to other contributors
- Provide constructive feedback
- Help newcomers get started

### Communication
- Use clear, professional language
- Ask questions when you're unsure
- Share your knowledge with others

## 📞 Getting Help

- **Issues**: Use GitHub issues for bugs and feature requests
- **Discussions**: Use GitHub Discussions for questions and ideas
- **Documentation**: Check the README and code comments

## 🏆 Recognition

Contributors will be recognized in:
- The project README
- Release notes
- GitHub contributors page

Thank you for contributing to XSS Sentinel! 🛡️ 