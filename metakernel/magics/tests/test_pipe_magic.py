from metakernel.tests.utils import (get_kernel, get_log_text, EvalKernel,
                                    clear_log_text)


def test_pipe_magic():
    kernel = get_kernel(EvalKernel)
    kernel.do_execute("""

def upper(text):
    return text.upper()

def lower(text):
    return text.lower()

def pl_word(word):
    if len(word) > 3:
        return word[1:] + word[0] + "ay"
    else:
        return word

def piglatin(text):
    return " ".join([pl_word(word) for word in text.split(" ")])

""")
    kernel.do_execute("""%%pipe upper
this is a test
 """)
    text = get_log_text(kernel)
    assert "THIS IS A TEST" in text, ("text: " + text)

    kernel.do_execute("""%%pipe upper | piglatin
this is a test
 """)
    text = get_log_text(kernel)
    assert "HISTay IS A ESTTay" in text, ("text: " + text)

    kernel.do_execute("""%%pipe piglatin | upper
this is a test
 """)
    text = get_log_text(kernel)
    assert "HISTAY IS A ESTTAY" in text, ("text: " + text)

    kernel.do_execute("""%%pipe piglatin | upper | lower
this is a test
 """)
    text = get_log_text(kernel)
    assert "histay is a esttay" in text, ("text: " + text)
    clear_log_text(kernel)


