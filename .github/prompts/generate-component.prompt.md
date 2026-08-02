---
mode: agent
description: 'Generate a React component plus a co-located Jest test following Quizly conventions.'
---

# Generate React Component

Create a new React component named **${input:COMPONENT_NAME:e.g. QuizTimer}** for the Quizly frontend.

## Component Requirements
Follow the conventions in `frontend/src/components/` (see `Quiz.js`):

- **Functional component** using hooks (`useState`, `useEffect`) — no class components.
- Destructure props in the function signature.
- Use `axios` for any API calls, with `API_BASE_URL` from `process.env.REACT_APP_API_BASE_URL` (fallback `http://localhost:8000`).
- Handle loading and error states explicitly.
- Add accessibility attributes (`aria-label`, roles) to interactive elements.
- The component name must match the filename.
- Place the file at `frontend/src/components/${input:COMPONENT_NAME}.js`.

## Test Requirements
Also create a co-located test at `tests/frontend/unit/components/${input:COMPONENT_NAME}.test.js`:

- Use Jest + React Testing Library.
- Mock `axios` and any child dependencies.
- Cover: initial render, loading state, successful data render, and error state.
- Use role/label-based queries (`getByRole`, `getByLabelText`) over test IDs.
