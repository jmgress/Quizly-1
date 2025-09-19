> **This document was generated using the instructions in `.github/prompts/architecture-blueprint-generator.prompt.md`.**

*Generated: September 16, 2025*

---

## 1. Architecture Detection and Analysis

**Technology Stacks Detected:**
- **Backend:** Python (FastAPI), SQLite, modular LLM provider system
- **Frontend:** React (JavaScript), REST API integration
- **Testing:** Pytest, Jest, Playwright (Python/JS)
- **Security:** GitLeaks, custom rules

**Architectural Patterns:**
- **Backend:** Layered/Modular Monolith with plugin-based LLM providers
- **Frontend:** Component-based (React), modular UI
- **Cross-cutting:** Configurable logging, security scanning, CI/CD

---

## 2. Architectural Overview

Quizly employs a modular, layered architecture:
- **Backend** separates API, config, logging, LLM providers, and database access.
- **Frontend** is organized by React components, with clear separation of concerns.
- **LLM Providers** are pluggable, supporting extensibility.
- **Logging/Security** are cross-cutting, integrated via config and scripts.

**Guiding Principles:**
- Separation of concerns
- Extensibility (LLM providers, logging)
- Testability (in-memory DB, mocks)
- Security by design

---

## 3. Architecture Visualization

**Component Relationships and Data Flow:**
- **Frontend (React)** ⟷ **Backend (FastAPI)** ⟷ **Database (SQLite)**
- **Backend** ↔ **LLM Providers** (Ollama, OpenAI, etc.)
- **Logging** and **Security** span all layers

**Component Interactions:**
- Frontend calls REST API endpoints
- Backend routes requests to quiz logic, LLM providers, or config/logging modules
- LLM providers are dynamically selected and invoked

**Data Flow:**
- User → Frontend → Backend API → DB/LLM → Response → Frontend

---

## 4. Core Architectural Components

### Backend
- **Purpose and Responsibility:**
  - API Layer: FastAPI endpoints for quiz, admin, logging, LLM config
  - Config Manager: Centralized config, exposed via API
  - LLM Providers: Pluggable, each in its own module
  - Logging: Configurable, path traversal protection
  - Database: SQLite, in-memory for tests
- **Internal Structure:**
  - Modular Python packages, base classes for providers
  - Pydantic models for validation
- **Interaction Patterns:**
  - Dependency injection for LLM providers
  - API exposes/consumes JSON
- **Evolution Patterns:**
  - Add new providers in `backend/llm_providers/`, update config
  - Configurable logging and provider selection

### Frontend
- **Purpose and Responsibility:**
  - React Components: Quiz, Admin, LLMSettings, LoggingSettings, etc.
  - State Management: Component state, props, context
  - API Integration: Fetches data from backend
- **Internal Structure:**
  - Organized by feature/component
- **Interaction Patterns:**
  - Fetch/axios for API calls
- **Evolution Patterns:**
  - Add new components in `frontend/src/components/`

---

## 5. Architectural Layers and Dependencies

- **Backend Layers:**
  - API (FastAPI)
  - Business Logic (Quiz, LLM, Config)
  - Data Access (SQLite)
  - Providers (LLM)
- **Frontend Layers:**
  - UI Components
  - State/Logic
  - API Integration

**Dependency Rules:**
- API depends on business logic, not vice versa
- LLM providers are injected/configured, not hardcoded
- Logging is decoupled via config

---

## 6. Data Architecture

- **Domain Model:** Quiz, Question, User (implied)
- **Entity Relationships:** Quiz ↔ Questions
- **Data Access:** Direct SQLite queries, repository pattern for extensibility
- **Validation:** Input validation at API and UI layers
- **Caching:** Not explicitly implemented

---

## 7. Cross-Cutting Concerns Implementation

- **Authentication & Authorization:**
  - Admin endpoints, permission checks (extendable)
- **Error Handling & Resilience:**
  - Exception handlers in FastAPI, error boundaries in React
- **Logging & Monitoring:**
  - Centralized logging config, logs stored in `logs/`
- **Validation:**
  - Pydantic models (backend), form validation (frontend)
- **Configuration Management:**
  - Centralized in `config_manager.py`, environment-specific via config files

---

## 8. Service Communication Patterns

- **Frontend ↔ Backend:** REST (JSON)
- **Backend ↔ LLM Providers:** Python interfaces, dynamic selection
- **API Versioning:** Not explicit, but endpoints are modular

---

## 9. Technology-Specific Architectural Patterns

### Python (Backend)
- Module organization approach, dependency injection for providers
- OOP for providers, functional for config/logging
- Asynchronous FastAPI endpoints

### React (Frontend)
- Component composition and reuse
- State via hooks/context
- Data fetching via fetch/axios
- Routing via React Router (if present)

---

## 10. Implementation Patterns

- **Interface Design Patterns:** Abstract base for LLM providers
- **Service Implementation Patterns:** Provider selection via config, dependency injection
- **Repository Implementation Patterns:** For DB access (extensible)
- **Controller/API Implementation Patterns:** FastAPI route handlers, Pydantic validation
- **Domain Model Implementation:** Python classes, Pydantic models

---

## 11. Testing Architecture

- **Testing Strategies:**
  - Backend: Pytest, in-memory DB, fixtures, mocks
  - Frontend: Jest, React Testing Library, Playwright
- **Test Boundary Patterns:** Arrange-Act-Assert, isolated tests, shared helpers
- **Test Data Strategies:** Fixtures, mock data
- **Tools/Frameworks:** Pytest, Jest, Playwright

---

## 12. Deployment Architecture

- **Deployment Topology:**
  - Startup: `./start.sh` launches backend and frontend
  - Testing: `./run_tests.sh` runs all tests and security scans
  - Config: Environment-specific via config files
  - Logs: Centralized in `logs/`
  - CI/CD: Integrated via scripts and GitHub Actions

---

## 13. Extension and Evolution Patterns

- **Feature Addition Patterns:**
  - Add new LLM provider in `backend/llm_providers/`, update config
  - Add new React component in `frontend/src/components/`
- **Modification Patterns:**
  - Update config via API/UI, maintain backward compatibility
- **Integration Patterns:**
  - Add new external service via provider interface

---

## 14. Architectural Pattern Examples

**Layer Separation Example (Backend):**
```python
# backend/llm_providers/base.py
class LLMProviderBase:
    def generate_question(self, prompt: str) -> str:
        raise NotImplementedError()
```

**Component Communication Example (Frontend):**
```js
// frontend/src/components/Quiz.js
fetch('/api/quiz')
  .then(res => res.json())
  .then(data => setQuestions(data.questions));
```

**Extension Point Example:**
```python
# backend/llm_providers/ollama_provider.py
from .base import LLMProviderBase
class OllamaProvider(LLMProviderBase):
    ...
```

---

## 15. Architectural Decision Records

- **Architectural Style Decisions:** Layered modular monolith for backend, React component model for frontend
- **Technology Selection Decisions:** FastAPI for async Python API, React for modern UI, SQLite for simplicity
- **Extensibility:** Pluggable LLM providers, config-driven logging
- **Security:** Integrated GitLeaks, path traversal protection

---

## 16. Architecture Governance

- **Consistency:** Enforced via config, modular structure, and test coverage
- **Automated Checks:** Security scans, CI/CD, test scripts
- **Review:** Code review guidelines, documentation in `docs/`

---

## 17. Blueprint for New Development

- **Development Workflow:**
  - Backend: Add API in FastAPI, business logic in module, update config/tests
  - Frontend: Add component, connect to API, add tests
- **Implementation Templates:**
  - Base class for providers, React component template
- **Common Pitfalls:**
  - Avoid tight coupling, circular dependencies, config hardcoding
  - Ensure test isolation, security compliance

---

*This blueprint was generated on September 16, 2025. Update as architecture evolves.*
## 1. Architecture Detection and Analysis

**Technology Stacks Detected:**
- **Backend:** Python (FastAPI), SQLite, modular LLM provider system
- **Frontend:** React (JavaScript), REST API integration
- **Testing:** Pytest, Jest, Playwright (Python/JS)
- **Security:** GitLeaks, custom rules

**Architectural Patterns:**
- **Backend:** Layered/Modular Monolith with plugin-based LLM providers
- **Frontend:** Component-based (React), modular UI
- **Cross-cutting:** Configurable logging, security scanning, CI/CD

---

## 2. Architectural Overview

Quizly employs a modular, layered architecture:
- **Backend** separates API, config, logging, LLM providers, and database access.
- **Frontend** is organized by React components, with clear separation of concerns.
- **LLM Providers** are pluggable, supporting extensibility.
- **Logging/Security** are cross-cutting, integrated via config and scripts.

**Guiding Principles:**
- Separation of concerns
- Extensibility (LLM providers, logging)
- Testability (in-memory DB, mocks)
- Security by design

---

## 3. Architecture Visualization

**High-Level Overview:**
- **Frontend (React)** ⟷ **Backend (FastAPI)** ⟷ **Database (SQLite)**
- **Backend** ↔ **LLM Providers** (Ollama, OpenAI, etc.)
- **Logging** and **Security** span all layers

**Component Interactions:**
- Frontend calls REST API endpoints
- Backend routes requests to quiz logic, LLM providers, or config/logging modules
- LLM providers are dynamically selected and invoked

**Data Flow:**
- User → Frontend → Backend API → DB/LLM → Response → Frontend

---

## 4. Core Architectural Components

### Backend
- **API Layer:** FastAPI endpoints for quiz, admin, logging, LLM config
- **Config Manager:** Centralized config, exposed via API
- **LLM Providers:** Pluggable, each in its own module
- **Logging:** Configurable, path traversal protection
- **Database:** SQLite, in-memory for tests

### Frontend
- **React Components:** Quiz, Admin, LLMSettings, LoggingSettings, etc.
- **State Management:** Component state, props, context
- **API Integration:** Fetches data from backend

---

## 5. Architectural Layers and Dependencies

- **Backend Layers:**
  - API (FastAPI)
  - Business Logic (Quiz, LLM, Config)
  - Data Access (SQLite)
  - Providers (LLM)
- **Frontend Layers:**
  - UI Components
  - State/Logic
  - API Integration

**Dependency Rules:**
- API depends on business logic, not vice versa
- LLM providers are injected/configured, not hardcoded
- Logging is decoupled via config

---

## 6. Data Architecture

- **Domain Model:** Quiz, Question, User (implied)
- **Entity Relationships:** Quiz ↔ Questions
- **Data Access:** Direct SQLite queries, repository pattern for extensibility
- **Validation:** Input validation at API and UI layers
- **Caching:** Not explicitly implemented

---

## 7. Cross-Cutting Concerns Implementation

- **Authentication & Authorization:**
  - Admin endpoints, permission checks (extendable)
- **Error Handling & Resilience:**
  - Exception handlers in FastAPI, error boundaries in React
- **Logging & Monitoring:**
  - Centralized logging config, logs stored in `logs/`
- **Validation:**
  - Pydantic models (backend), form validation (frontend)
- **Configuration Management:**
  - Centralized in `config_manager.py`, environment-specific via config files

---

## 8. Service Communication Patterns

- **Frontend ↔ Backend:** REST (JSON)
- **Backend ↔ LLM Providers:** Python interfaces, dynamic selection
- **API Versioning:** Not explicit, but endpoints are modular

---

## 9. Technology-Specific Architectural Patterns

### Python (Backend)
- Modular organization, dependency injection for providers
- OOP for providers, functional for config/logging
- Asynchronous FastAPI endpoints

### React (Frontend)
- Component composition, state via hooks/context
- Data fetching via fetch/axios
- Routing via React Router (if present)

---

## 10. Implementation Patterns

- **Interface Design:** Abstract base for LLM providers
- **Service Implementation:** Provider selection via config, dependency injection
- **Repository Pattern:** For DB access (extensible)
- **Controller/API:** FastAPI route handlers, Pydantic validation
- **Domain Model:** Python classes, Pydantic models

---

## 11. Testing Architecture

- **Backend:** Pytest, in-memory DB, fixtures, mocks
- **Frontend:** Jest, React Testing Library, Playwright
- **Test Structure:** Arrange-Act-Assert, isolated tests, shared helpers

---

## 12. Deployment Architecture

- **Startup:** `./start.sh` launches backend and frontend
- **Testing:** `./run_tests.sh` runs all tests and security scans
- **Config:** Environment-specific via config files
- **Logs:** Centralized in `logs/`
- **CI/CD:** Integrated via scripts and GitHub Actions

---

## 13. Extension and Evolution Patterns

- **Feature Addition:**
  - Add new LLM provider in `backend/llm_providers/`, update config
  - Add new React component in `frontend/src/components/`
- **Modification:**
  - Update config via API/UI, maintain backward compatibility
- **Integration:**
  - Add new external service via provider interface

---

## 14. Architectural Pattern Examples

**Layer Separation Example (Backend):**
```python
# backend/llm_providers/base.py
class LLMProviderBase:
    def generate_question(self, prompt: str) -> str:
        raise NotImplementedError()
```

**Component Communication Example (Frontend):**
```js
// frontend/src/components/Quiz.js
fetch('/api/quiz')
  .then(res => res.json())
  .then(data => setQuestions(data.questions));
```

**Extension Point Example:**
```python
# backend/llm_providers/ollama_provider.py
from .base import LLMProviderBase
class OllamaProvider(LLMProviderBase):
    ...
```

---

## 15. Architectural Decision Records

- **Pattern Choice:** Layered modular monolith for backend, React component model for frontend
- **Technology:** FastAPI for async Python API, React for modern UI, SQLite for simplicity
- **Extensibility:** Pluggable LLM providers, config-driven logging
- **Security:** Integrated GitLeaks, path traversal protection

---

## 16. Architecture Governance

- **Consistency:** Enforced via config, modular structure, and test coverage
- **Automated Checks:** Security scans, CI/CD, test scripts
- **Review:** Code review guidelines, documentation in `docs/`

---

## 17. Blueprint for New Development

- **Workflow:**
  - Backend: Add API in FastAPI, business logic in module, update config/tests
  - Frontend: Add component, connect to API, add tests
- **Templates:**
  - Base class for providers, React component template
- **Pitfalls:**
  - Avoid tight coupling, circular dependencies, config hardcoding
  - Ensure test isolation, security compliance

---

*This blueprint was generated on September 16, 2025. Update as architecture evolves.*
