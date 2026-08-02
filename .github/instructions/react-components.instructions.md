---
applyTo: 'frontend/src/components/**'
description: 'Coding rules for Quizly React components.'
---

# React Component Conventions

When writing or editing React components:

- Use **functional components with hooks** (`useState`, `useEffect`). No class components.
- Destructure props in the function signature.
- The component name must match its filename.
- Use `axios` for API calls, reading the base URL from `process.env.REACT_APP_API_BASE_URL` with a `http://localhost:8000` fallback.
- Always handle **loading** and **error** states explicitly in the UI.
- Add **accessibility attributes** (`aria-label`, appropriate roles) to interactive elements.
- Keep side effects inside `useEffect` with a correct dependency array.
- Do not hardcode API URLs or secrets in the component.
- Every component should have a matching test under `tests/frontend/unit/components/`.
