# Contributing to CodeReview AI

Thank you for your interest in contributing to CodeReview AI! We welcome contributions from the community.

## 🤝 How to Contribute

### Reporting Bugs

1. Check if the bug has already been reported in [Issues](https://github.com/yourusername/code-review-ai/issues)
2. If not, create a new issue with:
   - Clear title and description
   - Steps to reproduce
   - Expected vs actual behavior
   - System information (OS, Python version, etc.)
   - Screenshots if applicable

### Suggesting Features

1. Open an issue with the `enhancement` label
2. Describe the feature and its use case
3. Explain how it would benefit users
4. Be open to discussion and feedback

### Pull Requests

1. **Fork the repository**
   ```bash
   git clone https://github.com/yourusername/code-review-ai.git
   cd code-review-ai
   ```

2. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Set up development environment**
   ```bash
   make setup-dev
   ```

4. **Make your changes**
   - Write clean, readable code
   - Follow existing code style
   - Add tests for new features
   - Update documentation

5. **Run tests and linting**
   ```bash
   make test
   make lint
   make format
   ```

6. **Commit your changes**
   ```bash
   git add .
   git commit -m "feat: add amazing feature"
   ```

7. **Push to your fork**
   ```bash
   git push origin feature/your-feature-name
   ```

8. **Open a Pull Request**
   - Provide clear description of changes
   - Link related issues
   - Ensure CI passes

## 📝 Code Style

- **Python**: Follow PEP 8, use Black formatter
- **TypeScript**: Follow ESLint rules
- **Commits**: Use [Conventional Commits](https://www.conventionalcommits.org/)
  - `feat:` - New features
  - `fix:` - Bug fixes
  - `docs:` - Documentation changes
  - `refactor:` - Code refactoring
  - `test:` - Adding tests
  - `chore:` - Maintenance tasks

## 🧪 Testing

- Write unit tests for new features
- Ensure all tests pass before submitting PR
- Aim for >80% code coverage

## 🏗️ Project Structure

```
code-review-ai/
├── services/          # Microservices
├── shared/           # Shared modules
├── infrastructure/   # Docker, K8s configs
├── tests/           # Tests
└── docs/            # Documentation
```

## 📚 Documentation

- Update README.md for user-facing changes
- Add docstrings to functions and classes
- Update API documentation if needed

## ⚖️ Code of Conduct

- Be respectful and inclusive
- Welcome newcomers
- Focus on constructive feedback
- Follow the [Contributor Covenant](https://www.contributor-covenant.org/)

## 🎉 Recognition

Contributors will be recognized in:
- README.md contributors section
- Release notes
- GitHub contributors page

## 💬 Questions?

- Open a [Discussion](https://github.com/yourusername/code-review-ai/discussions)
- Join our community chat
- Email: support@codereview-ai.dev

Thank you for contributing! 🚀
