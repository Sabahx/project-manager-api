# Contributing to Project Manager API

Thank you for your interest in contributing! This document provides guidelines and instructions for contributing.

## Development Setup

1. Fork the repository
2. Clone your fork: `git clone https://github.com/YOUR_USERNAME/project_manager.git`
3. Create a virtual environment: `python -m venv venv`
4. Activate it: `venv\Scripts\activate` (Windows) or `source venv/bin/activate` (Linux/Mac)
5. Install dependencies: `pip install -r requirements.txt`
6. Copy `.env.example` to `.env` and configure
7. Run migrations: `python manage.py migrate`
8. Create superuser: `python manage.py createsuperuser`

## Code Style

- Follow PEP 8 guidelines
- Use Black for formatting: `black .`
- Use flake8 for linting: `flake8`
- Write meaningful commit messages

## Testing

- Write tests for new features
- Run tests before committing: `python manage.py test`
- Ensure all tests pass

## Pull Request Process

1. Create a new branch: `git checkout -b feature/your-feature-name`
2. Make your changes
3. Add tests for new functionality
4. Run tests and ensure they pass
5. Commit your changes with clear messages
6. Push to your fork
7. Create a Pull Request with a clear description

## Reporting Bugs

- Use GitHub Issues
- Describe the bug clearly
- Include steps to reproduce
- Mention your environment (OS, Python version, etc.)

## Feature Requests

- Open a GitHub Issue
- Describe the feature and its benefits
- Discuss implementation approach if possible
