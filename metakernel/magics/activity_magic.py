# Copyright (c) Metakernel Development Team.
# Distributed under the terms of the Modified BSD License.

from __future__ import annotations

import datetime
import getpass
import os
from typing import Any

try:
    from ipywidgets import widgets
except ImportError:
    widgets = None

from metakernel import Magic, MetaKernel


def touch(fname: str, times: Any = None) -> None:
    with open(fname, "a"):
        os.utime(fname, times)


class Activity:
    def __init__(self) -> None:
        self.questions: list[Any] = []
        self.filename: str | None = None
        self.results_filename: str | None = None
        self.instructors: list[Any] = []
        self.show_initial = True
        self.last_id = None

    def load(self, filename: str) -> None:
        if filename.startswith("~"):
            filename = os.path.expanduser(filename)
        filename = os.path.abspath(filename)
        self.filename = filename
        assert self.filename is not None
        with open(self.filename) as fp:
            json_text = "".join(fp.readlines())
        self.load_json(json_text)
        if self.results_filename is None:
            self.results_filename = filename + ".results"
        touch(self.results_filename)

    def load_json(self, json_text: str) -> None:
        # Allow use of widgets:
        if widgets is None:
            return
        json = eval(
            json_text.strip(), {key: getattr(widgets, key) for key in dir(widgets)}
        )
        if json.get("results_filename", None):
            self.results_filename = json["results_filename"]
        if json.get("instructors", []):
            for instructor in json["instructors"]:
                self.instructors.append(instructor)
        if json["activity"] == "poll":
            self.index = 0
            for item in json["items"]:
                if item["type"] == "multiple choice":
                    # FIXME: allow widgets; need to rewrite create/show:
                    question = item["question"]
                    # if isinstance(question, str):
                    #    question = widgets.HTML(question)
                    options = item["options"]
                    # for pos in range(len(options)):
                    #    option = options[pos]
                    #    if isinstance(option, str):
                    #        options[pos] = widgets.HTML(option)
                    q = Question(item["id"], question, options)
                    self.questions.append(q)
                else:
                    raise Exception(
                        "not a valid question 'type': use ['multiple choice']"
                    )
            self.create_widget()
            self.use_question(self.index)
        else:
            raise Exception("not a valid 'activity': use ['poll']")

    def use_question(self, index: int) -> None:
        self.set_question(self.questions[index].question)
        self.set_id(self.questions[index].id)
        self.results_html.layout.visibility = "hidden"
        self.results_button.layout.visibility = (
            "visible" if (getpass.getuser() in self.instructors) else "hidden"
        )
        self.prev_button.disabled = index == 0
        self.next_button.disabled = index == len(self.questions) - 1
        for i in range(5):
            self.choice_row_list[i].layout.visibility = "hidden"
            self.buttons[i].layout.visibility = "hidden"
        for i in range(len(self.questions[index].options)):
            self.choice_widgets[i].value = self.questions[index].options[i]
            self.choice_row_list[i].layout.visibility = "visible"
            self.buttons[i].layout.visibility = "visible"

    def create_widget(self) -> None:
        self.id_widget = widgets.HTML("")
        self.question_widget = widgets.HTML("")
        self.choice_widgets = []
        self.choice_row_list = []
        for count in range(1, 5 + 1):
            self.choice_widgets.append(widgets.HTML(""))
            self.choice_row_list.append(
                widgets.HBox(
                    [
                        widgets.HTML("<b>%s</b>)&nbsp;&nbsp;" % count),
                        self.choice_widgets[-1],
                    ]
                )
            )
        self.buttons = []
        for i in range(1, 5 + 1):
            button = widgets.Button(description=str(i))
            button.on_click(self.handle_submit)
            button.layout.margin = "20px"
            self.buttons.append(button)
        self.respond_row_widgets = widgets.HBox(
            [widgets.HTML("""<br/><br clear="all"/><b>Respond</b>: """)] + self.buttons
        )
        self.next_button = widgets.Button(description="Next")
        self.next_button.on_click(self.handle_next)
        self.results_button = widgets.Button(description="Results")
        self.results_button.on_click(self.handle_results)
        self.prev_button = widgets.Button(description="Previous")
        self.prev_button.on_click(self.handle_prev)
        self.results_html = widgets.HTML("")
        self.top_margin = widgets.HTML("")
        # self.top_margin.layout.height = "100px"
        right_stack = widgets.VBox([self.top_margin, self.results_html])
        self.stack = widgets.VBox(
            [self.id_widget, self.question_widget]
            + self.choice_row_list
            + [
                self.respond_row_widgets,
                widgets.HBox([self.prev_button, self.results_button, self.next_button]),
            ]
        )
        self.output = widgets.Output()
        self.top_level = widgets.VBox(
            [widgets.HBox([self.stack, right_stack]), self.output]
        )

    def set_question(self, question: str) -> None:
        self.question_widget.value = "<h1>%s</h1>" % question

    def set_id(self, id: Any) -> None:
        self.id_widget.value = "<p><b>Question ID</b>: %s</p>" % id
        self.id = id

    def handle_results(self, sender: Any) -> None:
        # write out when we show the Results:
        self.handle_submit(sender)
        if self.last_id == self.questions[self.index].id:
            self.show_initial = not self.show_initial
        else:
            self.show_initial = True
            self.last_id = self.questions[self.index].id
        data = {}
        assert self.results_filename is not None
        with open(self.results_filename) as fp:
            line = fp.readline()
            while line:
                if "::" in line:
                    id, user, _time, choice = line.split("::")
                    if self.questions[self.index].id == id:
                        if choice.strip() != "Results":
                            if self.show_initial:
                                if user.strip() not in data:
                                    data[user.strip()] = choice.strip()
                            else:  # shows last
                                data[user.strip()] = choice.strip()
                line = fp.readline()
        choices = {
            str(i): 0 for i in range(1, len(self.questions[self.index].options) + 1)
        }
        for datum in data.values():
            if datum not in choices:
                choices[datum] = 0
            choices[datum] += 1
        barvalues = [int(value) for key, value in sorted(choices.items())]
        self.stack.layout.width = "55%"
        try:
            from calysto.graphics import BarChart

            barchart = BarChart(
                size=(300, 400), data=barvalues, labels=sorted(choices.keys())
            )
            self.results_html.value = str(barchart)
            self.results_html.layout.visibility = "visible"
        except Exception:
            with self.output:
                print(sorted(choices.keys()))
                print(barvalues)

    def handle_submit(self, sender: Any) -> None:
        import portalocker

        with portalocker.Lock(self.results_filename, "a+") as g:
            g.write(
                "%s::%s::%s::%s\n"
                % (
                    self.id,
                    getpass.getuser(),
                    datetime.datetime.today(),
                    sender.description,
                )
            )
            g.flush()
            os.fsync(g.fileno())
        self.output.clear_output()
        with self.output:
            print("Received: " + sender.description)

    def handle_next(self, sender: Any) -> None:
        if self.index < len(self.questions) - 1:
            self.index += 1
            self.use_question(self.index)
            self.output.clear_output()

    def handle_prev(self, sender: Any) -> None:
        if self.index > 0:
            self.index -= 1
            self.use_question(self.index)
            self.output.clear_output()

    def render(self) -> None:
        from metakernel.display import display

        display(self.top_level)


class Question:
    def __init__(self, id: Any, question: str, options: Any) -> None:
        self.id = id
        self.question = question
        self.options = options


class ActivityMagic(Magic):
    def line_activity(self, filename: str, mode: Any = None) -> None:
        """
        %activity FILENAME - run a widget-based activity
          (poll, classroom response, clicker-like activity)

        This magic will load the JSON in the filename.

        Examples:
            %activity /home/teacher/activity1
            %activity /home/teacher/activity1 new
            %activity /home/teacher/activity1 edit
        """
        from IPython import get_ipython  # type:ignore[attr-defined]

        if mode == "new":
            text = '''
{"activity": "poll",
 "instructors": ["YOUR ID HERE"],
 "items": [
      {"id": "1",
       "question":  """When it comes to learning, metacognition (e.g., thinking about thinking) can be just as important as intelligence.""",
       "type": "multiple choice",
       "options": ["True", "False"]
      },
      {"id": "2",
       "question":  """What is the best way to learn from some text?""",
       "type": "multiple choice",
       "options": ["Read and reread the text.",
                   "Explain key ideas of the text to yourself while reading.",
                   "Underline key concepts.",
                   "Use a highlighter"]
      },
      {"id": "3",
       "question":  """Intelligence is fixed at birth.""",
       "type": "multiple choice",
       "options": ["True", "False"]
      },
      {"id": "4",
       "question":  """You have a test coming up. What's the best way to review the material?""",
       "type": "multiple choice",
       "options": ["Circle key points in the textbook.",
                   "Review relevant points of the lecture in audio format.",
                   "Take an informal quiz based on the material."]
      },
      {"id": "5",
       "question":  """To which of the following should you not tailor your learning?""",
       "type": "multiple choice",
       "options": ["Learning styles (visual, audio, etc.)", "Previous knowledge", "Interests", "Ability"]
      },
      {"id": "6",
       "question":  """Learning should be spaced out over time.""",
       "type": "multiple choice",
       "options": ["True", "False"]
      },
      {"id": "7",
       "question":  """Right-brained people learn differently from left-brained people.""",
       "type": "multiple choice",
       "options": ["True", "False"]
      }
   ]
}'''
            get_ipython().set_next_input(("%%%%activity %s\n\n" % filename) + text)
            return
        elif mode == "edit":
            text = "".join(open(filename).readlines())
            get_ipython().set_next_input(("%%%%activity %s\n\n" % filename) + text)
        else:
            activity = Activity()
            activity.load(filename)
            activity.render()

    def cell_activity(self, filename: str) -> None:
        """
        %%activity FILENAME - make an activity from
          a JSON structure

        This magic will construct a Python file from the cell's
        content, a JSON structure.

        Example:
            %%activity /home/teacher/activity1
            {"activity": "poll",
             "instructors": ["teacher01"],
             "results_file": "/home/teacher/activity1.results",
             "items": [{"id": "...",
                        "type": "multiple choice",
                        "question": "...",
                        "options": ["...", ...]
                       }, ...]
            }

        In this example, users will load
        /home/teacher/activity1
        """
        if filename.startswith("~"):
            filename = os.path.expanduser(filename)
        filename = os.path.abspath(filename)
        with open(filename, "w") as fp:
            fp.write(self.code)
        activity = Activity()
        activity.load(filename)
        # Make sure results file is writable:
        assert activity.results_filename is not None
        os.chmod(activity.results_filename, 0o777)
        # Ok, let's test it (MetaKernel):
        self.line_activity(filename)
        self.evaluate = False


def register_magics(kernel: MetaKernel) -> None:
    kernel.register_magics(ActivityMagic)


def register_ipython_magics() -> None:
    from IPython.core.magic import register_cell_magic, register_line_magic

    from metakernel import IPythonKernel
    from metakernel.utils import add_docs

    kernel = IPythonKernel()
    magic = ActivityMagic(kernel)
    # Make magics callable:
    kernel.line_magics["activity"] = magic
    kernel.cell_magics["activity"] = magic

    @register_line_magic
    @add_docs(magic.line_activity.__doc__)
    def activity(line):
        kernel.call_magic("%activity " + line)

    @register_cell_magic  # type: ignore[no-redef]
    @add_docs(magic.cell_activity.__doc__)
    def activity(line, cell):  # noqa: F811
        magic.code = cell
        magic.cell_activity(line)
