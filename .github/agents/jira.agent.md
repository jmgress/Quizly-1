---
description: 'Jira Chat Mode Configuration for Quizly'
tools: ['toolSetName', 'createJiraIssue', 'fetch', 'addCommentToJiraIssue', 'atlassianUserInfo', 'editJiraIssue', 'getJiraIssueRemoteIssueLinks', 'getJiraProjectIssueTypesMetadata', 'getTransitionsForJiraIssue', 'getVisibleJiraProjects', 'lookupJiraAccountId', 'searchJiraIssuesUsingJql', 'transitionJiraIssue']
---
## Purpose
This chat mode configuration enables verbose Jira integration for the Quizly knowledge testing application, providing detailed logging, issue tracking, and project management capabilities.

## Chat Mode Instructions

### Project Context
- **Project**: Quizly - Full-stack knowledge testing app
- **Stack**: FastAPI backend (Python, SQLite) + React frontend
- **Architecture**: Modular LLM providers, comprehensive logging, CI/CD workflows
- **Repository**: /Users/james.m.gress/Reops/Quizly-1

### Jira Integration Guidelines

#### Issue Creation & Management
- When creating Jira issues, include detailed context about:
  - Component affected (frontend/, backend/, tests/, docs/)
  - Environment (development, staging, production)
  - Related workflows (./start.sh, ./run_tests.sh, CI/CD pipelines)
  - Log file locations (logs/ directory)

#### Verbose Logging for Jira
- Enable detailed logging for all Jira-related activities
- Log format should include:
  - Timestamp
  - Component/module
  - Issue type (Bug, Feature, Task, Story)
  - Priority level
  - Affected files/directories
  - Test coverage impact

#### Issue Templates

**Bug Report Template:**
```
Title: [Component] Brief description
Type: Bug
Priority: [High/Medium/Low]
Components: [frontend/backend/tests/docs]
Environment: [dev/staging/prod]
Steps to Reproduce:
1. 
2. 
3. 
Expected Result:
Actual Result:
Logs: [Reference to logs/ directory files]
Test Files: [Related test files in tests/]
```

**Feature Request Template:**
```
Title: [Component] Feature description
Type: Story/Epic
Priority: [High/Medium/Low]
Components: [frontend/backend/llm_providers/tests]
User Story: As a [user], I want [goal] so that [benefit]
Acceptance Criteria:
- [ ] 
- [ ] 
- [ ] 
Technical Notes:
- Architecture impact: [backend/llm_providers/, frontend/, etc.]
- Test requirements: [backend tests, frontend tests, e2e tests]
- Security considerations: [GitLeaks scan, dependency vulnerabilities]
```

#### Workflow Integration
- Link Jira issues to:
  - GitHub commits and PRs
  - Test execution results (pytest, Jest)
  - Security scan reports (GitLeaks)
  - Deployment status
  - Log analysis from logs/ directory

#### Verbose Output Configuration
- Include full stack traces for backend issues
- Capture React component tree for frontend issues
- Log LLM provider responses for AI-related features
- Include database query logs for SQLite operations
- Capture full test output for failing tests

#### Project-Specific Jira Fields
- **Component**: frontend, backend, llm_providers, tests, docs, ci_cd
- **Environment**: development, testing, staging, production
- **Test Type**: unit, integration, e2e, security
- **Log Level**: debug, info, warning, error, critical
- **Provider**: ollama, openai, custom_llm

### Commands for Jira Integration

#### Issue Creation
```bash
# Create issue with verbose logging
jira create --project QUIZLY --type Bug --component backend --priority High --verbose

# Link to specific commit
jira create --project QUIZLY --type Feature --component frontend --link-commit $(git rev-parse HEAD)
```

#### Status Updates
```bash
# Update with test results
jira update QUIZLY-123 --status "In Progress" --comment "Tests passing: $(pytest --tb=short)" --verbose

# Update with deployment status
jira update QUIZLY-123 --status "Done" --comment "Deployed to staging, logs available in logs/"
```

### Security & Compliance
- Ensure no sensitive data in Jira descriptions
- Follow GitLeaks allowlist patterns
- Include security scan results in relevant issues
- Reference vulnerability reports from dependency scans

### Monitoring & Alerting
- Set up Jira alerts for:
  - Critical bugs in production
  - Security vulnerabilities
  - Test failures in CI/CD
  - Performance degradation
  - LLM provider failures

### Integration with Quizly Workflows
- Link Jira issues to:
  - Backend API endpoints (/api/*)
  - Frontend components (src/components/*)
  - LLM provider implementations (backend/llm_providers/*)
  - Test suites (tests/backend/, tests/frontend/, tests/e2e/)
  - Configuration files (logging_config.json, etc.)

---