# Repository Guidelines

## Project Structure & Modules
- `consys/` holds runtime code (`model.py`, `_db.py`, `handlers.py`, `files.py`, `types.py`).
- `tests/` contains pytest suites for models and file helpers; fixtures live alongside tests.
- `docs/CONSYS_ORM_DOCUMENTATION.md` is the canonical handbook; `README.md` is the quickstart.
- Build artifacts land in `build/` and `dist/` (clean via `make clean`); do not commit `env/` or `*.egg-info`.

## Setup, Build, Test
- Install runtime: `python -m pip install -e .`
- Install dev tools (lint/test/release): `python -m pip install -e .[dev]`
- Make targets:
  - `make setup` / `make setup-tests`: create venv in `env/`, install runtime/dev deps.
  - `make test-lint-all`: run pylint over source (config at `tests/.pylintrc`).
  - `make test-unit-all`: run full pytest suite.
  - `make test`: lint + tests.
  - `make release`: build wheel/sdist via `python -m build` and upload with twine.

## Coding Style & Naming
- Python 3.10+; 4-space indents; favor type hints where present.
- Keep descriptors explicit—adding undeclared attributes to models raises errors by design.
- Follow existing naming: classes `CamelCase`, functions/vars `snake_case`.
- Lint with pylint (`tests/.pylintrc`); match its max line length 88 and design limits.

## Testing Guidelines
- Tests use pytest (`tests/`); name files `test_*.py` and functions `test_*`.
- Prefer deterministic, in-repo fixtures (see `tests/files/data/` for image samples); avoid network/db calls in tests.
- Run `make test` before submitting; add targeted tests when changing behavior.

## Commit & PR Expectations
- Write concise, imperative commit messages (e.g., “Add partial reload doc”); group related changes.
- PRs should describe intent, key changes, and any testing performed; link issues when available.
- Include screenshots or logs only when UI or build outputs change; otherwise keep PRs text-first.
- Do not commit generated artifacts (`dist/`, `build/`, `env/`, `__pycache__/`, `.pytest_cache/`); use `.gitignore` patterns already present.

## Security & Configuration Notes
- No secrets should live in the repo; supply Mongo credentials via runtime configuration when using `make_base`.
- File upload helpers write to disk—use test data under `tests/files/data/` and avoid external URLs in automated runs.
