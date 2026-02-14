# Contributing to ReSynth

Thank you for your interest in contributing to ReSynth! This document provides guidelines for contributors.

## Getting Started

### Prerequisites

- Python 3.8 or higher
- Git
- Basic knowledge of Python development

### Development Setup

1. **Fork the repository**
   ```bash
   # Fork on GitHub, then clone your fork
   git clone https://github.com/your-username/resynth.git
   cd resynth
   ```

2. **Set up development environment**
   ```bash
   # Install development dependencies
   make dev-install
   
   # Set up pre-commit hooks
   pre-commit install
   ```

3. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

## Development Workflow

### 1. Create a Branch

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/issue-number
```

### 2. Make Changes

- Follow the existing code style
- Add tests for new functionality
- Update documentation as needed
- Ensure all tests pass

### 3. Code Quality

Run the following checks before committing:

```bash
# Format code
make format

# Run linting
make lint

# Run tests
make test
```

### 4. Commit Changes

Use clear, descriptive commit messages:

```
feat: add support for new paper source
fix: resolve chunking issue with large papers
docs: update API documentation
test: add integration tests for retrieval system
```

### 5. Submit Pull Request

- Push your branch to your fork
- Create a pull request with a clear description
- Link any relevant issues
- Wait for code review

## Code Style

### Python Style

We use:
- **Black** for code formatting
- **isort** for import sorting
- **flake8** for linting
- **mypy** for type checking

### Documentation

- Use docstrings for all public functions and classes
- Follow the Google style for docstrings
- Update README.md for user-facing changes
- Add inline comments for complex logic

### Testing

- Write unit tests for new functionality
- Add integration tests for major features
- Maintain test coverage above 80%
- Use descriptive test names

## Project Structure

```
resynth/
├── src/resynth/           # Main package
│   ├── fetchers/          # Paper fetching modules
│   ├── processors/        # Text processing
│   ├── embeddings/        # Vector embeddings
│   ├── retrieval/         # Query processing
│   └── synthesis/         # Answer generation
├── tests/                 # Test suite
├── docs/                  # Documentation
├── examples/              # Usage examples
└── scripts/              # Utility scripts
```

## Adding Features

### New Paper Sources

1. Create a new fetcher in `src/resynth/fetchers/`
2. Inherit from `BaseFetcher`
3. Implement required methods
4. Add tests
5. Update documentation

### New Citation Styles

1. Add formatting methods to `CitationFormatter`
2. Update citation style options
3. Add tests for new style
4. Update documentation

### New Embedding Models

1. Update `EmbeddingManager` to support new model
2. Add configuration options
3. Add tests
4. Update documentation

## Reporting Issues

### Bug Reports

- Use the GitHub issue tracker
- Provide clear reproduction steps
- Include environment details
- Add relevant logs or error messages

### Feature Requests

- Describe the use case
- Explain why it's needed
- Suggest implementation approach
- Consider potential edge cases

## Review Process

### What We Look For

- Code quality and style
- Test coverage
- Documentation
- Performance impact
- Security considerations
- Backward compatibility

### Review Guidelines

- Be constructive and respectful
- Focus on the code, not the person
- Provide specific suggestions
- Ask questions for clarity

## Release Process

### Version Management

- Follow semantic versioning
- Update version in `src/resynth/__init__.py`
- Update `CHANGELOG.md`
- Tag releases on GitHub

### Publishing

1. Update version and changelog
2. Run full test suite
3. Build package
4. Test installation
5. Publish to PyPI

## Community Guidelines

### Code of Conduct

- Be respectful and inclusive
- Welcome newcomers
- Focus on what's best for the community
- Show empathy towards other community members

### Getting Help

- Check documentation first
- Search existing issues
- Ask questions in discussions
- Join community channels

## Recognition

Contributors are recognized in:
- README.md contributors section
- Release notes
- GitHub contributors list

Thank you for contributing to ReSynth! 🚀
