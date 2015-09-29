# Copyright (c) Metakernel Development Team.
# Distributed under the terms of the Modified BSD License.

from IPython.html import widgets
from metakernel import Magic, option
import os
import fcntl
import getpass
import datetime

def touch(fname, times=None):
    with open(fname, 'a'):
        os.utime(fname, times)

class Activity(object):
    def __init__(self):
        self.questions = []
        self.filename = None
        self.results_filename = None
        self.instructors = []

    def load(self, filename):
        if filename.startswith("~"):
            filename = os.path.expanduser(filename)
        filename = os.path.abspath(filename)
        self.filename = filename
        with open(self.filename) as fp:
            json_text = "".join(fp.readlines())
        self.load_json(json_text)
        if self.results_filename is None:
            self.results_filename = filename + ".results"
        touch(self.results_filename)

    def load_json(self, json_text):
        from IPython.html import widgets
        # Allow use of widgets:
        json = eval(json_text.strip(), {key: getattr(widgets, key) for key in dir(widgets)})
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
                    #if isinstance(question, str):
                    #    question = widgets.HTML(question)
                    options = item["options"]
                    #for pos in range(len(options)):
                    #    option = options[pos]
                    #    if isinstance(option, str):
                    #        options[pos] = widgets.HTML(option)
                    q = Question(item["id"], question, options)
                    self.questions.append(q)
                else:
                    raise Exception("not a valid question 'type': use ['multiple choice']")
            self.create_widget()
            self.use_question(self.index)
        else:
            raise Exception("not a valid 'activity': use ['poll']")
        
    def use_question(self, index):
        self.set_question(self.questions[index].question)
        self.set_id(self.questions[index].id)
        self.results_html.visible = False
        self.results_button.visible = (getpass.getuser() in self.instructors)
        self.prev_button.disabled = index == 0
        self.next_button.disabled = index == len(self.questions) - 1
        for i in range(5):
            self.choice_row_list[i].visible = False
            self.buttons[i].visible = False
        for i in range(len(self.questions[index].options)):
            self.choice_widgets[i].value = self.questions[index].options[i]
            self.choice_row_list[i].visible = True
            self.buttons[i].visible = True
        
    def create_widget(self):
        self.id_widget = widgets.HTML("")
        self.question_widget = widgets.HTML("")
        self.choice_widgets = []
        self.choice_row_list = []
        for count in range(1, 5 + 1):
            self.choice_widgets.append(widgets.HTML(""))
            self.choice_row_list.append(widgets.HBox([widgets.HTML("<b>%s</b>)&nbsp;&nbsp;" % count), 
                                                      self.choice_widgets[-1]]))
        self.buttons = []
        for i in range(1, 5 + 1):
            button = widgets.Button(description = str(i))
            button.on_click(self.handle_submit)
            button.margin = 20
            self.buttons.append(button)
        self.respond_row_widgets = widgets.HBox([widgets.HTML("""<br/><br clear="all"/><b>Respond</b>: """)] + self.buttons)
        self.next_button = widgets.Button(description="Next")
        self.next_button.on_click(self.handle_next)
        self.results_button = widgets.Button(description="Results")
        self.results_button.on_click(self.handle_results)
        self.prev_button = widgets.Button(description="Previous")
        self.prev_button.on_click(self.handle_prev)
        self.results_html = widgets.HTML("")
        self.top_margin = widgets.HTML("")
        self.top_margin.height = "100px"
        right_stack = widgets.VBox([self.top_margin, self.results_html])
        self.stack = widgets.VBox([self.id_widget, self.question_widget] + self.choice_row_list +
                                  [self.respond_row_widgets, 
                                   widgets.HBox([self.prev_button, self.results_button, self.next_button])])
        self.stack.width = "75%"
        self.top_level = widgets.HBox([self.stack, right_stack])

    def set_question(self, question):
        self.question_widget.value = "<h1>%s</h1>" % question
        
    def set_id(self, id):
        self.id_widget.value = "<p><b>Question ID</b>: %s</p>" % id
        self.id = id

    def handle_results(self, sender):
        data = {}
        with open(self.results_filename) as fp:
            line = fp.readline()
            while line:
                if "::" in line:
                    id, user, time, choice = line.split("::")
                    data[user.strip()] = choice.strip()
                line = fp.readline()
        choices = {str(i): 0 for i in range(1, len(self.questions[self.index].options) + 1)}
        for datum in data.values():
            if datum not in choices:
                choices[datum] = 0
            choices[datum] += 1
        barvalues = [int(value) for key,value in sorted(choices.items())]
        try:
            from calysto.graphics import BarChart
            barchart = BarChart(size=(300, 400), data=barvalues, labels=sorted(choices.keys()))
            self.results_html.value = str(barchart)
            self.results_html.visible = True
        except:
            print(sorted(choices.keys()))
            print(barvalues)

    def handle_submit(self, sender):
        from metakernel.display import clear_output
        with open(self.results_filename, "a+") as g:
            fcntl.flock(g, fcntl.LOCK_EX)
            g.write("%s::%s::%s::%s\n" % (self.id, getpass.getuser(), datetime.datetime.today(), sender.description))
            fcntl.flock(g, fcntl.LOCK_UN)
        clear_output()
        print("Received: " + sender.description)

    def handle_next(self, sender):
        from metakernel.display import clear_output
        if self.index < len(self.questions) - 1:
            self.index += 1
            self.use_question(self.index)
            clear_output()
    
    def handle_prev(self, sender):
        from metakernel.display import clear_output
        if self.index > 0:
            self.index -= 1
            self.use_question(self.index)
            clear_output()
    
    def render(self):
        from metakernel.display import display
        display(self.top_level)

class Question(object):
    def __init__(self, id, question, options):
        self.id = id
        self.question = question
        self.options = options

class ActivityMagic(Magic):

    def line_activity(self, filename):
        """
        %activity FILENAME - run a widget-based activity 
          (poll, classroom response, clicker-like activity)

        This magic will load the JSON in the filename.

        Example:
            %activity /home/teacher/activity1
        """
        activity = Activity()
        activity.load(filename)
        activity.render()

    def cell_activity(self, filename):
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
        # Make sure results file is writable:
        activity = Activity()
        activity.load(filename)
        os.chmod(activity.results_filename, 0o777)
        # Ok, let's test it (MetaKernel):
        self.line_activity(filename)

def register_magics(kernel):
    kernel.register_magics(ActivityMagic)

def register_ipython_magics():
    from metakernel import IPythonKernel
    from metakernel.utils import add_docs
    from IPython.core.magic import register_line_magic, register_cell_magic
    kernel = IPythonKernel()
    magic = ActivityMagic(kernel)
    # Make magics callable:
    kernel.line_magics["activity"] = magic
    kernel.cell_magics["activity"] = magic

    @register_line_magic
    @add_docs(magic.line_activity.__doc__)
    def activity(line):
        kernel.call_magic("%activity " + line)

    @register_cell_magic
    @add_docs(magic.cell_activity.__doc__)
    def activity(line, cell):
        magic.code = cell
        magic.cell_activity(line)
