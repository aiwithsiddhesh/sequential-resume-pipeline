# sequential-resume-pipeline

A LangGraph pipeline that tailors a resume and drafts a cover letter for a
specific job description. Built as a sequential graph with structured
(Pydantic) state passed between stages, rather than a single freeform
LLM prompt.

## Pipeline design

Five stages, run in order:

1. **parse** — extract structured data (skills, experience bullets,
   requirements) from the raw resume and job description text.
2. **gap_analysis** — compare resume skills against JD requirements;
   produce matched skills, missing skills, and a match score.
3. **tailor** — rewrite/reorder resume bullets to emphasize what matches,
   using the gap report.
4. **cover_letter** — draft a cover letter that leans on the tailored
   bullets and addresses the top gaps.
5. **validate** — check that the tailored output actually covers the JD's
   key terms; produces a pass/fail and score.

```mermaid
flowchart LR
    START([START]) --> parse[parse]
    parse --> gap_analysis[gap_analysis]
    gap_analysis --> tailor[tailor]
    tailor --> cover_letter[cover_letter]
    cover_letter --> validate[validate]
    validate --> END([END])
```

## Status

- [x] Project scaffolding (`pyproject.toml`, `.env` config)
- [x] `app/config.py` — Groq API key loaded via `pydantic-settings`
- [x] `app/loaders.py` — read resume/JD from `.txt` or `.pdf`
- [x] `app/state.py` — Pydantic models for pipeline state
- [ ] `app/nodes.py` — the 5 node functions
- [ ] `app/graph.py` — builds and compiles the `StateGraph`
- [ ] `app/main.py` — entrypoint

## Setup

Requires Python 3.13+ and [uv](https://docs.astral.sh/uv/).

```bash
uv sync
cp .env.example .env
# then fill in GROQ_API_KEY in .env
```

## Run

```bash
uv run python -m app.main
```

(entrypoint not yet implemented)
