# Cell Magics

## `%%debug`

%%debug - step through the code expression by expression

This cell magic will step through the code in the cell,
if the kernel supports debugging.

Example:
    %%debug

    (define x 1)

## `%%file`

%%file [--append|-a] FILENAME - write contents of cell to file

This cell magic will create or append the cell contents into/onto
a file.

Example:
    %%file -a log.txt
    This will append this line onto the file "log.txt"


Options:
-------
-a --append    append onto an existing file [default: False]

## `%%help`



## `%%html`

%%html - display contents of cell as HTML

This cell magic will send the cell to the browser as
HTML.

Example:
    %%html

    <script src="..."></script>

    <div>Contents of div tag</div>

## `%%javascript`

%%javascript - send contents of cell as JavaScript

This cell magic will execute the contents of the cell as
JavaScript in the browser.

Example:
    %%javascript

    element.html("Hello this is <b>bold</b>!")

## `%%kx`

%%kx [-k NAME] - send the cell code to the kernel.

This cell magic will send the cell to be evaluated by
the kernel. The kernel must have been created use the
%%kernel magic.

Returns the result of the execution as output.

Example:

    %%kernel bash
    ls -al

Use `%kernel MODULE CLASS [-k NAME]` to create a kernel.

Options:
-------
-k --kernel_name kernel name given to use for execution [default: None]

## `%%latex`

%%latex - display contents of cell as LaTeX

This cell magic will display the TEXT in the cell as LaTeX.

Example:
    %%latex
    x_1 = \dfrac{a}{b}

    x_2 = a^{n - 1}

## `%%processing`

%%processing - run the cell in the language Processing

This cell magic will execute the contents of the cell as a
Processing program. This uses the Java-based Processing
language.

Example:

    %%processing
    setup() {
    }
    draw() {
    }

## `%%px`

%%px - send cell to the cluster.

Example:

    %%px
    (define x 42)

Use %parallel to initialize the cluster.

Options:
-------
-e --evaluate  evaluate code in the current kernel, too. The current kernel should be of the same language as the cluster. [default: False]
-k --kernel_name kernel name given to use for execution [default: None]

## `%%python`

%%python - evaluate contents of cell as Python

This cell magic will evaluate the cell (either expression or
statement) as Python code.

Unlike IPython's Python, this does not return the last expression.
To do that, you need to assign the last expression to the special
variable "retval".

The -e or --eval_output flag signals that the retval value expression
will be used as code for the cell to be evaluated by the host
language.

Examples:
    %%python
    x = 42

    %%python
    import math
    retval = x + math.pi

    %%python -e
    retval = "'(this is code in the kernel language)"

    %%python -e
    "'(this is code in the kernel language)"


Options:
-------
-e --eval_output Use the retval value from the Python cell as code in the kernel language. [default: False]

## `%%shell`

 %%shell - run the contents of the cell as shell commands

 This shell command will run the cell contents in the bash shell.

 Example:
     %%shell
        cd ..
        ls -al

Note: this is a persistent connection to a shell.
  The working directory is synchronized to that of the notebook
  before and after each call.

 You can also use "!!" instead of "%%shell".

## `%%show`

%%show [-o]- show cell contents or results in system pager

This cell magic will put the contents or results of the cell
into the system pager.

Examples:
    %%show
    This information will appear in the pager.

    %%show --output
    retval = 54 * 54

Options:
-------
-o --output    rather than showing the contents, show the results [default: False]

## `%%spell`

%%spell NAME - learn a new spell

This cell magic will learn the spell in the
cell. The cell contents are just commands (magics
or code in the kernel language).

Example:
    %%spell test
    print "Ok!"

    %spell test
    Ok!

## `%%time`

%%time - show time to run cell

Put this magic at the top of a cell and the amount of time
taken to execute the code will be displayed before the output.

Example:
    %%time
    [code for your language goes here!]

This just reports real time taken to execute a program. This
may fluctuate with number of users, system, load, etc.

