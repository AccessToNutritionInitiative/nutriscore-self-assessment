
This document describes how the survey application works and how to maintain it. The whole survey - questions, propositions, scoring rules, and recommendations - is driven by a single source of truth: `survey.json` at the repo root.

Anyone who edits `survey.json` is effectively editing the survey UI, the scoring engine, and the recommendation engine at the same time. There is no other place where questions live.

## How the pieces fit together

- `survey.json` is loaded by `SurveyService`  and validated against the Pydantic models in `src/nutri/domain/survey.py`.
- The API exposes three endpoints (`src/nutri/interface/api/routers/survey.py`):
  - `GET /survey/questions` - returns the list of questions **without** the recommendation text. The UI uses this to render the form.
  - `POST /survey/answers` - receives the user's scored answers, computes per-question recommendations, and (if `keep_data=True`) stores the submission via `SqliteSurveyRepository`.
  - `GET /survey/submissions` - enables admin users to pull submissions from the database.
- The Streamlit UI (`ui/survey.py`) renders the form, computes the score client-side from the proposition definitions, and submits answers back to the API.
- Recommendations are looked up server-side by matching the answer's `score` against the question's `recommandations` block.

## Anatomy of a question

Every entry in `survey.json` is one question with this shape:

```json
{
  "topic": "Management & Products",
  "question": "Do you have a business policy document?",
  "question_id": "1.1.1",
  "info": "",                      // optional - see "Info icon" below
  "dependency": "",                // optional - see "Dependencies" below
  "recommandations": { ... },      // optional - see "Recommendations" below
  "propositions": { ... }          // required - see "Propositions" below
}
```

| Field | Notes |
|---|---|
| `topic` | One of the values in `Topic` (`src/nutri/domain/survey.py`): `Management & Products`, `Marketing`, `Workforce Programs`, `Labeling`, `Engagement`. The UI groups questions into tabs by topic, in first-seen order. |
| `question` | Free text. Rendered as the question label. |
| `question_id` | Stable string id (e.g. `1.4.2`). Used for dependency lookup, score lookup, and persistence. **Must be unique.** |
| `info` | Optional help text. When non-empty, the UI renders a small ⓘ icon next to the question that reveals this string on hover. Use it for definitions, links to references, or anything you'd otherwise be tempted to cram into the question text. |
| `dependency` | If non-empty, the id of a parent question. The question is only shown when the parent has been answered "yes" (or any non-empty selection for `choices`). |
| `recommandations` | Optional. If absent or `null`, no recommendation is returned for this question. |
| `propositions` | Required. Defines what the user can answer and how that answer is scored. |

## Proposition types (how the user answers and scores are computed)

`propositions.type` is a discriminator. There are three types - adding a fourth means adding a new schema in `src/nutri/domain/survey.py` **and** new render/scoring branches in `ui/survey.py`.

### 1. `option` - single choice (radio)

```json
"propositions": {
  "type": "option",
  "propositions": [
    { "proposition": "Yes", "score": 5.0 },
    { "proposition": "No",  "score": 0.0 },
    { "proposition": "Specific market need", "score": 0.0, "text_inputs": true }
  ]
}
```

- Rendered as a radio in the UI; user picks exactly one.
- The `score` of the picked option becomes the answer's score.
- `text_inputs: true` (optional, defaults to `false`) renders an extra free-text box when that option is selected. If the user types something, the answer's `value` is sent as `[selected_option, text_detail]` (a two-element list) instead of the bare option label; if they leave it blank, only the label is sent. Either way, the `score` only depends on the picked option. Use this for "if yes, please specify"-style follow-ups.

### 2. `choices` - multi-select (checkboxes)

```json
"propositions": {
  "type": "choices",
  "count_score_coeff": 1.25,
  "count_score_map": [0, 2.5, 5, 5, 7.5, 7.5, 10],
  "none_of_the_above": true,
  "propositions": ["Choice A", "Choice B", "Choice C"]
}
```

- Rendered as checkboxes; user picks zero or more.
- Score is derived from how many boxes are ticked, **not** from per-choice scores. Two scoring modes, evaluated in this order in `ui/survey.py`:
  1. If `count_score_map` is a non-empty list, `score = count_score_map[min(count, len-1)]` - i.e., the array indexes by count and clamps at the last entry.
  2. Otherwise `score = count * count_score_coeff`.
- `none_of_the_above: true` adds a "None of the above" checkbox. When it's ticked, all other selections are cleared. The answer is still recorded (with `count = 0`), so the question shows up in the submission and gets its recommendation.

### 3. `text` - free text only

```json
"propositions": {
  "type": "text",
  "proposition": "Please explain how your company engages with the community"
}
```

- Rendered as a text area. The string in `proposition` is the placeholder/label.
- The answer score is always `0.0`. Text questions exist for qualitative context, not scoring. Pair with `recommandations.type: "fixed"` (or omit `recommandations`).

## Recommendation types

`recommandations.type` is a discriminator. The recommendation engine (`SurveyService._get_recommandations`) decides what text to return based on this.

### 1. `fixed` - same recommendation regardless of answer

```json
"recommandations": {
  "type": "fixed",
  "recommandation": "Being aware of national and international guidelines..."
}
```

- The text is returned verbatim whenever the question is answered.
- Use this for informational questions (e.g. `choices` and `text` propositions, or any question where the same advice applies whatever the user picks).

### 2. `scored` - recommendation chosen by score

```json
"recommandations": {
  "type": "scored",
  "recommandations": [
    { "score": 5.0, "recommandation": "Great - keep your business plan updated..." },
    { "score": 0.0, "recommandation": "We recommend you start with..." }
  ]
}
```

- The engine picks the entry whose `score` **exactly equals** the answer's score (`==` on floats).
- ⚠️ If no entry matches, `SurveyService._get_recommandations` raises `ValueError`. This means: **every score that an `option` proposition can produce must have a matching `scored` entry.** Mismatch = 500 from `POST /survey/answers`.

### Omitting recommendations

`recommandations` is optional. If you omit the key (or set it to `null`), the question contributes to the score but produces no recommendation entry in the submission response.

## Dependencies (conditional questions)

Set `"dependency": "<parent_id>"` to make a question conditional. The UI hides it until the parent answer satisfies one of these:

- For `option`: the parent must have been answered with anything **other than** the literal string `"No"`.
- For `choices`: the parent must have at least one box ticked.
- If the parent has not been answered at all, the dependent question is hidden.

Conventions used in `survey.json`:

- Dependent questions follow the pattern `X.Y.2` depending on `X.Y.1` (e.g. `1.4.2` → `1.4.1`).
- A dependent question typically uses `recommandations.type: "fixed"` because it's only shown to users who already qualified via the parent.

There is no support for chained dependencies (a question depending on another dependent) or for dependency on a specific answer value. If you need that, extend the logic in `ui/survey.py`.

## End-to-end scoring & recommendation flow

1. UI fetches the question list from `GET /survey/questions`.
2. As the user answers, the UI computes a score for each answer using the rules above and keeps it in `answers_by_id` keyed by `question_id`.
3. On submit, the UI posts `{company_name, country, company_size, answers: [{question_id, score, value}, ...]}` to `POST /survey/answers`.
4. The server reloads `survey.json`, then for each submitted answer:
   - Looks up the question by `question_id`.
   - If `recommandations` is `fixed` → returns the fixed text.
   - If `recommandations` is `scored` → finds the entry where `entry.score == answer.score`.
   - If no `recommandations` → no recommendation produced.
5. If `keep_data=True` (currently always true in the router), the submission is persisted to SQLite via `SqliteSurveyRepository`.
6. The response is a list of `{question_id, recommandation}` which the UI groups by topic and shows alongside per-topic score totals.

## Reading submissions (admin-only)

`GET /survey/submissions` returns the stored submissions so they can be exported, audited, or analysed offline. It is the only endpoint behind authentication.

An **admin key** is required to authorize the data download. It should have been given during the delivery of the project.

**Query parameters**:

| Param | Type | Default | Notes |
|---|---|---|---|
| `days` | int, `1 ≤ days ≤ 365` | `30` | Returns submissions whose `submitted_at` is within the last *N* days. Values outside the range produce a 422 from FastAPI. |


To pull the data, run this command in the terminal:

```bash
export ADMIN_API_KEY="<your-api-key>" 
curl -H "X-Admin-Key:$ADMIN_API_KEY" https://nutriapi.accesstonutrition.org/survey/submissions\?days\=60 -o submissions.json
```

This will create a new file `submissions.json` with all the data.

## Common edits - how to do them safely

**Add a new question.** Append a new object to `survey.json`. Pick a unique `question_id` and a `topic` from the `Topic` enum. Choose proposition + recommendation types using the rules above. Restart the API so the file is re-read (the questions endpoint is cached in the UI for 600s - refresh the browser or wait it out).

**Edit an `option` question's scores.** If the question has `scored` recommendations, you **must** update the `recommandations[].score` values in lockstep, or submissions will 500 on that question.

**Add a "None of the above" to a `choices` question.** Set `none_of_the_above: true`. No other change needed - the UI handles the cancel-all-others behavior.

**Make a question conditional.** Add `"dependency": "<parent_id>"`. Make sure the parent is `option` or `choices` (text parents won't work - they always score 0 and produce no truthy answer for the UI to react to).

**Rename a topic.** Update both `survey.json` and the `Topic` enum in `src/nutri/domain/survey.py`. The Pydantic validator will reject the file otherwise.

**Add a brand new proposition or recommendation type.** Three places to touch:

1. `src/nutri/domain/survey.py` - add a Pydantic class with a `type` literal and add it to the discriminated union.
2. `ui/survey_schemas.py` - duplicate the schema (UI and backend deploy separately, so schemas are duplicated by design - see `feedback_ui_backend_separate`).
3. `ui/survey.py` - add a render + scoring branch in the `for q in questions_by_topic[topic]` loop.
4. `src/nutri/application/survey.py` - extend `_get_recommandations` if the new type changes how recommendations are matched.

## Validation tips

- Pydantic validates `survey.json` on every API startup and on every `GET /survey/questions` / `POST /survey/answers`. A malformed file surfaces as a 500 from the API immediately - check the server logs.
- Tests are set up the validate the Pydantic schemas to the `survey.json`. If there is a problem with the matching, you should be notified.

## Info icon

Each question may set `"info": "<text>"`. When non-empty, the UI passes it to Streamlit's `help=` argument on the question label, which renders the standard small ⓘ tooltip. The text is shown verbatim - no markdown rendering, no links - and is purely cosmetic (it's stripped from the score and recommendation logic). If you don't want a tooltip, omit the field or leave it as `""`.

## Score totals and grading

`GET /survey/questions` returns two roll-up numbers alongside the question list:

- `max_score` - sum of every question's max possible score.
- `max_score_by_topic` - the same, broken down by topic.

`SurveyService._get_question_max_score` (`src/nutri/application/survey.py`) computes the per-question max:

| Proposition type | Max score formula |
|---|---|
| `option` | `max(p.score for p in propositions)` |
| `choices` | `max(count_score_map)` if non-empty, else `len(propositions) * count_score_coeff` |
| `text` | `0.0` (text questions never contribute to the score) |

The Streamlit UI converts the user's percentage of `max_score` into a grade in `percentage_to_grade` (`ui/survey.py`):

| Percentage of max | Grade |
|---|---|
| ≥ 80% | A |
| ≥ 60% | B |
| ≥ 40% | C |
| ≥ 20% | D |
| < 20% | E |

⚠️ Bumping any max-bearing score (e.g. raising an `option` from 5 → 7.5) moves the percentage denominator and therefore shifts every existing submission's grade. If you rebalance scores, do it deliberately and ideally in one batch.

