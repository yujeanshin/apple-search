log of choices made while building. Will be integrated into design doc in the future.


# v0.1.0
## filetree

```
apple-game/
├── README.md
├── DECISIONS.md
├── .gitignore
├── data/
│   ├── suites/                # 5x8-dev-v1.json, 5x8-main-v1.json
│   └── results/
└── backend/
    ├── README.md
    ├── DESIGN.md
    ├── pyproject.toml
    ├── uv.lock
    ├── .python-version
    ├── src/
    │   └── apple_game/
    │       ├── __init__.py
    │       ├── core.py
    │       ├── algorithms/
    │       │   ├── __init__.py
    │       │   ├── exhaustive.py
    │       │   ├── random_play.py
    │       │   ├── move_fewest.py
    │       │   ├── move_most.py
    │       │   ├── large_nums.py
    │       │   ├── constrained_first.py
    │       │   └── combined.py
    │       └── evals/
    │           ├── __init__.py
    │           ├── make_suite.py
    │           └── run_benchmark.py
    └── tests/
        ├── test_core.py
        ├── test_exhaustive.py
        └── test_algorithms.py
```

- Edited layout to create a Python package
- tests/ taken out of the package (as noted in pytest docs [Good Integration Practices](https://docs.pytest.org/en/stable/explanation/goodpractices.html))
- data/ taken out of the backend and placed in root
- removed initial_DESIGN