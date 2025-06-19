# Contributing to Cascadia Watershed Lookup

Thank you for your interest in contributing to the Cascadia Watershed Lookup project! This document provides guidelines for contributing to this cross-border watershed identification service.

## 🌊 Project Overview

Cascadia Watershed Lookup is a web service that helps people identify their watersheds across the Pacific Northwest bioregion, supporting both US and Canadian addresses with intelligent geocoding and validation.

## 🚀 Getting Started

### Development Setup

1. **Fork and clone the repository**
   ```bash
   git clone https://github.com/yourusername/CascadiaWatershedLookup.git
   cd CascadiaWatershedLookup
   ```

2. **Set up development environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Configure environment (optional but recommended)**
   ```bash
   export GOOGLE_MAPS_API_KEY="your-google-maps-api-key"
   ```

4. **Run the application**
   ```bash
   python app.py
   ```

5. **Run tests**
   ```bash
   python test_canadian_geocoding.py
   python -m pytest tests/ -v
   ```

## 📝 How to Contribute

### Types of Contributions

- **🐛 Bug Reports**: Found a bug? Please report it!
- **✨ Feature Requests**: Have an idea for improvement?
- **📚 Documentation**: Help improve our docs
- **🔧 Code Improvements**: Bug fixes, performance improvements
- **🗺️ Data Enhancements**: Expand watershed coverage
- **🧪 Testing**: Add test cases, improve test coverage

### Contribution Process

1. **Check existing issues** - Search for existing issues or discussions
2. **Create an issue** - For bugs or feature requests
3. **Fork the repository** - Create your own copy
4. **Create a feature branch** - `git checkout -b feature/amazing-feature`
5. **Make your changes** - Follow coding standards
6. **Test your changes** - Ensure tests pass
7. **Commit your changes** - Use clear commit messages
8. **Push to your fork** - `git push origin feature/amazing-feature`
9. **Open a Pull Request** - Describe your changes

## 🔧 Development Guidelines

### Code Style

- **Python**: Follow PEP 8 style guide
- **JavaScript**: Use consistent formatting and modern ES6+ features
- **HTML/CSS**: Semantic HTML, responsive design principles
- **Comments**: Write clear, helpful comments for complex logic

### Coding Standards

```python
# Good: Clear function with type hints
def geocode_address(self, address: str, api_key: Optional[str] = None) -> Optional[Tuple[float, float]]:
    """
    Convert address to coordinates using Google Maps API.
    
    Args:
        address: Full street address to geocode
        api_key: Optional Google Maps API key
        
    Returns:
        Tuple of (latitude, longitude) or None if geocoding fails
    """
    # Implementation here
```

### Testing Requirements

- **Unit Tests**: Test individual functions and methods
- **Integration Tests**: Test API endpoints and full workflows  
- **Manual Testing**: Test with real addresses from different regions
- **Error Handling**: Test edge cases and error conditions

```bash
# Run all tests
python -m pytest tests/ -v

# Run with coverage
python -m pytest tests/ --cov=.

# Manual testing
python test_canadian_geocoding.py
```

### Documentation

- Update README.md for new features
- Add docstrings for new functions
- Update API documentation for endpoint changes
- Include examples for new functionality

## 🗺️ Data Contributions

### Current Dataset
- **US Data**: 9,998 watersheds from USGS WBD
- **Canadian Data**: 14 sample BC watersheds
- **Total Coverage**: 10,012 watersheds

### Data Enhancement Opportunities

1. **Expand Canadian Coverage**
   - Download full BC Freshwater Atlas (19,469 watersheds)
   - Add Alberta, Yukon portions of Cascadia
   - Integrate additional provincial datasets

2. **Enhance US Coverage**
   - Add Alaska Southeast watersheds
   - Expand California coverage
   - Include enhanced metadata

3. **Data Quality Improvements**
   - Add elevation data
   - Include stream network information
   - Add ecological attributes

### Data Processing Scripts

```bash
# Download additional Canadian data
python scripts/download_canadian_data.py

# Process and integrate new data
python scripts/integrate_canadian_data.py

# Validate data quality
python scripts/inspect_data.py
```

## 🐛 Bug Reports

### Before Reporting
- Check existing issues for duplicates
- Try to reproduce the bug
- Test with different browsers/environments

### Bug Report Template
```markdown
**Bug Description**
A clear description of what the bug is.

**Steps to Reproduce**
1. Go to '...'
2. Click on '....'
3. Enter address '....'
4. See error

**Expected Behavior**
What you expected to happen.

**Actual Behavior**
What actually happened.

**Environment**
- Browser: [e.g. Chrome 91]
- OS: [e.g. macOS 11.4]
- Python version: [e.g. 3.9.5]

**Additional Context**
Any other context about the problem.
```

## ✨ Feature Requests

### Feature Request Template
```markdown
**Feature Description**
A clear description of the feature you'd like to see.

**Use Case**
Describe the problem this feature would solve.

**Proposed Solution**
Your ideas for how this could be implemented.

**Alternatives Considered**
Other approaches you've considered.

**Additional Context**
Any other context about the feature request.
```

## 📊 Performance Considerations

### Optimization Guidelines

- **Spatial Queries**: Use R-tree indexing for fast point-in-polygon
- **Memory Usage**: Optimize dataset loading and caching
- **API Calls**: Implement efficient geocoding service fallbacks
- **Frontend**: Minimize JavaScript bundle size, optimize images

### Performance Testing

```bash
# Test query performance
python -c "
import time
from watershed_lookup import CascadiaWatershedLookup
lookup = CascadiaWatershedLookup('data/cascadia_watersheds.gpkg')

start = time.time()
result = lookup.find_watershed_by_point(47.6062, -122.3321)
end = time.time()
print(f'Query time: {(end - start) * 1000:.2f}ms')
"
```

## 🚢 Deployment Contributions

### Docker Improvements
- Optimize container size
- Improve build performance
- Enhance security

### Cloud Platform Support
- Add deployment guides for new platforms
- Improve environment variable handling
- Add monitoring and logging enhancements

## 🔐 Security

### Security Guidelines
- Never commit API keys or credentials
- Validate all user inputs
- Use HTTPS in production
- Follow secure coding practices

### Reporting Security Issues
Please report security vulnerabilities privately to the maintainers rather than creating public issues.

## 📚 Documentation Contributions

### Areas for Improvement
- API documentation and examples
- Deployment guides for different platforms
- User guides and tutorials
- Code architecture documentation

### Documentation Standards
- Use clear, concise language
- Include practical examples
- Keep documentation up-to-date with code changes
- Test all code examples

## 🌍 Community Guidelines

### Code of Conduct
- Be respectful and inclusive
- Help others learn and grow
- Focus on constructive feedback
- Celebrate diverse perspectives

### Communication
- Use clear, professional language
- Be patient with newcomers
- Share knowledge generously
- Ask questions when unclear

## 🏷️ Version Control

### Commit Message Format
```
type(scope): brief description

Longer description if needed

- List specific changes
- Reference issues: #123
```

### Examples
```bash
git commit -m "feat(geocoding): add Google Places autocomplete integration"
git commit -m "fix(api): handle undefined properties in watershed results"
git commit -m "docs(readme): update installation instructions"
```

### Branch Naming
- `feature/description` - New features
- `fix/description` - Bug fixes
- `docs/description` - Documentation updates
- `refactor/description` - Code refactoring

## 🎯 Current Priorities

### High Priority
1. **Full Canadian Dataset Integration** - Expand beyond sample data
2. **Interactive Map Visualization** - Add Leaflet.js integration
3. **API Rate Limiting** - Implement production-ready rate limiting
4. **Mobile App** - Progressive Web App development

### Medium Priority
1. **Batch Processing** - CSV upload for multiple addresses
2. **Enhanced Testing** - Comprehensive test suite
3. **Performance Optimization** - Database migration to PostGIS
4. **Advanced Analytics** - Watershed health metrics

### Help Wanted
- Geographic Information Systems (GIS) expertise
- Frontend/UI design improvements
- Canadian data source expertise
- Cloud deployment and DevOps
- Mobile app development

## 📞 Getting Help

- **GitHub Issues**: For bugs and feature requests
- **GitHub Discussions**: For questions and general discussion
- **Documentation**: Check README.md and docs/ directory
- **Code Examples**: See test files and scripts/ directory

## 🙏 Recognition

Contributors will be recognized in:
- README.md acknowledgments
- Release notes
- Project documentation

Thank you for helping make watershed identification accessible across the Cascadia bioregion! 🌲

---

**Questions?** Feel free to open an issue or start a discussion. We're here to help!