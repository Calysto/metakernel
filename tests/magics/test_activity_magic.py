import importlib.util
import os
import sys

import pytest

pytestmark = pytest.mark.skipif(
    sys.platform == "win32", reason="activity magic not supported on Windows"
)

from metakernel.magics.activity_magic import Activity, touch
from tests.utils import EvalKernel, get_kernel, get_log_text

NO_WIDGETS = importlib.util.find_spec("ipywidgets") is None

# Minimal poll activity as a Python literal (load_json uses eval, not json.loads)
ACTIVITY_TEXT = """\
{
    "activity": "poll",
    "instructors": ["teacher01"],
    "items": [
        {
            "id": "q1",
            "type": "multiple choice",
            "question": "Is metakernel great?",
            "options": ["Yes", "Absolutely"]
        }
    ]
}
"""


# ---------------------------------------------------------------------------
# touch() utility
# ---------------------------------------------------------------------------


def test_touch_creates_file(tmp_path) -> None:
    fname = str(tmp_path / "new.txt")
    assert not os.path.exists(fname)
    touch(fname)
    assert os.path.exists(fname)


def test_touch_preserves_existing_content(tmp_path) -> None:
    fname = str(tmp_path / "existing.txt")
    with open(fname, "w") as f:
        f.write("hello")
    touch(fname)
    with open(fname) as f:
        assert f.read() == "hello"


# ---------------------------------------------------------------------------
# Activity.load()
# ---------------------------------------------------------------------------


def test_activity_load_creates_results_file(tmp_path) -> None:
    activity_file = tmp_path / "activity.poll"
    activity_file.write_text(ACTIVITY_TEXT)

    a = Activity()
    a.load(str(activity_file))

    assert a.filename == str(activity_file)
    expected = str(activity_file) + ".results"
    assert a.results_filename == expected
    assert os.path.exists(expected)


def test_activity_load_tilde_expansion(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("HOME", str(tmp_path))
    activity_file = tmp_path / "activity.poll"
    activity_file.write_text(ACTIVITY_TEXT)

    a = Activity()
    a.load("~/activity.poll")

    assert a.filename == str(activity_file)


def test_activity_load_custom_results_filename(tmp_path) -> None:
    custom_results = str(tmp_path / "custom.results")
    text = (
        '{"activity": "poll", "instructors": [],'
        f' "results_filename": "{custom_results}",'
        ' "items": [{"id": "1", "type": "multiple choice",'
        ' "question": "Q?", "options": ["A", "B"]}]}'
    )
    activity_file = tmp_path / "activity.poll"
    activity_file.write_text(text)

    a = Activity()
    a.load(str(activity_file))

    # When widgets are absent load_json returns early, but the results_filename
    # set in load() will be the json value only if widgets parsed it.
    if NO_WIDGETS:
        # load_json returned early; fallback path appends ".results"
        assert a.results_filename == str(activity_file) + ".results"
    else:
        assert a.results_filename == custom_results


# ---------------------------------------------------------------------------
# Activity.load_json()
# ---------------------------------------------------------------------------


def test_activity_load_json_no_widgets(monkeypatch) -> None:
    """load_json is a no-op when ipywidgets is unavailable."""
    import metakernel.magics.activity_magic as mod

    monkeypatch.setattr(mod, "widgets", None)
    a = Activity()
    a.load_json(ACTIVITY_TEXT)
    assert a.questions == []


@pytest.mark.skipif(NO_WIDGETS, reason="Requires ipywidgets")
def test_activity_load_json_parses_questions() -> None:
    a = Activity()
    a.load_json(ACTIVITY_TEXT)

    assert len(a.questions) == 1
    q = a.questions[0]
    assert q.id == "q1"
    assert q.question == "Is metakernel great?"
    assert q.options == ["Yes", "Absolutely"]


@pytest.mark.skipif(NO_WIDGETS, reason="Requires ipywidgets")
def test_activity_load_json_sets_instructors() -> None:
    a = Activity()
    a.load_json(ACTIVITY_TEXT)
    assert "teacher01" in a.instructors


@pytest.mark.skipif(NO_WIDGETS, reason="Requires ipywidgets")
def test_activity_load_json_invalid_activity_type() -> None:
    bad = '{"activity": "quiz", "instructors": [], "items": []}'
    a = Activity()
    with pytest.raises(Exception, match="not a valid 'activity'"):
        a.load_json(bad)


@pytest.mark.skipif(NO_WIDGETS, reason="Requires ipywidgets")
def test_activity_load_json_invalid_question_type() -> None:
    bad = (
        '{"activity": "poll", "instructors": [], "items": ['
        '{"id": "1", "type": "essay", "question": "Q?", "options": []}]}'
    )
    a = Activity()
    with pytest.raises(Exception, match="not a valid question 'type'"):
        a.load_json(bad)


# ---------------------------------------------------------------------------
# %%activity cell magic
# ---------------------------------------------------------------------------


def test_cell_activity_magic_writes_file(tmp_path) -> None:
    """%%activity writes the cell body to the named file and creates a results file."""
    activity_file = tmp_path / "test_activity"
    kernel = get_kernel(EvalKernel)
    kernel.do_execute(f"%%activity {activity_file}\n{ACTIVITY_TEXT}", False)

    assert activity_file.exists()
    assert "poll" in activity_file.read_text()
    assert os.path.exists(str(activity_file) + ".results")


@pytest.mark.skipif(NO_WIDGETS, reason="Requires ipywidgets")
def test_cell_activity_magic_displays_widget(tmp_path) -> None:
    """%%activity renders a widget when ipywidgets is available."""
    activity_file = tmp_path / "test_activity"
    kernel = get_kernel(EvalKernel)
    kernel.do_execute(f"%%activity {activity_file}\n{ACTIVITY_TEXT}", False)

    assert "Display Widget" in get_log_text(kernel)


# ---------------------------------------------------------------------------
# %activity line magic
# ---------------------------------------------------------------------------


@pytest.mark.skipif(NO_WIDGETS, reason="Requires ipywidgets")
def test_line_activity_magic_renders_widget(tmp_path) -> None:
    """%activity loads an existing activity file and renders a widget."""
    activity_file = tmp_path / "test_activity"
    activity_file.write_text(ACTIVITY_TEXT)

    kernel = get_kernel(EvalKernel)
    kernel.do_execute(f"%activity {activity_file}", False)

    assert "Display Widget" in get_log_text(kernel)
    assert os.path.exists(str(activity_file) + ".results")
