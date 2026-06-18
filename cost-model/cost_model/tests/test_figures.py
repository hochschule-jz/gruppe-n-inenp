import pytest


def test_render_all_writes_files(tmp_path):
    pytest.importorskip("matplotlib")  # skip cleanly if matplotlib is not installed
    from cost_model import load_assumptions
    from cost_model.figures import render_all

    paths = render_all(load_assumptions(), tmp_path, "base")
    assert paths, "render_all should return the written paths"
    assert all(p.exists() and p.stat().st_size > 0 for p in paths)
    # PNG (slides) + SVG (LaTeX) per chart, 4 charts.
    assert sum(p.suffix == ".png" for p in paths) == 4
    assert sum(p.suffix == ".svg" for p in paths) == 4
