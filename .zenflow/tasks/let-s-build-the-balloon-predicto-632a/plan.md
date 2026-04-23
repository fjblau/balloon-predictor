# balloon-predictor build plan

Build the `balloon-predictor` public MIT library as specified in the StratoChaser Two-Repo Skeleton document.

### [x] Step 1: Project scaffold
- Create `.gitignore`, `pyproject.toml`, `LICENSE`

### [x] Step 2: Core library implementation
- `balloon_predictor/__init__.py`
- `balloon_predictor/models.py` — Pydantic domain models
- `balloon_predictor/tawhiri.py` — async Tawhiri API client
- `balloon_predictor/burst.py` — burst altitude + helium calculators
- `balloon_predictor/monte_carlo.py` — ensemble runner
- `balloon_predictor/gfs.py` — GFS forecast cube fetcher (stub)
- `balloon_predictor/cli.py` — `balloon-predict` CLI

### [x] Step 3: Tests
- `tests/test_burst.py`
- `tests/test_tawhiri.py`

### [x] Step 4: Verification
- Install dev dependencies and run pytest
