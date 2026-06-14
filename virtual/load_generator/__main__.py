"""Entry point: ``python -m load_generator --profile load_generator/peak.json ...``"""

from .cli import main

if __name__ == "__main__":
    raise SystemExit(main())
