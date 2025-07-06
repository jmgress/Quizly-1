# GitHub Actions CI/CD Setup

This document explains how to set up and use GitHub Actions for the Quizly project.

## 🚀 Workflows Overview

### 1. CI Workflow (`.github/workflows/ci.yml`)
**Triggers:** Push and Pull Request to `main` and `develop` branches
**Purpose:** Run tests, linting, and code quality checks

**Jobs:**
- **Test Job:**
  - Sets up Python 3.9 and Node.js 18
  - Installs backend and frontend dependencies
  - Creates test database and environment
  - Runs all backend tests
  - Runs frontend tests
  - Executes the full test suite

- **Lint Job:**
  - Runs Python linting (flake8, black, isort)
  - Runs frontend linting

### 2. Full Test Suite (`.github/workflows/test.yml`)
**Triggers:** Push and Pull Request to `main` and `develop` branches
**Purpose:** Comprehensive testing across multiple environments

**Jobs:**
- **Backend Tests:** Tests across Python 3.9, 3.10, 3.11
- **Frontend Tests:** Tests across Node.js 18.x, 20.x
- **Integration Tests:** Full test suite execution
- **Security Scan:** Vulnerability scanning with Trivy
- **Docker Build:** Container build and testing

### 3. Deploy Workflow (`.github/workflows/deploy.yml`)
**Triggers:** Push to `main` branch or manual dispatch
**Purpose:** Deploy to production and create releases

**Jobs:**
- **Deploy:** Build, test, and deploy to production
- **Create Release:** Automatic release creation with test results

## 📋 Setup Instructions

### 1. Repository Settings
1. Go to your GitHub repository
2. Navigate to **Settings** → **Actions** → **General**
3. Ensure **Actions permissions** are enabled
4. Set **Workflow permissions** to **Read and write permissions**

### 2. Environment Variables (Optional)
If you need to add secrets or environment variables:
1. Go to **Settings** → **Secrets and variables** → **Actions**
2. Add repository secrets:
   - `OPENAI_API_KEY` (if using OpenAI)
   - `CODECOV_TOKEN` (if using Codecov)
   - Deployment secrets (if deploying)

### 3. Branch Protection Rules
1. Go to **Settings** → **Branches**
2. Add branch protection rules for `main`:
   - ✅ Require status checks to pass before merging
   - ✅ Require branches to be up to date before merging
   - ✅ Status checks: `test`, `lint`

## 🔧 Local Development

### Running the CI Tests Locally
```bash
# Install development dependencies
cd backend
pip install -r requirements-dev.txt

# Run the test suite
cd ..
./run_tests.sh

# Run individual components
cd backend
python test_backend.py
python test_logging_config.py
python test_ai_integration_simple.py

cd ../frontend
npm test -- --watchAll=false
```

### Code Quality Checks
```bash
# Python linting
cd backend
flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
black --check .
isort --check-only .

# Frontend linting
cd frontend
npm run lint
```

## 📊 Test Coverage

The CI pipeline generates test coverage reports for both backend and frontend:
- Backend: pytest-cov generates coverage reports
- Frontend: Jest generates coverage reports
- Reports are uploaded to Codecov (if configured)

## 🐛 Troubleshooting

### Common Issues

1. **Tests failing in CI but passing locally:**
   - Check environment variables
   - Verify database initialization
   - Check file permissions

2. **Node.js version conflicts:**
   - Ensure `.nvmrc` file specifies correct Node version
   - Update workflow to use correct Node version

3. **Python dependency conflicts:**
   - Pin dependency versions in requirements.txt
   - Use virtual environments locally

4. **Frontend build failures:**
   - Check for missing environment variables
   - Verify build scripts in package.json

### Debug CI Issues
```bash
# Test the exact CI environment locally using Docker
docker run --rm -it -v $(pwd):/app -w /app python:3.9 bash
# Then run the CI commands manually
```

## 🎯 Best Practices

1. **Keep workflows fast:**
   - Use caching for dependencies
   - Run tests in parallel where possible
   - Skip unnecessary steps

2. **Fail fast:**
   - Run quick tests first
   - Use matrix builds for broader coverage

3. **Security:**
   - Use official actions from trusted sources
   - Keep actions updated to latest versions
   - Scan for vulnerabilities

4. **Documentation:**
   - Add status badges to README
   - Document any manual steps
   - Keep workflow files well-commented

## 📈 Status Badges

Add these to your README.md:

```markdown
[![CI](https://github.com/yourusername/quizly/actions/workflows/ci.yml/badge.svg)](https://github.com/yourusername/quizly/actions/workflows/ci.yml)
[![Test Suite](https://github.com/yourusername/quizly/actions/workflows/test.yml/badge.svg)](https://github.com/yourusername/quizly/actions/workflows/test.yml)
[![Deploy](https://github.com/yourusername/quizly/actions/workflows/deploy.yml/badge.svg)](https://github.com/yourusername/quizly/actions/workflows/deploy.yml)
```

## 🚀 Next Steps

1. Push your code to GitHub to trigger the first CI run
2. Review the action results and fix any issues
3. Set up branch protection rules
4. Configure deployment targets
5. Add status badges to your README
6. Set up notifications for failed builds

Your CI/CD pipeline is now ready! 🎉
