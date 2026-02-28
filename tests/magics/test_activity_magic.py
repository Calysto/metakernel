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
NO_PORTALOCKER = importlib.util.find_spec("portalocker") is None

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

# Multi-question activity for navigation tests
ACTIVITY_TEXT_MULTI = """\
{
    "activity": "poll",
    "instructors": ["teacher01"],
    "items": [
        {
            "id": "q1",
            "type": "multiple choice",
            "question": "Question one?",
            "options": ["Yes", "No"]
        },
        {
            "id": "q2",
            "type": "multiple choice",
            "question": "Question two?",
            "options": ["A", "B", "C"]
        }
    ]
}
"""


class MockSender:
    def __init__(self, description: str) -> None:
        self.description = description


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


# ---------------------------------------------------------------------------
# Activity.create_widget()
# ---------------------------------------------------------------------------


@pytest.mark.skipif(NO_WIDGETS, reason="Requires ipywidgets")
def test_create_widget_creates_five_choice_slots() -> None:
    a = Activity()
    a.load_json(ACTIVITY_TEXT)
    assert len(a.buttons) == 5
    assert len(a.choice_widgets) == 5
    assert len(a.choice_row_list) == 5


@pytest.mark.skipif(NO_WIDGETS, reason="Requires ipywidgets")
def test_create_widget_creates_navigation_buttons() -> None:
    a = Activity()
    a.load_json(ACTIVITY_TEXT)
    assert hasattr(a, "next_button")
    assert hasattr(a, "prev_button")
    assert hasattr(a, "results_button")


@pytest.mark.skipif(NO_WIDGETS, reason="Requires ipywidgets")
def test_create_widget_creates_top_level_output_and_stack() -> None:
    a = Activity()
    a.load_json(ACTIVITY_TEXT)
    assert hasattr(a, "top_level")
    assert hasattr(a, "output")
    assert hasattr(a, "stack")


# ---------------------------------------------------------------------------
# Activity.set_question()
# ---------------------------------------------------------------------------


@pytest.mark.skipif(NO_WIDGETS, reason="Requires ipywidgets")
def test_set_question_updates_widget_value() -> None:
    a = Activity()
    a.load_json(ACTIVITY_TEXT)
    a.set_question("New question?")
    assert a.question_widget.value == "<h1>New question?</h1>"


# ---------------------------------------------------------------------------
# Activity.set_id()
# ---------------------------------------------------------------------------


@pytest.mark.skipif(NO_WIDGETS, reason="Requires ipywidgets")
def test_set_id_updates_widget_and_attribute() -> None:
    a = Activity()
    a.load_json(ACTIVITY_TEXT)
    a.set_id("q99")
    assert a.id_widget.value == "<p><b>Question ID</b>: q99</p>"
    assert a.id == "q99"


# ---------------------------------------------------------------------------
# Activity.use_question()
# ---------------------------------------------------------------------------


@pytest.mark.skipif(NO_WIDGETS, reason="Requires ipywidgets")
def test_use_question_first_question_disables_prev_button() -> None:
    a = Activity()
    a.load_json(ACTIVITY_TEXT_MULTI)
    a.use_question(0)
    assert a.prev_button.disabled is True
    assert a.next_button.disabled is False


@pytest.mark.skipif(NO_WIDGETS, reason="Requires ipywidgets")
def test_use_question_last_question_disables_next_button() -> None:
    a = Activity()
    a.load_json(ACTIVITY_TEXT_MULTI)
    a.use_question(1)
    assert a.prev_button.disabled is False
    assert a.next_button.disabled is True


@pytest.mark.skipif(NO_WIDGETS, reason="Requires ipywidgets")
def test_use_question_sets_question_text() -> None:
    a = Activity()
    a.load_json(ACTIVITY_TEXT_MULTI)
    a.use_question(1)
    assert "Question two?" in a.question_widget.value


@pytest.mark.skipif(NO_WIDGETS, reason="Requires ipywidgets")
def test_use_question_hides_unused_choice_rows() -> None:
    a = Activity()
    a.load_json(ACTIVITY_TEXT_MULTI)
    a.use_question(0)  # 2 options; rows 2-4 should be hidden
    assert a.choice_row_list[0].layout.visibility == "visible"
    assert a.choice_row_list[1].layout.visibility == "visible"
    assert a.choice_row_list[2].layout.visibility == "hidden"


@pytest.mark.skipif(NO_WIDGETS, reason="Requires ipywidgets")
def test_use_question_shows_correct_number_of_choice_rows() -> None:
    a = Activity()
    a.load_json(ACTIVITY_TEXT_MULTI)
    a.use_question(1)  # 3 options
    assert a.choice_row_list[0].layout.visibility == "visible"
    assert a.choice_row_list[1].layout.visibility == "visible"
    assert a.choice_row_list[2].layout.visibility == "visible"
    assert a.choice_row_list[3].layout.visibility == "hidden"


# ---------------------------------------------------------------------------
# Activity.handle_submit()
# ---------------------------------------------------------------------------


@pytest.mark.skipif(NO_WIDGETS, reason="Requires ipywidgets")
@pytest.mark.skipif(NO_PORTALOCKER, reason="Requires portalocker")
def test_handle_submit_writes_choice_to_results_file(tmp_path) -> None:
    activity_file = tmp_path / "activity.poll"
    activity_file.write_text(ACTIVITY_TEXT)
    a = Activity()
    a.load(str(activity_file))
    a.handle_submit(MockSender("1"))
    assert a.results_filename is not None
    with open(a.results_filename) as f:
        results = f.read()
    assert "::1\n" in results


@pytest.mark.skipif(NO_WIDGETS, reason="Requires ipywidgets")
@pytest.mark.skipif(NO_PORTALOCKER, reason="Requires portalocker")
def test_handle_submit_records_question_id(tmp_path) -> None:
    activity_file = tmp_path / "activity.poll"
    activity_file.write_text(ACTIVITY_TEXT)
    a = Activity()
    a.load(str(activity_file))
    a.set_id("q1")
    a.handle_submit(MockSender("2"))
    assert a.results_filename is not None
    with open(a.results_filename) as f:
        results = f.read()
    assert results.startswith("q1::")


# ---------------------------------------------------------------------------
# Activity.handle_next()
# ---------------------------------------------------------------------------


@pytest.mark.skipif(NO_WIDGETS, reason="Requires ipywidgets")
def test_handle_next_increments_index() -> None:
    a = Activity()
    a.load_json(ACTIVITY_TEXT_MULTI)
    assert a.index == 0
    a.handle_next(MockSender("Next"))
    assert a.index == 1


@pytest.mark.skipif(NO_WIDGETS, reason="Requires ipywidgets")
def test_handle_next_does_not_exceed_last_question() -> None:
    a = Activity()
    a.load_json(ACTIVITY_TEXT_MULTI)
    a.handle_next(MockSender("Next"))
    a.handle_next(MockSender("Next"))  # already at last question
    assert a.index == 1


# ---------------------------------------------------------------------------
# Activity.handle_prev()
# ---------------------------------------------------------------------------


@pytest.mark.skipif(NO_WIDGETS, reason="Requires ipywidgets")
def test_handle_prev_decrements_index() -> None:
    a = Activity()
    a.load_json(ACTIVITY_TEXT_MULTI)
    a.handle_next(MockSender("Next"))
    assert a.index == 1
    a.handle_prev(MockSender("Previous"))
    assert a.index == 0


@pytest.mark.skipif(NO_WIDGETS, reason="Requires ipywidgets")
def test_handle_prev_does_not_go_below_zero() -> None:
    a = Activity()
    a.load_json(ACTIVITY_TEXT_MULTI)
    a.handle_prev(MockSender("Previous"))  # already at index 0
    assert a.index == 0


# ---------------------------------------------------------------------------
# Activity.handle_results()
# ---------------------------------------------------------------------------


@pytest.mark.skipif(NO_WIDGETS, reason="Requires ipywidgets")
@pytest.mark.skipif(NO_PORTALOCKER, reason="Requires portalocker")
def test_handle_results_runs_without_error(tmp_path) -> None:
    activity_file = tmp_path / "activity.poll"
    activity_file.write_text(ACTIVITY_TEXT)
    a = Activity()
    a.load(str(activity_file))
    assert a.results_filename is not None
    with open(a.results_filename, "w") as f:
        f.write("q1::user1::2024-01-01::1\n")
        f.write("q1::user2::2024-01-01::2\n")
    a.handle_results(MockSender("Results"))


@pytest.mark.skipif(NO_WIDGETS, reason="Requires ipywidgets")
@pytest.mark.skipif(NO_PORTALOCKER, reason="Requires portalocker")
def test_handle_results_sets_last_id(tmp_path) -> None:
    activity_file = tmp_path / "activity.poll"
    activity_file.write_text(ACTIVITY_TEXT)
    a = Activity()
    a.load(str(activity_file))
    assert a.last_id is None
    a.handle_results(MockSender("Results"))
    assert a.last_id == "q1"


@pytest.mark.skipif(NO_WIDGETS, reason="Requires ipywidgets")
@pytest.mark.skipif(NO_PORTALOCKER, reason="Requires portalocker")
def test_handle_results_toggles_show_initial_on_repeat(tmp_path) -> None:
    activity_file = tmp_path / "activity.poll"
    activity_file.write_text(ACTIVITY_TEXT)
    a = Activity()
    a.load(str(activity_file))
    assert a.show_initial is True
    a.handle_results(MockSender("Results"))
    assert a.show_initial is True  # first call sets last_id, does not toggle
    a.handle_results(MockSender("Results"))
    assert a.show_initial is False  # second call on same id toggles


# ---------------------------------------------------------------------------
# Activity.render()
# ---------------------------------------------------------------------------


@pytest.mark.skipif(NO_WIDGETS, reason="Requires ipywidgets")
def test_render_calls_display_with_top_level(tmp_path, monkeypatch) -> None:
    import metakernel.display as display_mod

    activity_file = tmp_path / "activity.poll"
    activity_file.write_text(ACTIVITY_TEXT)
    a = Activity()
    a.load(str(activity_file))

    displayed = []
    monkeypatch.setattr(display_mod, "display", lambda obj: displayed.append(obj))
    a.render()

    assert len(displayed) == 1
    assert displayed[0] is a.top_level
