## Contributing to Vision Karts

Thank you for your interest in improving Vision Karts. Thoughtful contributions can help make this project the standard reference for computer-vision powered retail checkout.

This document describes how to propose changes, what we expect from contributions, and how to get your work reviewed and merged.

### Ways to Contribute

- **Bug reports**: Help us identify issues in real-world usage.
- **Feature requests**: Suggest improvements for automated checkout, analytics, or deployment.
- **Code contributions**: Implement fixes or new capabilities.
- **Documentation**: Improve examples, guides, and explanations.

### Getting Started

1. **Fork** the repository on GitHub.
2. **Clone** your fork locally:
   ```bash
   git clone https://github.com/<your-username>/Vision-Karts.git
   cd Vision-Karts
   ```
3. **Create a branch** for your work:
   ```bash
   git checkout -b feature/my-improvement
   ```
4. **Set up the environment**:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # or .venv\Scripts\activate on Windows
   pip install -r requirements.txt
   pip install -e ".[dev]"
   ```

### Development Guidelines

- **Style**: Use `black` and `flake8` for formatting and linting where applicable.
- **Typing**: Prefer adding or preserving type hints in new or modified code.
- **Structure**: Keep new functionality consistent with the existing modular layout (`core/`, `analytics/`, `accelerators/`, `utils/`, `data/`).
- **Dependencies**: Avoid adding new dependencies unless necessary; if you must, explain why in the pull request.

### Testing

Before opening a pull request:

1. Run the test suite (if present):
   ```bash
   pytest
   ```
2. Run basic sanity checks for key flows where possible, such as:
   - Product detection on a sample image
   - Billing using `src/prices.csv`
   - Any new functionality you introduce

Please describe how you tested your changes in the pull request description.

### Commit and Branching Practices

- Use clear, concise commit messages that explain the "why" as well as the "what".
- Group related changes into a single pull request instead of many small, tightly coupled ones.
- Keep branches focused: one feature or fix per branch where possible.

### Opening a Pull Request

When you are ready:

1. Push your branch to your fork:
   ```bash
   git push origin feature/my-improvement
   ```
2. Open a pull request against the main repository’s default branch.
3. In the pull request description, include:
   - **Motivation / background**
   - **What changed**
   - **How it was tested**
   - **Any follow-up work** that might be needed

### Code Review Expectations

- Be open to feedback and ready to iterate on your changes.
- Review comments are meant to improve code quality and maintainability.
- Small, focused pull requests are easier and faster to review.

### Community Standards

By participating in this project, you agree to follow the guidelines in `CODE_OF_CONDUCT.md`.

We’re excited to see what you build with Vision Karts and appreciate your help in making it better.

