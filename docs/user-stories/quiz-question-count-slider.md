# User Story: Select Number of Quiz Questions via Slider

## Story

**As a** quiz taker,
**I want** to use a slider to select how many questions are asked in my quiz,
**so that** I can tailor the quiz length to the time I have available and my desired difficulty/effort.

## Background / Context

Today, the number of questions per quiz is hard-coded in the frontend:

- Curated (database) quizzes request `limit=10` — see [frontend/src/components/Quiz.js](frontend/src/components/Quiz.js#L36)
- AI-generated quizzes request `limit=5` — see [frontend/src/components/Quiz.js](frontend/src/components/Quiz.js#L30)

The backend already supports a configurable `limit` query parameter on both endpoints:

- `GET /api/questions?category=...&limit=...` — see [backend/main.py](backend/main.py#L176)
- `GET /api/questions/ai?subject=...&limit=...` — see [backend/main.py](backend/main.py#L403)

A `DEFAULT_QUESTION_LIMIT` env variable also exists (see [README.md](README.md#L303)).

The user has no UI control to choose the number of questions. This story adds a slider on the
[SubjectSelection](frontend/src/components/SubjectSelection.js) screen.

## Acceptance Criteria

1. **Slider control on the subject selection screen**
   - A range slider labeled "Number of Questions" is visible on the subject selection card.
   - Range: minimum **1**, maximum **20**, step **1**.
   - Default value comes from `REACT_APP_DEFAULT_QUESTION_LIMIT` (or backend `DEFAULT_QUESTION_LIMIT`); falls back to **10** for curated and **5** for AI if not set.
   - Current selected value is displayed next to the slider and updates live as the user drags.

2. **Slider value drives quiz length**
   - The chosen value is passed via the `config` object from `SubjectSelection` to `Quiz`.
   - `Quiz.js` uses the value as the `limit` query parameter for both `/api/questions` and `/api/questions/ai`.
   - The resulting quiz contains exactly that many questions (or fewer if the database/LLM returns fewer; in that case display an informational message).

3. **Accessibility**
   - The slider has an associated `<label htmlFor>` and `aria-valuemin`, `aria-valuemax`, `aria-valuenow` attributes.
   - Keyboard users can adjust the value with arrow keys.
   - The numeric value is announced to screen readers when it changes.

4. **Validation & safety**
   - Frontend clamps the value to the [1, 20] range before sending.
   - Backend continues to validate `limit` server-side (reject non-positive or excessively large values) — confirm/extend existing validation in [backend/main.py](backend/main.py#L176).

5. **Persistence (nice-to-have)**
   - The last chosen slider value is remembered for the session via `localStorage` so returning users don't have to reset it.

6. **Tests**
   - **Frontend unit tests** ([frontend Jest + RTL](docs/TESTING_GUIDE.md)):
     - Slider renders with default value.
     - Changing the slider updates the displayed number.
     - `onSelectionComplete` is called with the chosen `limit` in the config payload.
   - **Backend tests**: confirm `/api/questions` and `/api/questions/ai` honor a custom `limit` (extend [tests/backend/integration/test_api_endpoints.py](tests/backend/integration/test_api_endpoints.py)).
   - **E2E test** ([tests/e2e/quiz_flow.test.js](tests/e2e/quiz_flow.test.js)): user moves slider to 3, starts quiz, sees exactly 3 questions.

7. **Documentation**
   - Update [README.md](README.md) usage section to mention the new slider.
   - Update API docs / [docs/TESTING_GUIDE.md](docs/TESTING_GUIDE.md) if test commands change.

## Out of Scope

- Changing per-question time limits.
- Difficulty selection.
- Server-side persistence of user preferences (no auth system today).

## Implementation Notes

Suggested config shape passed to `Quiz`:

```js
{
   category: selectedTopic,
   source: questionSource,   // 'database' | 'ai'
   limit: questionCount,     // integer 1..20
}
```

In [Quiz.js](frontend/src/components/Quiz.js#L30):

```js
const limit = config.limit ?? (config.source === 'ai' ? 5 : 10);
url = config.source === 'ai'
   ? `${API_BASE_URL}/api/questions/ai?subject=${encodeURIComponent(category)}&limit=${limit}`
   : `${API_BASE_URL}/api/questions?category=${encodeURIComponent(category)}&limit=${limit}`;
```

## Definition of Done

- [ ] Slider implemented in `SubjectSelection.js` with label and live value display.
- [ ] `Quiz.js` consumes `config.limit` for both question sources.
- [ ] Frontend, backend, and e2e tests added and passing (`./run_tests.sh`).
- [ ] Accessibility checks pass (keyboard + ARIA attributes).
- [ ] README and relevant docs updated.
- [ ] No regressions in existing quiz flow.
