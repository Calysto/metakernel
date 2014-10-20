import re
import os

IDENTIFIER_REGEX = r'[^\d\W]\w*'
FUNC_CALL_REGEX = r'([^\d\W][\w\.]*)\([^\)\()]*\Z'
MAGIC_PREFIXES = dict(magic='%', shell='!', help='?')
HELP_SUFFIX = '?'


class Parser(object):

    """Parse an input buffer using language-specific regexes."""

    def __init__(self, identifier_regex=IDENTIFIER_REGEX,
                 function_call_regex=FUNC_CALL_REGEX,
                 magic_prefixes=MAGIC_PREFIXES,
                 help_suffix=HELP_SUFFIX):
        """Set up the regexes and magic characters.

        Parameters
        ----------
        identifier_regex : str
            Regex for a valid identifier in the desired language.
        function_call_regex : str
            Regex for a function call that we are in the midst of.
        magic_prefixes : dict
            Map of magic types to the prefix characters
        help_suffix : str
            Character to use for help suffix.
        """
        self.func_call_regex = re.compile(function_call_regex + '\Z',
                                          re.UNICODE)
        default_regex = r'[^\d\W]\w*'
        self.id_regex = re.compile(r'(\{0}+{1}\Z|{2}\Z|\Z)'.format(
            magic_prefixes['magic'], default_regex,
            identifier_regex), re.UNICODE)

        self.magic_regex = '|'.join([default_regex, identifier_regex])

        full_path_regex = r'([\w/\.~][^\'"]*)\Z'
        self.full_path_regex = re.compile(r'[\'"]{0}|{0}'.format(
            full_path_regex), re.UNICODE)
        single_path_regex = r'([\w/\.~][^ ]*)\Z'
        self.single_path_regex = re.compile(single_path_regex, re.UNICODE)

        self.magic_prefixes = magic_prefixes
        self.help_suffix = help_suffix

    def parse_code(self, code, start=0, end=-1):
        """Parse an input buffer, extracting relevant information.

        Parameters
        ----------
        code : str
            Input buffer.
        start : int, optional
            The start location in the buffer.
        end : int, optional
            The end location in the buffer.

        Returns
        -------
        info : dict
            Metadata about the parsed buffer with the following items:
            magic : dict, Magic info, see `_parse_magic`.
            lines : int, Number of lines in code
            line_num : int, Current line Number
            line : str, Current line of text
            column : int, Index in current line of text
            obj : str, Matched object at the end of text
            full_obj : str, Obj plus valid text to the right of cursor
            help_obj : str, Full_obj or a function call.
            start : int, Start index in buffer.
            end: int, End index in buffer
            pre: str, Text before start
            mid : str, Text between start and end
            post : str, Text after end
            path_matches : list, File system path matches for text
           """
        if end == -1:
            end = len(code)
        end = min(len(code), end)

        start = min(start, end)
        start = max(0, start)

        info = dict(code=code, magic=dict())

        info['magic'] = self._parse_magic(code[:end])

        info['lines'] = lines = code[:end].splitlines()
        info['line_num'] = line_num = len(lines)

        info['line'] = line = lines[-1]
        info['column'] = col = len(lines[-1])

        obj = re.search(self.id_regex, line).group()

        full_obj = obj

        if obj:
            full_line = code.splitlines()[line_num - 1]
            rest = full_line[col:]
            match = re.match(self.id_regex, rest)
            if match:
                full_obj = obj + match.group()

        func_call = re.search(self.func_call_regex, line)
        if func_call and not obj:
            info['help_obj'] = func_call.groups()[0]
            info['help_col'] = line.index(obj) + len(obj)
            info['help_pos'] = end - len(line) + col
        else:
            info['help_obj'] = full_obj
            info['help_col'] = col
            info['help_pos'] = end

        info['obj'] = obj
        info['full_obj'] = full_obj

        info['start'] = end - len(obj)
        info['end'] = end
        info['pre'] = code[:start]
        info['mid'] = code[start: end]
        info['post'] = code[end:]

        info['path_matches'] = self._get_path_matches(info)
        return info

    def _parse_magic(self, code, pinned=True):
        """Find and parse magic calls in the buffer.

        Parameters
        ----------
        code : str
            Input text.
        pinned : bool, optional
            Whether the magic must occur at the start of the line.

        Notes
        -----
        - magics can be nested
        - magics return strings

        - help magic is special
        -- it can be at the end of the line and takes precidence
        -- no code is executed when a help magic is present

        Examples
        --------
        >>> a = ! ls -l
        >>> %time %python a = %paste

        Returns
        -------
        info : dict
            Information about the magic with the following items:
            name : str, Name of magic
            type : str, Type of magic {'line', 'cell', 'sticky'}
            index : str, Index of end of magic in text
            rest : str, Text after index
            args : str, First line of "rest", the argument to the magic
            code : str, Rest of lines of "rest", the cell block for the magic
            arg_magic: dict, Information about a magic with an argument,
                             can be nested
            code_magic: dict, Information about a magic within code,
                              can be nested.

        """
        info = {}
        pre_magics = {}
        for (name, prefix) in self.magic_prefixes.items():
            if name == 'shell':
                regex = r' *(\%s+)( *)(%s)' % (prefix, self.magic_regex)
            else:
                regex = r' *(\%s+)(%s)' % (prefix, self.magic_regex)
            if pinned:
                regex = r'\A%s' % regex
            match = re.search(regex, code, re.UNICODE)
            if match:
                pre_magics[name] = match.groups()

        types = ['none', 'line', 'cell', 'sticky']

        if 'help' in pre_magics:
            info['name'] = 'help'
            pre, obj = pre_magics['help']
            info['type'] = types[len(pre)]
            info['index'] = code.index(pre + obj)

        elif 'magic' in pre_magics:
            pre, obj = pre_magics['magic']
            info['type'] = types[len(pre)]
            info['name'] = obj
            info['index'] = code.index(pre + obj) + len(pre + obj)

        elif 'shell' in pre_magics:
            info['name'] = 'shell'
            pre, ws, obj = pre_magics['shell']
            info['type'] = types[len(pre)]
            info['index'] = code.index(pre + ws + obj) + len(pre + ws)

        elif code.rstrip().endswith(self.help_suffix):
            info['name'] = 'help'
            nchars = code[-3:].count(self.help_suffix)
            info['type'] = types[nchars]
            info['index'] = len(code) - nchars
        else:
            return info

        info['rest'] = code[info['index']:].strip()

        if info['rest']:
            lines = info['rest'].splitlines()
            info['args'] = lines[0].strip()
            info['code'] = '\n'.join(lines[1:])
             # look for other magics in the rest - recursive
            regex = r'(\%s+)(%s)' % (self.magic_prefixes['magic'],
                                     self.magic_regex)
            arg_match = re.search(regex, lines[0])
            if arg_match:
                info['arg_magic'] = self._parse_magic(info['rest'], False)
            code_match = re.search(regex, info['code'])
            if code_match:
                info['code_magic'] = self._parse_magic(info['code'])
        else:
            info['args'] = ''
            info['code'] = ''
        return info

    def _get_path_matches(self, info):
        """Get a list of matching file system paths.

        There are 3 types of matches:
        - start character and no quotes
        - quote mark followed by start character
        - single string of text with no spaces
        """
        line = info['line']
        obj = info['obj']

        def get_regex_matches(regex):
            matches = []
            path = re.findall(regex, line)
            if path:
                path = ''.join(path[0])
                matches = _complete_path(path)
                if len(path) > len(obj) and not path == '.':
                    matches = [m[len(path) - len(obj):] for m in matches]
                elif path == '.':
                    matches = [m[1:] for m in matches if m.startswith('.')]
            return [m.strip() for m in matches if not m.strip() == obj]

        matches = get_regex_matches(self.full_path_regex)
        matches += get_regex_matches(self.single_path_regex)

        return list(set(matches))


def _listdir(root):
    "List directory 'root' appending the path separator to subdirs."
    res = []
    root = os.path.expanduser(root)
    try:
        for name in os.listdir(root):
            path = os.path.join(root, name)
            if os.path.isdir(path):
                name += os.sep
            res.append(name)
    except:
        pass  # no need to report invalid paths
    return res


def _complete_path(path=None):
    """Perform completion of filesystem path.
    http://stackoverflow.com/questions/5637124/tab-completion-in-pythons-raw-input
    """
    if not path or path == '.':
        return _listdir('.')
    dirname, rest = os.path.split(path)
    tmp = dirname if dirname else '.'
    res = [os.path.join(dirname, p) for p in _listdir(tmp)
           if p.startswith(rest)]
    # more than one match, or single match which does not exist (typo)
    if len(res) > 1 or not os.path.exists(path):
        return res
    # resolved to a single directory, so return list of files below it
    if os.path.isdir(path):
        return [os.path.join(path, p) for p in _listdir(path)]
    # exact file match terminates this completion
    return [path + ' ']
