```bash
cd ./plugin-qgis
uv venv
source .venv/bin/activate

uv pip install -e ".[dev]"

uv run ruff check .
uv run ruff format --check .
uv run pytest

zip -r plugin.zip plugin-qgis -x "*/.*"
```