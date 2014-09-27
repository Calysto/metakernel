# -*- coding: utf-8 -*-

# Copyright (c) Calico Development Team.
# Distributed under the terms of the Modified BSD License.
# http://calicoproject.org/

from jupyter_kernel import Magic
from IPython.display import HTML, Javascript

class DebugMagic(Magic):

    def cell_debug(self):
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
  Speed: <input type="range" id="speed" min="1" max="10"/>
  <div id="result_output"/>
</div>

<script>

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
    return (info.gutterMarkers != null);
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
     // if output is a print statement
    if (out.msg_type == "stream") {
        res = out.content.data;
    } else if (out.msg_type === "pyout") {
        // if output is a python object
        res = out.content.data["text/plain"];
    } else if (out.msg_type == "pyerr") {
        // if output is a python error
        res = out.content.data["text/plain"];
    } else if (out.msg_type == "execute_result") {
        var str = out.content.data["text/plain"];
        data = JSON.parse(str.substring(1, str.length - 1));
        if (data) {
            //console.log(data);
            //console.log(breakpoint_q(data[0]));
            highlight(cell, data);
        }
        if (running) {
            if (data && breakpoint_q(data[0])) {
                //console.log("paused!");
                pause();
            } else {
                //console.log("continue!");
                
                var speed = Number(document.getElementById("speed").value);
                timer = setTimeout(step, 1000/speed);
            }
        }
        res = "";
    } else {
        // if output is something we haven't thought of
        res = out.toString();   
    }
    if (res) {
        document.getElementById("result_output").innerText = res.toString() + document.getElementById("result_output").innerText;
    }
}

var callbacks = { 'iopub' : {'output' : handle_output}};

function pause() {
    running = false;
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
}

function reset() {
    stop();
    document.getElementById("result_output").innerText = "";
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
        try:
            self.kernel.Display(Javascript("highlight(cell, %s);" % data))
        except Exception as e:
            self.kernel.Print(str(e))
        time.sleep(.1)
        self.evaluate = False

def register_magics(kernel):
    kernel.register_magics(DebugMagic)
