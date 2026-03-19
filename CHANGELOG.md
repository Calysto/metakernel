# Changelog Entries

## 1.0.1rc1

## 📦 Uncategorized

- Refactor tests workflow
   - PR: #393
- Add a workflow to update pre-commit versions and improve validate-pyproject
   - PR: #394
- Refactor CI into composite actions and add release/publish workflows
   - PR: #395
- Ensure Consistent use of actions/checkout
   - PR: #396
- Fix release action by installing uv
   - PR: #397
- Clean up release action
   - PR: #398

## 1.0.0rc1

([Full Changelog](https://github.com/Calysto/metakernel/compare/v1.0.0rc0...161618c81c69279785c341cf6eab449a244e580e))

### Maintenance and upkeep improvements

- Bump minimum dependency versions to releases from 2023 or later [#392](https://github.com/Calysto/metakernel/pull/392) ([@blink1073](https://github.com/blink1073), [@claude](https://github.com/claude))
- Add validate-pyproject lint hook and switch to prek [#390](https://github.com/Calysto/metakernel/pull/390) ([@blink1073](https://github.com/blink1073))
- Bump zizmorcore/zizmor-action from 0.5.0 to 0.5.2 in the actions group [#389](https://github.com/Calysto/metakernel/pull/389) ([@blink1073](https://github.com/blink1073))

### Contributors to this release

The following people contributed discussions, new ideas, code and documentation contributions, and review.
See [our definition of contributors](https://github-activity.readthedocs.io/en/latest/use/#how-does-this-tool-define-contributions-in-the-reports).

([GitHub contributors page for this release](https://github.com/Calysto/metakernel/graphs/contributors?from=2026-03-16&to=2026-03-17&type=c))

@blink1073 ([activity](https://github.com/search?q=repo%3ACalysto%2Fmetakernel+involves%3Ablink1073+updated%3A2026-03-16..2026-03-17&type=Issues)) | @claude ([activity](https://github.com/search?q=repo%3ACalysto%2Fmetakernel+involves%3Aclaude+updated%3A2026-03-16..2026-03-17&type=Issues))

## 1.0.0rc0

([Full Changelog](https://github.com/Calysto/metakernel/compare/v0.32.0...873b53e3a709278b91c75eaeeb38497490c28eb0))

### Enhancements made

- Use pre-fixed jigsaw_v2 HTML and expand test coverage [#385](https://github.com/Calysto/metakernel/pull/385) ([@blink1073](https://github.com/blink1073))
- Add schedule_display_output for pushing messages to frontends outside execution [#382](https://github.com/Calysto/metakernel/pull/382) ([@blink1073](https://github.com/blink1073))
- Add kernel_javascript support to write kernel.js during kernelspec install [#378](https://github.com/Calysto/metakernel/pull/378) ([@blink1073](https://github.com/blink1073))
- Add args parameter to REPLWrapper to support executable paths with spaces [#377](https://github.com/Calysto/metakernel/pull/377) ([@blink1073](https://github.com/blink1073))
- Fix %jigsaw cross-origin errors and restore button functionality [#375](https://github.com/Calysto/metakernel/pull/375) ([@blink1073](https://github.com/blink1073))
- Add DisplayData() for raw MIME bundle display [#368](https://github.com/Calysto/metakernel/pull/368) ([@blink1073](https://github.com/blink1073), [@codecov-commenter](https://github.com/codecov-commenter))
- Add %lsmagic -v for magic load debugging [#366](https://github.com/Calysto/metakernel/pull/366) ([@blink1073](https://github.com/blink1073), [@codecov-commenter](https://github.com/codecov-commenter))
- Add Binder support [#361](https://github.com/Calysto/metakernel/pull/361) ([@blink1073](https://github.com/blink1073), [@codecov-commenter](https://github.com/codecov-commenter))

### Bugs fixed

- Fix test_magics Windows CI failure: use %shell instead of %%shell [#388](https://github.com/Calysto/metakernel/pull/388) ([@blink1073](https://github.com/blink1073))
- Fix %px/%px errors not surfacing as proper error messages (closes #61) [#380](https://github.com/Calysto/metakernel/pull/380) ([@blink1073](https://github.com/blink1073))
- Fix %%tutor loading all iframes immediately (closes #68) [#379](https://github.com/Calysto/metakernel/pull/379) ([@blink1073](https://github.com/blink1073))
- Fix %jigsaw failing to save files when workspace path includes a subdirectory [#374](https://github.com/Calysto/metakernel/pull/374) ([@blink1073](https://github.com/blink1073), [@codecov-commenter](https://github.com/codecov-commenter))
- Add encoding parameter to REPLWrapper to fix startup hang on Windows [#373](https://github.com/Calysto/metakernel/pull/373) ([@blink1073](https://github.com/blink1073), [@codecov-commenter](https://github.com/codecov-commenter))
- Fix execute_reply reporting 'ok' status when do_execute_direct raises [#372](https://github.com/Calysto/metakernel/pull/372) ([@blink1073](https://github.com/blink1073), [@codecov-commenter](https://github.com/codecov-commenter))
- Fix %%python display() routing to wrong kernel [#371](https://github.com/Calysto/metakernel/pull/371) ([@blink1073](https://github.com/blink1073), [@codecov-commenter](https://github.com/codecov-commenter))
- Fix activity magic showing wrong results on repeated clicks [#370](https://github.com/Calysto/metakernel/pull/370) ([@blink1073](https://github.com/blink1073), [@claude](https://github.com/claude), [@codecov-commenter](https://github.com/codecov-commenter))
- Fix prompt_change_cmd storing unformatted template [#369](https://github.com/Calysto/metakernel/pull/369) ([@blink1073](https://github.com/blink1073), [@claude](https://github.com/claude), [@codecov-commenter](https://github.com/codecov-commenter))
- Fix ipywidgets Output context manager not working with MetaKernel [#365](https://github.com/Calysto/metakernel/pull/365) ([@blink1073](https://github.com/blink1073), [@codecov-commenter](https://github.com/codecov-commenter))
- Fix shell_magic load failure on Windows by lazy-initializing shell process [#364](https://github.com/Calysto/metakernel/pull/364) ([@blink1073](https://github.com/blink1073), [@codecov-commenter](https://github.com/codecov-commenter))
- Wait for any output instead of default prompt on startup [#357](https://github.com/Calysto/metakernel/pull/357) ([@blink1073](https://github.com/blink1073), [@codecov-commenter](https://github.com/codecov-commenter))
- Clear PS0 in bash REPL wrapper [#356](https://github.com/Calysto/metakernel/pull/356) ([@ellert](https://github.com/ellert), [@blink1073](https://github.com/blink1073), [@codecov-commenter](https://github.com/codecov-commenter))

### Maintenance and upkeep improvements

- Add GitHub issue templates for bug reports and feature requests [#384](https://github.com/Calysto/metakernel/pull/384) ([@blink1073](https://github.com/blink1073))
- Add ruff S (flake8-bandit) security checks [#383](https://github.com/Calysto/metakernel/pull/383) ([@blink1073](https://github.com/blink1073))
- Restructure CI coverage uploads and add codecov.yml [#381](https://github.com/Calysto/metakernel/pull/381) ([@blink1073](https://github.com/blink1073))
- Add GitHub pull request template [#376](https://github.com/Calysto/metakernel/pull/376) ([@blink1073](https://github.com/blink1073))
- Add example notebook CI [#363](https://github.com/Calysto/metakernel/pull/363) ([@blink1073](https://github.com/blink1073), [@codecov-commenter](https://github.com/codecov-commenter))
- Bump tornado from 6.5.4 to 6.5.5 [#360](https://github.com/Calysto/metakernel/pull/360) ([@blink1073](https://github.com/blink1073))
- Remove virtualenv pins from example kernels [#355](https://github.com/Calysto/metakernel/pull/355) ([@blink1073](https://github.com/blink1073), [@codecov-commenter](https://github.com/codecov-commenter), [@hroncok](https://github.com/hroncok))

### Documentation improvements

- Add JupyterHub deployment docs and cross-origin regression tests (issue #196) [#386](https://github.com/Calysto/metakernel/pull/386) ([@blink1073](https://github.com/blink1073))
- Include magics README in docs [#367](https://github.com/Calysto/metakernel/pull/367) ([@blink1073](https://github.com/blink1073), [@codecov-commenter](https://github.com/codecov-commenter))
- Add debugging section to new kernel docs [#362](https://github.com/Calysto/metakernel/pull/362) ([@blink1073](https://github.com/blink1073), [@codecov-commenter](https://github.com/codecov-commenter))
- Switch documentation from Sphinx to MkDocs [#358](https://github.com/Calysto/metakernel/pull/358) ([@blink1073](https://github.com/blink1073), [@codecov-commenter](https://github.com/codecov-commenter))

### Contributors to this release

The following people contributed discussions, new ideas, code and documentation contributions, and review.
See [our definition of contributors](https://github-activity.readthedocs.io/en/latest/use/#how-does-this-tool-define-contributions-in-the-reports).

([GitHub contributors page for this release](https://github.com/Calysto/metakernel/graphs/contributors?from=2026-03-10&to=2026-03-16&type=c))

@blink1073 ([activity](https://github.com/search?q=repo%3ACalysto%2Fmetakernel+involves%3Ablink1073+updated%3A2026-03-10..2026-03-16&type=Issues)) | @claude ([activity](https://github.com/search?q=repo%3ACalysto%2Fmetakernel+involves%3Aclaude+updated%3A2026-03-10..2026-03-16&type=Issues)) | @codecov-commenter ([activity](https://github.com/search?q=repo%3ACalysto%2Fmetakernel+involves%3Acodecov-commenter+updated%3A2026-03-10..2026-03-16&type=Issues)) | @ellert ([activity](https://github.com/search?q=repo%3ACalysto%2Fmetakernel+involves%3Aellert+updated%3A2026-03-10..2026-03-16&type=Issues)) | @hroncok ([activity](https://github.com/search?q=repo%3ACalysto%2Fmetakernel+involves%3Ahroncok+updated%3A2026-03-10..2026-03-16&type=Issues))

## 0.32.0

([Full Changelog](https://github.com/Calysto/metakernel/compare/v0.31.0...88ea17cb2c596d745713cea0f875346abca468c0))

### Enhancements made

- Add --display-name option to kernel install subcommand [#353](https://github.com/Calysto/metakernel/pull/353) ([@blink1073](https://github.com/blink1073), [@codecov-commenter](https://github.com/codecov-commenter))

### Bugs fixed

- Fix %matplotlib inline raising ValueError [#352](https://github.com/Calysto/metakernel/pull/352) ([@blink1073](https://github.com/blink1073), [@codecov-commenter](https://github.com/codecov-commenter))
- Fix soft continuation in REPLWrapper.run_command() [#350](https://github.com/Calysto/metakernel/pull/350) ([@blink1073](https://github.com/blink1073), [@codecov-commenter](https://github.com/codecov-commenter))
- Fix python helper function [#349](https://github.com/Calysto/metakernel/pull/349) ([@blink1073](https://github.com/blink1073), [@codecov-commenter](https://github.com/codecov-commenter), [@ellert](https://github.com/ellert))

### Maintenance and upkeep improvements

- Remove virtualenv pin [#354](https://github.com/Calysto/metakernel/pull/354) ([@blink1073](https://github.com/blink1073), [@codecov-commenter](https://github.com/codecov-commenter))
- Add branch-coverage tests for Activity.handle_results() and REPLWrapper [#348](https://github.com/Calysto/metakernel/pull/348) ([@blink1073](https://github.com/blink1073), [@claude](https://github.com/claude), [@codecov-commenter](https://github.com/codecov-commenter))
- Finish typing for tests [#347](https://github.com/Calysto/metakernel/pull/347) ([@blink1073](https://github.com/blink1073), [@codecov-commenter](https://github.com/codecov-commenter))
- Add type annotations to test helpers and resolve mypy errors [#346](https://github.com/Calysto/metakernel/pull/346) ([@blink1073](https://github.com/blink1073), [@codecov-commenter](https://github.com/codecov-commenter))
- Add typed wrappers for register_line/cell_magic and annotate all magics [#345](https://github.com/Calysto/metakernel/pull/345) ([@blink1073](https://github.com/blink1073), [@codecov-commenter](https://github.com/codecov-commenter))
- Adopt zizmor for GitHub Actions static analysis [#344](https://github.com/Calysto/metakernel/pull/344) ([@blink1073](https://github.com/blink1073), [@codecov-commenter](https://github.com/codecov-commenter))
- Fix testpaths for newer pytest versions [#343](https://github.com/Calysto/metakernel/pull/343) ([@ellert](https://github.com/ellert), [@blink1073](https://github.com/blink1073), [@codecov-commenter](https://github.com/codecov-commenter))
- Add typed get_ipython() helper and resolve all mypy errors in magics [#341](https://github.com/Calysto/metakernel/pull/341) ([@blink1073](https://github.com/blink1073), [@claude](https://github.com/claude), [@codecov-commenter](https://github.com/codecov-commenter))

### Documentation improvements

- Add new_magic.rst: guide for creating custom magics [#351](https://github.com/Calysto/metakernel/pull/351) ([@blink1073](https://github.com/blink1073), [@codecov-commenter](https://github.com/codecov-commenter))

### Contributors to this release

The following people contributed discussions, new ideas, code and documentation contributions, and review.
See [our definition of contributors](https://github-activity.readthedocs.io/en/latest/use/#how-does-this-tool-define-contributions-in-the-reports).

([GitHub contributors page for this release](https://github.com/Calysto/metakernel/graphs/contributors?from=2026-03-03&to=2026-03-10&type=c))

@blink1073 ([activity](https://github.com/search?q=repo%3ACalysto%2Fmetakernel+involves%3Ablink1073+updated%3A2026-03-03..2026-03-10&type=Issues)) | @claude ([activity](https://github.com/search?q=repo%3ACalysto%2Fmetakernel+involves%3Aclaude+updated%3A2026-03-03..2026-03-10&type=Issues)) | @codecov-commenter ([activity](https://github.com/search?q=repo%3ACalysto%2Fmetakernel+involves%3Acodecov-commenter+updated%3A2026-03-03..2026-03-10&type=Issues)) | @ellert ([activity](https://github.com/search?q=repo%3ACalysto%2Fmetakernel+involves%3Aellert+updated%3A2026-03-03..2026-03-10&type=Issues))

## 0.31.0

([Full Changelog](https://github.com/Calysto/metakernel/compare/v0.30.4...29bf8af248a61276d8ff3c4903e32ce274c16d47))

### Enhancements made

- Convert top-level kernel methods to async [#338](https://github.com/Calysto/metakernel/pull/338) ([@blink1073](https://github.com/blink1073), [@codecov-commenter](https://github.com/codecov-commenter))
- Support async do_execute_direct [#337](https://github.com/Calysto/metakernel/pull/337) ([@blink1073](https://github.com/blink1073), [@codecov-commenter](https://github.com/codecov-commenter))
- Use hatch build hook to bundle kernelspecs in wheels [#302](https://github.com/Calysto/metakernel/pull/302) ([@blink1073](https://github.com/blink1073))
- Add type annotations and mypy support [#300](https://github.com/Calysto/metakernel/pull/300) ([@blink1073](https://github.com/blink1073))

### Bugs fixed

- Use IPython DisplayFormatter directly for missing _repr_mimebundle_ [#299](https://github.com/Calysto/metakernel/pull/299) ([@blink1073](https://github.com/blink1073), [@morlic](https://github.com/morlic))

### Maintenance and upkeep improvements

- Update dependabot config [#335](https://github.com/Calysto/metakernel/pull/335) ([@blink1073](https://github.com/blink1073), [@codecov-commenter](https://github.com/codecov-commenter))
- Remove PY3 compatibility shim [#334](https://github.com/Calysto/metakernel/pull/334) ([@blink1073](https://github.com/blink1073), [@codecov-commenter](https://github.com/codecov-commenter))
- Add no-op u() function for backwards compatibility [#333](https://github.com/Calysto/metakernel/pull/333) ([@blink1073](https://github.com/blink1073), [@codecov-commenter](https://github.com/codecov-commenter))
- Add Python 3.14t free-threading CI on Ubuntu [#332](https://github.com/Calysto/metakernel/pull/332) ([@blink1073](https://github.com/blink1073), [@codecov-commenter](https://github.com/codecov-commenter))
- Add tests for core MetaKernel methods [#331](https://github.com/Calysto/metakernel/pull/331) ([@blink1073](https://github.com/blink1073), [@codecov-commenter](https://github.com/codecov-commenter))
- Add tests for include, install, kernel, and macro magics [#330](https://github.com/Calysto/metakernel/pull/330) ([@blink1073](https://github.com/blink1073), [@codecov-commenter](https://github.com/codecov-commenter))
- Add tests for Activity class methods and ParallelMagic methods [#329](https://github.com/Calysto/metakernel/pull/329) ([@blink1073](https://github.com/blink1073), [@claude](https://github.com/claude), [@codecov-commenter](https://github.com/codecov-commenter))
- Consolidate Windows CI into main test matrix [#328](https://github.com/Calysto/metakernel/pull/328) ([@blink1073](https://github.com/blink1073), [@claude](https://github.com/claude), [@codecov-commenter](https://github.com/codecov-commenter))
- Add tests for Error_display, do_execute_meta, get_magic_args, display, and process_metakernel classes [#327](https://github.com/Calysto/metakernel/pull/327) ([@blink1073](https://github.com/blink1073), [@codecov-commenter](https://github.com/codecov-commenter))
- Add tests for IPythonKernel, register_ipython_magics, and MetaKernelApp [#326](https://github.com/Calysto/metakernel/pull/326) ([@blink1073](https://github.com/blink1073), [@codecov-commenter](https://github.com/codecov-commenter))
- Add test module for tutor magic [#324](https://github.com/Calysto/metakernel/pull/324) ([@blink1073](https://github.com/blink1073), [@codecov-commenter](https://github.com/codecov-commenter))
- Add test module for conversation magic [#323](https://github.com/Calysto/metakernel/pull/323) ([@blink1073](https://github.com/blink1073), [@claude](https://github.com/claude), [@codecov-commenter](https://github.com/codecov-commenter))
- Add test module for brain magic [#322](https://github.com/Calysto/metakernel/pull/322) ([@blink1073](https://github.com/blink1073), [@claude](https://github.com/claude), [@codecov-commenter](https://github.com/codecov-commenter))
- Add test module for blockly magic and fix register_magics bug [#321](https://github.com/Calysto/metakernel/pull/321) ([@blink1073](https://github.com/blink1073), [@codecov-commenter](https://github.com/codecov-commenter))
- Add test module for scheme magic [#320](https://github.com/Calysto/metakernel/pull/320) ([@blink1073](https://github.com/blink1073), [@codecov-commenter](https://github.com/codecov-commenter))
- Bump cairosvg from 1.0.22 to 2.7.0 [#319](https://github.com/Calysto/metakernel/pull/319) ([@blink1073](https://github.com/blink1073))
- Add Windows CI job running just test-all [#318](https://github.com/Calysto/metakernel/pull/318) ([@blink1073](https://github.com/blink1073), [@codecov-commenter](https://github.com/codecov-commenter))
- Bump pillow from 11.3.0 to 12.1.1 [#317](https://github.com/Calysto/metakernel/pull/317) ([@blink1073](https://github.com/blink1073))
- Add test-all dependency group, activity and matplotlib magic tests [#316](https://github.com/Calysto/metakernel/pull/316) ([@blink1073](https://github.com/blink1073), [@codecov-commenter](https://github.com/codecov-commenter))
- Remove Python 2 compatibility shims and modernize string formatting [#315](https://github.com/Calysto/metakernel/pull/315) ([@blink1073](https://github.com/blink1073), [@codecov-commenter](https://github.com/codecov-commenter))
- Bump the actions group with 3 updates [#314](https://github.com/Calysto/metakernel/pull/314) ([@blink1073](https://github.com/blink1073))
- Add more pre-commit hooks and stricter typing [#312](https://github.com/Calysto/metakernel/pull/312) ([@blink1073](https://github.com/blink1073), [@codecov-commenter](https://github.com/codecov-commenter))
- Add rtd config [#311](https://github.com/Calysto/metakernel/pull/311) ([@blink1073](https://github.com/blink1073), [@codecov-commenter](https://github.com/codecov-commenter))
- Add documentation for creating a new MetaKernel-based kernel [#310](https://github.com/Calysto/metakernel/pull/310) ([@blink1073](https://github.com/blink1073))
- Add CodeQL analysis workflow configuration [#309](https://github.com/Calysto/metakernel/pull/309) ([@blink1073](https://github.com/blink1073))
- Add Codecov coverage upload [#308](https://github.com/Calysto/metakernel/pull/308) ([@blink1073](https://github.com/blink1073), [@codecov-commenter](https://github.com/codecov-commenter))
- Refactor test jobs [#307](https://github.com/Calysto/metakernel/pull/307) ([@blink1073](https://github.com/blink1073))
- Covert top level RST files to Markdown [#306](https://github.com/Calysto/metakernel/pull/306) ([@blink1073](https://github.com/blink1073))
- Switch to just and uv for development tooling [#305](https://github.com/Calysto/metakernel/pull/305) ([@blink1073](https://github.com/blink1073))
- Add pre-commit hooks with ruff, actionlint, and mdformat [#304](https://github.com/Calysto/metakernel/pull/304) ([@blink1073](https://github.com/blink1073))
- Move tests to top-level tests/ directory [#303](https://github.com/Calysto/metakernel/pull/303) ([@blink1073](https://github.com/blink1073))
- Fix deprecation warning pyparsing [#298](https://github.com/Calysto/metakernel/pull/298) ([@blink1073](https://github.com/blink1073))
- Bump actions/checkout from 4 to 6 [#297](https://github.com/Calysto/metakernel/pull/297) ([@blink1073](https://github.com/blink1073))

### Other merged PRs

- Added mit-scheme-kernel [#293](https://github.com/Calysto/metakernel/pull/293) ([@twaclaw](https://github.com/twaclaw), [@blink1073](https://github.com/blink1073))

### Contributors to this release

The following people contributed discussions, new ideas, code and documentation contributions, and review.
See [our definition of contributors](https://github-activity.readthedocs.io/en/latest/use/#how-does-this-tool-define-contributions-in-the-reports).

([GitHub contributors page for this release](https://github.com/Calysto/metakernel/graphs/contributors?from=2025-11-05&to=2026-03-03&type=c))

@blink1073 ([activity](https://github.com/search?q=repo%3ACalysto%2Fmetakernel+involves%3Ablink1073+updated%3A2025-11-05..2026-03-03&type=Issues)) | @claude ([activity](https://github.com/search?q=repo%3ACalysto%2Fmetakernel+involves%3Aclaude+updated%3A2025-11-05..2026-03-03&type=Issues)) | @codecov-commenter ([activity](https://github.com/search?q=repo%3ACalysto%2Fmetakernel+involves%3Acodecov-commenter+updated%3A2025-11-05..2026-03-03&type=Issues)) | @morlic ([activity](https://github.com/search?q=repo%3ACalysto%2Fmetakernel+involves%3Amorlic+updated%3A2025-11-05..2026-03-03&type=Issues)) | @twaclaw ([activity](https://github.com/search?q=repo%3ACalysto%2Fmetakernel+involves%3Atwaclaw+updated%3A2025-11-05..2026-03-03&type=Issues))

## 0.30.4

([Full Changelog](https://github.com/Calysto/metakernel/compare/v0.30.3...2fca1dcee729103a986e9a12c3cfc9dd9d00c73e))

### Maintenance and upkeep improvements

- Add support for ipykernel 7 and update supported Python versions [#296](https://github.com/Calysto/metakernel/pull/296) ([@blink1073](https://github.com/blink1073))
- Bump actions/create-github-app-token from 1 to 2 [#292](https://github.com/Calysto/metakernel/pull/292) ([@dependabot](https://github.com/dependabot))
- Update supported Pythons and fix links [#291](https://github.com/Calysto/metakernel/pull/291) ([@blink1073](https://github.com/blink1073))

### Contributors to this release

([GitHub contributors page for this release](https://github.com/Calysto/metakernel/graphs/contributors?from=2025-04-02&to=2025-11-05&type=c))

[@blink1073](https://github.com/search?q=repo%3ACalysto%2Fmetakernel+involves%3Ablink1073+updated%3A2025-04-02..2025-11-05&type=Issues) | [@dependabot](https://github.com/search?q=repo%3ACalysto%2Fmetakernel+involves%3Adependabot+updated%3A2025-04-02..2025-11-05&type=Issues)

## 0.30.3

([Full Changelog](https://github.com/Calysto/metakernel/compare/v0.30.2...864d7a2d768b082d7e86a102dde883845db27035))

### Maintenance and upkeep improvements

- Add ipython 9 compat [#290](https://github.com/Calysto/metakernel/pull/290) ([@blink1073](https://github.com/blink1073))
- Fix min version test [#278](https://github.com/Calysto/metakernel/pull/278) ([@blink1073](https://github.com/blink1073))

### Contributors to this release

([GitHub contributors page for this release](https://github.com/Calysto/metakernel/graphs/contributors?from=2024-03-26&to=2025-04-02&type=c))

[@blink1073](https://github.com/search?q=repo%3ACalysto%2Fmetakernel+involves%3Ablink1073+updated%3A2024-03-26..2025-04-02&type=Issues) | [@dsblank](https://github.com/search?q=repo%3ACalysto%2Fmetakernel+involves%3Adsblank+updated%3A2024-03-26..2025-04-02&type=Issues)

## 0.30.2

([Full Changelog](https://github.com/Calysto/metakernel/compare/v0.30.1...16f88e281040b5698b5eec32b580854424a236f7))

### Maintenance and upkeep improvements

- Add Release Workflows [#277](https://github.com/Calysto/metakernel/pull/277) ([@blink1073](https://github.com/blink1073))
- Pin upper version of ipykernel [#276](https://github.com/Calysto/metakernel/pull/276) ([@blink1073](https://github.com/blink1073))
- Clean up CI [#273](https://github.com/Calysto/metakernel/pull/273) ([@blink1073](https://github.com/blink1073))

### Other merged PRs

- Fix installation code blocks in readme [#274](https://github.com/Calysto/metakernel/pull/274) ([@Phoenix616](https://github.com/Phoenix616))

### Contributors to this release

([GitHub contributors page for this release](https://github.com/Calysto/metakernel/graphs/contributors?from=2023-09-11&to=2024-03-26&type=c))

[@blink1073](https://github.com/search?q=repo%3ACalysto%2Fmetakernel+involves%3Ablink1073+updated%3A2023-09-11..2024-03-26&type=Issues) | [@Phoenix616](https://github.com/search?q=repo%3ACalysto%2Fmetakernel+involves%3APhoenix616+updated%3A2023-09-11..2024-03-26&type=Issues)

## 0.30.1

([Full Changelog](https://github.com/Calysto/metakernel/compare/v0.30.0...0ab2d9b2e46acc10bd86ca79d18afc423eeef7eb))

### Maintenance and upkeep improvements

- Adapt to Python 3.12.0rc2 [#272](https://github.com/Calysto/metakernel/pull/272) ([@ellert](https://github.com/ellert))
- Bump actions/checkout from 3 to 4 [#271](https://github.com/Calysto/metakernel/pull/271) ([@dependabot](https://github.com/dependabot))

### Contributors to this release

([GitHub contributors page for this release](https://github.com/Calysto/metakernel/graphs/contributors?from=2023-08-29&to=2023-09-11&type=c))

[@dependabot](https://github.com/search?q=repo%3ACalysto%2Fmetakernel+involves%3Adependabot+updated%3A2023-08-29..2023-09-11&type=Issues) | [@ellert](https://github.com/search?q=repo%3ACalysto%2Fmetakernel+involves%3Aellert+updated%3A2023-08-29..2023-09-11&type=Issues)

## 0.30.0

([Full Changelog](https://github.com/Calysto/metakernel/compare/v0.29.5...c9350d39036218f82bff6eb90685d1d3c964cba1))

### Enhancements made

- Updated dot magic, with tests [#268](https://github.com/Calysto/metakernel/pull/268) ([@dsblank](https://github.com/dsblank))

### Bugs fixed

- Update tests.yml [#270](https://github.com/Calysto/metakernel/pull/270) ([@dsblank](https://github.com/dsblank))
- Fix magic completion [#269](https://github.com/Calysto/metakernel/pull/269) ([@dsblank](https://github.com/dsblank))

### Contributors to this release

([GitHub contributors page for this release](https://github.com/Calysto/metakernel/graphs/contributors?from=2023-07-10&to=2023-08-29&type=c))

[@blink1073](https://github.com/search?q=repo%3ACalysto%2Fmetakernel+involves%3Ablink1073+updated%3A2023-07-10..2023-08-29&type=Issues) | [@dsblank](https://github.com/search?q=repo%3ACalysto%2Fmetakernel+involves%3Adsblank+updated%3A2023-07-10..2023-08-29&type=Issues)

## 0.29.5

([Full Changelog](https://github.com/Calysto/metakernel/compare/v0.29.4...7fd364a76586c5312d4afe7ea4c0307434b69693))

### Maintenance and upkeep improvements

- Ignore DeprecationWarnings for datetime.utcnow() [#265](https://github.com/Calysto/metakernel/pull/265) ([@ellert](https://github.com/ellert))
- Update docs config [#263](https://github.com/Calysto/metakernel/pull/263) ([@blink1073](https://github.com/blink1073))
- Update ci badge [#262](https://github.com/Calysto/metakernel/pull/262) ([@blink1073](https://github.com/blink1073))

### Documentation improvements

- Change nbviewer URL to use Jupyter [#264](https://github.com/Calysto/metakernel/pull/264) ([@rgbkrk](https://github.com/rgbkrk))

### Contributors to this release

([GitHub contributors page for this release](https://github.com/Calysto/metakernel/graphs/contributors?from=2022-12-12&to=2023-07-10&type=c))

[@blink1073](https://github.com/search?q=repo%3ACalysto%2Fmetakernel+involves%3Ablink1073+updated%3A2022-12-12..2023-07-10&type=Issues) | [@ellert](https://github.com/search?q=repo%3ACalysto%2Fmetakernel+involves%3Aellert+updated%3A2022-12-12..2023-07-10&type=Issues) | [@rgbkrk](https://github.com/search?q=repo%3ACalysto%2Fmetakernel+involves%3Argbkrk+updated%3A2022-12-12..2023-07-10&type=Issues)

## 0.29.4

([Full Changelog](https://github.com/Calysto/metakernel/compare/v0.29.3...5ec51d6828bf079b7ee2007f6351f4321434b49e))

### Maintenance and upkeep improvements

- Add back magics tests [#261](https://github.com/Calysto/metakernel/pull/261) ([@ellert](https://github.com/ellert))
- Update tests for widgets 8 [#260](https://github.com/Calysto/metakernel/pull/260) ([@blink1073](https://github.com/blink1073))

### Contributors to this release

([GitHub contributors page for this release](https://github.com/Calysto/metakernel/graphs/contributors?from=2022-12-01&to=2022-12-12&type=c))

[@blink1073](https://github.com/search?q=repo%3ACalysto%2Fmetakernel+involves%3Ablink1073+updated%3A2022-12-01..2022-12-12&type=Issues) | [@ellert](https://github.com/search?q=repo%3ACalysto%2Fmetakernel+involves%3Aellert+updated%3A2022-12-01..2022-12-12&type=Issues)

## 0.29.3

([Full Changelog](https://github.com/Calysto/metakernel/compare/v0.29.2...758c19d08fc74daff077b242c0fae30f82313479))

### Maintenance and upkeep improvements

- Bump actions/checkout from 2 to 3 [#258](https://github.com/Calysto/metakernel/pull/258) ([@dependabot](https://github.com/dependabot))
- Maintenance cleanup [#257](https://github.com/Calysto/metakernel/pull/257) ([@blink1073](https://github.com/blink1073))
- Use hatch for example projects [#256](https://github.com/Calysto/metakernel/pull/256) ([@blink1073](https://github.com/blink1073))

### Contributors to this release

([GitHub contributors page for this release](https://github.com/Calysto/metakernel/graphs/contributors?from=2022-08-08&to=2022-12-01&type=c))

[@blink1073](https://github.com/search?q=repo%3ACalysto%2Fmetakernel+involves%3Ablink1073+updated%3A2022-08-08..2022-12-01&type=Issues) | [@dependabot](https://github.com/search?q=repo%3ACalysto%2Fmetakernel+involves%3Adependabot+updated%3A2022-08-08..2022-12-01&type=Issues)

## 0.29.2

([Full Changelog](https://github.com/Calysto/metakernel/compare/v0.29.1...dbe3fc91a87bca68412faf640b58778204102b29))

### Bugs fixed

- Restore versions of metakernel-echo and metakernel-python [#252](https://github.com/Calysto/metakernel/pull/252) ([@ellert](https://github.com/ellert))

### Maintenance and upkeep improvements

- Switch to hatch backend [#254](https://github.com/Calysto/metakernel/pull/254) ([@blink1073](https://github.com/blink1073))

### Contributors to this release

([GitHub contributors page for this release](https://github.com/Calysto/metakernel/graphs/contributors?from=2022-08-01&to=2022-08-08&type=c))

[@blink1073](https://github.com/search?q=repo%3ACalysto%2Fmetakernel+involves%3Ablink1073+updated%3A2022-08-01..2022-08-08&type=Issues) | [@ellert](https://github.com/search?q=repo%3ACalysto%2Fmetakernel+involves%3Aellert+updated%3A2022-08-01..2022-08-08&type=Issues)

## 0.29.1

([Full Changelog](https://github.com/Calysto/metakernel/compare/v0.29.0...68b0da7ad71de8e9802c9ab573344a3ea0a1a832))

### Bugs fixed

- Strip paste-bracketing control characters [#250](https://github.com/Calysto/metakernel/pull/250) ([@anewusername](https://github.com/anewusername))

### Maintenance and upkeep improvements

- Address deprecation warnings [#249](https://github.com/Calysto/metakernel/pull/249) ([@ellert](https://github.com/ellert))
- Switch to flit build backend [#246](https://github.com/Calysto/metakernel/pull/246) ([@blink1073](https://github.com/blink1073))

### Documentation improvements

- Correct spelling mistakes [#248](https://github.com/Calysto/metakernel/pull/248) ([@EdwardBetts](https://github.com/EdwardBetts))

### Contributors to this release

([GitHub contributors page for this release](https://github.com/Calysto/metakernel/graphs/contributors?from=2022-03-29&to=2022-08-01&type=c))

[@anewusername](https://github.com/search?q=repo%3ACalysto%2Fmetakernel+involves%3Aanewusername+updated%3A2022-03-29..2022-08-01&type=Issues) | [@blink1073](https://github.com/search?q=repo%3ACalysto%2Fmetakernel+involves%3Ablink1073+updated%3A2022-03-29..2022-08-01&type=Issues) | [@EdwardBetts](https://github.com/search?q=repo%3ACalysto%2Fmetakernel+involves%3AEdwardBetts+updated%3A2022-03-29..2022-08-01&type=Issues) | [@ellert](https://github.com/search?q=repo%3ACalysto%2Fmetakernel+involves%3Aellert+updated%3A2022-03-29..2022-08-01&type=Issues)

## 0.29.0

([Full Changelog](https://github.com/Calysto/metakernel/compare/v0.28.2...a339b3976ede13e5813f1f078acc031d6999f412))

### Maintenance and upkeep improvements

- Clean up testing and add more CI [#244](https://github.com/Calysto/metakernel/pull/244) ([@blink1073](https://github.com/blink1073))
- Fix macos tests [#243](https://github.com/Calysto/metakernel/pull/243) ([@blink1073](https://github.com/blink1073))
- Clean up CI and bump supported pythons [#242](https://github.com/Calysto/metakernel/pull/242) ([@blink1073](https://github.com/blink1073))

### Contributors to this release

([GitHub contributors page for this release](https://github.com/Calysto/metakernel/graphs/contributors?from=2021-12-02&to=2022-03-29&type=c))

[@blink1073](https://github.com/search?q=repo%3ACalysto%2Fmetakernel+involves%3Ablink1073+updated%3A2021-12-02..2022-03-29&type=Issues)

## 0.28.2

- Test with jupyter_kernel_test [#238](https://github.com/Calysto/metakernel/pull/238) ([@blink1073](https://github.com/blink1073))

## 0.28.1

- Fix trove classifier [#236](https://github.com/Calysto/metakernel/pull/236) ([@blink1073](https://github.com/blink1073))

## 0.28.0

*Note* This was not uploaded to PyPI because it had an incorrect trove classifier

- Add support for jupyter releaser [#234](https://github.com/Calysto/metakernel/pull/234) ([@blink1073](https://github.com/blink1073))
- Modernize build and test [#233](https://github.com/Calysto/metakernel/pull/233) ([@blink1073](https://github.com/blink1073))
- Fix Iframe display issue [#231](https://github.com/Calysto/metakernel/pull/231) ([@cathalmccabe](https://github.com/cathalmccabe))
- Add a blockly magic instead of a jigsaw magic [#229](https://github.com/Calysto/metakernel/pull/229) ([@ChrisJaunes](https://github.com/ChrisJaunes))

## 0.27.5

- Escape backslashes in strings [#226](https://github.com/Calysto/metakernel/pull/226) ([@ellert](https://github.com/ellert))
- Add missing dollar signs to %latex examples and tests [#225](https://github.com/Calysto/metakernel/pull/225) ([@ellert](https://github.com/ellert))
- Support older jedi versions [#224](https://github.com/Calysto/metakernel/pull/224) ([@ellert](https://github.com/ellert))

## 0.27.4

- Add support for `SOURCE_DATE_EPOCH` [#223](https://github.com/Calysto/metakernel/pull/223) ([@jnahmias](https://github.com/jnahmias))

## 0.27.3

- Fix warnings when running tests under python 3.9 [#222](https://github.com/Calysto/metakernel/pull/222) ([@jnahmias](https://github.com/jnahmias))

## 0.27.2

- Use `TERM=dumb` for bash `REPLWrapper` [#221](https://github.com/Calysto/metakernel/pull/221) ([@jnahmias](https://github.com/jnahmias))
- Use `tempfile` instead of writing to `cwd` [#220](https://github.com/Calysto/metakernel/pull/220) ([@jnahmias](https://github.com/jnahmias))

## 0.27.0

- More `py2` removal [#219](https://github.com/Calysto/metakernel/pull/219) ([@blink1073](https://github.com/blink1073))
- Remove `py2` [#218](https://github.com/Calysto/metakernel/pull/218) ([@joequant](https://github.com/joequant))
- Monkey patch display to output to kernel [#216](https://github.com/Calysto/metakernel/pull/216) ([@joequant](https://github.com/joequant))
- Fix warnings [#215](https://github.com/Calysto/metakernel/pull/215) ([@joequant](https://github.com/joequant))

## 0.26.1

- Dev/fix `retval` in `exec` [#214](https://github.com/Calysto/metakernel/pull/214) ([@joequant](https://github.com/joequant))

## 0.26.0

- Combine `exec`/`eval` evaluators [#213](https://github.com/Calysto/metakernel/pull/213) ([@joequant](https://github.com/joequant))
- Dev/fix `voila` [#212](https://github.com/Calysto/metakernel/pull/212) ([@joequant](https://github.com/joequant))
- Add `Error_display` method to `_metakernel.py` [#205](https://github.com/Calysto/metakernel/pull/205) ([@jld23](https://github.com/jld23))

## 0.25.0

- Fix python evals #208 [#210](https://github.com/Calysto/metakernel/pull/210) ([@joequant](https://github.com/joequant))
- Fix `ipywidgets` display [#209](https://github.com/Calysto/metakernel/pull/209) ([@joequant](https://github.com/joequant))

## v0.24.4

- Remove undefined line in expect stdin #203 [#204](https://github.com/Calysto/metakernel/pull/204) ([@dekuenstle](https://github.com/dekuenstle))
- Add `portalocker` and `ipyparallel` as optional dependencies [#202](https://github.com/Calysto/metakernel/pull/202) ([@mdeff](https://github.com/mdeff))

## v0.24.3

- Update `activity_magic.py` [#197](https://github.com/Calysto/metakernel/pull/197) ([@dovfields](https://github.com/dovfields))

## v0.24.2

- Fix `TypeError` [#192](https://github.com/Calysto/metakernel/pull/192) ([@ellert](https://github.com/ellert))

## v0.24.1

- Delay creating wrapper until we need to execute [#190](https://github.com/Calysto/metakernel/pull/190) ([@blink1073](https://github.com/blink1073))

## v0.24.0

- Add the full license [#189](https://github.com/Calysto/metakernel/pull/189) ([@toddrme2178](https://github.com/toddrme2178))
- Clean up stream/line handling for process kernels [#188](https://github.com/Calysto/metakernel/pull/188) ([@blink1073](https://github.com/blink1073))
- Remove local bash kernel and point to `calysto_bash` [#186](https://github.com/Calysto/metakernel/pull/186) ([@blink1073](https://github.com/blink1073))

## v0.23.0

- Clean up configurability handling and docs [#184](https://github.com/Calysto/metakernel/pull/184) ([@blink1073](https://github.com/blink1073))

## v0.22.0

- Add settings handling [#182](https://github.com/Calysto/metakernel/pull/182) ([@blink1073](https://github.com/blink1073))

## v0.21.3

- Switch to powershell on windows [#181](https://github.com/Calysto/metakernel/pull/181) ([@blink1073](https://github.com/blink1073))

## v0.21.2

- Clean up `replwrap` prompt handling [#180](https://github.com/Calysto/metakernel/pull/180) ([@blink1073](https://github.com/blink1073))

## v0.21.1

- Avoid double printing output in process kernels [#179](https://github.com/Calysto/metakernel/pull/179) ([@blink1073](https://github.com/blink1073))

## v0.21.0

- Carriage Return Handling for `ProcessKernel` [#178](https://github.com/Calysto/metakernel/pull/178) ([@blink1073](https://github.com/blink1073))
- Fix handling metadata in `_formatter` [#174](https://github.com/Calysto/metakernel/pull/174) ([@ccordoba12](https://github.com/ccordoba12))
- Fix for Python 2 compatibility [#173](https://github.com/Calysto/metakernel/pull/173) ([@ccordoba12](https://github.com/ccordoba12))
- Allow to redefine default MetaKernel magics with custom ones [#172](https://github.com/Calysto/metakernel/pull/172) ([@ccordoba12](https://github.com/ccordoba12))
- Don't rely on `'python'` in path during testing [#169](https://github.com/Calysto/metakernel/pull/169) ([@ellert](https://github.com/ellert))
- Include `LICENSE.txt` file in wheels [#168](https://github.com/Calysto/metakernel/pull/168) ([@toddrme2178](https://github.com/toddrme2178))

## v0.20.13

- Fix display of output in Bash kernel [#160](https://github.com/Calysto/metakernel/pull/160) ([@ellert](https://github.com/ellert))
- Use `sys.executable` when creating `kernel.json` [#159](https://github.com/Calysto/metakernel/pull/159) ([@ellert](https://github.com/ellert))

## v0.20.12

- Expose the prompt change cmd [#157](https://github.com/Calysto/metakernel/pull/157) ([@blink1073](https://github.com/blink1073))

## v0.20.11

- Replwrap fixes [#156](https://github.com/Calysto/metakernel/pull/156) ([@blink1073](https://github.com/blink1073))

## v0.20.10

- Clean up handling of command and args [#155](https://github.com/Calysto/metakernel/pull/155) ([@blink1073](https://github.com/blink1073))

## v0.20.9

- Allow a list to be passed as the command [#154](https://github.com/Calysto/metakernel/pull/154) ([@blink1073](https://github.com/blink1073))

## v0.20.8

- Fix handling of fallback images [#153](https://github.com/Calysto/metakernel/pull/153) ([@blink1073](https://github.com/blink1073))

## v0.20.6

- Get kernel images from package if possible [#152](https://github.com/Calysto/metakernel/pull/152) ([@blink1073](https://github.com/blink1073))
- Version 0.20.5 [#151](https://github.com/Calysto/metakernel/pull/151) ([@dsblank](https://github.com/dsblank))

## v0.20.1

- Adding call to close on child pty [#141](https://github.com/Calysto/metakernel/pull/141) ([@Daniel-V1](https://github.com/Daniel-V1))

## v0.20.0

- Mark tests that use the network [#139](https://github.com/Calysto/metakernel/pull/139) ([@QuLogic](https://github.com/QuLogic))
- Restore Jedi 0.9 compatibility [#138](https://github.com/Calysto/metakernel/pull/138) ([@QuLogic](https://github.com/QuLogic))
- Update versions of MetaKernel kernels. [#137](https://github.com/Calysto/metakernel/pull/137) ([@QuLogic](https://github.com/QuLogic))
- Remove shell ambiguity [#134](https://github.com/Calysto/metakernel/pull/134) ([@blink1073](https://github.com/blink1073))

## v0.19.0

- Require ipykernel [#132](https://github.com/Calysto/metakernel/pull/132) ([@blink1073](https://github.com/blink1073))
- Make help logic more robust [#131](https://github.com/Calysto/metakernel/pull/131) ([@blink1073](https://github.com/blink1073))
- Update for jedi 0.10 [#129](https://github.com/Calysto/metakernel/pull/129) ([@blink1073](https://github.com/blink1073))
- Clean up kernel magic [#128](https://github.com/Calysto/metakernel/pull/128) ([@blink1073](https://github.com/blink1073))

## v0.18.2

- Use clrf for end of line response from process [#124](https://github.com/Calysto/metakernel/pull/124) ([@blink1073](https://github.com/blink1073))

## v0.18.1

- Fix shell magic on Windows [#123](https://github.com/Calysto/metakernel/pull/123) ([@blink1073](https://github.com/blink1073))

## v0.18.0

- Replwrap cleanup [#122](https://github.com/Calysto/metakernel/pull/122) ([@blink1073](https://github.com/blink1073))

## v0.17.0

- Added support for better error handling to metakernel [#121](https://github.com/Calysto/metakernel/pull/121) ([@mariusvniekerk](https://github.com/mariusvniekerk))

## v0.16.0

- Add support for stdin requests and clean up replwrap [#120](https://github.com/Calysto/metakernel/pull/120) ([@blink1073](https://github.com/blink1073))
- Improvements to bash handling from bash_kernel [#119](https://github.com/Calysto/metakernel/pull/119) ([@blink1073](https://github.com/blink1073))
- Clean up plot magic handling and add width/height options [#118](https://github.com/Calysto/metakernel/pull/118) ([@blink1073](https://github.com/blink1073))
- Use pexpect and clean up handling of replwrap [#117](https://github.com/Calysto/metakernel/pull/117) ([@blink1073](https://github.com/blink1073))

## v0.15.1

- Better handling of ipywidgets import [#114](https://github.com/Calysto/metakernel/pull/114) ([@blink1073](https://github.com/blink1073))
- Expose path escaper. [#110](https://github.com/Calysto/metakernel/pull/110) ([@anntzer](https://github.com/anntzer))
- Remove workaround [#109](https://github.com/Calysto/metakernel/pull/109) ([@dsblank](https://github.com/dsblank))
- Save history as JSON, to handle multiline entries. [#105](https://github.com/Calysto/metakernel/pull/105) ([@anntzer](https://github.com/anntzer))

## v0.13.1

- Fix kernelspec install. [#98](https://github.com/Calysto/metakernel/pull/98) ([@anntzer](https://github.com/anntzer))
- New kernelspec install. [#97](https://github.com/Calysto/metakernel/pull/97) ([@anntzer](https://github.com/anntzer))

## v0.12.1

- Remove redundant if statement. [#89](https://github.com/Calysto/metakernel/pull/89) ([@bsvh](https://github.com/bsvh))
- wrap output in TextOutput in ProcessMetaKernel [#88](https://github.com/Calysto/metakernel/pull/88) ([@minrk](https://github.com/minrk))
- Allow long running tasks to print [#86](https://github.com/Calysto/metakernel/pull/86) ([@blink1073](https://github.com/blink1073))
- Fix import from ipywidgets [#85](https://github.com/Calysto/metakernel/pull/85) ([@has2k1](https://github.com/has2k1))

## v0.11.7

- still timeout=None seems to be ignored [#84](https://github.com/Calysto/metakernel/pull/84) ([@schlichtanders](https://github.com/schlichtanders))

## v0.11.6

- bug fixed timeout=None [#83](https://github.com/Calysto/metakernel/pull/83) ([@schlichtanders](https://github.com/schlichtanders))
- Fix intermittent failing "ls" test [#82](https://github.com/Calysto/metakernel/pull/82) ([@blink1073](https://github.com/blink1073))
- Fix handling of multiple commands [#81](https://github.com/Calysto/metakernel/pull/81) ([@blink1073](https://github.com/blink1073))

## v0.11.5

- Fix handling of multiple commands [#81](https://github.com/Calysto/metakernel/pull/81) ([@blink1073](https://github.com/blink1073))
- Make widgets optional [#77](https://github.com/Calysto/metakernel/pull/77) ([@blink1073](https://github.com/blink1073))
- Jupyter 4 test [#75](https://github.com/Calysto/metakernel/pull/75) ([@blink1073](https://github.com/blink1073))
