# Changelog Entries

<!-- <START NEW CHANGELOG ENTRY> -->

## 0.29.0

([Full Changelog](https://github.com/Calysto/metakernel/compare/v0.28.2...a339b3976ede13e5813f1f078acc031d6999f412))

### Maintenance and upkeep improvements

- Clean up testing and add more CI [#244](https://github.com/Calysto/metakernel/pull/244) ([@blink1073](https://github.com/blink1073))
- Fix macos tests [#243](https://github.com/Calysto/metakernel/pull/243) ([@blink1073](https://github.com/blink1073))
- Clean up CI and bump supported pythons [#242](https://github.com/Calysto/metakernel/pull/242) ([@blink1073](https://github.com/blink1073))

### Contributors to this release

([GitHub contributors page for this release](https://github.com/Calysto/metakernel/graphs/contributors?from=2021-12-02&to=2022-03-29&type=c))

[@blink1073](https://github.com/search?q=repo%3ACalysto%2Fmetakernel+involves%3Ablink1073+updated%3A2021-12-02..2022-03-29&type=Issues)

<!-- <END NEW CHANGELOG ENTRY> -->

## 0.28.2

- Test with jupyter_kernel_test [#238](https://github.com/Calysto/metakernel/pull/238) ([@blink1073](https://github.com/blink1073))

## 0.28.1

- Fix trove classifier [#236](https://github.com/Calysto/metakernel/pull/236) ([@blink1073](https://github.com/blink1073))

## 0.28.0

*Note*  This was not uploaded to PyPI because it had an incorrect trove classifier

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
