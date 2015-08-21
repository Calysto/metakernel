# -*- coding: utf-8 -*-

# Copyright (c) Metakernel Development Team.
# Distributed under the terms of the Modified BSD License.


from metakernel import Magic
from IPython.display import HTML, Javascript

class DebugMagic(Magic):

    def cell_debug(self, dummy):
        """
        %%debug - step through the code expression by expression

        This cell magic will step through the code in the cell,
        if the kernel supports debugging.

        Example:
            %%debug

            (define x 1)
        """

        html_code = """
<style type="text/css">
      .breakpoints {width: 1.5em;}
      .styled-background { background-color: #ff7; }
</style>

<div class="animation" align="left" width="400">
  <button onclick="step()">Step</button>
  <button onclick="play()">Play</button>
  <button onclick="pause()">Pause</button>
  <button onclick="stop()">Stop</button>
  <button onclick="clear_breakpoints()">Clear Breakpoints</button>
  <button onclick="reset()">Reset</button><br/>
  Speed: <input type="range" id="speed" min="1" max="100"/>
  Inspect: <input type="text" id="inspect" onkeydown="if (event.keyCode == 13) inspector()"/>
  <table width="100%">
  <tr>
    <td width="50%" style="vertical-align: top"><div id="result_stream"/></td>
    <td width="50%" style="vertical-align: top"><div id="result_output"/></td>
  </tr>
  </table>
</div>

<script>

function inspector() {
    var v = document.getElementById("inspect").value;
    document.getElementById("inspect").value = "";
    var msg_id = kernel.execute("~~META~~: inspect " + v,
                                callbacks,
                                {silent: false});
}

function clear_breakpoints() {
    for (var n = 0 ; n < cell.code_mirror.doc.size; n++) {
        cell.code_mirror.setGutterMarker(n, "breakpoints", null);
    }
}

function makeMarker() {
    var marker = document.createElement("div");
    marker.style.color = "#822";
    marker.innerHTML = "●";
    return marker;
}

function breakpoint_q(line) {
    var info = cell.code_mirror.lineInfo(line - 1);
    return (info && info.gutterMarkers != null);
}

var cell = IPython.notebook.get_selected_cell();
if (cell) {
    // The following can be replaced once get_prev_cell is fixed
    // see https://github.com/ipython/ipython/pull/6565
    var index = IPython.notebook.find_cell_index(cell);
    cell = IPython.notebook.get_cell(index - 1);
    cell.code_mirror.setOption("lineNumbers", true);
    if (cell.code_mirror.getOption("gutters").length < 2) {
        cell.code_mirror.setOption("gutters", ["CodeMirror-linenumbers", "breakpoints"]);
        cell.code_mirror.refresh();
        cell.code_mirror.on("gutterClick", function(cm, n) {
          var info = cm.lineInfo(n);
          cm.setGutterMarker(n, "breakpoints", info.gutterMarkers ? null : makeMarker());
        });
    }
}

var mt;
var i;

function highlight(cell, data) {
    if (cell) {
        var line1 = data[0];
        var col1 = data[1];
        var line2 = data[2];
        var col2 = data[3];
        if (mt) {
            mt.clear();
        }
        mt = cell.code_mirror.markText({line: line1 - 1, ch: col1 - 1},
                                       {line: line2 - 1, ch: col2 },
                                       {className: "styled-background"});
    }
}

var running = false;  // is it running?
var timer = null;
var kernel = IPython.notebook.kernel;

function handle_output(out){
    var res = null;
    var data = null;
    if (out.msg_type == "stream") {
        res = out.content.text;
        document.getElementById("result_stream").innerText = res.toString() + document.getElementById("result_stream").innerText;
    } else if (out.msg_type === "pyout") {
        // if output is a python object
        res = out.content.data["text/plain"];
        document.getElementById("result_stream").innerText = res.toString() + document.getElementById("result_stream").innerText;
    } else if (out.msg_type == "pyerr") {
        // if output is a python error
        res = out.content.data["text/plain"];
        document.getElementById("result_stream").innerText = res.toString() + document.getElementById("result_stream").innerText;
    } else if (out.msg_type == "execute_result") {
        var str = out.content.data["text/plain"];
        if (str.indexOf("\\"highlight: ") >= 0) { // is a highlight response:
            data = JSON.parse(str.substring(12, str.length - 1));
            var speed = Number(document.getElementById("speed").value);
            if (data) {
                var breakp = breakpoint_q(data[0]);
                if (speed < 100 || !running || breakp) { // max_speed
                    highlight(cell, data);
                }
            }
            if (running) {
                if (data && breakpoint_q(data[0])) {
                    pause();
                } else {
                    timer = setTimeout(step, 2000/speed);
                }
            }
        } else { // display result
            res = str;
            if (res.indexOf("u") == 0)
                res = res.substring(2, res.length - 1) + "\\n";
            if (res) {
                document.getElementById("result_output").innerText = res.toString() + document.getElementById("result_output").innerText;
            }
        }
    } else {
        // if output is something we haven't thought of
        res = out.toString();
        document.getElementById("result_stream").innerText = res.toString() + document.getElementById("result_stream").innerText;
    }
}

var callbacks = { 'iopub' : {'output' : handle_output}};

function pause() {
    running = false;
    document.getElementById("result_output").innerText = "Pause\\n" + document.getElementById("result_output").innerText;
    if (timer) {
        clearInterval(timer);
        timer = null;
    }
}

function play() {
    pause();
    running = true;
    step();
}

function step() {
    var msg_id = kernel.execute("~~META~~: step",
                                callbacks,
                                {silent: false});
}

function stop() {
    pause();
    if (mt) {
        mt.clear();
    }
    var msg_id = kernel.execute("~~META~~: stop",
                                callbacks,
                                {silent: false});
}

function reset() {
    stop();
    document.getElementById("result_output").innerText = "";
    document.getElementById("result_stream").innerText = "";
    var msg_id = kernel.execute("~~META~~: reset",
                                callbacks,
                                {silent: false});
}

</script>
"""
        import time
        html = HTML(html_code)
        self.kernel.Display(html)
        time.sleep(.1)
        data = self.kernel.initialize_debug("\n" + self.code) ## add a line so line numbers will be correct
        time.sleep(.1)
        if data.startswith("highlight: "):
            self.kernel.Display(Javascript("highlight(cell, %s);" % data[11:]))
        time.sleep(.1)
        self.evaluate = False

def register_magics(kernel):
    kernel.register_magics(DebugMagic)
