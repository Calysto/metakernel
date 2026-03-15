# Copyright (c) Metakernel Development Team.
# Distributed under the terms of the Modified BSD License.
from __future__ import annotations

import json as _json
import os
import random
import string
import urllib.request

from IPython.display import IFrame, Javascript

from metakernel import Magic, MetaKernel, option

urlopen = urllib.request.urlopen


def download(url: str) -> str:
    g = urlopen(url)
    return g.read().decode("utf-8")  # type: ignore[no-any-return]


class JigsawMagic(Magic):
    @option(
        "-w",
        "--workspace",
        action="store",
        default=None,
        help="use the provided name as workspace filename",
    )
    @option("-h", "--height", action="store", default=350, help="set height of iframe ")
    def line_jigsaw(
        self, language: str, workspace: str | None = None, height: int = 350
    ) -> None:
        """
        %jigsaw LANGUAGE - show visual code editor/generator

        This line magic will allow visual code editing or generation.

        Examples:
            %jigsaw Processing
            %jigsaw Python
            %jigsaw Processing --workspace workspace1 --height 600
        """
        # Copy iframe html to here (must come from same domain):
        # Make up a random workspace name:
        if workspace is None:
            workspace = "jigsaw-workspace-" + (
                "".join(
                    random.SystemRandom().choice(string.ascii_uppercase + string.digits)
                    for i in range(6)
                )
            )
        workspace_filename = workspace + ".xml"
        html_text = download(
            "https://calysto.github.io/jigsaw_v2/" + language + ".html"
        )
        html_filename = workspace + ".html"
        html_dir = os.path.dirname(html_filename)
        if html_dir:
            os.makedirs(html_dir, exist_ok=True)
        # Read any previously saved workspace XML to embed in the HTML.
        saved_xml = ""
        if os.path.isfile(workspace_filename):
            try:
                with open(workspace_filename) as f:
                    saved_xml = f.read()
            except OSError:
                pass
        # Embed saved XML into the placeholder injected by the local server HTML.
        html_text = html_text.replace(
            'window.__jigsaw_saved_xml__ = "";',
            f"window.__jigsaw_saved_xml__ = {_json.dumps(saved_xml)};",
        )
        html_text = html_text.replace("MYWORKSPACENAME", workspace_filename)
        with open(html_filename, "w") as fp:
            fp.write(html_text)
        # Parent-side message listener: handles execute/insert/clear actions
        # sent via postMessage from the jigsaw iframe.  postMessage works
        # across any origin boundary, unlike direct property access (#170).
        # Use an f-string so workspace_filename is embedded directly; the
        # script uses it to cache the owning cell at run time (while `element`
        # is available) rather than relying on event.source.frameElement, which
        # returns null for cross-origin/null-origin source frames.
        script = f"""
    // Cross-version notebook API helpers.
    // Supports classic Jupyter Notebook (IPython/Jupyter.notebook),
    // JupyterLab (window.jupyterapp/jupyterlab), and Notebook 7 (DOM + WebSocket).
    function _nb_classic() {{
        if (typeof IPython !== 'undefined' && IPython.notebook) return IPython.notebook;
        if (typeof Jupyter  !== 'undefined' && Jupyter.notebook)  return Jupyter.notebook;
        return null;
    }}
    function _nb_lab_panel() {{
        try {{
            var app = window.jupyterapp || window.jupyterlab || window.JupyterLab;
            if (!app) {{
                var _keys = Object.keys(window);
                for (var _ki = 0; _ki < _keys.length; _ki++) {{
                    var _k = _keys[_ki];
                    if (_k.toLowerCase().indexOf('jupyter') !== -1 &&
                            window[_k] && window[_k].shell) {{
                        app = window[_k]; break;
                    }}
                }}
            }}
            if (app) {{
                var w = app.shell.currentWidget;
                if (!w || !w.content) {{
                    var _it = app.shell.widgets('main');
                    var _nr;
                    while ((_nr = _it.next()) && !_nr.done) {{
                        if (_nr.value && _nr.value.content && _nr.value.content.model) {{
                            w = _nr.value; break;
                        }}
                    }}
                }}
                if (w && w.content) return w;
            }}
        }} catch(e) {{}}
        return null;
    }}
    function _nb_cells() {{
        try {{
            var nb = _nb_classic();
            if (nb) return nb.get_cells();
            var panel = _nb_lab_panel();
            if (panel) return Array.prototype.slice.call(panel.content.widgets);
        }} catch(e) {{}}
        return [];
    }}
    function _nb_output_area(cell) {{
        return cell && (cell.output_area || cell.outputArea) || null;
    }}
    function _nb_iframe_in_cell(cell, html_src) {{
        try {{
            var oa = _nb_output_area(cell);
            if (!oa) return false;
            if (oa.element)
                return oa.element.find('iframe').filter(function() {{
                    return this.src && this.src.indexOf(html_src) !== -1;
                }}).length > 0;
            if (oa.node) {{
                var frames = oa.node.querySelectorAll('iframe');
                for (var i = 0; i < frames.length; i++)
                    if (frames[i].src && frames[i].src.indexOf(html_src) !== -1) return true;
            }}
        }} catch(e) {{}}
        return false;
    }}
    function _nb_clear_stream(cell) {{
        try {{
            var oa = _nb_output_area(cell);
            if (!oa) return;
            if (oa.element) {{
                oa.element.find('.output_subarea.output_stdout, .output_subarea.output_stderr')
                    .closest('.output_area').remove();
                oa.element.find('.jigsaw-generated-code').closest('.output_area').remove();
                oa.outputs = oa.outputs.filter(function(o) {{
                    return o.output_type !== 'stream' && !(o.metadata && o.metadata.jigsaw_code);
                }});
            }} else if (oa.model) {{
                var toRemove = [];
                for (var i = 0; i < oa.model.length; i++)
                    if (oa.model.get(i).type === 'stream') toRemove.push(i);
                for (var j = toRemove.length - 1; j >= 0; j--) oa.model.remove(toRemove[j]);
            }}
        }} catch(e) {{}}
    }}
    // DOM-based helpers for Notebook 7 (when no notebook JS API is available).
    // Find the jigsaw cell's own output area element.
    function _dom_jig_cell(workspaceFilename) {{
        try {{
            var htmlSrc = workspaceFilename.replace(/\\.xml$/, '.html');
            var frames = document.querySelectorAll('iframe');
            for (var i = 0; i < frames.length; i++) {{
                if (frames[i].src && frames[i].src.indexOf(htmlSrc) !== -1) {{
                    return frames[i].closest('.jp-Cell, .cell') || null;
                }}
            }}
        }} catch(e) {{}}
        return null;
    }}
    function _dom_jig_output_area(workspaceFilename) {{
        var jigCell = _dom_jig_cell(workspaceFilename);
        return jigCell ? (jigCell.querySelector(
            '.jp-OutputArea, .jp-Cell-outputArea, .output_area') || null) : null;
    }}
    function _dom_clear_stream(oaEl) {{
        if (!oaEl) return;
        try {{
            var tagged = oaEl.querySelectorAll('.jigsaw-stream');
            for (var i = 0; i < tagged.length; i++) tagged[i].remove();
        }} catch(e) {{}}
    }}
    function _dom_clear_all(oaEl) {{
        if (!oaEl) return;
        try {{
            var tagged = oaEl.querySelectorAll('.jigsaw-stream, .jigsaw-generated-code');
            for (var i = 0; i < tagged.length; i++) tagged[i].remove();
        }} catch(e) {{}}
    }}
    function _dom_append_stream(oaEl, text) {{
        if (!oaEl) return;
        try {{
            var child = document.createElement('div');
            child.className = 'jp-OutputArea-child jigsaw-stream';
            var prompt = document.createElement('div');
            prompt.className = 'jp-OutputArea-prompt';
            var out = document.createElement('div');
            out.className = 'jp-OutputArea-output jp-RenderedText jp-mod-trusted';
            out.setAttribute('data-mime-type', 'application/vnd.jupyter.stdout');
            var pre = document.createElement('pre');
            pre.textContent = text;
            out.appendChild(pre);
            child.appendChild(prompt);
            child.appendChild(out);
            oaEl.appendChild(child);
        }} catch(e) {{}}
    }}
    // Show generated code as a copyable block in the jigsaw cell's own output area.
    // Tries the classic NB6 output_area API first; falls back to DOM manipulation for NB7.
    function _dom_show_code(workspaceFilename, code) {{
        try {{
            // NB6: use the classic OutputArea.append_output API.
            var _jCell = window._jigsaw_cells && window._jigsaw_cells[workspaceFilename];
            var _jOa = _jCell && _nb_output_area(_jCell);
            if (_jOa && _jOa.element && _jOa.append_output) {{
                // Remove any previously appended generated-code block from the DOM
                // and sync the outputs array so Jupyter stays consistent.
                _jOa.element.find('.jigsaw-generated-code').closest('.output_area').remove();
                if (_jOa.outputs) {{
                    _jOa.outputs = _jOa.outputs.filter(function(o) {{
                        return !(o.metadata && o.metadata.jigsaw_code);
                    }});
                }}
                var _safe = code.replace(/&/g, '&amp;').replace(/</g, '&lt;')
                                .replace(/>/g, '&gt;');
                var _html = '<div class="jigsaw-generated-code">' +
                    '<pre style="padding:8px;background:#f5f5f5;border-radius:4px;' +
                    'overflow:auto;margin:0;font-family:monospace;white-space:pre;">'
                    + _safe + '</pre></div>';
                _jOa.append_output({{
                    output_type: 'display_data',
                    data: {{'text/html': _html}},
                    metadata: {{jigsaw_code: true}}
                }});
                return;
            }}
            // NB7 / DOM-only fallback.
            var oaEl = _dom_jig_output_area(workspaceFilename);
            if (!oaEl) return;
            // Replace any previous generated-code block.
            var existing = oaEl.querySelectorAll('.jigsaw-generated-code');
            for (var i = 0; i < existing.length; i++) existing[i].remove();
            var child = document.createElement('div');
            child.className = 'jp-OutputArea-child jigsaw-generated-code';
            var prompt = document.createElement('div');
            prompt.className = 'jp-OutputArea-prompt';
            var out = document.createElement('div');
            out.className = 'jp-OutputArea-output jp-mod-trusted';
            var pre = document.createElement('pre');
            pre.style.cssText = 'padding:8px;background:#f5f5f5;border-radius:4px;' +
                                 'overflow:auto;margin:0;font-family:monospace;white-space:pre;';
            pre.textContent = code;
            out.appendChild(pre);
            child.appendChild(prompt);
            child.appendChild(out);
            oaEl.appendChild(child);
        }} catch(e) {{ console.log('jigsaw dom show code error:', e); }}
    }}
    function _nb_execute(code, on_output) {{
        try {{
            var nb = _nb_classic();
            if (nb) {{
                nb.kernel.execute(code, {{iopub: {{output: function(msg) {{
                    if (on_output) on_output({{
                        msg_type: msg.header.msg_type, content: msg.content
                    }});
                }}}}}}, {{silent: false}});
                return;
            }}
            var panel = _nb_lab_panel();
            if (panel) {{
                var future = panel.sessionContext.session.kernel.requestExecute({{code: code}});
                if (on_output) {{
                    future.onIOPub = function(msg) {{
                        on_output({{msg_type: msg.header.msg_type, content: msg.content}});
                    }};
                }}
                return;
            }}
        }} catch(e) {{ console.log('jigsaw execute error (nb):', e); }}
        // Final fallback: connect directly to the kernel via the Jupyter server REST API.
        _nb_ws_execute(code, on_output);
    }}
    function _nb_ws_execute(code, on_output) {{
        try {{
            var cfgEl = document.getElementById('jupyter-config-data');
            var cfg = cfgEl ? JSON.parse(cfgEl.textContent) : {{}};
            var baseUrl = (cfg.baseUrl || '/').replace(/\\/+$/, '');
            var token = cfg.token || '';
            var authHdr = token ? {{'Authorization': 'token ' + token}} : {{}};
            // Determine the notebook path from the page URL.
            var nbPath = decodeURIComponent(location.pathname);
            if (baseUrl) nbPath = nbPath.replace(baseUrl, '');
            nbPath = nbPath.replace(/^\\/(notebooks|doc|lab\\/tree)\\//, '');
            fetch(baseUrl + '/api/sessions', {{headers: authHdr}})
                .then(function(r) {{ return r.json(); }})
                .then(function(sessions) {{
                    var kernelId = null;
                    for (var i = 0; i < sessions.length; i++) {{
                        var sp = sessions[i].path;
                        if (sp === nbPath || nbPath.endsWith(sp) || nbPath.endsWith('/' + sp)) {{
                            kernelId = sessions[i].kernel.id; break;
                        }}
                    }}
                    // Single-session fallback.
                    if (!kernelId && sessions.length === 1)
                        kernelId = sessions[0].kernel.id;
                    if (!kernelId) return;
                    var wsProto = location.protocol === 'https:' ? 'wss:' : 'ws:';
                    var wsUrl = wsProto + '//' + location.host + baseUrl +
                        '/api/kernels/' + kernelId + '/channels' +
                        (token ? '?token=' + encodeURIComponent(token) : '');
                    var ws = new WebSocket(wsUrl);
                    var msgId = 'jig_' + Date.now() + '_' + Math.random().toString(36).slice(2);
                    ws.onopen = function() {{
                        ws.send(JSON.stringify({{
                            header: {{msg_id: msgId, msg_type: 'execute_request',
                                      username: '', session: msgId,
                                      date: new Date().toISOString(), version: '5.3'}},
                            parent_header: {{}}, metadata: {{}}, buffers: [],
                            content: {{code: code, silent: false, store_history: true,
                                       user_expressions: {{}}, allow_stdin: false}}
                        }}));
                    }};
                    ws.onmessage = function(evt) {{
                        try {{
                            var msg = JSON.parse(evt.data);
                            if (msg.parent_header && msg.parent_header.msg_id === msgId) {{
                                if (on_output) on_output({{msg_type: msg.header.msg_type, content: msg.content}});
                                if (msg.header.msg_type === 'execute_reply')
                                    setTimeout(function() {{ ws.close(); }}, 500);
                            }}
                        }} catch(e) {{ console.log('jigsaw ws onmessage error:', e); }}
                    }};
                    ws.onerror = function(e) {{ console.log('jigsaw ws error:', e); }};
                }})
                .catch(function(e) {{ console.log('jigsaw ws sessions error:', e); }});
        }} catch(e) {{ console.log('jigsaw ws execute error:', e); }}
    }}

    // Always replace the handler so each %jigsaw run installs the latest
    // implementation.  The outer dispatcher (registered once) delegates here.
    document.jigsaw_handle_message = function(event) {{
        var data = event.data;
        if (!data || data.type !== 'jigsaw') return;
        var cell = window._jigsaw_cells && window._jigsaw_cells[data.workspace_filename];
        // Fallback: scan all cells for the one whose output contains this iframe.
        if (!cell) {{
            try {{
                var _h = data.workspace_filename.replace(/\\.xml$/, '.html');
                var _cs = _nb_cells();
                for (var _ci = 0; _ci < _cs.length; _ci++) {{
                    if (_nb_iframe_in_cell(_cs[_ci], _h)) {{
                        cell = _cs[_ci];
                        if (!window._jigsaw_cells) window._jigsaw_cells = {{}};
                        window._jigsaw_cells[data.workspace_filename] = cell;
                        break;
                    }}
                }}
            }} catch(e) {{}}
        }}

        if (data.action === 'execute') {{
            try {{
                var save_prefix = data.save_xml
                    ? 'open(' + JSON.stringify(data.workspace_filename)
                      + ', "w").write(' + JSON.stringify(data.save_xml) + ')\\n'
                    : '';
                var _wfn = data.workspace_filename;
                // Output target: NB6 classic API if available, DOM fallback for NB7.
                var _jOa = cell && _nb_output_area(cell);
                var _domOa = (_jOa && (_jOa.element || _jOa.append_output)) ? null
                    : (_dom_jig_output_area(_wfn));
                // Clear previous run outputs (streams only, preserve IFrame/generated code).
                if (_jOa && _jOa.element) {{
                    _jOa.element.find('.output_subarea.output_stdout, .output_subarea.output_stderr')
                        .closest('.output_area').remove();
                    if (_jOa.outputs) _jOa.outputs = _jOa.outputs.filter(function(o) {{
                        return o.output_type !== 'stream';
                    }});
                }} else {{
                    _dom_clear_stream(_domOa);
                }}
                _nb_execute(save_prefix + data.code, function(out) {{
                    try {{
                        var res = null;
                        if (out.msg_type === 'stream') {{
                            res = out.content.text;
                        }} else if (out.msg_type === 'execute_result') {{
                            res = out.content.data['text/plain'];
                        }} else if (out.msg_type === 'error') {{
                            res = out.content.ename + ': ' + out.content.evalue + '\\n';
                        }}
                        if (res) {{
                            if (_jOa && _jOa.append_output) {{
                                _jOa.append_output({{output_type: 'stream',
                                    text: res.toString(), name: 'stdout'}});
                            }} else {{
                                _dom_append_stream(_domOa, res.toString());
                            }}
                        }}
                    }} catch(e) {{ console.log('jigsaw output callback error:', e); }}
                }});
            }} catch(err) {{
                console.log('jigsaw execute error:', err);
            }}
        }} else if (data.action === 'insert') {{
            try {{
                if (data.save_xml) {{
                    _nb_execute(
                        'open(' + JSON.stringify(data.workspace_filename)
                        + ', "w").write(' + JSON.stringify(data.save_xml) + ')', null);
                }}
                _dom_show_code(data.workspace_filename, data.code);
            }} catch(err) {{
                console.log('jigsaw insert error:', err);
            }}
        }} else if (data.action === 'clear') {{
            try {{
                if (cell) _nb_clear_stream(cell);
                else _dom_clear_all(_dom_jig_output_area(data.workspace_filename));
            }} catch(err) {{
                console.log('jigsaw clear error:', err);
            }}
        }}
    }};

    // Compatibility shims: old HTML files call window.parent.document.jigsaw_generate /
    // jigsaw_clear_output directly (same-origin).  Route them through the new handler
    // so both old and new iframe HTML work without regenerating the file.
    document.jigsaw_generate = function(workspace_filename, language, insert_code) {{
        try {{
            var html_src = workspace_filename.replace(/\\.xml$/, '.html');
            var iframes = document.querySelectorAll('iframe');
            for (var _i = 0; _i < iframes.length; _i++) {{
                if (iframes[_i].src.indexOf(html_src) !== -1) {{
                    var iw = iframes[_i].contentWindow;
                    var code = iw.Blockly[language].workspaceToCode(iw.workspace);
                    var xml  = iw.Blockly.Xml.domToText(iw.Blockly.Xml.workspaceToDom(iw.workspace));
                    document.jigsaw_handle_message({{data: {{
                        type: 'jigsaw',
                        action: insert_code == 1 ? 'insert' : 'execute',
                        workspace_filename: workspace_filename,
                        code: code, save_xml: xml
                    }}}});
                    break;
                }}
            }}
        }} catch(e) {{ console.log('jigsaw_generate shim error:', e); }}
    }};
    document.jigsaw_clear_output = function(workspace_filename) {{
        document.jigsaw_handle_message({{data: {{
            type: 'jigsaw', action: 'clear',
            workspace_filename: workspace_filename
        }}}});
    }};

    // Register the outer dispatcher only once; it deduplicates and delegates
    // to document.jigsaw_handle_message so updates above take effect immediately.
    if (document.jigsaw_listener_set === undefined) {{
        document.jigsaw_listener_set = true;
        var _jigsaw_seen = {{}};
        window.addEventListener('message', function(event) {{
            var data = event.data;
            if (!data || data.type !== 'jigsaw') return;
            // Deduplicate: the iframe sends to both parent and top.
            if (data.msg_id) {{
                if (_jigsaw_seen[data.msg_id]) return;
                _jigsaw_seen[data.msg_id] = true;
            }}
            if (document.jigsaw_handle_message) {{
                document.jigsaw_handle_message(event);
            }}
        }});
    }}

    // Cache the owning cell now, while `element` is in scope, so the message
    // handler above can find it later without frameElement (which is null for
    // cross-origin source frames).
    try {{
        if (!window._jigsaw_cells) window._jigsaw_cells = {{}};
        var _wf = {_json.dumps(workspace_filename)};
        var _el = element && element[0];
        while (_el && (!_el.className || _el.className.indexOf('cell') === -1)) {{
            _el = _el.parentNode;
        }}
        if (_el) {{
            var _cells = _nb_cells();
            for (var _i = 0; _i < _cells.length; _i++) {{
                // Classic notebook: cell.element[0]; JupyterLab: cell.node
                var _cn = (_cells[_i].element && _cells[_i].element[0]) || _cells[_i].node;
                if (_cn === _el) {{
                    window._jigsaw_cells[_wf] = _cells[_i];
                    break;
                }}
            }}
        }}
    }} catch(e) {{}}
"""
        self.kernel.Display(Javascript(script))  # type: ignore[no-untyped-call]
        self.kernel.Display(IFrame(html_filename, width="100%", height=height))


def register_magics(kernel: MetaKernel) -> None:
    kernel.register_magics(JigsawMagic)


def register_ipython_magics() -> None:
    from metakernel import IPythonKernel
    from metakernel.magic import register_line_magic

    kernel = IPythonKernel()
    magic = JigsawMagic(kernel)
    # Make magics callable:
    kernel.line_magics["jigsaw"] = magic

    @register_line_magic
    def jigsaw(line: str) -> None:
        """
        Use the Jigsaw code visualizer and generator.
        """
        kernel.call_magic("%jigsaw " + line)
